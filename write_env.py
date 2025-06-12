import os

# Get the API key from environment variable or prompt
api_key = os.getenv('OPENROUTER_API_KEY', '')
if not api_key:
    api_key = input('Please enter your OpenRouter API key: ')

with open('.env', 'w', encoding='utf-8', newline='\n') as f:
    f.write('''# OpenRouter API Configuration
OPENROUTER_API_KEY=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
USE_CLOUD_STORAGE=false

# Optional AWS Configuration (only if USE_CLOUD_STORAGE=true)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# Optional SMTP Configuration (for email alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
''') 