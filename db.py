#!/usr/bin/env python3

from uuid import uuid4
from pymongo import MongoClient


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

    def add_member(self, json_member):
        json = json_member
        json['_id'] = str(uuid4())
        self.db.insert_one(json)

    def remove_member(self, member_id):
        self.db.delete_one({'_id': member_id})


if __name__ == '__main__':
    db = MemberDatabase('mongodb://localhost:27017/', 'pep-test', True)
    db.add_member({'name': 'Simpson', 'first_name': 'Homer'})
    db.add_member(
        {
            'name': 'Burns',
            'first_name': 'Charles',
            'middle_name': 'Montgomery'
        })

    print('Number of members:', db.size())

    for member in db.list_members():
        print(member)

    found_member = db.find_member({'name': 'Simpson'})
    print('Member found:', found_member)

    member_id = found_member['_id']
    db.remove_member(member_id)

    print('Number of members:', db.size())
