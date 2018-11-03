import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.abspath('memberdb.sqlite')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
