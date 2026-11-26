import streamlit as st
from src.RequestRetriever.UI.loadui import load_ui

st.set_page_config(page_title="Agentic Incident Resolution Assistant", page_icon="🔎", layout="wide")
load_ui()
