from random import randrange, choice
from typing import List, Tuple
import random
import os
import itertools
import pytest

from matching.classes import FastStreamer, Post, Match

departments = ['HO', 'DWP', 'HMRC', 'DH', 'CO', 'GDS', 'MOD', 'DDCMS', 'DCLG', 'DEFRA', 'MOJ', 'DFT', 'DFE', 'DFID']
skills = ['Software Engineering', 'User Research', 'Strategy & Policy', 'Product Design', 'Content & Analysis',
          'Delivery', 'Operations', 'Commercial Management']
anchors = ['Digital', 'Corporate', 'Operations']
locations = ['London', 'South West', 'Midlands', 'Scotland', 'The North', 'Overseas']
clearances = ['BPSS', 'CTC', 'SC', 'DV']


def random_select(list_to_select_from: List[str]) -> str:
    return list_to_select_from[randrange(0, len(list_to_select_from))]


@pytest.fixture
def model_fser():
    return FastStreamer(123456, skills=['PPM', 'CM'], anchors=['Policy', 'Corporate'],
                        restrictions=['None'], clearance='SC')


@pytest.fixture
def model_post():
    return Post(skills=['Digital', 'CM'], identifier=789, anchor='Digital', clearance='SC', location='London',
                department='Home Office', private_office=False)


@pytest.fixture
def random_fser() -> FastStreamer:
    r = FastStreamer(identifier=randrange(0, 1000))
    r.set_preferences(skills=[random_select(skills), random_select(skills)], anchors={1: random_select(anchors),
                                                                                      2: random_select(anchors)},
                      loc=random_select(locations), sec=random.choice([True, False]),
                      dv=random.choice([True, False]), po=random.choice([True, False]))
    return r


@pytest.fixture
def random_post() -> Post:
    p = Post(skills=[random_select(skills), random_select(skills)], identifier=randrange(0, 1000),
             anchor=random_select(anchors), clearance=random_select(clearances), location=random_select(locations),
             department=random_select(departments), private_office=choice[True, False])
    return p


@pytest.fixture
def model_fser_with_prefs() -> FastStreamer:
    fs = FastStreamer(123456, skills=['PPM', 'CM'], anchors=['Policy', 'Corporate'],
                      restrictions=['None'], clearance='SC')
    fs.set_preferences(skills=['Digital', 'PM'], anchors={1: 'Digital', 2: 'Operations'}, dv=False, po=False,
                       loc=['London', 'Scotland'], sec=False, departments={"DWP", "HO", "HMRC", "DDCMS", "DH"})
    return fs


@pytest.fixture
def test_data() -> Tuple[List[Match], List[FastStreamer], List[Post]]:
    if os.getenv("ENV") == "test":
        amount = 500
    else:
        amount = 100
    l_p = [Post(skills=random.sample(skills, 2), identifier=i,
                anchor=random.choice(anchors), clearance=random.choice(clearances),
                location=random.choice(locations),
                department=random.choice(departments), private_office=not bool(random.choice(range(0, 10)))) for i in
           range(amount)]
    l_fs = [FastStreamer(identifier=i, clearance='SC') for i in range(amount, 2 * amount)]
    for f in l_fs:
        f.set_preferences(skills=random.sample(skills, 2), anchors={1: random.choice(anchors),
                                                                    2: random.choice(anchors)},
                          departments=random.sample(departments, 10),
                          loc=random.sample(locations, 2), sec=random.choice([True, False]),
                          dv=random.choice([True, False]), po=random.choice([True, False]))
    number = itertools.count().__next__
    return [Match(identifier=number(), fser_object=f, post_object=p) for f in l_fs for p in l_p], l_fs, l_p


@pytest.fixture()
def test_db():
    pass
