import streamlit as st
from transformers import pipeline
from classifier_logic import TextClassifier

# --- Page Config ---
st.set_page_config(page_title="Multilingual Video Categorizer", page_icon="🌍", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    .stTextArea textarea { font-family: 'Arial', sans-serif; font-size: 16px; }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dcdcdc;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🌍 Multilingual Video Categorizer")
st.markdown("Powered by **mDeBERTa Zero-Shot** | Graduation Project: *YouTube Note Generator*")
st.markdown("---")

# --- 🚀 Load Model (Cached) ---
@st.cache_resource
def load_model():
    """
    Loads the Hugging Face pipeline.
    This runs only once at the start to prevent reloading on every interaction.
    """
    with st.spinner("⏳ Initializing AI Model... (This may take a moment on first run)"):
        # Using mDeBERTa for best Multilingual (Arabic/English) performance
        pipe = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
        return pipe

# Attempt to load the model immediately
try:
    ai_pipeline = load_model()
    model_status = "✅ Model Ready"
except Exception as e:
    ai_pipeline = None
    model_status = "❌ Model Failed"
    st.error(f"Critical Error loading model: {e}")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ System Status")
    if "Ready" in model_status:
        st.success(model_status)
    else:
        st.error(model_status)
        
    st.info("Model: MoritzLaurer/mDeBERTa-v3 (Optimized for Arabic & English)")
    st.markdown("---")
    st.caption("Offline Inference Enabled.")

# --- Main Interface ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Input Text")
    text_input = st.text_area(
        "Paste Video Summary or Script:", 
        height=250, 
        placeholder="Example: Inflation is the rate at which prices for goods and services rise...")
    
    classify_btn = st.button("🚀 Classify Text", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 Results")
    
    if classify_btn:
        if not text_input.strip():
            st.warning("⚠️ Please enter some text to analyze.")
        elif ai_pipeline is None:
            st.error("🚨 AI Model is not active. Please restart the app.")
        else:
            # Initialize Logic
            classifier = TextClassifier(ai_pipeline)
            
            with st.spinner("🔍 Analyzing content context & semantics..."):
                results = classifier.classify_text(text_input)

                # --- Display Logic ---
                if "error" in results:
                    st.error(results["error"])
                else:
                    st.success("Analysis Complete!")
                    
                    # Display Metrics
                    st.metric(label="Main Topic", value=results.get('topic', 'N/A'))
                    st.metric(label="Content Type", value=results.get('type', 'N/A'))
                    st.metric(label="Tone / Vibe", value=results.get('tone', 'N/A'))
                    
                    # Details Expander
                    with st.expander("View Confidence Scores"):
                        st.json(results.get("scores", {}))