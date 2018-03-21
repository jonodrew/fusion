import random

from flask import render_template, redirect, url_for, session

from app.matching import bp
from app.matching.forms import HowManyRandom
from app.models import Candidate, Role, Specialism, Preferences


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
    candidate_ids = random.sample([c[0] for c in candidate_ids], requested_data)
    candidates = Candidate.query.filter(Candidate.id.in_(candidate_ids)).all()
    return render_template('matching/data.html', candidates=candidates, data=requested_data)