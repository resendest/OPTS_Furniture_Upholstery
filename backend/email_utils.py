from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

mail = Mail()                                  # one Mail() instance app-wide

# locate the templates/emails directory relative to project root
_env = Environment(
    loader=FileSystemLoader(Path(__file__).resolve().parents[1] / "templates" / "emails")
)

def init_mail(app):
    """Call once (e.g., in app.py) so Mail picks up SMTP settings from app.config."""
    mail.init_app(app)

def _build_token(secret_key: str, client_id: int, order_id: int) -> str:
    s = URLSafeTimedSerializer(secret_key)
    return s.dumps({"cid": client_id, "oid": order_id})

def send_registration_email(client_id: int, client_email: str, order_id: int) -> None:
    """
    Compose and dispatch the ‘create your account’ message.
    Assumes init_mail() has already been called.
    """
    app = current_app
    token = _build_token(app.config["SECRET_KEY"], client_id, order_id)
    link  = f"{app.config['BASE_URL']}/register?token={token}"

    html_body = _env.get_template("registration.html").render(
        link=link,
        order_id=order_id,
    )

    msg = Message(
        subject=f"Lousso Upholstery – Create your account for Order #{order_id}",
        recipients=[client_email],
        html=html_body,
    )
    mail.send(msg)
