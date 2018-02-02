from flask_login import current_user, login_user
from werkzeug.urls import url_parse

from app import app
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, DepartmentalRoleForm
from app.models import User
from flask_login import logout_user, login_required


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'jonathandrewkerr+admin@gmail.com'}
    return render_template('index.html', title="Home", user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign in', form=form)


@app.route('/submit-role', methods=['GET', 'POST'])
def submit_role():
    form = DepartmentalRoleForm()
    if form.validate_on_submit():
        flash('Role {} submitted'.format(form.title))
        return redirect(url_for('index'))
    return render_template('submit-role.html', title="Submit a role", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))