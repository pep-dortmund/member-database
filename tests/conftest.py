import pytest
import tempfile


@pytest.fixture(scope='session')
def client():
    from database import app, db

    with tempfile.NamedTemporaryFile(suffix='.sqlite', prefix='db_testing') as f:
        app.config.from_object('config.TestingConfig')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + f.name

        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
