from app.email import send_email


def send_password_reset_email(user):
    token = user.generate_token('reset_password')
    return send_email(user, subject="You requested a password reset", from_email='admin@gov-matching-service.uk',
                      substitutions={'-name-': user.first_name, '-token-': token})


def send_email_confirmation(user):
    token = user.generate_token('confirm_email')
    return send_email(user, subject="Welcome to the matching service", from_email='admin@gov-matching-service.uk',
                      substitutions={'-name-': user.first_name, '-token-': 'localhost:5000/confirm-email/' + token})
