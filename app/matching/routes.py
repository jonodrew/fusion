import random

from flask import render_template, redirect, url_for, session

from app.matching import bp
from app.matching.forms import HowManyRandom
from app.models import Candidate, Role, Specialism, Preferences, MatchTable


@bp.route('/trial', methods=['GET', 'POST'])
def trial():
    return render_template('matching/trial.html')


@bp.route('/generate', methods=['POST', 'GET'])
def generate():
    form = HowManyRandom()
    if form.validate_on_submit():
        session['data'] = form.number.data
        return redirect(url_for('matching.data'))
    return render_template('matching/generate.html', form=form)


@bp.route('/data')
def data():
    try:
        requested_data = session['data']
    except KeyError:
        requested_data = 10
    candidate_ids = Preferences.query.with_entities(Preferences.candidate_id).all()
    roles = Role.query.all()
    role_ids = [role.id for role in roles]
    random_ids = random.sample(role_ids, requested_data)
    roles = [role for role in roles if role.id in random_ids]
    candidate_ids = random.sample([c[0] for c in candidate_ids], requested_data)
    candidates = Candidate.query.filter(Candidate.id.in_(candidate_ids)).all()
    session['candidates'] = [c.id for c in candidates]
    session['roles'] = [r.id for r in roles]
    return render_template('matching/data.html', candidates=candidates, data=requested_data, roles=roles)


@bp.route('/match')
def match():
    try:
        candidate_ids = session['candidates']
        role_ids = session['roles']
    except KeyError:
        # return redirect(url_for('matching.trial'))
        cands = Candidate.query.all()
        roles = Role.query.all()
        candidate_ids = random.sample([c.id for c in cands], 10)
        role_ids = random.sample([r.id for r in roles], 10)
    candidates = Candidate.query.filter(Candidate.id.in_(candidate_ids)).all()
    roles = Role.query.filter(Role.id.in_(role_ids)).all()
    m = MatchTable(role_object=roles[0], candidate_object=candidates[0])
    return str(m.skills_match)