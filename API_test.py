import os
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("No API key found in .env")
    exit(1)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Example endpoint (adjust if needed)
url = "https://openrouter.ai/api/v1/models"

response = requests.get(url, headers=headers)
print("Status code:", response.status_code)
print("Response:", response.text)
