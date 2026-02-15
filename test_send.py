import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import settings

email = "moxmad0711@gmail.com"

text = """This message was sent to you
        using
        python"""

server = smtplib.SMTP("smtp.gmail.com", 587)

server.starttls()
with open("password.txt", "r") as f:
    password = f.read().strip()

server.login(email, settings.APP_PASSWORD_SECRET)


msg = MIMEMultipart()
msg["From"] = email
msg["To"] = "madinas1979@gmail.com"
msg["Subject"] = "Just a test email"


with open("message.txt", "r") as f:
    message = f.read()

msg.attach(MIMEText(message, "plain"))


text = msg.as_string()

server.send_message(msg)
