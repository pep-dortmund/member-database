#!/usr/bin/env python3

import getpass
from uuid import uuid4
from mongoengine import connect
from pymongo import MongoClient

from database.member import Member


class MemberDatabase(object):
    def __init__(self, db=None, reset=False, host='localhost', port=27017, **kwargs):
        if reset:
            try:
                # drop old database
                MongoClient(f'mongodb://{host}:{port}').drop_database(db)
            except:
                raise
        self.db = connect(db=db, host=host, port=port, **kwargs)


if __name__ == '__main__':
    db = MemberDatabase('pep-test', True)
    Member('Homer', 'Simpson', 'm', 'homer@simpson.com').save()

    mr_burns = Member('Charles', 'Burns', 'm', 'burns@burns.com')
    mr_burns['middle_name'] = 'Montgomery'
    mr_burns.save()

    print('Number of members:', Member.objects.count())

    for member in Member.objects:
        print(member)

    found_member = Member.objects(last_name='Simpson').first()
    print('Member found:', found_member)

    found_member.delete()

    print('Number of members:', Member.objects.count())
