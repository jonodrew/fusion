from flask import render_template, redirect, url_for, session

from app import db
from app.submit import bp


@bp.route('/start', methods=['GET', 'POST'])
def start():
    return render_template('submit/start.html', title='Submit a Fast Stream role')


@bp.route('/role-details', methods=['GET', 'POST'])
def role_details():
    question = {'textarea': {'label': 'Role description',
                             'hint': "Please give a description of the role and some context. For example, what "
                                     "are the team's priorities?"},
                'radio': {'heading': 'What security classificaiton is required for this role?'}}
    return render_template('submit/role-details.html', title='Role details', question=question)
