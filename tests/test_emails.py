from app.email import send_email
from app.models import User


def test_sending_email():
    u = User(email='test@example.com')
    response = send_email(u, 'test subject', 'test-sender@example.com', {'-name-': 'Alexander'},
                          'text').status_code
    assert 200 == response
