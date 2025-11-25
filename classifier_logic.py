from typing import List, Dict


class TextClassifier:
    def __init__(self, pipeline_model):

        self.classifier = pipeline_model

        self.topics = [
            "Science & Technology",
            "Economics & Finance",
            "History & Geopolitics",
            "Psychology & Philosophy",
            "Health & Medicine",
            "Business & Entrepreneurship",
            "Arts & Literature",
            "Law & Politics",
            "Self-Development",
            "True Crime & Mystery",
            "Sports & Fitness",
        ]

        self.types = [
            "Concept Explanation",
            "Documentary / Storytelling",
            "Tutorial / How-to",
            "News / Current Events",
            "Debate / Opinion Piece",
            "Biography / Profile",
            "Review / Critique",
            "Motivational Speech",
        ]

        self.tones = [
            "Academic & Formal",
            "Casual & Humorous",
            "Serious & Objective",
            "Emotional & Inspiring",
            "Critical & Controversial",
            "Urgent & Alarming",
        ]

    def classify_text(self, text: str) -> Dict[str, str]:
        """
        Classifies text using the provided Zero-Shot Classification pipeline.
        """
        try:

            # 1. Analyze Topic
            topic_res = self.classifier(text, self.topics, multi_label=False)

            # 2. Analyze Type
            type_res = self.classifier(text, self.types, multi_label=False)

            # 3. Analyze Tone
            tone_res = self.classifier(text, self.tones, multi_label=False)

            return {
                "topic": topic_res["labels"][0],
                "type": type_res["labels"][0],
                "tone": tone_res["labels"][0],
                "scores": {
                    "topic_conf": round(topic_res["scores"][0], 2),
                    "type_conf": round(type_res["scores"][0], 2),
                    "tone_conf": round(tone_res["scores"][0], 2),
                },
            }
        except Exception as e:
            return {"error": f"Classification Error: {str(e)}"}
