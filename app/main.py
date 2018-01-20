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


def main():
    t1 = time.clock()
    number = 500
    l_p = [Post(skills=[random_select(skills), random_select(skills)], identifier=i,
                anchor=random_select(anchors), clearance=random_select(clearances), location=random_select(locations),
                department=random_select(departments)) for i in range(number)]

    l_fs = [FastStreamer(identifier=i, clearance=random_select(clearances)) for i in range(number, number+number)]
    for f in l_fs:
        f.set_preference(**{'skills': [random_select(skills), random_select(skills)], 'anchors': random_select(anchors),
                            'location': random_select(locations)})
    print("Data generated at {}".format(time.clock()))
    l_m = [Match(fser_object=f, post_object=p) for f in l_fs for p in l_p]
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


    """
    matrix = [[5, 9, 3],
              [1, 4, 0],
              [9, 2, 4]]
    cost_matrix = []
    for row in matrix:
        cost_row = []
        for col in row:
            cost_row += [sys.maxsize - col]
        cost_matrix += [cost_row]
    print(cost_matrix)
    m = munkres.Munkres()
    indexes = m.compute(cost_matrix)
    munkres.print_matrix(matrix, msg="Highest profit through this matrix: ")
    total = 0
    for row, column in indexes:
        value = matrix[row][column]
        total += value
        print('(%d, %d) -> %d' % (row, column, value))
    print('total profit=%d' % total)
    """


if __name__ == '__main__':
    main()
