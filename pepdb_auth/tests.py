import pytest

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.contrib.auth import get_user

from pepdb.urls import urlpatterns as default_patterns



TEST_PASSWORD = "E=mc^2"


@pytest.fixture(scope="function")
def test_user(db):
    from pepdb_auth.models import User
    u = User(name='Albert Einstein', email="albert@einstein.invalid", is_staff=True)
    u.set_password(TEST_PASSWORD)
    u.save()
    return u


@pytest.mark.django_db
def test_create_user(test_user):
    assert test_user.name == "Albert Einstein"
    assert test_user.email == "albert@einstein.invalid"
    assert test_user.is_staff
    assert test_user.check_password(TEST_PASSWORD)
    assert not test_user.check_password("foo")
    assert test_user.pk is not None


# add a dummy restricted view to test the authentication
@login_required
def restricted_view(request):
    return HttpResponse("<h1>Restricted Area</h1>")

urlpatterns = default_patterns + [path('restricted/', restricted_view)]


@pytest.mark.django_db()
@pytest.mark.urls(__name__)
def test_login_logout(client, test_user):
    # restricted
    assert not get_user(client).is_authenticated

    assert client.get("/restricted/").status_code == 302 # redirect to login

    # invalid username
    client.post("/login/", dict(password=TEST_PASSWORD, username="user@example.org"))
    assert not get_user(client).is_authenticated
    assert client.get("/restricted/").status_code == 302 # redirect to login

    # invalid password
    client.post("/login/", dict(password="foo", username=test_user.email))
    assert not get_user(client).is_authenticated
    assert client.get("/restricted/").status_code == 302 # redirect to login

    # valid credentials
    client.post("/login/", dict(password=TEST_PASSWORD, username=test_user.email))
    user = get_user(client)
    assert user == test_user
    assert user.is_authenticated
    assert client.get("/restricted/").status_code == 200 # logged in

    # logout again
    client.get("/logout/")
    assert not get_user(client).is_authenticated
    assert client.get("/restricted/").status_code == 302 # redirect to login
