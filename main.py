import sys
import munkres
import numpy as np
import os
import time
from operator import itemgetter
from typing import List, Dict
import sendgrid
import yaml
from matching.classes import Match
from sendgrid.helpers.mail import *
from tests.conftest import test_data


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


def main():
    env = os.getenv("ENVIRONMENT")
    l_m = test_data()  # will contain data drawn from database
    # for m in l_m:
    #     m.total = randrange(1, 101)
    results = calculate_matches(l_m)
    print("Run {}: \n\tAverage score: {}\n\tProcessing time: {}".format(len(results['matches']), results['aggregate'] /
                                                                        len(results['matches']), results['processing']))
    for m in results['matches']:
        if m.total < 15:
            """Example output - at scale you wouldn't read it all but you could group and send to CLs"""
            ws = m.weighted_scores
            print("\nFastStreamer id: {}\nPost id: {}\nMatch score: {}\n\tAnchor score: {}\n\tLocation score: {}\n\t"
                  "Skills score: {}\n\n".format(m.fast_streamer.identifier, m.post.identifier, m.total,
                                                ws['anchor'], ws['location'], ws['skills']))
    match_scores = [m.total for m in results['matches']]
    histo = np.histogram(match_scores, bins=[x for x in range(0, max(match_scores)+1)])
    print(histo[0], "\n", histo[1])
    if env == "test":
        send_email(to_name="Subject X", from_email="test@example.com", to_email="jonathandrewkerr@gmail.com",
                   subject="Test", content="Hello world")


if __name__ == '__main__':
    main()
