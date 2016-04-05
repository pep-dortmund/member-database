#!/usr/bin/env python3

import pprint


class Member(object):
    def __init__(self, first_name, last_name, gender, email_address):
        self.json_config = {
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender,
            'email_address': email_address
        }

    def __repr__(self):
        return pprint.pformat(self.json_config, indent=4)

    def __getitem__(self, key):
        if key not in self.json_config.keys():
            raise KeyError
        return self.json_config[key]

    def __setitem__(self, key, value):
        self.json_config[key] = value

    @property
    def json(self):
        return self.json_config


if __name__ == '__main__':
    new_member = Member('Homer', 'Simpson', 'm', 'homer@simpson.com')

    print(new_member)

    new_member['degree'] = 'Dr.'
    new_member['postal_address'] = '742 Evergreen Terrace\n Springfield'

    print(new_member)
