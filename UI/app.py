import os
import sys
import tempfile

import matplotlib.pyplot as plt
import streamlit as st

# If a previous (hot) reload left analyzer half-loaded, discard it and import fresh
if "analyzer" in sys.modules and getattr(sys.modules["analyzer"].__spec__, "_initializing", False):
    del sys.modules["analyzer"]
import analyzer  # your original code, unchanged

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

# ---- Force white theme (all handled here in app.py) --------------------------
st.markdown(
    """
    <style>
    :root, html, body { color-scheme: light !important; background: #FFFFFF !important; }

    /* page + header + every main container */
    .stApp, [data-testid="stApp"], [data-testid="stAppViewContainer"],
    [data-testid="stMain"], [data-testid="stMainBlockContainer"],
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stBottom"],
    [data-testid="stDecoration"], section.main, .main, .block-container {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
    }

    /* all normal text */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label,
    .stApp li, .stApp span, .stApp div[data-testid="stMarkdownContainer"],
    [data-testid="stWidgetLabel"], [data-testid="stCaptionContainer"] {
        color: #1F2937 !important;
    }

    /* file uploader */
    [data-testid="stFileUploaderDropzone"] {
        background-color: #F3F6FB !important; border: 1px dashed #CBD5E1 !important;
    }
    [data-testid="stFileUploaderDropzone"] * { color: #1F2937 !important; }
    [data-testid="stFileUploaderDropzone"] button {
        background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important;
    }
    [data-testid="stFileUploaderFile"] * { color: #1F2937 !important; }

    /* info / success boxes */
    [data-testid="stAlert"], [data-testid="stAlertContainer"] {
        background-color: #EAF2FF !important; color: #1F2937 !important;
    }
    [data-testid="stAlert"] * { color: #1F2937 !important; }

    /* radio, text input, expander */
    [data-baseweb="radio"] div { color: #1F2937 !important; }
    input { background-color: #FFFFFF !important; color: #1F2937 !important; }
    [data-baseweb="input"], [data-baseweb="base-input"] {
        background-color: #FFFFFF !important; border-color: #CBD5E1 !important;
    }
    [data-testid="stExpander"], [data-testid="stExpander"] details {
        background-color: #FFFFFF !important; border-color: #E5EAF2 !important;
    }
    [data-testid="stExpander"] * { color: #1F2937 !important; }
    [data-testid="stJson"], [data-testid="stCode"], pre { background-color: #F3F6FB !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("WhatsApp Chat Analyzer")

# ---- 1. Upload + preprocess (uses your preprocess()) -----------------------
uploaded = st.file_uploader("Upload your exported chat file (.txt)", type=["txt"])

if uploaded is None:
    st.info("Upload your chat file to begin.")
    st.stop()

if st.session_state.get("processed_file") != (uploaded.name, uploaded.size):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(uploaded.getvalue())
        tmp_path = tmp.name
    try:
        with st.spinner("Preprocessing..."):
            analyzer.preprocess(tmp_path)
        st.session_state["processed_file"] = (uploaded.name, uploaded.size)
    except Exception as e:
        st.error(f"Could not process this file: {e}")
        st.stop()
    finally:
        os.remove(tmp_path)

st.success("Chat processed.")

# ---- 2. Choose analysis -----------------------------------------------------
choice = st.radio("What do you want to see?", ["Overall stats", "Individual stats"], horizontal=True)

if choice == "Overall stats":
    analyzer.overall()              # your function
    st.pyplot(plt.gcf())
    plt.close("all")
else:
    with st.expander("Participants in this chat"):
        st.write(list(analyzer.df["user"].unique()))
    name = st.text_input("Enter a name (partial names work)")
    if name.strip():
        analyzer.individual(name.strip())   # your function
        st.pyplot(plt.gcf())
        plt.close("all")
