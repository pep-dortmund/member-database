import pytest
from bs4 import BeautifulSoup
import re


@pytest.mark.parametrize("endpoint", ["id", "shortlink"])
def test_event(client, endpoint, admin_user):
    from member_database import db
    from member_database.events import EventRegistration, Event
    from member_database.mail import mail

    event = Event(
        name="Test Event",
        description="Just to test this stuff",
        registration_open=True,
        max_participants=1,
        shortlink="test" if endpoint == "shortlink" else None,
        registration_schema={
            "properties": {
                "semester": {"type": "integer", "label": "Semester"},
                "course": {"type": "string", "enum": ["Physik", "Medizinphysik"]},
            },
            "required": ["semester", "course"],
        },
    )
    db.session.add(event)
    db.session.commit()

    # test registration form is accessible
    event_id = event.id if endpoint == "id" else event.shortlink
    ret = client.get(f"/events/{event_id}/registration/")
    assert ret.status_code == 200
    text = ret.data.decode("utf-8")
    assert "Es sind noch 1 Plätze" in text

    # test event is shown on main page
    ret = client.get("/events/")
    assert ret.status_code == 200
    assert "Test Event" in ret.data.decode("utf-8")

    mails = "test1", "test2"
    expected_state = "confirmed", "waitinglist"
    start = db.session.query(EventRegistration).count() + 1
    for i, (email, state) in enumerate(zip(mails, expected_state), start=start):
        # test registering
        with mail.record_messages() as outbox:
            ret = client.post(
                f"/events/{event_id}/registration/",
                data={
                    "semester": 1,
                    "course": "Physik",
                    "email": f"{email}@example.org",
                    "name": "Test User",
                    "submit": True,
                },
                follow_redirects=True,
            )
            assert ret.status_code == 200

        registration = db.session.get(EventRegistration, i)
        assert registration.status_name == "pending"

        # test mail was send
        assert len(outbox) == 1
        assert event.name in outbox[0].subject
        m = re.search(r"http(s)?:\/\/.*events\/registration\/.*", outbox[0].body)
        assert m
        link = m.group(0)

        # test confirmation
        ret = client.get(link)
        assert ret.status_code == 200
        soup = BeautifulSoup(ret.data.decode("utf-8"), "html.parser")
        if state == "waitinglist":
            assert soup.find("div", {"class": "alert alert-warning"})
        else:
            assert soup.find("div", {"class": "alert alert-success"})

        assert db.session.get(EventRegistration, i).status_name == state

    # test event is now full
    r = client.get(f"/events/{event_id}/registration/")
    s = BeautifulSoup(r.data.decode("utf-8"), "html.parser")
    alert = s.find("div", {"class": "alert alert-warning"})
    assert alert
    assert "Warteliste" in alert.text

    # test participant page
    # not logged in, should fail
    ret = client.get(f"/events/{event_id}/participants/")
    assert ret.status_code == 401

    # login and try again
    ret = client.post("/login/", data=admin_user.login_data)
    assert ret.status_code == 302  # successul login redirects

    ret = client.get(f"/events/{event_id}/participants/")
    assert ret.status_code == 200

    ret = client.post("/logout/")
    assert ret.status_code == 302
