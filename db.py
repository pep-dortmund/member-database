#!/usr/bin/env python3

import getpass
from uuid import uuid4
from pymongo import MongoClient

from member import Member

class MemberDatabase(object):
    def __init__(self, db_address, db_name, reset=False):
        if reset:
            try:
                # drop old database
                MongoClient(db_address).drop_database(db_name)
            except:
                pass
        self.db = MongoClient(db_address)[db_name]['members']

    def size(self):
        return self.db.count()

    def find_member(self, filter_pattern):
        return self.db.find_one(filter_pattern)

    def list_members(self):
        for member in self.db.find():
            yield member

    def add_member(self, member_obj):
        json = member_obj.json
        json['_id'] = str(uuid4())
        self.db.insert_one(json)

    def remove_member(self, member_id):
        self.db.delete_one({'_id': member_id})


if __name__ == '__main__':
    db = MemberDatabase('mongodb://localhost:27017/', 'pep-test', True)
    db.add_member(Member('Homer', 'Simpson', 'm', 'homer@simpson.com'))

    mr_burns = Member('Charles', 'Burns', 'm', 'burns@burns.com')
    mr_burns['middle_name'] = 'Montgomery'
    db.add_member(mr_burns)

    print('Number of members:', db.size())

    for member in db.list_members():
        print(member)

    found_member = db.find_member({'last_name': 'Simpson'})
    print('Member found:', found_member)

    member_id = found_member['_id']
    db.remove_member(member_id)

    print('Number of members:', db.size())
