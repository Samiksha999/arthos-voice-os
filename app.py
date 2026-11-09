import streamlit as st
import requests
import pandas as pd
import re
import os
import copy
import speech_recognition as sr
from io import BytesIO

# ==========================================
# PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="ArthOS | Sovereign Indic Voice OS",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ ArthOS: Sovereign Indic Voice OS")
st.caption("Frictionless Local Speech Extraction & Gnani AI Timbre v2.5 Voice Confirmation")

# ==========================================
# SIDEBAR: CONFIG & COMMANDS
# ==========================================
with st.sidebar:
    st.header("🔑 Configuration")
    api_key = st.text_input(
        "Enter Gnani API Key (X-API-Key-ID)",
        value=os.getenv("GNANI_API_KEY", ""),
        type="password",
        placeholder="vach_..."
    )
    st.info("Your API key is used strictly for the Gnani Timbre TTS voice output synthesis.")

    st.divider()
    st.subheader("🗣️ Try Speaking These:")
    st.markdown("""
    - **Hinglish Order:** *"Bhaiya, do kilo sugar aur ek Amul butter add karo"*
    - **Hindi Order:** *"Teen Maggi aur ek milk bill mein daalo"*
    - **Marathi Khata:** *"Ye bill Ramesh ke khata mein daal do"*
    - **Balance Check:** *"Amit ka kitna udhaar baaki hai?"*
    - **Clear Bill:** *"Bill clear karo"*
    """)

# ==========================================
# DATA CONFIGURATION & CONSTANTS
# ==========================================
INITIAL_INVENTORY = {
    "sugar": {"name": "Sugar (1 kg)", "price": 45, "stock": 20, "aliases": ["sugar", "cheeni", "sakhar", "चीनी", "साखर"]},
    "atta": {"name": "Aashirvaad Atta (1 kg)", "price": 55, "stock": 15, "aliases": ["atta", "aata", "flour", "आटा", "कणिक"]},
    "milk": {"name": "Amul Milk (1 L)", "price": 66, "stock": 12, "aliases": ["milk", "doodh", "dudh", "दूध"]},
    "rice": {"name": "Basmati Rice (1 kg)", "price": 90, "stock": 18, "aliases": ["rice", "chawal", "tandul", "चावल", "तांदूळ"]},
    "maggi": {"name": "Maggi Noodles (Pack)", "price": 15, "stock": 30, "aliases": ["maggi", "maggie", "noodles", "मैगी", "मॅगी"]},
    "butter": {"name": "Amul Butter (100g)", "price": 58, "stock": 3, "aliases": ["butter", "makhan", "makkhan", "मक्खन", "लोणी"]},
}

NUMBER_WORDS = {
    "ek": 1, "one": 1, "एक": 1,
    "do": 2, "two": 2, "don": 2, "दो": 2, "दोन": 2,
    "teen": 3, "three": 3, "tin": 3, "तीन": 3,
    "char": 4, "four": 4, "चार": 4,
    "panch": 5, "five": 5, "ंच": 5, "पाच": 5,
}

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "inventory" not in st.session_state:
    st.session_state.inventory = copy.deepcopy(INITIAL_INVENTORY)

if "cart" not in st.session_state:
    st.session_state.cart = list()

if "khata" not in st.session_state:
    st.session_state.khata = {
        "Ramesh": 450,
        "Amit": 1200,
        "Suresh": 300,
        "Priya": 0
    }

if "history" not in st.session_state:
    st.session_state.history = list()

# ==========================================
# CORE VOICE PIPELINE ENGINE
# ==========================================
def extract_local_stt(audio_bytes):
    recognizer = sr.Recognizer()
    audio_file = BytesIO(audio_bytes)
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    # Using open speech routing that natively accommodates code-mixed Indic vocabulary
    return recognizer.recognize_google(audio_data, language="hi-IN")

def run_tts(text, key):
    url = "https://vachana.ai"
    headers = {
        "X-API-Key-ID": key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "language": "hi-IN",
        "voice": "Nalini",
        "model": "timbre-v2.5"
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.content

# ==========================================
# PROCESSING UTILITIES
# ==========================================
def extract_quantity(text_segment):
    digit_match = re.search(r"\b(\d+)\b", text_segment)
    if digit_match:
        return int(digit_match.group(1))
    for word, val in NUMBER_WORDS.items():
        if re.search(rf"\b{re.escape(word)}\b", text_segment):
            return val
    return 1

def process_voice_command(transcript):
    text = transcript.lower().strip()

    if any(w in text for w in ["clear", "reset", "hatao", "cancel"]):
        st.session_state.cart = list()
        return "Bill clear kar diya gaya hai."

    if any(w in text for w in ["baaki", "baki", "balance", "kitna"]):
        for customer, bal in st.session_state.khata.items():
            if customer.lower() in text:
                return f"{customer} ka total {bal} rupaye udhaar baaki hai."

    if any(w in text for w in ["khata", "udhaar", "udhar"]):
        target_customer = "Ramesh"
        for customer in st.session_state.khata.keys():
            if customer.lower() in text:
                target_customer = customer
                break

        cart_total = sum(item["subtotal"] for item in st.session_state.cart)
        if cart_total == 0:
            return "Abhi bill mein koi item nahi hai."

        st.session_state.khata[target_customer] += cart_total
        st.session_state.cart = list()
        return f"{cart_total} rupaye {target_customer} ke khata mein add kar diye hain. Ab unka total udhaar {st.session_state.khata[target_customer]} rupaye hai."

    added_items = list()
    for sku, info in st.session_state.inventory.items():
        for alias in info["aliases"]:
            if alias in text:
                alias_idx = text.find(alias)
                lookback_window = text[max(0, alias_idx - 15):alias_idx]
                qty = extract_quantity(lookback_window)

                if info["stock"] < qty:
                    return f"Maaf kijiye, {info['name']} out of stock hai."

                info["stock"] -= qty
                subtotal = qty * info["price"]

                st.session_state.cart.append({
                    "name": info["name"],
                    "qty": qty,
                    "price": info["price"],
                    "subtotal": subtotal
                })
                added_items.append(f"{qty} {info['name']}")
                break

    if added_items:
        total_bill = sum(i["subtotal"] for i in st.session_state.cart)
        return f"{', '.join(added_items)} add kar diya hai. Total bill {total_bill} rupaye hua."

    return "Kripya item ka naam ya khata command phir se bolein."

# ==========================================
# DASHBOARD UI GRID LAYOUT
# ==========================================
col_left, col_right = st.columns((1.0, 1.1), gap="large")

with col_left:
    st.subheader("🎙️ Voice Command Console")
    audio_value = st.audio_input("Record your order or khata command")

    if audio_value is not None:
        if st.button("🚀 Process Voice Command", type="primary", use_container_width=True):
            try:
                with st.spinner("Extracting local multi-lingual speech signals..."):
                    audio_bytes = audio_value.read()
                    transcript = extract_local_stt(audio_bytes)
                    
                if not transcript.strip():
                    st.warning("Could not capture speech clearly. Please speak closer to your microphone.")
                else:
                    reply_text = process_voice_command(transcript)
                    
                    # Synthesize with Gnani Timbre if API key is provided
                    tts_audio = None
                    if api_key.strip():
                        with st.spinner("Synthesizing responsive voice output via Gnani Timbre..."):
                            try:
                                tts_audio = run_tts(reply_text, api_key)
                            except:
                                pass

                    st.session_state.history.insert(0, {
                        "user": transcript,
                        "bot": reply_text,
                        "audio": tts_audio
                    })
            except Exception as e:
                st.error(f"Execution Error: {e}. Please ensure your mic recording is longer than 2 seconds.")

    st.divider()
    st.subheader("💬 Recent Voice Interactions")
    if not st.session_state.history:
        st.caption("No commands processed yet.")
    else:
        for entry in st.session_state.history[:3]:
            with st.container(border=True):
                st.markdown(f"**You Said:** *\"{entry['user']}\"*")
                st.markdown(f"**ArthOS:** {entry['bot']}")
                if entry["audio"]:
                    st.audio(entry["audio"], format="audio/wav")

with col_right:
    st.subheader("🧾 Active Bill (Current Cart)")
    if st.session_state.cart:
        cart_df = pd.DataFrame(st.session_state.cart)[["name", "qty", "price", "subtotal"]]
        cart_df.columns = ["Item", "Qty", "Rate (₹)", "Subtotal (₹)"]
        st.dataframe(cart_df, use_container_width=True, hide_index=True)
        st.metric(label="Total Payable", value=f"₹ {sum(i['subtotal'] for i in st.session_state.cart)}")
    else:
        st.info("Cart khali hai. Try speaking: 'Do kilo sugar aur ek Amul butter add karo'")

    st.divider()
    tab_khata, tab_stock = st.tabs(["📒 Customer Khata Ledger", "📦 Live Store Inventory"])
    
    with tab_khata:
        khata_df = pd.DataFrame([{"Customer Name": k, "Pending Udhaar (₹)": v} for k, v in st.session_state.khata.items()])
        st.dataframe(khata_df, use_container_width=True, hide_index=True)
        
    with tab_stock:
        stock_rows = [{"Item Description": info["name"], "In Stock": info["stock"], "Status": "⚠️ LOW STOCK" if info["stock"] <= 3 else "✅ Active"} for info in st.session_state.inventory.values()]
