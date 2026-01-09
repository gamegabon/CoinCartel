import os
import time
import threading
import telebot
import google.generativeai as genai
from flask import Flask
from telebot import types

# --- CONFIGURATION DES CLÉS ---
# Il est fortement conseillé d'utiliser les variables d'environnement sur Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8226273057:AAFhvZnAoc0S9OehhngBtDP8DeO12F2mxYU")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBlgzYmiBG-xivYsJfLJ5PRtT8nyc1oTHE")

# --- CONFIGURATION IA GEMINI ---
SYSTEM_PROMPT = """
Tu es un assistant personnel intelligent nommé 'GeminiBot'. 
Ton ton est amical, professionnel et tu réponds toujours en français.
Tu dois aider l'utilisateur avec ses questions, coder avec lui ou simplement discuter.
Utilise des emojis pour rendre la discussion vivante. ✨
"""

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# --- CONFIGURATION BOT TELEGRAM ---
bot = telebot.TeleBot(TELEGRAM_TOKEN)
user_chats = {}

def get_chat_session(user_id):
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])
    return user_chats[user_id]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = "👋 **Bienvenue !** Je suis prêt à vous aider. /reset pour recommencer."
    bot.reply_to(message, welcome_msg, parse_mode='Markdown')

@bot.message_handler(commands=['reset'])
def reset_history(message):
    user_id = message.from_user.id
    if user_id in user_chats:
        del user_chats[user_id]
    bot.reply_to(message, "🔄 Mémoire réinitialisée !")

@bot.message_handler(func=lambda message: True)
def handle_ai_chat(message):
    user_id = message.from_user.id
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        chat = get_chat_session(user_id)
        response = chat.send_message(message.text)
        bot.reply_to(message, response.text, parse_mode='Markdown')
    except Exception as e:
        print(f"Erreur: {e}")
        bot.reply_to(message, "⚠️ Erreur technique. Réessayez !")

# --- CONFIGURATION FLASK (Pour Render) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is alive!", 200

def run_bot():
    print("🚀 Bot Telegram démarré...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Erreur polling: {e}")
            time.sleep(5)

# --- POINT D'ENTRÉE ---
if __name__ == "__main__":
    # Lancement du bot dans un thread séparé
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Lancement de Flask sur le port requis par Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
