from dotenv import load_dotenv
import os, smtplib

# 1) Load .env
load_dotenv()

# 2) Fetch config
host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
port = int(os.getenv("EMAIL_PORT", "587"))
user = os.getenv("EMAIL_USERNAME")
pwd  = os.getenv("EMAIL_PASSWORD")

# 3) Quick guard
if not all([host, port, user, pwd]):
    print("ERROR: Missing one of host/port/user/pwd:", host, port, user, pwd)
    exit(1)

print(f"→ Connecting to {host}:{port} as {user}")

# 4) Talk to SMTP
server = smtplib.SMTP(host, port, timeout=10)
server.set_debuglevel(1)   # prints the EHLO/STARTTLS/AUTH exchange
server.ehlo()
server.starttls()
server.ehlo()
try:
    server.login(user, pwd)
    print("SMTP login succeeded")
except smtplib.SMTPAuthenticationError as e:
    print("SMTP login failed:", e)
finally:
    server.quit()
