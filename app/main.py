import sys
import munkres
import numpy as np
import os
from app.classes import Match
from tests.conftest import *
import time
from operator import itemgetter
import random
from typing import List, Dict, Union
import itertools
import sendgrid
import yaml
from sendgrid.helpers.mail import *


def load_config(environment: str="test") -> Dict[str, str]:
    my_path = os.path.dirname(__file__)
    config_path = os.path.join(my_path, '../config.yml')
    try:
        with open(config_path, 'r') as ymlfile:
            print("Success!")
            c = yaml.load(ymlfile)
    except FileNotFoundError:
        c = None
        pass
    return c[environment]


def send_email(to_name: str, from_email: str, to_email: str, subject: str, content: str,
               env_name: str = "test") -> Dict[str, str]:
    """
    This function sends an email using the SendGrid API
    Args:
        to_name: the name of the individual to whom the email is being sent
        from_email: the email from which the email is sent
        to_email: the email address of the individual to whom the email is being sent
        subject: subject of email
        content: content
        env_name: environment name; either 'test' or 'production'

    Returns:
        Dict[str, str]: Dictionary containing HTTP response

    """
    content = Content("text/plain", content)
    try:
        cfg = load_config(env_name)
        sendgrid_api = cfg.get("sendgrid").get("api")
    except FileNotFoundError:
        sendgrid_api = os.getenv("SENDGRID_API")
    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api)
    from_email = Email(from_email, name="Fusion Admin")
    to_email = Email(to_email, to_name)
    m = Mail(from_email, subject, to_email, content)
    return sg.client.mail.send.post(request_body=m.get())


def calculate_aggregate_match_score(matched_list: List[int]) -> int:
    return sum(matched_list)


def generate_test_data(amount: int) -> List[Match]:
    l_p = [Post(skills=[random_select(skills), random_select(skills)], identifier=i,
                anchor=random_select(anchors), clearance=random_select(clearances), location=random_select(locations),
                department=random_select(departments)) for i in range(amount)]

    l_fs = [FastStreamer(identifier=i, clearance='SC') for i in range(amount, 2 * amount)]
    for f in l_fs:
        f.set_preferences(skills=[random_select(skills), random_select(skills)], anchors={1: random_select(anchors),
                                                                                          2: random_select(anchors)},
                          loc=random_select(locations), sec=random.choice([True, False]),
                          dv=random.choice([True, False]), po=random.choice([True, False]))
    number = itertools.count().__next__
    print("Test data generated!")
    return [Match(identifier=number(), fser_object=f, post_object=p) for f in l_fs for p in l_p]


def test_run(number: int) -> Dict[str, Union[int, List[Match]]]:
    t1 = time.clock()
    l_m = generate_test_data(number)
    # for m in l_m:
    #     m.total = randrange(1, 101)
    tuples_data = [(m.post.identifier, m.fast_streamer.identifier, m.total, m.identifier) for m in l_m]
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
    rm = []
    for pfs in post_fs:
        rm.extend(list(filter(lambda x: x.identifier == pfs, l_m)))
    print("Run {} complete!".format(number))
    t2 = time.clock()
    total_time = t2 - t1
    return {'aggregate': aggregate, 'processing': total_time, 'matches': rm}


def main():
    env = os.getenv("ENVIRONMENT")
    number = 100
    results = test_run(number)
    print("Run {}: \n\tAverage score: {}\n\tProcessing time: {}".format(number, results['aggregate'] / number,
                                                                        results['processing']))
    for m in results['matches']:
        """Example output - at scale you wouldn't read it all but you could group and send to CLs"""
        ws = m.weighted_scores
        print("FastStreamer id: {}\nPost id: {}\nMatch score: {}\n\tAnchor score: {}\n\tLocation score: {}\n\n"
              .format(m.fast_streamer.identifier, m.post.identifier, m.total, ws['anchor'], ws['location']))
    match_scores = [m.total for m in results['matches']]
    histo = np.histogram(match_scores, bins=[x for x in range(0, 13)])
    print(histo[0], "\n", histo[1])
    if env == "test":
        send_email(to_name="Subject X", from_email="test@example.com", to_email="jonathandrewkerr@gmail.com",
                   subject="Test", content="Hello world")


if __name__ == '__main__':
    main()
