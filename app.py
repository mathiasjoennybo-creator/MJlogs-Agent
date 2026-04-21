import streamlit as st
import pandas as pd
from datetime import datetime
import google.generativeai as genai
from twilio.rest import Client
import time

# --- 0. SESSION STATE (MØRK TILSTAND) ---
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def skift_tema():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Farvepaletter (Lys / Mørk)
if st.session_state.dark_mode:
    bg_main, bg_box, color_text, bg_tab, color_tab = "#0E1117", "#1A1D27", "#C5D0E6", "#2D3243", "#C5D0E6"
else:
    bg_main, bg_box, color_text, bg_tab, color_tab = "#F4F7F6", "#FFFFFF", "#333333", "#E9ECEF", "#6C757D"

# --- 1. SYSTEM KONFIGURATION ---
st.set_page_config(page_title="MJlogs_ Workflow", layout="centered")

# Dynamisk CSS
st.markdown(f"""
    <style>
    header {{visibility: hidden;}}
    .stApp {{ background-color: {bg_main} !important; }}
    .block-container {{ padding-top: 1rem !important; max-width: 800px !important; color: {color_text} !important; }}
    h1, h2, h3, h4, p, span, div, label {{ color: {color_text} !important; }}
    
    .stButton > button {{ background-color: #0F52BA !important; color: white !important; border-radius: 8px !important; border: none !important; padding: 14px 24px !important; font-weight: 600 !important; width: 100%; box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important; }}
    
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{ height: 50px; background-color: {bg_tab} !important; color: {color_tab} !important; border-radius: 8px; padding: 0px 16px; }}
    .stTabs [aria-selected="true"] {{ background-color: #0F52BA !important; color: white !important; }}
    
    .log-box {{ background-color: {bg_box}; border-radius: 8px; border: 1px solid {bg_tab}; padding: 16px; font-size: 14px
