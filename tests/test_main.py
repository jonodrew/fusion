from main import calculate_matches


def test_calculate_matches(test_data):
    output = calculate_matches(test_data[0])
    assert type(output) == dict
    assert len(output['matches'])*10 <= output['aggregate']
