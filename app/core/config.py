
import os

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()


# Application settings
LOG_RETENTION_DAYS = os.getenv("LOG_RETENTION_DAYS", 30)


# Log file path
LOG_FILE_PATH = "logs/app.log"
if not os.path.exists(os.path.dirname(LOG_FILE_PATH)):
    os.makedirs(os.path.dirname(LOG_FILE_PATH))