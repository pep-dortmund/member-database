def test_new_user(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check if the username and password fields are defined correctly
    """
    assert new_user.username == 'anobel'
    assert new_user.check_password('testpw') != 'testpw'
