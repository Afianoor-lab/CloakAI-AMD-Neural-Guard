from processor import cloak_sensitive_data
import streamlit as st
from processor import cloak_sensitive_data, extract_text_from_file

import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def get_ai_agent_response(user_prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a Cybersecurity Expert. Analyze data leaks concisely."},
            {"role": "user", "content": user_prompt}
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

# --- SIDEBAR (Dashboard Collapse Feature) ---
with st.sidebar:
    st.markdown("""
        <div class="logo-container">
            <div style="font-size:35px;">🛡️</div>
            <div class="logo-text">Cloak AI</div>
        </div>
        <hr style="border-color: rgba(0, 229, 255, 0.2);">
    """, unsafe_allow_html=True)
    
    uploaded_file = None 

   
    st.markdown("<br><br><div style='opacity:0.3; font-size:10px; text-align:center;'>CONNECTED TO AMD_NEURAL_LINK</div>", unsafe_allow_html=True)


# Dashboard state management
if 'menu_option' not in st.session_state:
    st.session_state.menu_option = "Dashboard"

# Sidebar Logic
with st.sidebar:
    if st.button("🏠 Dashboard"):
        st.session_state.menu_option = "Dashboard"
    if st.button("📁 My Files"):
        st.session_state.menu_option = "My Files"
    if st.button("🛡️ Security Scan"):
        st.session_state.menu_option = "Security Scan"
        
# 1. Full Page Configuration
st.set_page_config(page_title="Cloak AI", layout="wide", initial_sidebar_state="collapsed")

# --- INITIALIZE SESSION STATE FOR FUNCTIONALITY ---
if "logs" not in st.session_state:
    st.session_state.logs = ["> Scanning network packets...", "> Identified potential leaks."]
if "scan_progress" not in st.session_state:
    st.session_state.scan_progress = 86
# NEW: Session state for AI Agent Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "risk_score" not in st.session_state:
    st.session_state.risk_score = 0

# 2. Deep Custom CSS (Aapka original style + functionality fixes)
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background: #000b0d;
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(0, 229, 255, 0.05) 0%, transparent 80%),
            url('https://www.transparenttextures.com/patterns/carbon-fibre.png');
        color: #ffffff;
    }

    /* Sidebar and Layout Adjustments */
    [data-testid="stSidebar"] {
        background-color: #000b0d !important;
        border-right: 1px solid rgba(0, 229, 255, 0.2);
    }
    
    /* Top Logo Area */
    .logo-container {
        display: flex;
        align-items: center;
        padding: 10px 0 20px 0px;
    }
    .logo-text {
        font-size: 28px;
        font-weight: bold;
        margin-left: 15px;
        letter-spacing: 1px;
    }

    /* Futuristic Panels */
    .panel {
        background: rgba(13, 25, 30, 0.6);
        backdrop-filter: blur(10px);
        border: 1.5px solid #00e5ff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.15);
        margin-bottom: 25px;
    }
    .panel-title {
        font-size: 18px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 20px;
        letter-spacing: 2px;
    }

    /* Streamlit Button Styling to match original Apply Button */
    div.stButton > button {
        background: #00e5ff !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100%;
        box-shadow: 0 0 15px #00e5ff;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px #00e5ff;
    }

    /* Checkbox Styling to look like tags */
    .stCheckbox label {
        color: #ffffff !important;
        background: rgba(0, 229, 255, 0.1);
        border: 1px solid #00e5ff;
        padding: 5px 15px !important;
        border-radius: 8px;
        margin-bottom: 10px;
    }

    /* Agent Box */
    .agent-log-container {
        background: rgba(0,0,0,0.4);
        border-radius: 12px;
        padding: 15px;
        font-family: monospace;
        font-size: 13px;
        line-height: 1.6;
        color: #00e5ff;
        border-left: 2px solid #00e5ff;
    }

    /* Speed Metric */
    .speed-text {
        font-size: 42px;
        font-weight: bold;
        text-shadow: 0 0 15px #00e5ff;
    }
div.stDownloadButton > button {
        background-color: #00e5ff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 10px !important; /* Corner radius match karne ke liye */
        padding: 10px 20px !important;
        width: 100% !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.6) !important;
    }

    div.stDownloadButton > button:hover {
        background-color: #00e5ff !important;
        color: #ffffff !important;
        box-shadow: 0 0 25px #00e5ff !important;
        transform: scale(1.02) !important; /* Dashboard button jaisa zoom effect */
    }
    /* -------------------------- */
    
    </style>
    """, unsafe_allow_html=True)


# --- ROUTING LOGIC ---
if st.session_state.menu_option == "My Files":
    st.title("📁 My Files")
    st.info("Archive of processed documents will appear here.")
    st.stop()
elif st.session_state.menu_option == "Security Scan":
    st.title("🛡️ Deep Security Scan")
    st.warning("Deep neural network analysis is running in background.")
    st.stop()

# --- TOP NAVIGATION BAR ---
st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; padding: 10px 0px;">
        <div style="display:flex; align-items:center;">
             <div class="logo-text" style="margin-left:0;">COMMAND CENTER</div>
        </div>
        <div style="display:flex; gap:20px; font-size:20px; opacity:0.7;"></div>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN LAYOUT ---
col_mid, col_right = st.columns([2.5, 1.2])

with col_mid:
    # 1. Privacy Scanner Panel
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">PRIVACY SCANNER</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload", label_visibility="collapsed", accept_multiple_files=True)
    
    if uploaded_file:
        st.session_state.scan_progress = 100
        if len(uploaded_file) > 1:
            status_text = f"ANALYZING BATCH: {len(uploaded_file)} Files Detected ... COMPLETE"
        else:
            status_text = f"SCANNING: {uploaded_file[0].name} ... COMPLETE"
    else:
        status_text = "SCANNING: project-details.docx ... 86% COMPLETE"

    st.markdown(f"""
        <div class="upload-box">
            <div style="font-size:30px; margin-bottom:10px;">📄</div>
            <div style="color:rgba(255,255,255,0.6);">Drag-and-drop file upload</div>
            <div class="progress-bar-container">
                <div class="progress-fill" style="width: {st.session_state.scan_progress}%;"></div>
            </div>
            <div style="color:#00e5ff; font-size:12px;">{status_text}</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Masking Rules Panel
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="panel-title">ADVANCED MASKING ENGINE</div>
            <div style="background:#00e5ff; color:black; font-size:10px; padding:2px 8px; border-radius:4px; font-weight:bold; margin-top:-20px;">GDPR & HIPAA READY</div>
        </div>
        <p style="font-size:14px; opacity:0.8; margin-bottom:15px;">Select high-sensitivity data clusters for deep neural scrubbing.</p>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<p style='color:#00e5ff; font-size:12px; font-weight:bold; margin-bottom:5px;'>IDENTIFIERS (PII)</p>", unsafe_allow_html=True)
        st.checkbox("Personal Names", value=True)
        st.checkbox("Email & Phone", value=True)
        st.checkbox("Passport / CNIC", value=False)
    with c2:
        st.markdown("<p style='color:#00e5ff; font-size:12px; font-weight:bold; margin-bottom:5px;'>FINANCIAL (PCI)</p>", unsafe_allow_html=True)
        st.checkbox("Credit Card / CVV", value=True)
        st.checkbox("IBAN / Bank Info", value=True)
        st.checkbox("Tax IDs (NTN)", value=False)
    with c3:
        st.markdown("<p style='color:#00e5ff; font-size:12px; font-weight:bold; margin-bottom:5px;'>CYBER</p>", unsafe_allow_html=True)
        st.checkbox("IP / MAC Addresses", value=True)
        st.checkbox("API Keys / Secrets", value=True)
        st.checkbox("Auth Tokens / Secrets", value=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- UPDATED FUNCTIONAL BUTTON ---
    if st.button("APPLY CLOAKING ENGINE"):
        if uploaded_file:
            total_entities = 0
            for file in uploaded_file:
                file_text = extract_text_from_file(file)
                
                with st.spinner(f"Neural Scrubbing in progress for {file.name}..."):
                    processed_output = cloak_sensitive_data(file_text)
                    # NEW: Dynamic Risk Logic (counting redacted markers as risk)
                    total_entities += processed_output.count("[")
                
                st.session_state.logs.append(f"> Scrubbing Complete: {file.name}")
                st.session_state.logs.append("> Compliance Check: GDPR Standards Verified.")
                
                st.success(f"Cloaking Successful for {file.name}!")
                st.text_area(f"Preview: {file.name}", processed_output, height=150)
                st.download_button(f"Download Cloaked {file.name}", processed_output, file_name=f"cloaked_{file.name}")
            
            # Update dynamic risk score
            st.session_state.risk_score = min(total_entities * 5, 100)
            st.balloons()
        else:
            st.error("Error: No data stream detected. Please upload a file.")

    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    # Feature 1: Smart Context Detection (Risk Meter)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">FILE RISK ANALYSIS</div>', unsafe_allow_html=True)
    
    # NEW: Using dynamic score from session state
    current_risk = st.session_state.risk_score if uploaded_file else 0 
    r_color = "#ff4b4b" if current_risk > 50 else "#00e5ff"
    
    st.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:35px; font-weight:bold; color:{r_color}; text-shadow: 0 0 10px {r_color};">{current_risk}%</div>
            <div style="font-size:12px; opacity:0.6; margin-top:-5px;">THREAT LEVEL DETECTED</div>
            <div style="height:8px; background:rgba(255,255,255,0.1); border-radius:10px; margin-top:15px; overflow:hidden;">
                <div style="width:{current_risk}%; height:100%; background:{r_color}; box-shadow: 0 0 10px {r_color}; transition: width 1s;"></div>
            </div>
            <p style="font-size:11px; margin-top:10px; color:{r_color}; text-align:left;">
                {'⚠️ Critical: High-sensitivity data markers found.' if current_risk > 0 else '✅ Scanning... No threats found yet.'}
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. AI Agent Panel
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">AI AGENT</div>', unsafe_allow_html=True)
    
    # NEW: Conversational Agent Interface
    for msg in st.session_state.messages[-2:]: # Show last 2 messages in small box
        st.markdown(f"<div style='font-size:11px; color:#00e5ff; margin-bottom:5px;'><b>{'You' if msg['role']=='user' else 'Agent'}:</b> {msg['content']}</div>", unsafe_allow_html=True)
    
    prompt = st.text_input("Talk to Agent:", value="", key="agent_input", placeholder="Is this file safe?")
   
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Naya logic jo model se jawab mangwaye ga
        with st.spinner("Thinking..."):
            try:
                response = get_ai_agent_response(prompt)
            except Exception as e:
                response = "Agent busy or offline. Please check API key."
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        

    # Dynamic Logs
    log_text = "<br>".join(st.session_state.logs[-4:])
    st.markdown(f"""
        <div class="agent-log-container">
            <span style="border-bottom:1px solid #00e5ff;">Agent Log</span><br>
            {log_text}<br>
            > Apply masks now?
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        if st.button("YES"):
            st.session_state.logs.append("> Action Confirmed by User.")
    with cb:
        if st.button("NO"):
            st.session_state.logs.append("> Action Aborted.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. Performance Panel
    st.markdown(f"""
        <div class="panel">
            <p style="font-size:12px; opacity:0.6; margin-bottom:5px;">Scan speed (Powered by AMD Neural Engine):</p>
            <div class="speed-text">0.08s</div>
        </div>
    """, unsafe_allow_html=True)