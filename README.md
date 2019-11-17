# member-database
Our member database application

## Design Choices
- keep it simple
- keep it maintainable
- proven technologies > fancy stuff
- use things that we know

therefore we want to use
- pipenv (dependency management)
- sqlite or mysql (database)
- flask (API)
- itsdangerous (token-based authentication)
- sqlalchemy (ORM)
- if we don't know what to do: follow [the flask mega tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
- vue.js for the interface(s)
  - if possible CDNs, avoiding webpack et. al

## Development

We strongly recommend to read through the first chapters of the [the flask mega tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

1. Install python (>=3.6) and make sure you have pip

1. install pipenv using `pip install pipenv`, if you use your system's python, use
`pip install --user pipenv`

1. Install the dependencies using `pipenv install`

1. copy `env-template` to `.env` and fill the variables with the appropriate information

  The `DATABASE_URL` is set to an sqlite database in the current directory, which is nice for developing

1. run `export FLASK_APP=database`

1. To initialise the database, run
  ```
  $ pipenv run flask db init
  $ pipenv run flask db migrate
  $ pipenv run flask db upgrade
  ```

1. Start the server using `FLASK_DEBUG=true pipenv run flask run`

### Adding Users

To authenticate to certain endpoints you need to add a user. The simplest way
for now is to do this interactively in an iPython shell.

1. Make sure you installed the development dependencies `pipenv install --dev`

1. Fire up iPython via `pipenv run iphython`

1. Setup the global namespace with everything you need
   ```python
   In [1]: from database import app, db
   In [2]: from database.models import Person, User
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

   # you can even chack the super secure hash of this password
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
   from database import app, db
   from database.models import Role, AccessLevel
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
   from database import app, db
   from database.models import Role, User
   user = User.query.filter_by(username='aeinstein').first()
   user.roles.append(Role.query.get('admin'))
   db.session.add(user)
   db.session.commit()
   ```

Now, the user `aeinstein` will have access to the `get_members` and
`get_persons` access levels via the `admin` role.

### Testing

run `pipenv install --dev pytest` to install `pytest` to `pipenv`.
run `pipenv install --dev pytest-flask`.
run `pipenv run pytest` to test the flask app.
