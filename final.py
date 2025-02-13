import streamlit as st
import requests
import datetime
import os
import io
from langchain.llms.ollama import Ollama

TELEGRAM_BOT_TOKEN = "7649680660:AAFVgGrxKyAPnpeBUGEqBzYfqYNLTupy6cI"
TELEGRAM_CHAT_ID = "1065095470"       

BANNED_WORDS = [
    "violence",
    "terrorism",
    "drugs",
    "weapon",
    "fraud",
    "scam",
    "hate speech",
    "exploit",
    "abuse",
    "illegal",
    "pornography",
    "child exploitation",
    "racism",
    "extremism",
    "cybercrime",
    "hacking",
    "phishing",
    "harassment",
    "torture",
    "suicide"
]
NEGATIVE_KEYWORDS = [
    "fuck",
    "shit",
    "bitch",
    "asshole",
    "bastard",
    "damn",
    "dick",
    "prick",
    "cunt",
    "motherfucker",
    "slut",
    "whore"
]

# Дизайн
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    /* Фон приложения */
    .stApp {
        background-color: #476C9D;
    }

    /* Сайдбар */
    section[data-testid="stSidebar"] {
        background-color: #2E4C72;
    }

    /* Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #1B3553;
        border: 1px solid #1B3553;
    }
    ul {
        background-color: #1B3553;
        border: #1B3553;
    }
    li:hover {
        background-color: #2E4C72;
    }

    /* Поля ввода input и textarea */
    input[type="text"], input[type="number"], textarea {
        background-color: #2E4C72;
        border: 1px solid #2E4C72;
    }

    /* Стили для textarea (st.text_area) */
    div[data-testid="stTextArea"] textarea {
        background-color: #2E4C72;
        border: 1px solid #2E4C72;
    }

    /* Фокус для всех input и textarea */
    input:focus, textarea:focus {
        border: 1px solid #7497CF !important;
        outline: none;
    }

    /* Кнопка */
    div.stButton > button:first-child {
        background-color: #2E4C72;
        border: 1px solid #1B3553;
    }
    div.stButton > button:hover {
        background-color: #1B3553;
        color: white;
    }
    div.stButton > button:active {
        background-color: #7497CF;
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def check_query(query: str):
    """
    Проверяет запрос на наличие запрещённых слов и негативных эмоций.
    Возвращает два флага: (flagged, negative_flag)
    """
    query_lower = query.lower()
    flagged = any(bad_word in query_lower for bad_word in BANNED_WORDS)
    negative_flag = any(neg in query_lower for neg in NEGATIVE_KEYWORDS)
    return flagged, negative_flag

# Функция для отправки уведомления в Telegram
def send_telegram_notification(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            st.write("Notification sent to manager.")
        else:
            st.write("Error sending notification:", response.text)
    except Exception as e:
        st.write("Error sending notification:", e)

# --- Memory settings ---
# Краткосрочная память – хранится в сессии Streamlit
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Долговременная память – сохраняется в файле (можно заменить на базу данных)
LONG_TERM_MEMORY_FILE = "chat_history.txt"

def save_to_long_term_memory(user: str, query: str, response: str):
    """
    Сохраняет диалог в файл с отметкой времени.
    """
    timestamp = datetime.datetime.now().isoformat()
    with open(LONG_TERM_MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {user} | {query} | {response}\n")

def get_long_term_memory():
    """
    Возвращает содержимое долговременной памяти.
    """
    if os.path.exists(LONG_TERM_MEMORY_FILE):
        with open(LONG_TERM_MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return "Long-term memory is empty."

# Выбор модели через боковую панель Streamlit
st.sidebar.header("Model settings")
model_choice = st.sidebar.selectbox(
    "Select LLM model:",
    ["llama3.2", "mistral", "llama2"]
)
st.sidebar.write(f"Current model: {model_choice}")

llm = Ollama(model=model_choice, base_url="http://localhost:11434", temperature=0)

# Генерация ответа от LLM
def generate_response(query: str, context: str = "") -> str:
    response = llm(query)
    return response

# --- Streamlit Interface ---
st.title("Smart Customer Support Assistant")
st.image("blue_cat.jpg", width=150)
st.markdown("Enter your query below:")

# Поле ввода запроса
user_input = st.text_input("Your request:")

if st.button("Send request") and user_input:
    # Проверка запроса на запрещённые слова и негатив
    flagged, negative_flag = check_query(user_input)
    if flagged:
        st.error("The request contains forbidden language. Please rephrase the request.")
    else:
        if negative_flag:
            # При обнаружении негатива отправляем уведомление менеджеру
            send_telegram_notification(f"Negative request: {user_input}")
        
        # Добавляем запрос в краткосрочную память
        st.session_state.chat_history.append({"user": "User", "message": user_input})
        # Формируем контекст диалога из краткосрочной памяти
        context = "\n".join([f"{entry['user']}: {entry['message']}" for entry in st.session_state.chat_history])
        # Генерируем ответ с учётом контекста
        response = generate_response(user_input, context)
        st.session_state.chat_history.append({"user": "Assistant", "message": response})
        # Сохраняем диалог в долговременную память
        save_to_long_term_memory("User", user_input, response)
        st.success("Assistant's answer:")
        st.write(response)

with st.sidebar:
    # Отображение истории диалога (краткосрочная память)
    st.markdown("## Dialogue history (short-term memory)")
    for entry in st.session_state.chat_history:
        st.write(f"**{entry['user']}:** {entry['message']}")
    
    # Отображение долговременной памяти (история общения)
    st.markdown("## Long-term memory (communication history)")
    long_term_content = get_long_term_memory()
    st.text_area("Long-term memory", long_term_content, height=200)

