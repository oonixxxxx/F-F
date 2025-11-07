from urllib.parse import quote_plus

USER = "friend_user"
PASSWORD = "3011"
DATABASE_URL = f"postgresql://{USER}:{quote_plus(PASSWORD)}@localhost:5433/F%26F"  # или F%26F, смотри выше
API_TOKEN = ""