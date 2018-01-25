from app.main import calculate_matches


def test_calculate_matches(test_data):
    output = calculate_matches(test_data)
    assert type(output) == dict
    assert output['aggregate'] > 1000
    assert len(output['matches']) == 100