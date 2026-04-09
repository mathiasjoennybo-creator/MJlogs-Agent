import streamlit as st
import pandas as pd
from datetime import datetime
import time

# 1. PAGE CONFIGURATION & CSS
st.set_page_config(page_title="MJlogs Scheduling", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 2rem !important; max-width: 800px !important; }
    * { font-family: 'Courier New', Courier, monospace !important; color: #C5D0E6; }
    [data-testid="stDataFrame"], [data-testid="stNumberInput"], [data-testid="stSelectbox"] {
        background-color: #1A1D27 !important; border: 1px solid #2D3243 !important; border-radius: 12px !important;
    }
    .stButton > button {
        background-color: #7B61FF !important; color: white !important; border-radius: 12px !important;
        border: none !important; padding: 12px 24px !important; font-weight: bold !important;
        box-shadow: 0 4px 20px rgba(123, 97, 255, 0.3) !important; display: block; margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGO
st.markdown("""
<div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 2rem;">
    <div style="display: flex; align-items: center;">
        <div style="background: #7B61FF; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
            <div style="color: white; font-size: 20px; font-weight: bold;">≡</div>
        </div>
        <div style="font-size: 28px; font-weight: bold; color: white;">MJ<span style="color: #7B61FF;">logs</span><span style="color: #81E6D9;">_</span></div>
    </div>
    <div style="font-size: 9px; color: #636D83; letter-spacing: 3px; margin-top: 4px;">CLOUD EDITION • V2.5</div>
</div>
""", unsafe_allow_html=True)

# 3. KONTROLPANEL
col_m, col_b = st.columns([1, 2])
with col_m:
    maaned = st.selectbox("Vælg Måned", ["Oktober", "November", "December"])
with col_b:
    budget = st.number_input(f"Budget for {maaned} (kr):", value=15000, step=1000)

st.divider()

# 4. DATA INPUTS
st.write(f"📊 DATA-INPUT: {maaned.upper()}")
if "personale" not in st.session_state:
    st.session_state.personale = pd.DataFrame([
        {"navn": "Lukas", "type": "Ung", "timelon": 75, "max_timer": 40},
        {"navn": "Emma", "type": "Ung", "timelon": 75, "max_timer": 40},
        {"navn": "Jens", "type": "Senior", "timelon": 160, "max_timer": 160}
    ])
edited_personale = st.data_editor(st.session_state.personale, num_rows="dynamic", use_container_width=True)

if "vagter" not in st.session_state:
    st.session_state.vagter = pd.DataFrame([
        {"dag": "Uge 1", "timer": 40},
        {"dag": "Uge 2", "timer": 40},
        {"dag": "Uge 3", "timer": 40},
        {"dag": "Uge 4", "timer": 40}
    ])
edited_vagter = st.data_editor(st.session_state.vagter, num_rows="dynamic", use_container_width=True)

# 5. LOKAL EXECUTION (Ingen Uvicorn nødvendig)
if st.button(f"KØR OPTIMERING FOR {maaned.upper()}"):
    
    # Simuleret beregning direkte i appen (Klar til udskiftning med OpenAI)
    total_timer = edited_vagter['timer'].sum()
    estimeret_forbrug = total_timer * 75  # Simpel beregning med ungarbejder-løn
    overskud = budget - estimeret_forbrug
    
    log_html = f'<div style="margin-bottom:4px;"><span style="color:#515C74;">{datetime.now().strftime("%H:%M")}</span> <span style="color:#81E6D9;">INFO</span> &nbsp;Cloud-analyse fuldført (Uden Uvicorn).</div>'
    
    st.markdown(f"""
    <div style="background-color: #1A1D27; border-radius: 12px; border: 1px solid #2D3243; padding: 16px; margin-top: 20px;">
        <div style="color: #636D83; font-size: 11px; margin-bottom: 10px;">mjlogs — {maaned.lower()}.log</div>
        <div style="font-size: 13px;">{log_html}</div>
        <div style="margin-top: 10px; color: #81E6D9;">> Result: {estimeret_forbrug} kr brugt af {budget} kr. Overskud: {overskud} kr.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.dataframe(edited_vagter, use_container_width=True)