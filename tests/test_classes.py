from typing import List, Union
from tests.conftest import random_fser, random_post
from app.classes import Match, FastStreamer, Post


def random_list(object_to_create: str, number: int) -> List[Union[Post, FastStreamer]]:
    r = []
    for i in range(number):
        if object_to_create == 'post':
            r.append(random_post())
        elif object_to_create == 'fser':
            r.append(random_fser())
        else:
            pass
    return r


def test_fser_inits_correctly(model_fser):
    assert model_fser.profile['skills'][0] == 'PPM'
    assert model_fser.preferences['anchors'] == ""


def test_set_fser_preferences(model_fser):
    model_fser.set_preference(**{'skills': ['Digital', 'PM']})
    assert model_fser.preferences['skills'] == ['Digital', 'PM']
    model_fser.set_preference(**{'brains': None})
    assert model_fser.preferences['brains'] is None


def test_score_if_equal(model_fser: FastStreamer, model_post: Post):
    m = Match(model_post, model_fser)
    model_fser.set_preference(**{'skills': ['Digital', 'PM'], 'anchors': 'Digital'})
    assert m.score_if_equal(model_post.anchor, model_fser.preferences['anchors'], 5) == 5
    assert m.score_if_equal(model_post.skills[0], model_fser.preferences['skills'], 5) != 5


def test_given_clearance_return_value(model_fser, model_post):
    m = Match(model_post, model_fser)
    clearances = ['SC', 'BPSS', 'DV', 'CTC']
    converted = {c: m.convert_clearances(c) for c in clearances}
    assert converted['DV'] > converted['SC'] > converted['CTC'] > converted['BPSS']


def test_compare_clearances(model_fser, model_post):
    m = Match(model_post, model_fser)
    assert m.compare_clearance()
    m.post.clearance = 'DV'
    assert not m.compare_clearance()


def test_no_clearance_voids_match_total(model_fser_with_prefs, model_post):
    assert 10 == Match(model_post, model_fser_with_prefs).total
    fs = FastStreamer(identifier=1, clearance='BPSS')
    assert Match(model_post, fs).total == 0

