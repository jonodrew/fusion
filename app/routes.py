from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, DepartmentalRoleForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'jonathandrewkerr+admin@gmail.com'}
    return render_template('index.html', title="Home", user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/submit-role', methods=['GET', 'POST'])
def submit_role():
    form = DepartmentalRoleForm()
    if form.validate_on_submit():
        flash('Role {} submitted'.format(form.title))
        return redirect(url_for('index'))
    return render_template('submit-role.html', title="Submit a role", form=form)

