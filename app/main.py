import sys
import munkres
from app.classes import Match
from tests.conftest import *
import time
from operator import itemgetter
import random
from typing import List


def calculate_aggregate_match_score(matched_list: List[int]) -> int:
    return sum(matched_list)


def generate_test_data(amount: int) -> List[Match]:
    l_p = [Post(skills=[random_select(skills), random_select(skills)], identifier=i,
                anchor=random_select(anchors), clearance=random_select(clearances), location=random_select(locations),
                department=random_select(departments)) for i in range(amount)]

    l_fs = [FastStreamer(identifier=i, clearance=random_select(clearances)) for i in range(amount, 2*amount)]
    for f in l_fs:
        f.set_preferences(skills=[random_select(skills), random_select(skills)], anchors={1: random_select(anchors),
                          2: random_select(anchors)}, loc=random_select(locations), sec=random.choice([True, False]),
                          dv=random.choice([True, False]), po=random.choice([True, False]))
    return [Match(fser_object=f, post_object=p) for f in l_fs for p in l_p]


def test_run(number):
    t1 = time.clock()
    l_m = generate_test_data(number)
    for m in l_m:
        m.total = random.randrange(0, 100)
    tuples_data = [(m.post.identifier, m.fast_streamer.identifier, m.total) for m in l_m]
    r = []
    t = set([t[0] for t in tuples_data])
    for i in t:
        s = list(filter(lambda x: x[0] == i, tuples_data))
        s.sort(key=itemgetter(1))
        r.append(s)
    cost_matrix = []
    for row in r:
        cost_row = []
        for col in row:
            cost_row += [sys.maxsize - col[2]]
        cost_matrix += [cost_row]
    m = munkres.Munkres()
    m.pad_matrix(cost_matrix)
    indices = m.compute(cost_matrix)
    t2 = time.clock()
    total_time = t2 - t1
    print("Run {} complete!".format(number))
    aggregate = calculate_aggregate_match_score([r[row][col][2] for row, col in indices])
    return {'aggregate': aggregate, 'processing': total_time}


def main():
    results = ((i, test_run(i)) for i in range(10, 20))
    for r in results:
        print("Run {}: \n\tAverage score: {}\n\tProcessing time: {}".format(r[0], r[1]['aggregate']/r[0], r[1]['processing']))


if __name__ == '__main__':
    main()
