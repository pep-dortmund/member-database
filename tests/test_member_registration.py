import re


def test_member_registration(app, client, admin_user):
    from member_database.mail import mail
    from member_database.models import Person

    name = 'Enrico Fermi'
    email = 'fermi@example.org'

    with mail.record_messages() as outbox:
        ret = client.post(
            '/register/', data=dict(name=name, email=email),
            follow_redirects=True,
        )

    assert ret.status_code == 200
    assert 'Bestätigungsemail' in ret.data.decode('utf-8')

    # check person was created and has membership status email_unverified
    person = Person.query.filter_by(email=email).one()
    assert person.name == name
    assert person.membership_status_id == 'email_unverified'

    assert len(outbox) == 1

    assert outbox[0].recipients == [email]
    m = re.search(r'http(s)?:\/\/.*edit\/.*', outbox[0].body)
    assert m
    link = m.group(0)

    # verify email, board should be notified for a new membership application
    with mail.record_messages() as outbox:
        r = client.get(link)

    assert len(outbox) == 1
    assert outbox[0].recipients == [app.config['APPROVE_MAIL']]
    assert f'Name: {name}' in outbox[0].body

    assert r.status_code == 200

    person = Person.query.filter_by(email=email).one()
    assert person.membership_status_id == 'pending'

    # login admin user
    r = client.post('/login/', data=admin_user.login_data, follow_redirects=True)
    assert r.status_code == 200

    # check application processing
    with mail.record_messages() as outbox:
        r = client.post(
            f'/applications/{person.id}/',
            data=dict(decision='accept'),
            follow_redirects=True,
        )
        assert r.status_code == 200

    assert len(outbox) == 1
    assert outbox[0].recipients == [email]

    person = Person.query.filter_by(email=email).one()
    assert person.membership_status_id == 'confirmed'
