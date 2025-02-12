import streamlit as st
import requests
import datetime
import os
from langchain.llms.ollama import Ollama
TELEGRAM_BOT_TOKEN = "7649680660:AAFVgGrxKyAPnpeBUGEqBzYfqYNLTupy6cI"
TELEGRAM_CHAT_ID = os.getenv("codsassistantbot")        

BANNED_WORDS = ["блять", "сука", "пиздец", "хуй"]  # добавьте реальные примеры нецензурных слов
NEGATIVE_KEYWORDS = ["пошел нахуй", "иди в жопу", "заебал", "хуй", "пизда"]

def check_query(query: str):
    """
    Проверка запроса на наличие нецензурной лексики и негативных эмоций.
    Возвращает два флага: (flagged, negative_flag)
    """
    query_lower = query.lower()
    flagged = any(bad_word in query_lower for bad_word in BANNED_WORDS)
    negative_flag = any(neg in query_lower for neg in NEGATIVE_KEYWORDS)
    return flagged, negative_flag

# ------------------------------
# Функция для отправки уведомления в Telegram
# ------------------------------
def send_telegram_notification(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            st.write("Уведомление отправлено менеджеру.")
        else:
            st.write("Ошибка при отправке уведомления:", response.text)
    except Exception as e:
        st.write("Ошибка при отправке уведомления:", e)

# ------------------------------
# Настройка памяти
# ------------------------------

# Краткосрочная память – храним текущий диалог в сессии Streamlit
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Долговременная память – для простоты сохраняем историю в файл (можно заменить на БД)
LONG_TERM_MEMORY_FILE = "chat_history.txt"

def save_to_long_term_memory(user: str, query: str, response: str):
    """Сохраняет диалог в файл с отметкой времени."""
    timestamp = datetime.datetime.now().isoformat()
    with open(LONG_TERM_MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {user} | {query} | {response}\n")

def get_long_term_memory():
    """Возвращает содержимое долговременной памяти."""
    if os.path.exists(LONG_TERM_MEMORY_FILE):
        with open(LONG_TERM_MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return "Долговременная память пуста."

llm = Ollama(model="llama3.2", base_url="http://localhost:11434", temperature=0)

def generate_response(query: str, context: str = "") -> str:
    """
    Генерирует ответ LLM с учетом контекста.
    Формируем запрос, включающий контекст (историю диалога).
    """
    prompt = f"Контекст диалога:\n{context}\n\nВопрос: {query}\nОтвет:"
    response = llm(prompt)
    return response

# ------------------------------
# Интерфейс Streamlit
# ------------------------------
st.title("Умный ассистент поддержки клиентов")
st.markdown("Введите ваш запрос ниже:")

# Поле ввода запроса
user_input = st.text_input("Ваш запрос:")

if st.button("Отправить запрос") and user_input:
    # Проверка запроса на нецензурную лексику и негатив
    flagged, negative_flag = check_query(user_input)
    if flagged:
        st.error("Запрос содержит нецензурную лексику. Пожалуйста, переформулируйте запрос.")
    else:
        if negative_flag:
            # Если обнаружены негативные эмоции, отправляем уведомление менеджеру
            send_telegram_notification(f"Негативный запрос: {user_input}")
        
        # Добавляем запрос в краткосрочную память
        st.session_state.chat_history.append({"user": "Пользователь", "message": user_input})
        # Формируем контекст из краткосрочной памяти (история диалога)
        context = "\n".join([f"{entry['user']}: {entry['message']}" for entry in st.session_state.chat_history])
        # Генерируем ответ с учетом контекста
        response = generate_response(user_input, context)
        st.session_state.chat_history.append({"user": "Ассистент", "message": response})
        # Сохраняем диалог в долговременную память
        save_to_long_term_memory("Пользователь", user_input, response)
        st.success("Ответ ассистента:")
        st.write(response)

# Отображение истории диалога (краткосрочная память)
st.markdown("## История диалога (краткосрочная память)")
for entry in st.session_state.chat_history:
    st.write(f"**{entry['user']}:** {entry['message']}")

# Отображение долговременной памяти (история общения)
st.markdown("## Долговременная память (история общения)")
long_term_content = get_long_term_memory()
st.text_area("Долговременная память", long_term_content, height=200)

# Возможность загрузки файлов (например, скриншотов проблемы)
st.markdown("## Загрузить файл (например, скриншот проблемы)")
uploaded_file = st.file_uploader("Выберите файл", type=["png", "jpg", "jpeg", "pdf"])
if uploaded_file is not None:
    st.image(uploaded_file, caption="Загруженное изображение", use_column_width=True)