import random
import copy
import statistics
import sys

import math
import munkres
from flask import render_template, redirect, url_for, session

from app import db
from app.matching import bp
from app.matching.forms import HowManyRandom
from app.models import Candidate, Role, Specialism, Preferences, Match, Algorithm


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
        requested_data = 50
    candidate_ids = Preferences.query.with_entities(Preferences.candidate_id).all()
    roles = Role.query.all()
    role_ids = [role.id for role in roles]
    random_ids = random.sample(role_ids, int(requested_data*1.5))
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
        requested_data = 50
        candidate_ids = random.sample([c.id for c in cands], requested_data)
        role_ids = random.sample([r.id for r in roles], int(requested_data*1.5))
    ag = Algorithm(weighted_dict={'location': 5, 'skills': 10, 'private office': 10, 'organisation': 5},
                   candidate_ids=candidate_ids, role_ids=role_ids)

    candidates = Candidate.query.filter(Candidate.id.in_(candidate_ids)).all()
    roles = Role.query.filter(Role.id.in_(role_ids)).all()
    matches = [Match(r, c) for r in roles for c in candidates]
    sorted_matches = sorted(matches, key=lambda m: m.role_id)
    m = munkres.Munkres()
    table_of_objects = [sorted_matches[i:i + len(roles)] for i in range(0, len(matches), len(roles))]
    table_of_totals = [[sys.maxsize - m.total for m in row] for row in table_of_objects]
    best_match_indices = m.compute(table_of_totals)
    best_matches = [table_of_objects[row][column] for row, column in best_match_indices]
    aggregate = sum([m.total for m in best_matches])
    totals = [m.total for m in best_matches]
    median_average = "{:.1%}".format(statistics.median(totals)/50)
    return render_template('matching/match.html', aggregate=aggregate, matches=best_matches, average=median_average)

    # strings0 = ["Role: {}<br>Candidate: {}<br>Score: {}<br><hr>".format(m.role_id, m.candidate_id, m.total) for m in
    #            sorted_matches]
    # strings = ["Matched:<br>Role id: {}<br>Candidate id: {}<br>Score: {}<br><hr>".
    #                format(i.role_id, i.candidate_id, i.total) for i in best_matches]
    # output0 = '<br>'.join(strings0)
    # output1 = ''.join(strings)
    # return ''.join([output0, output1])
