# member-database

![build status](https://www.travis-ci.org/pep-dortmund/member-database.svg?branch=master) ![coverage](https://contabo.pep-dortmund.org/travis-ci/coverage.svg)

Our member database application

## Design Choices
- keep it simple
- keep it maintainable
- proven technologies > fancy stuff
- use things that we know

therefore we want to use
- poetry (dependency management, packaging, virtualenv)
- sqlite or postgresql (database)
- flask (API)
- itsdangerous (token-based authentication)
- sqlalchemy (ORM)
- if we don't know what to do: follow [the flask mega tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
- vue.js for the interface(s)
  - if possible CDNs, avoiding webpack et. al

## Development

We strongly recommend to read through the first chapters of the [the flask mega tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

1. Install python (>=3.6) and make sure you have pip

1. install poetry using `pip install poetry`, if you use your system's python, use
`pip install --user poetry`

1. Install the dependencies using `poetry install`

1. copy `env-template` to `.env` and fill the variables with the appropriate information
  
  For the mail settings, you can either use your own mail account or just use DEBUG mode,
  which will log email text but not actually send it.

1. To initialise the database, run
  ```
  $ poetry run flask db upgrade
  ```

1. Start the server using `FLASK_DEBUG=true poetry run flask run`

### Runnig the tests

We are using `pytest` to test our app, see <https://flask.palletsprojects.com/en/1.1.x/testing/>.

To run the test, use
```
$ poetry run python -m pytest --cov database
```
The test results will be printen on the console. To get an idea what tests
might be missing you can also view per-line information in the browser by
running
```
$ poetry run python -m pytest --cov database --cov-report html
$ cd htmlcov
$ python -m http.server
```

### Adding Users

To authenticate to certain endpoints you need to add a user. The simplest way
for now is to do this interactively in an iPython shell.

1. Fire up iPython via `poetry run ipython`

1. Setup the global namespace with everything you need
   ```python
   In [1]: from member_database import app, db
   In [2]: from member_database.models import Person, User
   ```

1. Every User needs to be linked to a Person, so first you need to create a
   person, and store it in the database
   ```python
   In [3]: p = Person()
   In [4]: p.name = 'Albert Einstein'
   In [5]: p.email = 'albert@aol.de'
   ```

1. Now you can create a User and set its password
   ```python
   In [6]: u = User()
   In [7]: u.person = p
   In [8]: u.username = 'aeinstein'
   In [9]: u.set_password('supersecurepassword')

   # you can even check the super secure hash of this password
   In [10]: u.password_hash
   ```

1. Finally store everything in the database
   ```python
   # this is needed to connect to the correct database
   In [12]: app.app_context().push()

   In [13]: db.session.add(p, u)
   In [14]: db.session.commit()
   ```

1. You can now login at the `/login` endpoint 🎉

### Adding Roles

To enable fine-grained access management for users to specific endpoints,
each protected endpoint is associated with a uniquely named access level.  
A role combines multiple access levels and multiple roles can be assigned to
different users.  
All access levels that are currently available will be added to the database
automatically at app startup.  
Just like in the above example, you can fire up an ipython session and...

1. To create a new role with some access levels run
   ```python
   from member_database import app, db
   from member_database.models import Role, AccessLevel
   admin_role = Role(id='admin')
   admin_role.access_levels = [
       AccessLevel.query.get('get_persons'),
       AccessLevel.query.get('get_members'),
   ]
   db.session.add(admin_role)
   db.session.commit()
   ```

1. You can simply assign a role to a user via
   ```python
   from member_database import app, db
   from member_database.models import Role, User
   user = User.query.filter_by(username='aeinstein').first()
   user.roles.append(Role.query.get('admin'))
   db.session.add(user)
   db.session.commit()
   ```

Now, the user `aeinstein` will have access to the `get_members` and
`get_persons` access levels via the `admin` role.
