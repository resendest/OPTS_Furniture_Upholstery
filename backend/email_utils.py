# this file is for sending emails using Flask-Mail and Google SMTP
# it includes a function to send registration emails
# and a function to initialize the Flask-Mail instance

import os
from flask_mail import Mail, Message
from flask import current_app

# create the Mail instance
mail = Mail()

# Function to initialize Flask-Mail with app configuration
def init_mail(app):
    """
    Configure Flask-Mail on the app and attach the Mail() instance.
    """
    # make sure these variables match .env settings
    app.config.update(
        MAIL_SERVER        = os.getenv("EMAIL_HOST"),
        MAIL_PORT          = int(os.getenv("EMAIL_PORT", 587)),
        MAIL_USE_TLS       = os.getenv("EMAIL_USE_TLS", "false").lower() in ("1","true","yes"),
        MAIL_USERNAME      = os.getenv("EMAIL_USERNAME"),
        MAIL_PASSWORD      = os.getenv("EMAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER= os.getenv("EMAIL_DEFAULT_SENDER")
    )
    app.config["MAIL_DEBUG"] = True
    mail.init_app(app)

# Sending registration email
def send_registration_email(user_id: int, to_addr: str, token: str, order_id: int):
    """
    Send registration email to new customer with account setup link.
    """
    msg = Message(
        subject="Complete Your Registration",
        recipients=[to_addr],
    )
    link = (
    f"{current_app.config['BASE_URL']}"
    f"/register?token={token}&order_id={order_id}"
    )
    msg.subject = "Complete Your Registration"
    msg.body = (
        "Hi there!\n\n"
        "You have a new order with Lousso Designs! Your project can now be viewed in our Order Tracker!\n\n"
        f"Click here to finish setting up your account:\n{link}\n\n"
        "If you already have an account with us, you can log in here:\n"
        f"{current_app.config['BASE_URL']}/login"
    )
    try:
        mail.send(msg)
        current_app.logger.info("Email sent OK")
    except Exception as e:
        current_app.logger.error(f"Email send failed: {e}")
        raise

