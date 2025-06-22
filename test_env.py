from dotenv import load_dotenv
import os

load_dotenv()
print("SMTP_USER:", os.getenv("SMTP_USER"))
print("SMTP_PASS:", os.getenv("SMTP_PASS"))
