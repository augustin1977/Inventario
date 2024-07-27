import smtplib
from email.mime.text import MIMEText
from django.conf import settings
import random
import string

def generate_random_password(length=12):
        """Gera uma senha aleatória de comprimento especificado."""
        letters = string.ascii_letters + string.digits + string.punctuation
        password=""
        for letter in range(length):
            password+=random.choice(letters)
        return password
    
def enviar_email(subject,body,sender,recipients,password):
        html_message = MIMEText(body, 'html')
        html_message['Subject'] = subject
        html_message['From'] = sender
        html_message['To'] = ', '.join(recipients)
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, html_message.as_string())   