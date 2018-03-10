import itertools
import os
import sys
import time
from operator import itemgetter
from typing import List
import munkres
import numpy as np
from app.matching.classes import Match
from tests.conftest import test_data


def calculate_aggregate_match_score(matched_list: List[int]) -> int:
    return sum(matched_list)


def calculate_matches(list_of_matches: List[Match]):
    t1 = time.clock()
    tuples_data = [(m.post.identifier, m.fast_streamer.identifier, m.total, m.identifier) for m in list_of_matches]
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
    aggregate = calculate_aggregate_match_score([r[row][col][2] for row, col in indices])
    post_fs = [r[row][col][3] for row, col in indices]
    final_matches = []
    for pfs in post_fs:
        final_matches.extend(list(filter(lambda x: x.identifier == pfs, list_of_matches)))
    t2 = time.clock()
    total_time = t2 - t1
    return {'aggregate': aggregate, 'processing': total_time, 'matches': final_matches}


def demo_mode():
    data = test_data()
    l_p = data[2]
    l_fs = data[1]
    for p in l_p:
        print("Post {}:\n\tSkills: {}, {}\n\tAnchor: {}\n\tClearance: {}\n\tLocation: {}\n\tDepartment: {}\n\t "
              "Private Office: {}".format(p.identifier, p.skills[0], p.skills[1], p.anchor, p.clearance, p.location,
                                          p.department, p.is_private_office))

    for f in l_fs:
        print("Candidate {}:\n\tSkills: {}, {}\n\tAnchors: {}, {}\n\tClearance\n\tSkills: {}\n\tDepartments: {}\n\t"
              "Will undertake DV: {}\n\tnWould like Private Office {}\n".
              format(f.identifier, f.preferences.skills[0], f.preferences.skills[1], f.preferences.anchors[1],
                     f.preferences.anchors[2], f.clearance, ', '.join(f.preferences.skills),
                     ', '.join(f.preferences.departments), f.preferences.will_undertake_dv,
                     f.preferences.wants_private_office))
    number = itertools.count().__next__
    return [Match(identifier=number(), fser_object=f, post_object=p) for f in l_fs for p in l_p]


def main():
    env = os.getenv("ENVIRONMENT")
    # l_m = test_data()  # will contain data drawn from database
    # for m in l_m:
    #     m.total = randrange(1, 101)
    l_m = demo_mode()
    results = calculate_matches(l_m)
    print("Run {}: \n\tAverage score: {}\n\tProcessing time: {}".format(len(results['matches']), results['aggregate'] /
                                                                        len(results['matches']), results['processing']))
    for m in results['matches']:
        if m.total < 18:
            """Example output - at scale you wouldn't read it all but you could group and send to CLs"""
            ws = m.weighted_scores
            print("\nFastStreamer id: {}\nPost id: {}\nMatch score: {}\n\tAnchor score: {}\n\tLocation score: {}\n\t"
                  "Skills score: {}\n\n".format(m.fast_streamer.identifier, m.post.identifier, m.total,
                                                ws['anchor'], ws['location'], ws['skills']))
    match_scores = [m.total for m in results['matches']]
    histo = np.histogram(match_scores, bins=[x for x in range(0, max(match_scores) + 1)])
    print(histo[0], "\n", histo[1])
    # if env == "test":
    #     send_email(to_name="Subject X", from_email="test@example.com", to_email="jonathandrewkerr@gmail.com",
    #                subject="Test", content="Hello world")


if __name__ == '__main__':
    main()
