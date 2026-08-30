import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
from pathlib import Path
from string import Template

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_HOST = os.environ.get("EMAIL_HOST") or "smtp.gmail.com"
EMAIL_PORT = os.environ.get("EMAIL_PORT") or "465"


def send_mail(to_email: str,
              from_email: str,
              subject: str = "No subject provided",
              content: str = "No Content Provided"
              ):
    template = Template(Path("template.html").read_text())

    message = MIMEMultipart()
    message["from"] = from_email
    message["to"] = to_email
    message["subject"] = subject

    body = template.substitute({"content": content})

    message.attach(MIMEText(body, "html"))
    # message.attach(MIMEImage(Path("xyz.png").read_bytes())) # Add search for image and attach support later

    with smtplib.SMTP(host=EMAIL_HOST, port=int(EMAIL_PORT)) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)
        print("Sent")
