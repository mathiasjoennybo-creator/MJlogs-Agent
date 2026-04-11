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
    [data-testid="stDataFrame"], [data-testid="stTextInput"], [data-testid="stTextArea"] { background-color: #1A1D27 !important; border: 1px solid #2D3243 !important; border-radius: 12px !important; }
    .stButton > button { background-color: #7B61FF !important; color: white !important; border-radius: 12px !important; border: none !important; padding: 12px 24px !important; font-weight: bold !important; display: block; margin: 0 auto; box-shadow: 0 4px 20px rgba(123, 97, 255, 0.3) !important; }
    .log-box { background-color: #1A1D27; border-radius: 12px; border: 1px solid #2D3243; padding: 16px; font-size: 13px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FORBINDELSER (API'ER) ---
# AI (Gemini)
ai_klar = False
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_klar = True

# SMS (Twilio)
sms_klar = False
if "TWILIO_ACCOUNT_SID" in st.secrets and len(st.secrets["TWILIO_ACCOUNT_SID"]) > 20:
    twilio_client = Client(st.secrets["TWILIO_ACCOUNT_SID"], st.secrets["TWILIO_AUTH_TOKEN"])
    sms_klar = True

# --- 3. DATABASE (LOKAL ELLER GOOGLE SHEETS) ---
if "vagtplan" not in st.session_state:
    st.session_state.vagtplan = pd.DataFrame([
        {"dato": "2026-04-12", "vagt": "Morgen", "medarbejder": "Anne", "status": "Aktiv"},
        {"dato": "2026-04-12", "vagt": "Aften", "medarbejder": "Lukas", "status": "Aktiv"},
        {"dato": "2026-04-13", "vagt": "Morgen", "medarbejder": "Jens", "status": "Aktiv"}
    ])

if "personale" not in st.session_state:
    st.session_state.personale = pd.DataFrame([
        {"navn": "Anne", "telefon": "+4511111111", "timelon": 130},
        {"navn": "Peter", "telefon": "+4522222222", "timelon": 130},
        {"navn": "Lukas", "telefon": "+4533333333", "timelon": 75}
    ])

# --- 4. FUNKTIONER ---
def send_sms(til_nummer, besked, type_modtager="Afløser"):
    """Håndterer afsendelse af SMS (Ægte eller Simuleret)"""
    if sms_klar:
        try:
            msg = twilio_client.messages.create(body=besked, from_=st.secrets["TWILIO_PHONE_NUMBER"], to=til_nummer)
            return f"ÆGTE SMS sendt til {type_modtager} ({til_nummer})"
        except Exception as e:
            return f"FEJL i SMS: {e}"
    else:
        time.sleep(1) # Simulerer at det tager lidt tid at sende en SMS
        return f"SIMULERET SMS sendt til {type_modtager}: '{besked}'"

# --- 5. UI: HEADER & DATA ---
st.markdown("""
<div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 2rem;">
    <div style="font-size: 28px; font-weight: bold; color: white;">MJ<span style="color: #7B61FF;">logs</span><span style="color: #81E6D9;">_</span></div>
    <div style="font-size: 9px; color: #636D83; letter-spacing: 3px; margin-top: 4px;">AUTONOMOUS WORKFLOW • V4.1</div>
</div>
""", unsafe_allow_html=True)

st.write("📅 DATA OVERSIGT (Eksportér til butikssystem ved månedens udgang)")
st.dataframe(st.session_state.vagtplan, use_container_width=True)

st.divider()

# --- 6. AGENT WORKFLOW (HJERTET I APPEN) ---
st.markdown("<h3 style='color: #FFB86C;'>🚨 Workflow Command Center</h3>", unsafe_allow_html=True)

if not ai_klar:
    st.error("SYSTEM LÅST: Indsæt GEMINI_API_KEY i Streamlit Secrets for at aktivere AI.")
else:
    indgaaende_besked = st.text_area("Indbakke (Besked fra medarbejder):", value="Hej MJlogs. Jeg er syg og kan ikke tage min morgenvagt i morgen (2026-04-12). Mvh Anne")

    if st.button("AKTIVER AUTONOMT WORKFLOW"):
        terminal = st.empty()
        
        # Her er fejlen rettet! Vi bruger en sikker liste til loggen.
        log_data = []
        
        def update_log(tekst, farve="#81E6D9", tag="INFO"):
            tid = datetime.now().strftime("%H:%M:%S")
            log_data.append(f'<div style="margin-bottom:4px;"><span style="color:#515C74;">{tid}</span> <span style="color:{farve}; font-weight:bold;">{tag}</span> &nbsp;{tekst}</div>')
            samlet_log = '<div class="log-box"><div style="color:#515C74; margin-bottom:10px;">mjlogs — system.log</div>' + "".join(log_data) + '</div>'
            terminal.markdown(samlet_log, unsafe_allow_html=True)

        update_log("Besked modtaget. Analyserer data...")
        
        # TRIN 1: AI ANALYSE
        prompt = f"""
        System: MJlogs Vagtplanlægger.
        Personale: {st.session_state.personale.to_dict('records')}
        Vagtplan: {st.session_state.vagtplan.to_dict('records')}
        Besked: "{indgaaende_besked}"
        
        Opgave:
        1. Find den syge.
        2. Find den billigste ledige afløser til den specifikke vagt.
        
        Formatér KUN dit svar som:
        SYG: [Navn]
        DATO: [Dato]
        AFLØSER: [Navn]
        """
        
        try:
            svar = model.generate_content(prompt).text
            syg, dato, afloeser = "", "", ""
            for linje in svar.split('\n'):
                if "SYG:" in linje: syg = linje.replace("SYG:", "").strip()
                if "DATO:" in linje: dato = linje.replace("DATO:", "").strip()
                if "AFLØSER:" in linje: afloeser = linje.replace("AFLØSER:", "").strip()

            update_log(f"AI Konklusion -> Syg: {syg} | Vagt: {dato} | Ny kandidat: {afloeser}", "#FFB86C", "ANALYSE")
            
            # TRIN 2: OPDATER DATABASE
            st.session_state.vagtplan.loc[(st.session_state.vagtplan['medarbejder'] == syg) & (st.session_state.vagtplan['dato'] == dato), 'medarbejder'] = f"{afloeser} (Overtaget)"
            update_log("Vagtplan opdateret i hukommelsen.", "#22D489", "DATABASE")
            
            # TRIN 3: KOMMUNIKATION (SMS TIL AFLØSER)
            afloeser_data = st.session_state.personale[st.session_state.personale['navn'] == afloeser].iloc[0]
            sms_tekst_kandidat = f"Hej {afloeser}. {syg} er syg. Kan du overtage vagten {dato}? Svar JA for at bekræfte."
            log_sms_kandidat = send_sms(afloeser_data['telefon'], sms_tekst_kandidat, "Afløser")
            update_log(log_sms_kandidat, "#7B61FF", "SMS-OUT")
            
            # TRIN 4: KOMMUNIKATION (NOTIFIKATION TIL CHEF)
            chef_nummer = st.secrets.get("CHEF_PHONE_NUMBER", "+4500000000")
            sms_tekst_chef = f"MJlogs Info: {syg} er sygemeldt {dato}. Vagten er automatisk overdraget til {afloeser}. Vagtplanen er opdateret."
            log_sms_chef = send_sms(chef_nummer, sms_tekst_chef, "Butikschef")
            update_log(log_sms_chef, "#7B61FF", "SMS-OUT")
            
            update_log("Workflow fuldført med succes.", "#22D489", "SUCCES")
            time.sleep(2)
            st.rerun() 
            
        except Exception as e:
            update_log(f"Fejl i AI forbindelsen: {e}", "#FF4B4B", "ERROR")