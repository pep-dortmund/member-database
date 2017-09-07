#!/usr/bin/env python3

from mongoengine import DynamicDocument, StringField


class Member(DynamicDocument):  # could/should be Documnet
    first_name = StringField()
    last_name = StringField()
    gender = StringField()
    email_address = StringField()


if __name__ == '__main__':
    new_member = Member('Homer', 'Simpson', 'm', 'homer@simpson.com')

    print(new_member)

    new_member['degree'] = 'Dr.'
    new_member['postal_address'] = '742 Evergreen Terrace\n Springfield'

    print(new_member)
