#!/usr/bin/env python3
"""
Send email via SMTP using credentials from himalaya config.
Usage: python3 send-email.py "Subject" "Body text"
       python3 send-email.py "Subject" --file body.txt
"""

import sys
import smtplib
import tomllib
from email.mime.text import MIMEText
from pathlib import Path

CONFIG_PATH = Path.home() / ".config/himalaya/config.toml"

def load_config():
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)

def send_email(subject: str, body: str):
    config = load_config()
    gmail = config["accounts"]["gmail"]
    
    email = gmail["email"]
    smtp_host = gmail["message"]["send"]["backend"]["host"]
    smtp_port = gmail["message"]["send"]["backend"]["port"]
    password = gmail["message"]["send"]["backend"]["auth"]["raw"]
    
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = f"Alyosha <{email}>"
    msg["To"] = email
    
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(email, password)
        server.send_message(msg)
    
    print(f"✅ Email sent: {subject}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: send-email.py 'Subject' 'Body' OR send-email.py 'Subject' --file body.txt")
        sys.exit(1)
    
    subject = sys.argv[1]
    
    if sys.argv[2] == "--file":
        with open(sys.argv[3]) as f:
            body = f.read()
    else:
        body = sys.argv[2]
    
    send_email(subject, body)
