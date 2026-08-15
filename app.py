import streamlit as st
from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException
import speech_recognition as sr
from gtts import gTTS
import io
import time
from xhtml2pdf import pisa
import PyPDF2
from PIL import Image as PILImage
import pytesseract
from audio_recorder_streamlit import audio_recorder

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TechNeekX AI Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session States
if 'history' not in st.session_state:
    st.session_state.history = []
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'source_text' not in st.session_state:
    st.session_state.source_text = ""
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = ""

# Load Custom CSS securely
def load_css(file_name):
    try:
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("style.css")

# Base Theme Configurations Injection
if st.session_state.theme == 'light':
    st.markdown(
        """
        <style>
        .stApp { background-color: #f8fafc !important; color: #0f172a !important; }
        .stSidebar { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
        .translation-card, .utility-container, .history-card { background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; color: #0f172a !important; }
        .stTextArea textarea { background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #94a3b8 !important; }
        div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #94a3b8 !important; }
        div[data-baseweb="popover"] li, div[role="listbox"] li { background-color: #ffffff !important; color: #0f172a !important; }
        div[data-baseweb="select"] span { color: #0f172a !important; }
        p, span, label, h1, h2, h3, h4, div { color: #0f172a !important; }
        .metrics-counter { color: #64748b !important; }
        button[kind="secondary"] { background-color: #f1f5f9 !important; color: #0f172a !important; border: 1px solid #cbd5e1 !important; }
        button[kind="secondary"]:hover { background-color: #e2e8f0 !important; border-color: #3b82f6 !important; color: #3b82f6 !important; }
        div[data-testid="stExpander"] { background-color: #ffffff !important; border: 1px solid #e2e8f0 !important; }
        </style>
        """, unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        .stApp { background-color: #0f172a !important; color: #f8fafc !important; }
        .stSidebar { background-color: #1e293b !important; border-right: 1px solid #334155; }
        .translation-card, .utility-container, .history-card { background-color: #1e293b !important; border: 1px solid #334155 !important; color: #f8fafc !important; }
        .stTextArea textarea { background-color: #1e293b !important; color: #f8fafc !important; border: 1px solid #475569 !important; }
        div[data-baseweb="select"] > div { background-color: #1e293b !important; color: #f8fafc !important; border: 1px solid #475569 !important; }
        div[data-baseweb="select"] span { color: #f8fafc !important; }
        p, span, label, h1, h2, h3, h4 { color: #f8fafc !important; }
        .metrics-counter { color: #94a3b8 !important; }
        button[kind="secondary"] { background-color: #1e293b !important; color: #f8fafc !important; border: 1px solid #475569 !important; }
        div[data-testid="stExpander"] { background-color: #1e293b !important; border: 1px solid #334155 !important; }
        </style>
        """, unsafe_allow_html=True
    )

# -----------------------------------------------------------------------------
# 2. Supported Languages mapping
# -----------------------------------------------------------------------------
SUPPORTED_LANGUAGES = {
    'english': 'en', 'spanish': 'es', 'french': 'fr', 'german': 'de',
    'hindi': 'hi', 'chinese (simplified)': 'zh-CN', 'arabic': 'ar',
    'russian': 'ru', 'japanese': 'ja', 'italian': 'it', 'portuguese': 'pt',
    'bengali': 'bn', 'marathi': 'mr', 'telugu': 'te', 'tamil': 'ta'
}
LANG_DISPLAY_TO_CODE = {k.title(): v for k, v in SUPPORTED_LANGUAGES.items()}
SRC_LANG_OPTIONS = ["Auto Detect"] + sorted(list(LANG_DISPLAY_TO_CODE.keys()))
TARGET_LANG_OPTIONS = sorted(list(LANG_DISPLAY_TO_CODE.keys()))

# -----------------------------------------------------------------------------
# 3. Sidebar Setup
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='text-align: center; font-weight: 700; margin-bottom: 24px;'>🌐 Configuration</h2>", unsafe_allow_html=True)
    
    st.markdown("### UI Settings")
    theme_choice = st.toggle("Enable Light Mode", value=(st.session_state.theme == 'light'))
    new_theme = 'light' if theme_choice else 'dark'
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()
        
    st.markdown("---")
    
    with st.expander("ℹ️ About Project", expanded=True):
        st.markdown("**TechNeekX AI Translator** is a professional-grade web utility optimized for modern cross-language conversion.")
        
    with st.expander("👨‍💻 Developer Stack", expanded=False):
        st.markdown("* **Role:** Full Stack Developer & UI/UX Designer\n* **Framework:** Streamlit\n* **Engine:** Python 3.10+")
        
    with st.expander("📦 Core Libraries", expanded=False):
        st.markdown("`deep-translator`  \n`SpeechRecognition`  \n`audio-recorder-streamlit`  \n`gTTS`  \n`xhtml2pdf`  \n`PyPDF2`  \n`pytesseract`")

# -----------------------------------------------------------------------------
# 4. Branding & Logo Header
# -----------------------------------------------------------------------------
logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
with logo_col2:
    try:
        st.image("assets/logo.png", width=120)
    except Exception:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 12px;">
                <span style="background-color: #3b82f6; color: #ffffff; padding: 10px 18px; border-radius: 12px; font-weight: 800; font-size: 1.25rem; letter-spacing: 0.05em; display: inline-block; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                    TechNeekX AI
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<h1 style='text-align: center; font-weight: 800; font-size: 2.5rem; margin-bottom: 6px; letter-spacing: -0.02em;'>TechNeekX AI Translator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.05rem; margin-bottom: 32px; font-weight: 400;'>Translate text instantly with AI-powered multilingual support.</p>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. Engine Controllers (Text, Voice, File)
# -----------------------------------------------------------------------------
def trigger_translation(text_input, src_l, tgt_l):
    if not text_input or not text_input.strip():
        st.warning("⚠️ Input Required: Please enter or record text to translate.")
        return
        
    src_code = 'auto' if src_l == "Auto Detect" else LANG_DISPLAY_TO_CODE[src_l]
    tgt_code = LANG_DISPLAY_TO_CODE[tgt_l]
    
    with st.spinner("Translating..."):
        try:
            translator = GoogleTranslator(source=src_code, target=tgt_code)
            result = translator.translate(text_input)
            
            if result:
                st.session_state.translated_text = result
                st.session_state.history.insert(0, {
                    "timestamp": time.strftime("%H:%M:%S"),
                    "source_lang": src_l,
                    "target_lang": tgt_l,
                    "input": text_input,
                    "output": result
                })
                st.toast("✅ Translation completed successfully.", icon="🚀")
            else:
                st.error("❌ Translation Failed: Received empty response from API pipeline.")

        except LanguageNotSupportedException:
            st.error("⚠️ Unsupported Language: Selected language matrix is not supported.")
        except Exception as e:
            err_msg = str(e).lower()
            if any(k in err_msg for k in ["connection", "timeout", "network", "unreachable"]):
                st.error("🌐 Connection Failure: Unable to connect to server. Check your internet connection.")
            elif "api" in err_msg or "http" in err_msg:
                st.error("⚡ Translation API Error: Service temporarily unavailable. Please try again later.")
            else:
                st.error(f"❌ Unexpected Error: An issue occurred during processing. ({str(e)})")

def process_uploaded_file(uploaded_file):
    extracted_text = ""
    try:
        # PDF Parsing
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
        
        # Image OCR Parsing
        elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
            image = PILImage.open(uploaded_file)
            extracted_text = pytesseract.image_to_string(image)
        
        # Update Session State
        if extracted_text.strip():
            st.session_state.source_text = extracted_text.strip()
            st.success("✅ Text extracted from file successfully!")
        else:
            st.warning("⚠️ No readable text could be found in the uploaded file.")
            
    except pytesseract.TesseractNotFoundError:
        st.error("❌ Tesseract OCR is not configured in environment. PDF extraction works natively.")
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")

# -----------------------------------------------------------------------------
# 6. Main Operational Workspace Layout
# -----------------------------------------------------------------------------
layout_col1, layout_col2, layout_col3 = st.columns([9, 2, 9])

with layout_col1:
    st.markdown("<div class='translation-card'>", unsafe_allow_html=True)
    src_lang_selection = st.selectbox("Source Language", options=SRC_LANG_OPTIONS, index=0, help="Select origin language or Auto Detect")
    
    # Document/Image File Uploader Section
    uploaded_file = st.file_uploader("📂 Upload Document/Image (PDF, JPG, PNG)", type=['pdf', 'png', 'jpg', 'jpeg'], help="Extract text from files for translation")
    if uploaded_file is not None:
        if st.button("📄 Extract Text from File", use_container_width=True):
            with st.spinner("Extracting text..."):
                process_uploaded_file(uploaded_file)
                st.rerun()

    input_payload = st.text_area(
        "Source Input Buffer", 
        value=st.session_state.source_text, 
        placeholder="Type, speak, or upload a file to translate...", 
        height=210,
        label_visibility="collapsed"
    )
    st.session_state.source_text = input_payload
    
    char_count = len(input_payload)
    word_count = len(input_payload.split()) if input_payload.strip() else 0
    st.markdown(f"<p class='metrics-counter'>Metrics &mdash; Characters: {char_count} | Words: {word_count}</p>", unsafe_allow_html=True)
    
    # Browser-Based Direct Audio Recorder (Cloud & Mobile Compatible)
    rec_col, clear_col = st.columns([6, 6])
    with rec_col:
        st.markdown("<p style='font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;'>🎙️ Record Voice (Click Mic):</p>", unsafe_allow_html=True)
        audio_bytes = audio_recorder(
            text="",
            recording_color="#ef4444",
            neutral_color="#3b82f6",
            icon_size="2x"
        )
        if audio_bytes:
            with st.spinner("Transcribing speech..."):
                try:
                    recognizer = sr.Recognizer()
                    audio_file = io.BytesIO(audio_bytes)
                    with sr.AudioFile(audio_file) as source:
                        audio_data = recognizer.record(source)
                        captured_text = recognizer.recognize_google(audio_data)
                        st.session_state.source_text = captured_text
                        st.success("✅ Voice transcribed successfully!")
                        st.rerun()
                except sr.UnknownValueError:
                    st.warning("⚠️ Audio not recognized. Please speak clearly.")
                except Exception as e:
                    st.error(f"Voice Transcription Error: {str(e)}")
                    
    with clear_col:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Workspace", use_container_width=True, help="Clear input and output areas"):
            st.session_state.source_text = ""
            st.session_state.translated_text = ""
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)

with layout_col2:
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    if st.button("↔️ Swap", use_container_width=True, help="Swap source and target languages"):
        if src_lang_selection != "Auto Detect":
            current_src = src_lang_selection
            current_tgt = st.session_state.get('tgt_selection', TARGET_LANG_OPTIONS[0])
            st.session_state.source_text, st.session_state.translated_text = st.session_state.translated_text, st.session_state.source_text
            st.session_state['src_idx'] = SRC_LANG_OPTIONS.index(current_tgt) if current_tgt in SRC_LANG_OPTIONS else 0
            st.session_state['tgt_idx'] = TARGET_LANG_OPTIONS.index(current_src) if current_src in TARGET_LANG_OPTIONS else 0
            st.rerun()
        else:
            st.warning("Cannot swap when 'Auto Detect' is active.")

with layout_col3:
    st.markdown("<div class='translation-card'>", unsafe_allow_html=True)
    default_tgt_idx = st.session_state.get('tgt_idx', TARGET_LANG_OPTIONS.index("Hindi") if "Hindi" in TARGET_LANG_OPTIONS else 0)
    target_lang_selection = st.selectbox("Destination Language", options=TARGET_LANG_OPTIONS, index=default_tgt_idx, help="Select target output language")
    st.session_state['tgt_selection'] = target_lang_selection
    
    st.text_area(
        "Translation Output Window", 
        value=st.session_state.translated_text, 
        placeholder="Translation result will appear here...",
        height=325, 
        disabled=True,
        label_visibility="collapsed"
    )
    
    is_input_empty = not st.session_state.source_text.strip()
    if st.button(
        "🚀 Process Translation", 
        type="primary", 
        use_container_width=True, 
        disabled=is_input_empty,
        help="Click to translate text" if not is_input_empty else "Enter text above to enable translation"
    ):
        trigger_translation(st.session_state.source_text, src_lang_selection, target_lang_selection)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 7. Translation Post-Processing Action Tools
# -----------------------------------------------------------------------------
if st.session_state.translated_text:
    st.markdown("<div class='utility-container'>", unsafe_allow_html=True)
    ut_col1, ut_col2, ut_col3, ut_col4 = st.columns(4)
    
    with ut_col1:
        copy_script = f"""
        <script>
        function runClipboardCopy() {{
            navigator.clipboard.writeText("{st.session_state.translated_text.encode('unicode_escape').decode('utf-8')}");
        }}
        </script>
        <button class="custom-copy-btn" onclick="runClipboardCopy()">📋 Copy Output</button>
        """
        st.components.v1.html(copy_script, height=45)
        
    with ut_col2:
        if st.button("🔊 Speech Output", use_container_width=True):
            try:
                tts = gTTS(text=st.session_state.translated_text, lang=LANG_DISPLAY_TO_CODE[target_lang_selection])
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                st.audio(audio_buffer.getvalue(), format="audio/mp3")
            except Exception as e:
                st.error(f"TTS Error: {str(e)}")
                
    with ut_col3:
        txt_buffer = io.BytesIO(st.session_state.translated_text.encode('utf-8'))
        st.download_button(label="📥 Download (.TXT)", data=txt_buffer.getvalue(), file_name="TechNeekX_Translation.txt", mime="text/plain", use_container_width=True)
        
    with ut_col4:
        html_report = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Arial', 'Nirmala UI', sans-serif; padding: 30px; color: #0f172a; }}
                h1 {{ color: #3b82f6; font-size: 24px; margin-bottom: 5px; }}
                .meta {{ font-size: 14px; color: #64748b; margin-bottom: 25px; }}
                .section-title {{ font-weight: bold; font-size: 16px; margin-top: 20px; color: #1e293b; }}
                .content-box {{ background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 6px; margin-top: 8px; font-size: 14px; min-height: 80px; }}
            </style>
        </head>
        <body>
            <h1>TECHNEEKX AI TRANSLATION REPORT</h1>
            <div class="meta">Route Matrix: {src_lang_selection} &rarr; {target_lang_selection}</div>
            <div class="section-title">Source Content Text:</div>
            <div class="content-box">{st.session_state.source_text.replace('\n', '<br/>')}</div>
            <div style="margin-top: 30px;" class="section-title">Compiled Translation Output:</div>
            <div class="content-box" style="border-left: 4px solid #3b82f6;">{st.session_state.translated_text.replace('\n', '<br/>')}</div>
        </body>
        </html>
        """
        pdf_buffer = io.BytesIO()
        pisa.CreatePDF(html_report, dest=pdf_buffer, encoding='utf-8')
        st.download_button(label="📄 Download (.PDF)", data=pdf_buffer.getvalue(), file_name="TechNeekX_Report.pdf", mime="application/pdf", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. Transactions Logs Ledger
# -----------------------------------------------------------------------------
st.markdown("<h2 style='margin-top: 45px; font-weight: 700; font-size: 1.65rem;'>📜 Live Translation History</h2>", unsafe_allow_html=True)

if st.session_state.history:
    if st.button("🧹 Clear History", type="secondary"):
        st.session_state.history = []
        st.success("Session history cleared.")
        st.rerun()
        
    for record in st.session_state.history:
        st.markdown(
            f"""
            <div class='history-card'>
                <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; margin-bottom: 10px;'>
                    <span style='font-weight: 600; font-size: 0.85rem; color: #3b82f6;'>[{record['timestamp']}] Record</span>
                    <span style='font-size: 0.85rem;'>Path: <b>{record['source_lang']}</b> ➔ <b>{record['target_lang']}</b></span>
                </div>
                <div style='display: flex; gap: 20px;'>
                    <div style='flex: 1;'>
                        <p style='margin: 0; font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase;'>Input Payload</p>
                        <p style='margin: 4px 0 0 0; font-size: 0.9rem;'>{record['input']}</p>
                    </div>
                    <div style='flex: 1; border-left: 2px solid #cbd5e1; padding-left: 16px;'>
                        <p style='margin: 0; font-size: 0.75rem; color: #3b82f6; font-weight: 600; text-transform: uppercase;'>Compiled Output</p>
                        <p style='margin: 4px 0 0 0; font-size: 0.9rem; font-weight: 500;'>{record['output']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("No active translations in current session.")

# -----------------------------------------------------------------------------
# 9. Professional Footer
# -----------------------------------------------------------------------------
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 12px 0 24px 0;'>
        <p style='font-size: 0.95rem; font-weight: 600; margin-bottom: 4px; color: #3b82f6;'>Developed by Aman Singh</p>
        <p style='font-size: 0.85rem; font-weight: 500; margin-bottom: 8px; color: #64748b;'>CodeAlpha Artificial Intelligence Internship 2026</p>
        <p style='font-size: 0.78rem; font-weight: 400; color: #94a3b8; letter-spacing: 0.02em;'>Powered by Python • Streamlit • Deep Translator</p>
    </div>
    """, unsafe_allow_html=True
)
