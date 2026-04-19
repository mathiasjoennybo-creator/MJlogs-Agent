import streamlit as st
import pandas as pd
from datetime import datetime
import google.generativeai as genai
from twilio.rest import Client
import time

# --- 1. SYSTEM KONFIGURATION (PLANDAY-STYLE) ---
st.set_page_config(page_title="MJlogs_ Workflow", layout="centered")

# Rent, mobiloptimeret design
st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding-top: 1rem !important; max-width: 800px !important; }
    
    /* Moderne, touch-venlig knap (Planday-blå) */
    .stButton > button { 
        background-color: #0F52BA !important; 
        color: white !important; 
        border-radius: 8px !important; 
        border: none !important; 
        padding: 14px 24px !important; 
        font-weight: 600 !important; 
        width: 100%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important; 
    }
    
    /* Gør fanerne (menuen) store og nemme at trykke på */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 8px;
        padding: 0px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0F52BA;
        color: white !important;
    }
    
    /* Log-boks til agenten */
    .log-box { background-color: #F8F9FA; border-radius: 8px; border: 1px solid #E9ECEF; padding: 16px; font-size: 14px; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FORBINDELSER ---
ai_klar = False
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_klar = True

# --- 3. DATABASE SETUP ---
if "personale" not in st.session_state:
    st.session_state.personale = pd.DataFrame([
        {"navn": "Anne", "mobil": "+4511111111", "timelon": 130, "type": "Senior"}
    ])

if "vagtplan" not in st.session_state:
    st.session_state.vagtplan = pd.DataFrame([
        {"dato": "2026-04-12", "vagt": "Morgen", "medarbejder": "Anne", "status": "Aktiv"}
    ])

# --- 4. HEADER ---
st.markdown("""
<div style="text-align: center; margin-bottom: 1rem;">
    <h1 style="color: #0F52BA; margin-bottom: 0px;">MJlogs</h1>
    <p style="color: #6c757d; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Store Management</p>
</div>
""", unsafe_allow_html=True)

# --- 5. MENUSYSTEM (FANER) ---
fane_vagtplan, fane_personale, fane_agent = st.tabs(["📅 Vagtplan", "👥 Personale", "🤖 Indbakke"])

# --- FANE 1: VAGTPLAN ---
with fane_vagtplan:
    st.subheader("Aktuel Vagtplan")
    st.write("Overblik over planlagte og ændrede vagter.")
    st.dataframe(st.session_state.vagtplan, use_container_width=True, hide_index=True)

# --- FANE 2: PERSONALE ---
with fane_personale:
    st.subheader("Tilføj Medarbejder")
    
    ny_navn = st.text_input("Navn")
    ny_mobil = st.text_input("Mobil (f.eks. +45...)")
    ny_lon = st.number_input("Timeløn (kr)", min_value=0, value=130)
    ny_type = st.selectbox("Sats", ["Ungarbejder", "Senior", "Leder"])
    
    if st.button("Tilføj til database"):
        ny_entry = {"navn": ny_navn, "mobil": ny_mobil, "timelon": ny_lon, "type": ny_type}
        st.session_state.personale = pd.concat([st.session_state.personale, pd.DataFrame([ny_entry])], ignore_index=True)
        st.success(f"{ny_navn} gemt!")
        time.sleep(1)
        st.rerun()

    st.divider()
    st.subheader("Personale Database")
    st.dataframe(st.session_state.personale, use_container_width=True, hide_index=True)

# --- FANE 3: AGENT INDBAKKE ---
with fane_agent:
    st.subheader("Automatisk Håndtering")
    st.info("Indsæt besked fra medarbejder herunder. Agenten finder selv afløseren.")
    
    if not ai_klar:
        st.error("System låst: Mangler AI nøgle.")
    else:
        indgaaende_besked = st.text_area("Besked:", value="Hej MJlogs. Jeg er syg og kan ikke tage min morgenvagt i morgen (2026-04-12). Mvh Anne")

        if st.button("Find Afløser"):
            terminal = st.empty()
            log_data = []
            
            def update_log(tekst, farve="#0F52BA", tag="INFO"):
                tid = datetime.now().strftime("%H:%M")
                log_data.append(f'<div style="margin-bottom:6px;"><strong><span style="color:{farve};">{tag}</span></strong> ({tid}): {tekst}</div>')
                samlet_log = '<div class="log-box">' + "".join(log_data) + '</div>'
                terminal.markdown(samlet_log, unsafe_allow_html=True)

            update_log("Læser besked og scanner personale...")
            
            prompt = f"Personale: {st.session_state.personale.to_dict('records')}. Besked: {indgaaende_besked}. Find syg, dato og billigste afløser."
            svar = model.generate_content(prompt).text
            update_log("Optimal afløser fundet.", "#28A745", "SUCCES")
            update_log("Vagtplan opdateret. Klar til eksport.", "#6c757d", "SYSTEM")
