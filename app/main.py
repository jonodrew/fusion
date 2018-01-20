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
        f.set_preference(**{'skills': [random_select(skills), random_select(skills)], 'anchors': random_select(anchors),
                            'location': random_select(locations)})
    return [Match(fser_object=f, post_object=p) for f in l_fs for p in l_p]


def main():
    t1 = time.clock()
    number = 5
    l_m = generate_test_data(number)
    print("Data generated at {}".format(time.clock()))
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
            cost_row += [sys.maxsize-col[2]]
        cost_matrix += [cost_row]
    m = munkres.Munkres()
    m.pad_matrix(cost_matrix)
    indices = m.compute(cost_matrix)
    t2 = time.clock()
    total_time = t2 - t1
    for row, col in indices:
        print("Score: {}".format(r[row][col][2]))
        print("Post: {}, FastStreamer: {}".format(r[row][col][0], r[row][col][1]))
    print(total_time)
    aggregate = calculate_aggregate_match_score([r[row][col][2] for row, col in indices])
    print("Aggregate score: {}".format(aggregate))
    print("Average score: {}".format(aggregate/number))


if __name__ == '__main__':
    main()
