from bs4 import BeautifulSoup
import re


def test_event(client):
    from member_database import db
    from member_database.events import EventRegistration, Event
    from member_database.mail import mail

    e = Event(
        name='Test Event',
        description='Just to test this stuff',
        registration_open=True,
        max_participants=1,
        registration_schema={
            'properties': {
                'semester': {'type': 'integer', 'label': 'Semester'},
                'course': {'type': 'string', 'enum': ['Physik', 'Medizinphysik']},
            },
            'required': ['semester', 'course'],
        }
    )
    db.session.add(e)
    db.session.commit()

    # test registration form is accessible
    ret = client.get(f'/events/{e.id}/registration/')
    assert ret.status_code == 200
    text = ret.data.decode('utf-8')
    assert 'Es sind noch 1 Plätze' in text

    # test event is shown on main page
    ret = client.get('/events/')
    assert ret.status_code == 200
    assert 'Test Event' in ret.data.decode('utf-8')

    mails = 'test1', 'test2'
    expected_state = 'confirmed', 'waitinglist'
    cancel_link = ""
    for i, (email, state) in enumerate(zip(mails, expected_state), start=1):
        # test registering
        with mail.record_messages() as outbox:
            ret = client.post('/events/1/registration/', data={
                'semester': 1,
                'course': 'Physik',
                'email': f'{email}@example.org',
                'name': 'Test User',
                'submit': True,
            }, follow_redirects=True)
            assert ret.status_code == 200

        assert EventRegistration.query.get(i).status_name == 'pending'

        # test mail was send
        assert len(outbox) == 1
        assert e.name in outbox[0].subject
        m = re.search(r'http(s)?:\/\/.*events\/registration\/.*', outbox[0].body)
        assert m
        link = m.group(0)

        # test confirmation
        with mail.record_messages() as outbox:
            ret = client.get(link)
            assert ret.status_code == 200
        assert len(outbox) == 1
        m = re.search(r'http(s)?:\/\/.*events\/cancel\/.*', outbox[0].body)
        assert m
        if i == 1:
            cancel_link = m.group(0)
        
        soup = BeautifulSoup(ret.data.decode('utf-8'), 'html.parser')
        if state == 'waitinglist':
            assert soup.find('div', {'class': 'alert alert-warning'})
        else:
            assert soup.find('div', {'class': 'alert alert-success'})

        assert EventRegistration.query.get(i).status_name == state

    # test event is now full
    r = client.get('/events/1/registration/')
    s = BeautifulSoup(r.data.decode('utf-8'), 'html.parser')
    alert = s.find('div', {'class': 'alert alert-warning'})
    assert alert
    assert 'Warteliste' in alert.text
    
    # test event cancel 
    r = client.post(cancel_link, data={'submit': True}, follow_redirects=True)
    assert r.status_code == 200
    # event should not be full anymore
    r = client.get('/events/1/registration/')
    s = BeautifulSoup(r.data.decode('utf-8'), 'html.parser')
    alert = s.find('div', {'class': 'alert alert-success'})
    assert alert
    assert 'verfügbar' in alert.text
