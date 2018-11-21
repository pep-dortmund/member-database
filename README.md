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
