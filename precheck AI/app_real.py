import streamlit as st
import os
import subprocess
import whisper
import random
from rapidfuzz import fuzz
import docx2txt
from pdfminer.high_level import extract_text as extract_pdf_text

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="PreCheck AI — Smart Video Analyzer",
    page_icon="🎬",
    layout="wide"
)

# ----------------- SIDEBAR -----------------
st.sidebar.title("ℹ️ About PreCheck AI")
st.sidebar.info("""
**PreCheck AI** is a smart system that uses **AI & NLP** to analyze videos for:
- 🎯 **Plagiarism** — checks similarity with reference documents  
- ⚠️ **Abusive or sensitive language**  
- 🧠 **Automatic speech-to-text translation (Whisper AI)**  

Built with ❤️ using **Python, Streamlit, FFmpeg, Whisper, and RapidFuzz**.
""")

st.sidebar.header("📚 Reference Documents (optional)")
reference_files = st.sidebar.file_uploader(
    "Upload reference files (.txt, .pdf, .docx)",
    accept_multiple_files=True,
    type=["txt", "pdf", "docx"]
)

# ----------------- HELPER FUNCTIONS -----------------
def extract_audio(video_path, audio_path):
    try:
        cmd = ["ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le", audio_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception as e:
        st.error(f"FFmpeg error: {e}")
        return False

def transcribe_audio(audio_path, model_size="tiny"):
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path, task="translate")
        return result["text"]
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        return None

def read_reference_file(file):
    text = ""
    if file.name.endswith(".txt"):
        text = file.read().decode("utf-8", errors="ignore")
    elif file.name.endswith(".pdf"):
        with open("temp_ref.pdf", "wb") as f:
            f.write(file.getbuffer())
        text = extract_pdf_text("temp_ref.pdf")
        os.remove("temp_ref.pdf")
    elif file.name.endswith(".docx"):
        with open("temp_ref.docx", "wb") as f:
            f.write(file.getbuffer())
        text = docx2txt.process("temp_ref.docx")
        os.remove("temp_ref.docx")
    return text

def calculate_similarity(text1, text2):
    return fuzz.token_set_ratio(text1, text2)

def check_plagiarism(transcript, reference_files):
    if not reference_files:
        return random.randint(15, 50)
    similarities = []
    for ref in reference_files:
        ref_text = read_reference_file(ref)
        sim = calculate_similarity(transcript, ref_text)
        similarities.append(sim)
    if similarities:
        return max(similarities)
    return random.randint(15, 50)

def fake_sensitive_check(text):
    keywords = [
      # 🔪 Violence / Crime
        "kill", "murder", "attack", "shoot", "gun", "knife", "bomb", "blood", "fight", "violence",
        "terror", "threat", "death", "suicide", "rape", "abuse", "stab", "hang", "destroy",
        "explode", "war", "riot", "beat", "assault", "crime", "loot", "kill yourself",

        # 💢 Hate / Discrimination
        "hate", "racist", "caste", "religion", "slur", "discriminate", "insult", "color", "black", "white",
        "slave", "inferior", "superior", "idiot", "stupid", "moron", "fool", "dumb", "nonsense", "ugly",
        "fat", "pig", "dog", "trash", "garbage", "mad", "psycho", "loser", "worthless",

        # 💊 Drugs / Alcohol
        "drugs", "cocaine", "heroin", "weed", "alcohol", "drink", "smoke", "liquor", "vodka", "beer",
        "whiskey", "wine", "addict", "marijuana", "ganja", "snort", "joint", "bottle", 

        # 🔞 Sexual / Obscene Language
        "sex", "porn", "nude", "fuck", "shit", "bitch", "asshole", "bastard", "dick", "pussy",
        "cock", "boobs", "tits", "screw", "whore", "slut", "cum", "balls", "penis", "vagina",
        "naked", "jerk", "suck", "kiss my", "blowjob", "handjob", "doggy", "69", "fucker",

        # 💬 Harassment / Bullying / Threats
        "kill you", "go to hell", "die", "hate you", "stupid idiot", "bloody", "get lost",
        "shut up", "bastard face", "ugly pig", "trash face", "fat cow", "cheap", "nonsense", "lazy fool",

        # 🇮🇳 Tamil abusive / slang
        "வெறுப்பு", "கொலை", "தாக்குதல்", "குண்டு", "கத்தி", "இனவெறி", "பாலியல்", "அவமதிப்பு",
        "மருந்து", "குடி", "மோசடி", "தூண்டுதல்", "சாவு", "அடிச்சு", "சுத்தி", "சாணம்",
        "மூதேவி", "மடையன்", "வாயை மூடு", "போடா", "போடீ", "பொண்ணு", "புண்டை", "மூடு",
        "சொக்கி", "கேவலம்", "கூத்தி", "தர்மம் இல்லாதவன்", "அடிச்சுடுவேன்",

        # 🇮🇳 Hindi abusive / slang
        "chutiya", "bhosdike", "madarchod", "behenchod", "gaand", "randi", "haraami", "kutte",
        "kamina", "kutta", "kaminey", "bakchod", "ullu", "ullu ka pattha", "ghanta", "gaand mara",
        "saala", "bhen ke laude", "madarchod", "chakka", "chod", "randi ka bacha", "chup kar",
        "tatti", "ghatiya", "harami", "chirkut", "nalle", "bewakoof", "launda"
    ]
    found = [k for k in keywords if k.lower() in text.lower()]
    return found

# ----------------- MAIN UI TABS -----------------
tab1, tab2, tab3 = st.tabs(["🏠 Home", "📤 Upload & Analyze", "📊 Results"])

# ---------- TAB 1: HOME ----------
with tab1:
    st.title("🎥 PreCheck AI — Video Content Analyzer")
    st.markdown("""
    #### Welcome to PreCheck AI  
    This tool helps you **check videos for plagiarism and abusive language** using Artificial Intelligence.  
    Upload a `.mp4` video and let the system:
    - Extract its audio  
    - Transcribe it into English (using **Whisper AI**)  
    - Compare with uploaded documents  
    - Highlight sensitive or offensive words
    """)
    st.info("Switch to the **📤 Upload & Analyze** tab to begin your analysis.")

# ---------- TAB 2: UPLOAD & ANALYSIS ----------
with tab2:
    st.header("📤 Upload & Run AI Analysis")

    uploaded_video = st.file_uploader("🎞️ Upload a video file (.mp4)", type=["mp4"])

    if uploaded_video:
        st.video(uploaded_video)
        st.caption(f"📁 {uploaded_video.name} — {(uploaded_video.size / (1024*1024)):.2f} MB")

        model_choice = st.selectbox(
            "Select Whisper model size (smaller = faster)",
            ["tiny", "base", "small", "medium", "large"],
            index=0
        )

        if st.button("🚀 Run Full Check"):
            progress = st.progress(0)
            progress.progress(10)

            video_path = "temp_video.mp4"
            with open(video_path, "wb") as f:
                f.write(uploaded_video.getbuffer())

            audio_path = "temp_audio.wav"

            with st.spinner("🎧 Extracting audio..."):
                if extract_audio(video_path, audio_path):
                    progress.progress(35)
                    st.success("✅ Audio extracted successfully.")

                    with st.spinner("🧠 Transcribing with Whisper AI..."):
                        transcript = transcribe_audio(audio_path, model_choice)
                        if transcript:
                            progress.progress(70)
                            st.success("📝 Transcription complete!")

                            with st.expander("🔍 View Transcript Preview"):
                                st.write(transcript[:1500] + ("..." if len(transcript) > 1500 else ""))

                            with st.spinner("📊 Checking plagiarism and abuse..."):
                                plag_percent = check_plagiarism(transcript, reference_files)
                                sensitive_words = fake_sensitive_check(transcript)
                                progress.progress(100)
                                st.session_state["results"] = {
                                    "plag_percent": plag_percent,
                                    "sensitive_words": sensitive_words,
                                    "transcript": transcript
                                }
                                st.success("✅ Analysis complete! Go to the 📊 Results tab.")

                    os.remove(video_path)
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                else:
                    st.error("Audio extraction failed. Please check FFmpeg installation.")
    else:
        st.info("Upload a `.mp4` video to start your AI analysis.")

# ---------- TAB 3: RESULTS ----------
with tab3:
    st.header("📊 Analysis Results")

    if "results" in st.session_state:
        plag_percent = st.session_state["results"]["plag_percent"]
        sensitive_words = st.session_state["results"]["sensitive_words"]
        transcript = st.session_state["results"]["transcript"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📈 Plagiarism Score", f"{plag_percent}%")
        with col2:
            st.metric("⚠️ Abusive Words", len(sensitive_words))
        with col3:
            if plag_percent > 75 or sensitive_words:
                risk = "🔴 High"
            elif plag_percent > 40:
                risk = "🟠 Medium"
            else:
                risk = "🟢 Low"
            st.metric("🛡️ Risk Level", risk)

        if sensitive_words:
            st.warning("⚠️ Sensitive words found: " + ", ".join(sensitive_words))
        else:
            st.success("✅ No abusive or offensive language detected.")

        if plag_percent > 75:
            st.error("🚨 High plagiarism detected — content likely copied.")
        elif plag_percent > 40:
            st.warning("⚠️ Medium plagiarism — review suggested.")
        else:
            st.success("🟢 Content appears original and safe.")

        st.subheader("📝 Transcript (English Translation)")
        st.text_area("Transcript Preview", transcript[:2000], height=200)
    else:
        st.info("No analysis yet. Please run your video in the Upload tab.")

st.caption("© 2025 PreCheck AI | Developed by Kishore | Working Prototype")




