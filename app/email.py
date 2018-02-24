from typing import Dict, Any

from python_http_client import exceptions

from app.models import User
from sendgrid.helpers.mail import Content, Email, Mail, Substitution, Personalization
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
    print(content)
    content = Content("text/html", content)
    print(content.value)
    sendgrid_api = os.getenv("SENDGRID_API")
    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api)
    from_email = Email(from_email, name="Service Admin")
    to_email = Email(user.email, user.first_name)
    m = Mail(from_email, subject, to_email, content)
    for key, value in substitutions.items():
        print(key, value)
        m.personalizations[0].add_substitution(Substitution(key, value))
    if os.environ.get('ENV') == 'TEST':
        m.mail_settings['sandbox_mode']['enable'] = True
    m.template_id = '5a1b969f-77c5-4d27-8b6e-e77c9c237a8e'
    try:
        response = sg.client.mail.send.post(request_body=m.get())
    except exceptions.BadRequestsError as e:
        print(e.body)
        exit()
    print(response.status_code)
    print(response.body)
    print(response.headers)
    return response


def send_password_reset_email(user):
    token = user.generate_token('reset_password')
    return send_email(user, subject="You requested a password reset", from_email='admin@gov-matching-service.uk',
                      substitutions={'-name-': user.first_name, '-token-': token})


def send_email_confirmation(user):
    token = user.generate_token('confirm_email')
    return send_email(user, subject="You requested a password reset", from_email='admin@gov-matching-service.uk',
                      substitutions={'-name-': user.first_name, '-token-': token})


