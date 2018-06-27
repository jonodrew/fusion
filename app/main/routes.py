from flask_login import current_user
from app import db
from flask import render_template, flash, redirect, url_for
from app.main.forms import DepartmentalRoleForm, PreferencesForm
from app.models import User, Candidate, Preferences
from app.main import bp
from flask_login import login_required
import datetime as dt


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    if current_user.type == 'cohort_leader':
        action = Candidate.query.filter_by(line_manager_id=current_user.id).join(Preferences).\
            filter_by(completed=False).all()
    elif current_user.type == 'candidate':
        action = Preferences.query.filter(Preferences.candidate_id == current_user.id, Preferences.completed == False)\
            .first()
    else:
        action = None
    print(action)
    return render_template('index.html', title="Home", action=action)


@bp.route('/submit-role', methods=['GET', 'POST'])
def submit_role():
    form = DepartmentalRoleForm()
    if form.validate_on_submit():
        flash('Role submitted')
        return redirect(url_for('main.index'))
    return render_template('submit/role-details.html', title="Submit a Fast Stream role", form=form)


@bp.route('/profile')
@login_required
def profile():
    open_form = bool(Preferences.query.filter_by(candidate_id=current_user.get_id(), completed=False).count())
    user = User.query.filter_by(id=current_user.id).first_or_404()
    posts = [
        {'department': 'Home Office', 'anchor': 'Digital', 'score': 'Achieved'},
        {'department': 'HMRC', 'anchor': 'Policy', 'score': 'Exceeded'}
    ]
    return render_template('profile.html', user=user, posts=posts, form_available=open_form)


@bp.route('/submit-preferences', methods=['POST', 'GET'])
@login_required
def submit_preferences():
    open_form = Preferences.query.filter_by(candidate_id=current_user.get_id(), completed=False).first()
    form = PreferencesForm()
    if form.validate_on_submit():
        open_form.skill1 = form.skill1.data
        open_form.skill2 = form.skill2.data
        open_form.completed = True
        open_form.completed_date = dt.datetime.today()
        open_form.want_private_office = form.private_office.data
        db.session.commit()
        return redirect(url_for('main.profile'))
    return render_template('preferences.html', title='Submit my preferences', form=form, form_available=bool(open_form))


@bp.route('/my-cohort')
@login_required
def my_cohort():
    cohort = [
        {
            'name': 'Frank Jones',
            'specialism': 'Digital',
            'role': {
                'name': 'Scrum Master',
                'organisation': 'HMRC',
                'location': 'Worthing'
            }
        },
        {
            'name': 'Farah Ahmed',
            'specialism': 'Digital',
            'role': {
                'name': 'CyberOps',
                'organisation': 'DWP',
                'location': 'Blackpool'
            }
        }

    ]
    return render_template('my-cohort.html', data=cohort)



