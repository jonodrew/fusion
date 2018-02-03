from flask_login import current_user, login_user
from werkzeug.urls import url_parse

from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, DepartmentalRoleForm, RegistrationForm, RegisterAsForm
from app.models import User, Candidate
from flask_login import logout_user, login_required


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title="Home")


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


@app.route('/register', methods=['POST', 'GET'])
def register():
    """passes user through to correct registration form.
    TODO: WRITE FORMS
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterAsForm()
    if form.validate_on_submit():
        if form.type_of_user.data == 'cohort leader':
            pass
        elif form.type_of_user.data == 'activity manager':
            return redirect(url_for('register_as_activity_manager'))
        else:
            return redirect(url_for('register_as_candidate'))
    return render_template('register.html', title='What kid of user are you?', form=form)


@app.route('/register-as-candidate', methods=['GET', 'POST'])
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
        flash("Congratulations, you've registered successfully")
        return redirect(url_for('login'))
    return render_template('register-as-candidate.html', title='Register as a candidate', form=form)


@app.route('/user/<user_id>')
@login_required
def user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    posts = [
        {'department': 'Home Office', 'anchor': 'Digital', 'score': 'Achieved'},
        {'department': 'HMRC', 'anchor': 'Policy', 'score': 'Exceeded'}
    ]
    return render_template('user.html', user=user, posts=posts)