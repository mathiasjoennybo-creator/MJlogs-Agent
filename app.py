import streamlit as st
import pandas as pd
from datetime import datetime
import google.generativeai as genai
from twilio.rest import Client
import time

# --- 0. SESSION STATE (HUKOMMELSE) ---
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = ""

def skift_tema():
    st.session_state.dark_mode = not st.session_state.dark_mode

def log_ud():
    st.session_state.logged_in = False
    st.session_state.user_role = ""

# Farvepaletter
if st.session_state.dark_mode:
    bg_main, bg_box, color_text, bg_tab, color_tab = "#0E1117", "#1A1D27", "#C5D0E6", "#2D3243", "#C5D0E6"
else:
    bg_main, bg_box, color_text, bg_tab, color_tab = "#F4F7F6", "#FFFFFF", "#333333", "#E9ECEF", "#6C757D"

# --- 1. SYSTEM KONFIGURATION ---
st.set_page_config(page_title="MJlogs_ Workflow", layout="centered")

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
    .log-box {{ background-color: {bg_box}; border-radius: 8px; border: 1px solid {bg_tab}; padding: 16px; font-size: 14px; }}
    [data-testid="stDataFrame"], [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stSelectbox"] div {{ background-color: {bg_box} !important; color: {color_text} !important; border-color: {bg_tab} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. FORBINDELSER & DATABASE ---
ai_klar = False
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_klar = True

sms_klar = False
if "TWILIO_ACCOUNT_SID" in st.secrets and len(st.secrets["TWILIO_ACCOUNT_SID"]) > 20:
    twilio_client = Client(st.secrets["TWILIO_ACCOUNT_SID"], st.secrets["TWILIO_AUTH_TOKEN"])
    sms_klar = True

if "personale" not in st.session_state:
    st.session_state.personale = pd.DataFrame([
        {"navn": "Lukas", "mobil": "+4500000000", "timelon": 75, "type": "Ungarbejder"},
        {"navn": "Anne", "mobil": "+4511111111", "timelon": 130, "type": "Senior"}
    ])

if "vagtplan" not in st.session_state:
    st.session_state.vagtplan = pd.DataFrame([{"dato": "2026-04-12", "vagt": "Morgen", "medarbejder": "Anne", "status": "Aktiv"}])

def send_sms(til_nummer, besked, type_modtager="Afløser"):
    if sms_klar:
        try:
            msg = twilio_client.messages.create(body=besked, from_=st.secrets["TWILIO_PHONE_NUMBER"], to=til_nummer)
            return f"ÆGTE SMS sendt til {type_modtager} ({til_nummer})"
        except Exception as e:
            return f"FEJL i SMS: {e}"
    else:
        time.sleep(1)
        return f"SIMULERET SMS sendt til {type_modtager}: '{besked}'"

# --- 3. LOGIN SKÆRM ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #0F52BA !important; margin-top: 2rem;'>MJlogs Login</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 14px;'>Brugernavn: <b>admin</b> eller <b>medarbejder</b></p>", unsafe_allow_html=True)
    
    brugernavn = st.text_input("Brugernavn")
    adgangskode = st.text_input("Adgangskode", type="password")
    
    if st.button("Log Ind"):
        admin_kode = st.secrets.get("ADMIN_PASS", "1234")
        medarbejder_kode = st.secrets.get("MEDARBEJDER_PASS", "0000")
        
        if brugernavn.lower() == "admin" and adgangskode == admin_kode:
            st.session_state.logged_in = True
            st.session_state.user_role = "Admin"
            st.rerun()
        elif brugernavn.lower() == "medarbejder" and adgangskode == medarbejder_kode:
            st.session_state.logged_in = True
            st.session_state.user_role = "Medarbejder"
            st.rerun()
        else:
            st.error("❌ Forkert brugernavn eller adgangskode.")

# --- 4. HOVED-APP ---
else:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h1 style="color: #0F52BA !important; margin-bottom: 0px;">MJlogs</h1>
        <p style="font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Store Management</p>
    </div>
    """, unsafe_allow_html=True)

    # --- ADMIN VISNING ---
    if st.session_state.user_role == "Admin":
        fane_vagtplan, fane_personale, fane_agent, fane_indstillinger = st.tabs(["📅 Vagtplan", "👥 Personale", "🤖 Indbakke", "⚙️ Indstil."])

        with fane_vagtplan:
            st.subheader("Aktuel Vagtplan")
            st.dataframe(st.session_state.vagtplan, use_container_width=True, hide_index=True)

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
            st.dataframe(st.session_state.personale, use_container_width=True, hide_index=True)

        with fane_agent:
            st.subheader("Automatisk Håndtering (Admin)")
            if not ai_klar:
                st.error("System låst: Mangler AI nøgle.")
            else:
                indgaaende_besked = st.text_area("Besked:", value="Hej MJlogs. Jeg er syg og kan ikke tage min morgenvagt i morgen (2026-04-12). Mvh Anne", key="admin_indbakke")
                if st.button("Find Afløser"):
                    terminal = st.empty()
                    log_data = []
                    def update_log(tekst, farve="#0F52BA", tag="INFO"):
                        tid = datetime.now().strftime("%H:%M")
                        log_data.append(f'<div style="margin-bottom:6px;"><strong><span style="color:{farve} !important;">{tag}</span></strong> ({tid}): {tekst}</div>')
                        terminal.markdown('<div class="log-box">' + "".join(log_data) + '</div>', unsafe_allow_html=True)

                    update_log("Analyserer data...")
                    prompt = f"Personale: {st.session_state.personale.to_dict('records')}. Vagtplan: {st.session_state.vagtplan.to_dict('records')}. Besked: '{indgaaende_besked}'. Find den syge og den billigste ledige afløser. Svar KUN sådan:\nSYG: [Navn]\nDATO: [Dato]\nAFLØSER: [Navn]"
                    svar = model.generate_content(prompt).text
                    syg, dato, afloeser = "", "", ""
                    for linje in svar.split('\n'):
                        if "SYG:" in linje: syg = linje.replace("SYG:", "").strip()
                        if "DATO:" in linje: dato = linje.replace("DATO:", "").strip()
                        if "AFLØSER:" in linje: afloeser = linje.replace("AFLØSER:", "").strip()

                    update_log(f"Valgt afløser: {afloeser}", "#FFB86C", "ANALYSE")
                    st.session_state.vagtplan.loc[(st.session_state.vagtplan['medarbejder'] == syg) & (st.session_state.vagtplan['dato'] == dato), 'medarbejder'] = f"{afloeser} (Overtaget)"
                    update_log("Vagtplan opdateret.", "#28A745", "DATABASE")
                    
                    try:
                        afloeser_data = st.session_state.personale[st.session_state.personale['navn'] == afloeser].iloc[0]
                        sms_tekst = f"Hej {afloeser}. {syg} er syg. Kan du overtage vagten {dato}? Svar JA for at bekræfte."
                        log_sms = send_sms(afloeser_data['mobil'], sms_tekst, "Afløser")
                        update_log(log_sms, "#17A2B8", "SMS")
                    except IndexError:
                        update_log(f"Kunne ikke finde nummer på {afloeser}", "#DC3545", "FEJL")
                    
                    chef_nummer = st.secrets.get("CHEF_PHONE_NUMBER", "+4500000000")
                    chef_tekst = f"MJlogs: {syg} er syg {dato}. Vagten er tilbudt {afloeser}."
                    log_chef = send_sms(chef_nummer, chef_tekst, "Chef")
                    update_log(log_chef, "#17A2B8", "SMS")

        with fane_indstillinger:
            st.subheader("Systemindstillinger")
            st.toggle("🌙 Aktivér Mørk Tilstand", value=st.session_state.dark_mode, on_change=skift_tema)
            st.divider()
            if ai_klar: st.success("✅ AI Hjerne (Gemini) Aktiv")
            else: st.error("❌ AI Hjerne Mangler")
            if sms_klar: st.success("✅ SMS Modul (Twilio) Aktiv")
            else: st.warning("⚠️ SMS Modul i Test-Tilstand")
            st.divider()
            if st.button("Log Ud 🔒"):
                log_ud()
                st.rerun()

    # --- MEDARBEJDER VISNING ---
    elif st.session_state.user_role == "Medarbejder":
        fane_vagtplan, fane_indbakke, fane_profil = st.tabs(["📅 Vagtplan", "🤖 Indbakke", "👤 Profil"])
        
        with fane_vagtplan:
            st.subheader("Aktuel Vagtplan")
            st.write("Overblik over vagter i butikken.")
            st.dataframe(st.session_state.vagtplan, use_container_width=True, hide_index=True)

        with fane_indbakke:
            st.subheader("Kontakt Systemet")
            st.info("Meld sygdom her. Systemet forsøger automatisk at finde en afløser for dig.")
            
            if not ai_klar:
                st.error("System låst: Mangler AI nøgle.")
            else:
                medarbejder_besked = st.text_area("Din besked:", value="Hej MJlogs. Jeg er syg og kan ikke tage min morgenvagt...", key="medarbejder_indbakke")
                if st.button("Send Besked"):
                    terminal = st.empty()
                    log_data = []
                    def update_log(tekst, farve="#0F52BA", tag="INFO"):
                        tid = datetime.now().strftime("%H:%M")
                        log_data.append(f'<div style="margin-bottom:6px;"><strong><span style="color:{farve} !important;">{tag}</span></strong> ({tid}): {tekst}</div>')
                        terminal.markdown('<div class="log-box">' + "".join(log_data) + '</div>', unsafe_allow_html=True)

                    update_log("Besked modtaget. Leder efter afløser...")
                    
                    # AI analyserer medarbejderens besked
                    prompt = f"Personale: {st.session_state.personale.to_dict('records')}. Vagtplan: {st.session_state.vagtplan.to_dict('records')}. Besked: '{medarbejder_besked}'. Find den syge og den billigste ledige afløser. Svar KUN sådan:\nSYG: [Navn]\nDATO: [Dato]\nAFLØSER: [Navn]"
                    svar = model.generate_content(prompt).text
                    syg, dato, afloeser = "", "", ""
                    for linje in svar.split('\n'):
                        if "SYG:" in linje: syg = linje.replace("SYG:", "").strip()
                        if "DATO:" in linje: dato = linje.replace("DATO:", "").strip()
                        if "AFLØSER:" in linje: afloeser = linje.replace("AFLØSER:", "").strip()

                    st.session_state.vagtplan.loc[(st.session_state.vagtplan['medarbejder'] == syg) & (st.session_state.vagtplan['dato'] == dato), 'medarbejder'] = f"{afloeser} (Overtaget)"
                    update_log(f"Vagtplanen er midlertidigt opdateret.", "#28A745", "DATABASE")
                    
                    try:
                        afloeser_data = st.session_state.personale[st.session_state.personale['navn'] == afloeser].iloc[0]
                        sms_tekst = f"Hej {afloeser}. {syg} er syg. Kan du overtage vagten {dato}? Svar JA for at bekræfte."
                        send_sms(afloeser_data['mobil'], sms_tekst, "Afløser")
                        update_log("Der er sendt en SMS til en mulig afløser.", "#17A2B8", "SMS")
                    except IndexError:
                        update_log(f"Kunne ikke finde en afløser i systemet.", "#DC3545", "FEJL")
                    
                    chef_nummer = st.secrets.get("CHEF_PHONE_NUMBER", "+4500000000")
                    chef_tekst = f"MJlogs: {syg} er syg {dato}. Vagten er tilbudt {afloeser}."
                    send_sms(chef_nummer, chef_tekst, "Chef")
                    update_log("Din leder har fået direkte besked. God bedring!", "#17A2B8", "SMS")
            
        with fane_profil:
            st.subheader("Medarbejder Profil")
            st.toggle("🌙 Aktivér Mørk Tilstand", value=st.session_state.dark_mode, on_change=skift_tema)
            st.divider()
            if st.button("Log Ud 🔒"):
                log_ud()
                st.rerun()
