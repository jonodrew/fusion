from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, render_template, url_for, flash, request, abort
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.email import send_email_confirmation, send_password_reset_email
from app.auth.forms import LoginForm, RegistrationForm, RegisterAsForm, ResetPasswordRequestForm
from app.models import User, Candidate


@bp.route('/register', methods=['POST', 'GET'])
def register():
    """passes user through to correct registration form.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterAsForm()
    if form.validate_on_submit():
        if form.type_of_user.data == 'cohort leader':
            abort(404)
        elif form.type_of_user.data == 'activity manager':
            abort(404)
        else:
            redirect_url = 'auth.register_as_candidate'
        return redirect(url_for(redirect_url))

    return render_template('auth/register.html', title='What kind of user are you?', form=form)


@bp.route('/register-as-candidate', methods=['GET', 'POST'])
def register_as_candidate():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        candidate = Candidate()
        form.populate_obj(candidate)
        candidate.set_password(form.password.data)
        db.session.add(candidate)
        db.session.commit()
        send_email_confirmation(candidate)
        flash("Congratulations, you've registered successfully. Now check your email to confirm your account")
        return redirect(url_for('auth.login'))
    return render_template('auth/register-as-candidate.html', title='Register as a candidate', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign in', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@bp.route('/reset-password-request', methods=['POST', 'GET'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset-password-request.html', title='Reset Password', form=form)


@bp.route('/confirm-email/<token>/')
@login_required
def confirm_email(token):
    if current_user.confirmed:
        return redirect(url_for('index'))
    elif current_user.confirm_user(token):
        flash("Thank you for confirming your account!")
    else:
        flash("The link is invalid or expired")
    return redirect(url_for('index'))

