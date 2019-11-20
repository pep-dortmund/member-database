def test_home(client):
    """
    Check if the index delivers a valid response
    """
    response = client.get('/')
    assert response.status_code == 200


def test_login(client):
    """
    Check if the login page delivers a valid response
    """
    response = client.get('/login')
    assert response.status_code == 200
