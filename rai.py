import os
import openai
from openai import OpenAI
import streamlit as st
import tempfile
from pydub import AudioSegment
import requests
from io import BytesIO
import re

# Set up OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI()

# Create the assistant
assistant = client.beta.assistants.create(
    name="911 Operator Assistant",
    instructions='You are a 911 operator assistant. Answer questions using information only from the provided file. \
                  Your response must be in an informative, yet concise list format. If there is no information in \
                  the file that can answer a question, answer with "Sorry, I am unable to answer this question, as \
                  it is not covered by protocol."',
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)

# Create vector store + upload docs
vector_store = client.vector_stores.create(name="911 Operator Protocol")

pdf_urls = [
    "https://raw.githubusercontent.com/blazeshadowflame/testdeploy/main/RescueAI_Traffic_Accidents%20dialogue%20transcript.pdf",
    "https://raw.githubusercontent.com/blazeshadowflame/testdeploy/main/RescueAI_Synthetic_911_Scenarios.pdf"
]

file_streams = []
for url in pdf_urls:
    response = requests.get(url)
    response.raise_for_status()
    filename = url.split("/")[-1]
    file_streams.append((filename, BytesIO(response.content), "application/pdf"))

client.vector_stores.file_batches.upload_and_poll(vector_store_id=vector_store.id, files=file_streams)

# Attach vector store to assistant
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

def assistant_chatbot(message):
    thread = client.beta.threads.create(messages=[{"role": "user", "content": message}])
    run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant.id)
    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
    return messages[0].content[0].text.value


def clean_recommendation(text):
    cleaned_text = re.sub(r'【.*?】', '', text)
    return cleaned_text.strip()


def transcribe_audio_chunks_live(audio_path, chunk_length_ms=5000):
    audio = AudioSegment.from_file(audio_path)
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

    full_transcription = ""
    transcription_placeholder = st.empty()

    with st.spinner("Transcribing audio in real-time simulation..."):
        for chunk in chunks:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                chunk.export(temp_audio_file.name, format="wav")
                response = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=open(temp_audio_file.name, "rb"),
                    language="en",
                )
                full_transcription += response.text.strip() + " "
                transcription_placeholder.markdown(full_transcription.strip())

    return full_transcription.strip()


def extract_keywords(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": f"You are a 911 operator assistant. Extract keywords from {text} that would be important \
                for a 911 operator to use. Your response should be in a comma-separated list format. Avoid filler \
                and irrelevant information.",
            },
        ],
    )
    return response.choices[0].message.content


def generate_operator_recommendation(transcription):
    prompt = f"Based on this 911 call transcription: {transcription}, recommend an immediate course of action for the operator. List 2-3 key steps."
    raw_response = assistant_chatbot(prompt)
    return clean_recommendation(raw_response)

# ===== UI CUSTOM STYLES ===== 🔧 MODIFIED
st.markdown(
    """
    <style>
    .stApp {background-color: #183866; color: #fdf6e3;}
    section[data-testid="stSidebar"] {background-color: #c2a611 !important; color: black !important;}
    section[data-testid="stSidebar"] h2 {color: black !important;}
    .stTextArea textarea {
        border: none !important;
        background-color: transparent !important;
        color: #fdf6e3 !important;
        font-size: 1rem;
    }
    .stTextArea textarea:disabled {
        background-color: transparent !important;
        color: #aaaaaa !important;
    }
    .stButton>button {background-color: #ffd700; color: black; border-radius: 8px;}
    h1 {color: #c2a611;}
    .description-text {color: #fdf6e3; font-size: 1.05rem; margin-bottom: 1.5rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ===== MAIN UI ===== 🔧 MODIFIED
st.title("📞 Emergency Audio Transcription")
st.markdown(
    """
    <div class="description-text">
    <strong style="color:#ffd700;">Record your 911 call audio below.</strong><br>
    The system will transcribe the message live, allow confirmation, highlight important keywords, and suggest actions.
    </div>
    """,
    unsafe_allow_html=True
)

if "full_transcription" not in st.session_state:
    st.session_state.full_transcription = ""
if "audio_processed" not in st.session_state:
    st.session_state.audio_processed = False
if "confirm_clicked" not in st.session_state:
    st.session_state.confirm_clicked = False

audio_file = st.audio_input("🎙️ Record your audio:")

if audio_file and not st.session_state.audio_processed:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_file.read())
        tmp_audio_path = tmp_file.name

    st.subheader("🔍 Live Transcription Feed")
    full_transcription = transcribe_audio_chunks_live(tmp_audio_path)

    st.session_state.full_transcription = full_transcription
    st.session_state.audio_processed = True

if st.session_state.audio_processed:
    edited_transcription = st.text_area(
        "Review and edit the transcription below if needed:",
        value=st.session_state.full_transcription.strip(),
        height=300,
        key="edited_transcription_area",
        disabled=st.session_state.confirm_clicked
    )

    confirm_button = st.button("✅ Confirm Transcription", disabled=st.session_state.confirm_clicked)

    if confirm_button:
        st.session_state.confirm_clicked = True

        st.subheader("🔍 Extracted Emergency Keywords")
        keywords = extract_keywords(edited_transcription)
        st.text_area("Keywords:", keywords, height=200)

        st.subheader("📋 Operator Action Recommendation")
        recommendation = generate_operator_recommendation(edited_transcription)
        st.markdown(recommendation)

# ===== CHATBOT SIDEBAR ===== 🔧 MODIFIED
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

with st.sidebar:
    st.markdown("## 🧠 Rai – 911 Assistant Chatbot")
    st.markdown(
        "Ask Rai about emergency protocols, traffic accident procedures, or how dispatchers should respond to various scenarios. Responses are based on real dispatcher documents."
    )

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("💬 Ask Rai a question...")
    if user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.spinner("Rai is thinking..."):
            raw_response = assistant_chatbot(user_input)
            clean_response = clean_recommendation(raw_response)  # 🛠️ Clean it here!
        st.session_state.chat_messages.append({"role": "assistant", "content": clean_response})
        st.rerun()

