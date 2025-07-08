import os
from flask_mail import Mail, Message
from flask import current_app

# create the Mail instance
mail = Mail()

def init_mail(app):
    """
    Configure Flask-Mail on the app and attach the Mail() instance.
    """
    # you can adjust these env-var names to match your .env
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


def send_registration_email(user_id: int, to_addr: str, token: str, order_id: int):
    """
    Example helper you already tried before—uses app.config['BASE_URL'].
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
    msg.body = f"Hi there!\n\nYou have a new order with Lousso Designs! Your project can now be viewed in our Order Tracker!\n\nClick here to finish setting up your account:\n{link}"
    try:
        mail.send(msg)
        current_app.logger.info("Email sent OK")
    except Exception as e:
        current_app.logger.error(f"Email send failed: {e}")
        raise

