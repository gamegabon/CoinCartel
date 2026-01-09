import os
import time
import telebot
import google.generativeai as genai
from telebot import types

# --- VOS IDENTIFIANTS (Gardez-les secrets à l'avenir !) ---
TELEGRAM_TOKEN = "8226273057:AAFhvZnAoc0S9OehhngBtDP8DeO12F2mxYU"
GEMINI_API_KEY = "AIzaSyBlgzYmiBG-xivYsJfLJ5PRtT8nyc1oTHE"

# --- VOTRE PROMPT PERSONNALISÉ ---
# Modifiez ce texte pour changer le comportement de l'IA
SYSTEM_PROMPT = """
Tu es un assistant personnel intelligent nommé 'GeminiBot'. 
Ton ton est amical, professionnel et tu réponds toujours en français.
Tu dois aider l'utilisateur avec ses questions, coder avec lui ou simplement discuter.
Utilise des emojis pour rendre la discussion vivante. ✨
"""

# Configuration de l'IA Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# Configuration du Bot Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Dictionnaire pour stocker l'historique des conversations par utilisateur
user_chats = {}

def get_chat_session(user_id):
    """Initialise ou récupère une session de chat pour l'utilisateur."""
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])
    return user_chats[user_id]

# Commande /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        "👋 **Bienvenue sur votre Bot Gemini !**\n\n"
        "Je suis prêt à répondre à toutes vos questions.\n"
        "Utilisez /reset pour effacer notre mémoire."
    )
    bot.reply_to(message, welcome_msg, parse_mode='Markdown')

# Commande /reset pour effacer l'historique
@bot.message_handler(commands=['reset'])
def reset_history(message):
    user_id = message.from_user.id
    if user_id in user_chats:
        del user_chats[user_id]
    bot.reply_to(message, "🔄 Mémoire réinitialisée ! On repart de zéro.")

# Gestionnaire de messages texte
@bot.message_handler(func=lambda message: True)
def handle_ai_chat(message):
    user_id = message.from_user.id
    user_text = message.text

    # Indique que le bot est en train d'écrire
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        # Récupère la session de l'utilisateur
        chat = get_chat_session(user_id)
        
        # Envoie le message à Gemini
        response = chat.send_message(user_text)
        
        # Répond à l'utilisateur sur Telegram
        bot.reply_to(message, response.text, parse_mode='Markdown')

    except Exception as e:
        print(f"Erreur Gemini: {e}")
        bot.reply_to(message, "⚠️ Désolé, j'ai eu un petit problème technique. Réessayez !")

# --- LANCEMENT DU BOT ---
def run_bot():
    print("🚀 Le bot est en cours d'exécution...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Erreur de connexion : {e}")
            time.sleep(5)  # Attend 5 secondes avant de tenter de se reconnecter

if __name__ == "__main__":
    run_bot()
