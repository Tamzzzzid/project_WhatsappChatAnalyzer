import os
import tempfile

import matplotlib.pyplot as plt
import streamlit as st

import analyzer  # your original code, unchanged

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
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
