import random

from flask import render_template, redirect, url_for, session

from app.matching import bp
from app.matching.forms import HowManyRandom
from app.models import Candidate, Role


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
    requested_data = session['data']
    candidate_ids = random.sample(range(247), requested_data)
    candidates = Candidate.query.filter(Candidate.id.in_(candidate_ids))
    roles = [Role(description='Gladiatorial combat', organisation='Fantastic Four'),
             Role(description='Cat herding', organisation='Primary School')]
    return render_template('matching/data.html', candidates=candidates, roles=roles)