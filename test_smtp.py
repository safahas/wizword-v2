import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
smtp_port = int(os.getenv('SMTP_PORT', '587'))
smtp_user = os.getenv('SMTP_USER')
smtp_pass = os.getenv('SMTP_PASS')

to_addr = input('Enter recipient email for test: ')
from_addr = smtp_user
subject = 'SMTP Test Email'
body = 'This is a test email from your WizWord SMTP configuration.'

msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = from_addr
msg['To'] = to_addr

print(f"SMTP_USER: {smtp_user}, SMTP_PASS length: {len(smtp_pass) if smtp_pass else 0}")

try:
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(from_addr, [to_addr], msg.as_string())
    print('Test email sent successfully!')
except Exception as e:
    print(f'Failed to send test email: {e}') 