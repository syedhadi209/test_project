from flask_mail import Message
from blog_app import  mail

def send_email(to, subjec, template):
    msg= Message(
        subject=subjec,
        recipients=[to],
        html=template
    )
    mail.send(msg)