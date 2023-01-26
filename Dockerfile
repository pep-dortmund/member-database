FROM python:3.10-slim

# we always want to serve the member_database app
ENV FLASK_APP=member_database \
	PORT=5000 \
	PIP_NO_CACHE_DIR=1 \
	PIP_DISABLE_PIP_VERSION_CHECK=1 \
	PYTHONUNBUFFERED=1

# everything should run as the memberdb user (not root, best practice)
RUN useradd --system --user-group memberdb

# we need the pg_dump executable for auto backups
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.3.1
WORKDIR /home/memberdb/

# this will be our startup script
COPY run.sh .

# migrations are needed at startup
COPY migrations migrations

# copy relevant files
COPY pyproject.toml poetry.lock ./

# install production dependencies
# this is our production server
# on top, for production we use postgresql, which needs psycopg2 and
# pg_config
# this will create a wheel file that contains all dependencies
RUN poetry config virtualenvs.create false \
	&& poetry install -E deploy --only main

COPY member_database ./member_database

# switch to our production user
USER memberdb
CMD ./run.sh
