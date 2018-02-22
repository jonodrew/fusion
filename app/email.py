from typing import Dict, Any
from app.models import User
from sendgrid.helpers.mail import Content, Email, Mail, Substitution
import sendgrid
import os


def send_email(user: User, subject: str, content: str, from_email: str, substitutions: [Dict[Any, Any]]) -> Dict[
    str, str]:
    """
    This function sends an email using the SendGrid API
    Args:
       from_email: the email from which the email is sent
       user: the USer object containing the name and email address of the intended recipient
       subject: subject of email
       content: content

    Returns:
       Dict[str, str]: Dictionary containing HTTP response

    """
    content = Content("text/HTML", content)
    sendgrid_api = os.getenv("SENDGRID_API")
    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api)
    from_email = Email(from_email, name="Service Admin")
    to_email = Email(user.email, user.first_name)
    m = Mail(from_email, subject, to_email, content)
    for key, value in substitutions.items():
        m.personalizations[0].add_substitution(Substitution(key, value))
    if os.environ.get('ENV') == 'TEST':
        m.mail_settings['sandbox_mode']['enable'] = True
    m.template_id = '5a1b969f-77c5-4d27-8b6e-e77c9c237a8e'
    return sg.client.mail.send.post(request_body=m.get())


def send_password_reset_email(user):
    token = user.generate_token('reset_password')
    return send_email(user, subject="You requested a password reset", content='', from_email='admin@service.gov.uk',
                      substitutions={'-name-': user.first_name, '-token-': token})


def send_email_confirmation(user):
    token = user.generate_token('confirm_email')
    return send_email(user, subject="You requested a password reset", content='', from_email='admin@service.gov.uk',
                      substitutions={'-name-': user.first_name, '-token-': token})


