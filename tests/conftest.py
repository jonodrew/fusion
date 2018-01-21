from random import randrange, choice
from typing import List
import random
import pytest

from app.classes import FastStreamer, Post

departments = ['Home Office', 'DWP', 'HMRC']
skills = ['Project and People Management', 'Change Management']
anchors = ['Digital', 'Corporate', 'Operations']
locations = ['London', 'The North', 'Overseas']
clearances = ['BPSS', 'CTC', 'SC', 'DV']

list_length = 500


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
                          2: random_select(anchors)}, loc=random_select(locations), sec=random.choice([True, False]),
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
                       loc='London', sec=False)
    return fs
