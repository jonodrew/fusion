import sys

from app.models import Candidate, Algorithm, Match


def test_filtered_list(session):
    c = Candidate()
    c.id = 1
    session.add(c)
    session.commit()
    query = Algorithm.filtered_list_of_table_objects(Candidate, [1])
    assert type(c) == type(query[0])


def test_prepare_data():
    candidate_ids = [11, 12, 13]
    role_ids = [21, 22, 23]
    ag = Algorithm(candidate_ids=candidate_ids, role_ids=role_ids)
    class TestClass:
        def __init__(self, cid, rid, total):
            self.candidate_id = cid
            self.role_id = rid
            self.total = total
    match_list = [TestClass(i, j, 0) for i in candidate_ids for j in role_ids]
    scores = [5, 9, 1, 10, 3, 2, 8, 7, 4]
    for i, score in enumerate(scores):
        match_list[i].total = score
    tables = ag.prepare_data_for_munkres(match_list)
    assert sys.maxsize - tables[0][0][0].total == tables[1][0][0]

