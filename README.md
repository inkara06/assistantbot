# README

## Project Description
This project is a web application built using the Streamlit framework. It integrates the Ollama language model via the LangChain library and utilizes the Telegram API to send notifications. A banned words filter is implemented to ensure safety.

## Features
- Users input text through the Streamlit interface.
- The text is processed using the Ollama model.
- The text is checked for banned words (BANNED_WORDS list).
- If a banned word is detected, a notification is sent to Telegram.
- The model's output is displayed.

## Technologies Used
- Python
- Streamlit
- LangChain (Ollama)
- Telegram API

## How to Run the Project
1. Install the required libraries:
    ```bash
    pip install streamlit langchain requests
    ```
2. Run the application:
    ```bash
    streamlit run final.py
    ```

## Variables
- `TELEGRAM_BOT_TOKEN` – your Telegram bot token.
- `TELEGRAM_CHAT_ID` – the chat ID to which notifications will be sent.
- `BANNED_WORDS` – the list of banned words.

## Important
Before running the application, ensure you replace the values of `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` with your own, so notifications are sent correctly.

## Authors
This project was created by:
Dariya Ablanova
Inkar Ussurbayeva
Leila Alpieva
