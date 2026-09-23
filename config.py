from datetime import timedelta

# Telegram Alert Configuration
TELEGRAM_BOT_TOKEN = "8773968873:AAFkcIjjNKcbRwNEjS4AZWwojuNGsr01zGs"
TELEGRAM_CHAT_ID = "@ractz_store_message"
TELEGRAM_ALERT_COOLDOWN = 300  # Cooldown in seconds (5 minutes) to prevent alert spamming

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = "sqlite:///mydb.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session & Security configuration
    SECRET_KEY = "ractz-demo-secret-key"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=1440)  # session TTL (1 day)

