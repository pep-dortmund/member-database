import pytest
import tempfile


@pytest.fixture(scope='session')
def app():
    from config import TestingConfig
    from member_database import create_app

    app = create_app(TestingConfig)
    return app


@pytest.fixture(scope='session')
def client(app):
    from member_database import db

    with tempfile.NamedTemporaryFile(suffix='.sqlite', prefix='db_testing') as f:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + f.name

        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
