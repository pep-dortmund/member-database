# member-database
Our member database application

# Development

## MongoDB

### Mac OS X

```bash
brew install mongodb
brew services start mongodb
```

## Testing

```bash
pip install -e .

python database/db.py
python database/member.py

FLASK_APP=database FLASK_DEBUG=true flask run
```
