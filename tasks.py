import os
import requests
from dotenv import load_dotenv
import jinja2

if os.path.exists("env_config.py"):
    import env_config

load_dotenv()
template_loader = jinja2.FileSystemLoader("templates")
templet_env = jinja2.Environment(loader=template_loader)


def render_template(template_filename, **context):
    return templet_env.get_template(template_filename).render(**context)


def send_simple_message(to, subject, body, html):
    load_dotenv()
    if os.path.exists("env_config.py"):
        domain = env_config.MAILGUN_DOMAIN
        key = env_config.MAILGUN_API_KEY
    else:
        domain = os.getenv("MAILGUN_DOMAIN")
        key = os.getenv("MAILGUN_API_KEY")
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", f"{key}"),
        data={"from": f"Mail User <mailgun@{domain}>",
              "to": [to],
              "subject": subject,
              "text": body,
              "html": html})


def send_user_registration_email(email, username):
    return send_simple_message(to=email,
                               subject="Signup",
                               body=f"Successfully signed up. {username}",
                               html=render_template("emails/action.html", username=username)
                               )
