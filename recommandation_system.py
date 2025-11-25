from apiclient.discovery import build
from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

# -----------------
# 1. Configuration
# -----------------
DEVELOPER_KEY="AIzaSyBEqm0H0QqlxWuCj9WWGzWa7X6RwyFBg2w"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# -----------------
# 2. Keyword Extraction (KeyBERT - Multilingual)
# -----------------

def Extrcat_Keywords(summary):
  
  MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
  kw_model = KeyBERT(MODEL_NAME) 

  keywords = kw_model.extract_keywords(
    summary,
    keyphrase_ngram_range=(1,2), 
    use_mmr=True,                  
    diversity=0.5,                
    top_n=3,                       
   
)
  search_keywords = [kw[0] for kw in keywords] 
  search_query = " ".join(search_keywords)
  return search_query

# -----------------
# 3. YouTube Search
# -----------------

def Search_key_words(search_query , max_result):
  """
  get Videos from Youtube with content_based filteration
  search_query -> Keywords of Summary to search with
  max_result -> number of results to return
  """
  # creating Youtube Resource Object
  try:
      Youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
  except Exception as e:
      print(f"Error initializing YouTube API: {e}")

  search_response = Youtube_object.search().list(q=search_query,part="id, snippet",maxResults=max_result,type="video").execute()
  results = search_response.get("items", [])

  #  get info of vedios
  video_details = []
  for item in results:
      snippet = item["snippet"]
      full_content = snippet["title"] + " " + snippet["description"] # Preparing the full video content (Title + Description)
      # save information of videos
      video_details.append({
              "title": snippet["title"],
              "description": snippet["description"],
              "full_content": full_content,
              "video_id": item["id"]["videoId"],
              "recommandations_score":0    # Initializing score
          })
  return video_details

# -----------------
# 4. Content-Based Filter (TF-IDF & Cosine Similarity)
# -----------------

def calculate_and_sort_recommendations(all_content, video_details, top_n=3):
  """
   Apply Tfidf and cosine matrix to calculate similartiy
   all_content -> list of query and results
   video_details -> list of results from youtube
   top_n -> number of results to return
  """

  # Applying TF-IDF to convert texts into numerical vectors
  vectorizer = TfidfVectorizer(max_features = 1000,stop_words='english')
  item_features = vectorizer.fit_transform(all_content)

  # Calculating similarity between all vectors
  similarity_matrix = cosine_similarity(item_features)

  # Extracting similarity scores for our summary (Row 0, excluding the first element)
  summary_similarity_scores = similarity_matrix[0,1:]

  # Mapping each similarity score back to its corresponding video in the results list
  for i, score in enumerate(summary_similarity_scores):
    video_details[i]["recommandations_score"] = score

  # Using the sorted function to rank the video list (results) by score, in descending order
  sorted_items = sorted(video_details, key=lambda item: item["recommandations_score"],reverse=True)

  return sorted_items[:top_n]

# -----------------
# 5. Collaborative Filter (Popularity Stats)
# -----------------
def get_statistical_videos(video_details):
  """ get the statistical information for videos to combine content_based filteration , collaboritive filteration
      video_details -> vlist of results from youtube
  """

  # creating Youtube Resource Object
  try:
      Youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
  except Exception as e:
      print(f"Error initializing YouTube API: {e}")

  videos_ids = [video["video_id"] for video in video_details]
  ids_string = ",".join(videos_ids)

  try:
      stats_response=Youtube_object.videos().list(id=ids_string,part="statistics").execute()
      stats_items = stats_response.get("items", [])

      stats_dict = {}
      for item in stats_items:

        stats = item.get("statistics", {})
        stats_dict[item["id"]] = {
            "viewCount": int(stats.get("viewCount", 1)),  # if not exist :retur 1
            "likeCount": int(stats.get("likeCount", 1))}

  except Exception as e:
          print(f"Error getting statistics: {e}")
          stats_dict = {}
  return stats_dict

# -----------------
# 6. Hybrid Scoring (Normalization)
# -----------------
def Normalization(video_details , stats_dict,n_top=3):
  """
    Applies Log Transform then Min-Max Scaling to calculate popularity score.
    video_details -> List of videos (from content-based step)
    stats_data -> Dict of stats (from get_statistical_videos)
    """
  for video in video_details:
    video_id = video["video_id"]
    stats = stats_dict.get(video_id, {})  # Get stats for this video ID

    video["likeCount"]=stats.get("likeCount",1)
    video["viewCount"]=stats.get("viewCount",1)

    # apply logarthim to avoide skewness
    video["log_likes"] = np.log10(video["likeCount"]+1) # +1 to avoid log(0)
    video["log_views"] = np.log10(video["viewCount"]+1)

  # apply min_max normalization
  log_views_all = [v["log_views"] for v in video_details]
  log_likes_all = [v["log_likes"] for v in video_details]

  min_log_views = min(log_views_all)
  max_log_views = max(log_views_all)

  min_log_likes = min(log_likes_all)
  max_log_likes = max(log_likes_all)

  # Calculate the "range" (max - min)
  range_log_views = max_log_views - min_log_views
  range_log_likes = max_log_likes - min_log_likes

  for video in video_details:
        if range_log_views > 0:
            view_score = (video["log_views"] - min_log_views) / range_log_views
        else:
            view_score = 0

        if range_log_likes > 0:
            like_score = (video["log_likes"] - min_log_likes) / range_log_likes
        else:
            like_score = 0

        # Final score is the average of the two
        video["popularity_score"] = (view_score + like_score) / 2


  W_CONTENT = 0.7
  W_POPULARITY = 0.3

  for video in video_details:
        content_score = video["recommandations_score"]
        popularity_score = video["popularity_score"]
        video["hybrid_score"] = (content_score * W_CONTENT) + (popularity_score * W_POPULARITY)

  final_hybrid_recommendations = sorted(video_details, key=lambda v: v["hybrid_score"], reverse=True)

  return final_hybrid_recommendations[:n_top]




def get_hybrid_recommendations(summary):
  search_query = Extrcat_Keywords(summary)
  video_details = Search_key_words(search_query, 100)
  all_content = [summary] + [item["full_content"] for item in video_details]

  # calc similarity
  top_recommendations = calculate_and_sort_recommendations(all_content, video_details, top_n=30)
  stats_dict= get_statistical_videos(top_recommendations)
  final_hybrid_recommendations = Normalization(top_recommendations, stats_dict,5)


  # # # display
  # print("---------------------------------------------------------")
  # print(f"top {len(final_hybrid_recommendations)} recommanadtion")
  # print("---------------------------------------------------------")

  # for i, item in enumerate(final_hybrid_recommendations):
  #     score_percentage = f"{item['hybrid_score']*100:.2f}%"
  #     video_url = f"https://www.youtube.com/watch?v={item['video_id']}"

  #     print(f"recommndation#{i+1} | hybrid_score: {score_percentage}")
  #     print(f"title: {item['title']}")
  #     print(f"link (URL): {video_url}")
  #     print("-" * 50)


  json_recommendations = json.dumps({
      "summary": summary,
      "recommendations": final_hybrid_recommendations
  })
  return json_recommendations


my_summary= "الذكاء الاصطناعي التوليدي (Generative AI) هو فرع متقدم جدًا من فروع الذكاء الاصطناعي بيستخدم نماذج عملاقة زي **Large Language Models (LLMs)**، زي GPT-4، عشان يقدر يخلق محتوى جديد وأصلي مش مجرد يحلل البيانات الموجودة. النماذج دي بتتدرب على **كمية ضخمة من البيانات (Massive datasets)**، وبعد التدريب تقدر تولد نصوص (Text generation)، وصور (Image synthesis)، وأكواد برمجية.الفكرة الأساسية بتعتمد على الـ **Neural Networks** وتحديداً الـ **Transformers** اللي بتسمح للموديل إنه يفهم الـ Context بتاع الجملة بالكامل قبل ما يتوقع الكلمة اللي بعدها. استخدامات Generative AI ضخمة: من تصميم أدوية جديدة (Drug discovery) لحد إنتاج محتوى إعلاني (Creative content production). بالرغم من كل المميزات، هناك تحديات كبيرة تواجهنا زي قضايا **حقوق النشر (Copyright issues)** والتحيز (Bias) اللي ممكن يكون موجود في الـ Training Data. هذا المجال يمثل ثورة تكنولوجية حقيقية."
json_file = get_hybrid_recommendations(my_summary)
