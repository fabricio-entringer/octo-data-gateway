
import os

if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv()


NINJAS_API_KEY = os.getenv("NINJAS_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")