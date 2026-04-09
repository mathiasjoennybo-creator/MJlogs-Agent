import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="MJlogs Scheduling", layout="centered", initial_sidebar_state="collapsed")

# 2. THE MJLOGS VISUAL DNA (Design-DNA indsprøjtning)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 2rem !important; max-width: 800px !important; }
    * { font-family: 'Courier New', Courier, monospace !important; color: #C5D0E6; }
    
    /* Inputs og Tabeller */
    [data-testid="stDataFrame"], [data-testid="stNumberInput"], [data-testid="stSelectbox"] {
        background-color: #1A1D27 !important;
        border: 1px solid #2D3243 !important;
        border-radius: 12px !important;
    }
    
    /* Den lilla MJlogs knap */
    .stButton > button {
        background-color: #7B61FF !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 20px rgba(123, 97, 255, 0.3) !important;
        display: block; margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGO SEKTION
st.markdown("""
<div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 2rem;">
    <div style="display: flex; align-items: center;">
        <div style="background: #7B61FF; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
            <div style="color: white; font-size: 20px; font-weight: bold;">≡</div>
        </div>
        <div style="font-size: 28px; font-weight: bold; color: white;">MJ<span style="color: #7B61FF;">logs</span><span style="color: #81E6D9;">_</span></div>
    </div>
    <div style="font-size: 9px; color: #636D83; letter-spacing: 3px; margin-top: 4px;">SCHEDULING • V2.0</div>
</div>
""", unsafe_allow_html=True)

# 4. MÅNEDS-VÆLGER OG BUDGET
col_m, col_b = st.columns([1, 2])
with col_m:
    maaned = st.selectbox("Vælg Måned", ["Januar", "Februar", "Marts", "April", "Maj", "Juni", "Juli", "August", "September", "Oktober", "November", "December"])
with col_b:
    budget = st.number_input(f"Budget for {maaned} (kr):", value=15000, step=1000)

st.divider()

# 5. DATA INPUTS
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

# 6. EXECUTION
if st.button(f"KØR OPTIMERING FOR {maaned.upper()}"):
    payload = {
        "budget": budget,
        "vagter": edited_vagter.to_dict(orient="records"),
        "personale": edited_personale.to_dict(orient="records")
    }
    
    try:
        response = requests.post("http://127.0.0.1:8000/api/v1/optimer-vagtplan", json=payload)
        resultat = response.json()["data"]
        
        # TERMINAL UI
        log_html = "".join([f'<div style="margin-bottom:4px;"><span style="color:#515C74;">{datetime.now().strftime("%H:%M")}</span> <span style="color:#81E6D9;">INFO</span> &nbsp;{l}</div>' for l in resultat["log"][-5:]])
        
        st.markdown(f"""
        <div style="background-color: #1A1D27; border-radius: 12px; border: 1px solid #2D3243; padding: 16px; margin-top: 20px;">
            <div style="color: #636D83; font-size: 11px; margin-bottom: 10px;">mjlogs — {maaned.lower()}.log</div>
            <div style="font-size: 13px;">{log_html}</div>
            <div style="margin-top: 10px; color: #81E6D9;">> Result: {resultat['forbrugt']} kr brugt af {budget} kr.</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(resultat["vagter"], use_container_width=True)
                
    except:
        st.error("API ikke fundet. Start uvicorn!")