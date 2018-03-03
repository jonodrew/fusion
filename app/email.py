from typing import Dict, Any

from python_http_client import exceptions

from app.models import User
from sendgrid.helpers.mail import Content, Email, Mail, Substitution, MailSettings, SandBoxMode
import sendgrid
import os


def send_email(user: User, subject: str, from_email: str, substitutions: [Dict[Any, Any]], content: str='text') -> Dict[
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
    content = Content("text/html", content)
    sendgrid_api = os.getenv("SENDGRID_API")
    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api)
    from_email = Email(from_email, name="Service Admin")
    to_email = Email(user.email, user.first_name)
    m = Mail(from_email, subject, to_email, content)
    for key, value in substitutions.items():
        m.personalizations[0].add_substitution(Substitution(key, value))
    if os.environ.get('ENV') == 'test':
        settings = MailSettings()
        settings.sandbox_mode = SandBoxMode(enable=True)
        m.mail_settings = settings
    m.template_id = '5a1b969f-77c5-4d27-8b6e-e77c9c237a8e'
    try:
        response = sg.client.mail.send.post(request_body=m.get())
    except exceptions.BadRequestsError as e:
        exit()
    return response




