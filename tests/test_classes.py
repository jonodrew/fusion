from typing import List, Union
from app.matching.classes import Match, FastStreamer, Post
from app.models import random_weighted_value


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


def test_given_clearance_return_value(model_fser_with_prefs, model_post):
    m = Match(1, model_post, model_fser_with_prefs)
    clearances = ['SC', 'BPSS', 'DV', 'CTC']
    converted = {c: m.convert_clearances(c) for c in clearances}
    assert converted['DV'] > converted['SC'] > converted['CTC'] > converted['BPSS']


def test_compare_clearances(model_fser_with_prefs, model_post):
    m = Match(1, model_post, model_fser_with_prefs)
    assert m.compare_clearance()
    m.post.clearance = 'DV'
    assert not m.compare_clearance()
    m.post.clearance = "CTC"
    m.fast_streamer.clearance = "BPSS"
    assert not m.compare_clearance()


def test_no_clearance_voids_match_total(model_fser_with_prefs, model_post):
    assert 17 == Match(1, model_post, model_fser_with_prefs).total
    fs = FastStreamer(identifier=1, clearance='BPSS')
    assert 0 == Match(1, post_object=model_post, fser_object=fs).total


class TestMatchClass:
    def test_suitable_location_check(self, model_fser_with_prefs, model_post):
        m = Match(1, model_post, model_fser_with_prefs)
        assert m.suitable_location_check()
        model_fser_with_prefs.location_restriction = True
        assert m.suitable_location_check()
        model_post.location = 'Midlands'
        assert m.suitable_location_check() is False


def test_random_weighted_value():
    r = 9
    f = 89
    weighted_dict = {10: 'True', 90: 'False'}
    assert random_weighted_value(r, weighted_dict)
    assert 'False' == random_weighted_value(f, weighted_dict)