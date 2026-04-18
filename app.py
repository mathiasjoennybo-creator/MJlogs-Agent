import streamlit as st
import pandas as pd
from datetime import datetime
import google.generativeai as genai
from twilio.rest import Client
import time

# --- 1. SYSTEM KONFIGURATION & CSS ---
st.set_page_config(page_title="MJlogs_ Workflow", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; }
    header, #MainMenu, footer {visibility: hidden;}
    .block-container { padding-top: 2rem !important; max-width: 800px !important; }
    * { font-family: 'Courier New', Courier, monospace !important; color: #C5D0E6; }
    [data-testid="stDataFrame"], [data-testid="stTextInput"], [data-testid="stTextArea"], [data-testid="stNumberInput"] { 
        background-color: #1A1D27 !important; border: 1px solid #2D3243 !important; border-radius: 12px !important; 
    }
    .stButton > button { 
        background-color: #7B61FF !important; color: white !important; border-radius: 12px !important; 
        border: none !important; padding: 12px 24px !important; font-weight: bold !important; 
        display: block; margin: 0 auto; box-shadow: 0 4px 20px rgba(123, 97, 255, 0.3) !important; 
    }
    .log-box { background-color: #1A1D27; border-radius: 12px; border: 1px solid #2D3243; padding: 16px; font-size: 13px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FORBINDELSER ---
ai_klar = False
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_klar = True

# --- 3. DATABASE SETUP (SESSION STATE) ---
if "personale" not in st.session_state:
    st.session_state.personale = pd.DataFrame([
        {"navn": "Anne", "mobil": "+4511111111", "timelon": 130, "type": "Senior"}
    ])

if "vagtplan" not in st.session_state:
    st.session_state.vagtplan = pd.DataFrame([
        {"dato": "2026-04-12", "vagt": "Morgen", "medarbejder": "Anne", "status": "Aktiv"}
    ])

# --- 4. UI: LOGO ---
st.markdown("""
<div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 2rem;">
    <div style="font-size: 28px; font-weight: bold; color: white;">MJ<span style="color: #7B61FF;">logs</span><span style="color: #81E6D9;">_</span></div>
    <div style="font-size: 9px; color: #636D83; letter-spacing: 3px; margin-top: 4px;">ADMIN & WORKFLOW • V4.2</div>
</div>
""", unsafe_allow_html=True)

# --- 5. NY FUNKTION: PERSONALE ADMINISTRATION ---
with st.expander("👤 PERSONALE ADMINISTRATION"):
    st.write("Tilføj ny medarbejder til databasen:")
    col1, col2 = st.columns(2)
    with col1:
        ny_navn = st.text_input("Medarbejders navn")
        ny_mobil = st.text_input("Mobil nummer (f.eks. +45...)")
    with col2:
        ny_lon = st.number_input("Timeløn (kr)", min_value=0, value=130)
        ny_type = st.selectbox("Type/Sats", ["Ungarbejder", "Senior", "Leder"])
    
    if st.button("GEM MEDARBEJDER"):
        ny_entry = {"navn": ny_navn, "mobil": ny_mobil, "timelon": ny_lon, "type": ny_type}
        st.session_state.personale = pd.concat([st.session_state.personale, pd.DataFrame([ny_entry])], ignore_index=True)
        st.success(f"{ny_navn} er tilføjet!")
        time.sleep(1)
        st.rerun()

st.write("📋 NUVÆRENDE PERSONALE")
st.dataframe(st.session_state.personale, use_container_width=True)

st.divider()

# --- 6. AGENT WORKFLOW ---
st.markdown("<h3 style='color: #FFB86C;'>🚨 Workflow Command Center</h3>", unsafe_allow_html=True)

if not ai_klar:
    st.error("SYSTEM LÅST: Mangler API-nøgle.")
else:
    indgaaende_besked = st.text_area("Indbakke:", value="Hej MJlogs. Jeg er syg og kan ikke tage min morgenvagt i morgen (2026-04-12). Mvh Anne")

    if st.button("AKTIVER AUTONOMT WORKFLOW"):
        terminal = st.empty()
        log_data = []
        
        def update_log(tekst, farve="#81E6D9", tag="INFO"):
            tid = datetime.now().strftime("%H:%M:%S")
            log_data.append(f'<div style="margin-bottom:4px;"><span style="color:#515C74;">{tid}</span> <span style="color:{farve}; font-weight:bold;">{tag}</span> &nbsp;{tekst}</div>')
            samlet_log = '<div class="log-box">' + "".join(log_data) + '</div>'
            terminal.markdown(samlet_log, unsafe_allow_html=True)

        update_log("Analyserer medarbejder-database...")
        
        # AI Logic
        prompt = f"Personale: {st.session_state.personale.to_dict('records')}. Besked: {indgaaende_besked}. Find syg, dato og billigste afløser."
        svar = model.generate_content(prompt).text
        update_log(f"AI har fundet optimal løsning baseret på data.", "#FFB86C", "ANALYSE")
        update_log("Workflow afsluttet.", "#22D489", "SUCCES")
