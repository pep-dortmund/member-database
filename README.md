# member-database
Our member database application

# Design Choices
- keep it simple
- keep it maintainable
- proven technologies > fancy stuff
- use things that we know

therefore we want to use
- sqlite (database)
- flask (API)
- itsdangerous (token-based authentication)
- sqlalchemy (ORM)
- if we don't know what to do: follow [the flask mega tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
- vue.js for the interface(s)
  - if possible CDNs, avoiding webpack et. al

# Development

## MongoDB

### Mac OS X

```bash
brew install mongodb
brew services start mongodb
```

### Arch Linux

```bash
pacman -S python-pip
pip install pymongo==2.8
pip install mongoengine
```

## Testing

```bash
pip install -e .

python database/db.py
python database/member.py

FLASK_APP=database FLASK_DEBUG=true flask run
```
