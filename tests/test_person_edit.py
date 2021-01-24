from member_database.mail import mail
from member_database.models import Person
import re


def test_person_edit_form(client, test_person):

    assert client.get('/request_edit').status_code == 200


    with mail.record_messages() as outbox:
        ret = client.post('/request_edit', data={'email': test_person.email}, follow_redirects=True)

        assert ret.status_code == 200
        assert 'E-Mail mit Link für die Datenänderung verschickt' in ret.data.decode('utf-8')

    assert len(outbox) == 1

    assert outbox[0].recipients == [test_person.email]
    m = re.search(r'http(s)?:\/\/.*edit\/.*', outbox[0].body)
    assert m
    link = m.group(0)

    assert test_person.tu_status_id is None
    assert client.get(link).status_code == 200

    ret = client.post(link, data={'tu_status': 2}, follow_redirects=True)

    assert ret.status_code == 200
    assert 'Ihre Daten wurden erfolgreich aktualisiert.' in ret.data.decode('utf-8')

    person = Person.query.filter_by(email=test_person.email).one()
    assert person.tu_status.name == 'Doktorand*in'
