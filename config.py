from datetime import timedelta

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = "sqlite:///mydb.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session & Security configuration
    SECRET_KEY = "ractz-demo-secret-key"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=1440)  # session TTL (1 day)