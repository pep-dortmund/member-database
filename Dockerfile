# create a build stage
# see https://stackoverflow.com/a/54763270/3838691
FROM python:3.8-slim

# we need the pg_dump executable for auto backups
RUN apt-get update && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.0.5
WORKDIR /home/memberdb/

# copy relevant files
COPY pyproject.toml poetry.lock ./

# install production dependencies
# this is our production server
# on top, for production we use postgresql, which needs psycopg2 and
# pg_config
# this will create a wheel file that contains all dependencies
RUN poetry config virtualenvs.create false \
	&& poetry install -E deploy --no-dev

COPY member_database ./member_database

# everything should run as the memberdb user (not root, best practice)
RUN useradd --system --user-group memberdb

# this will be our startup script
COPY run.sh .
# migrations are needed at startup
COPY migrations migrations

# we always want to serve the member_database app
ENV FLASK_APP=member_database
ENV PORT=5000

# switch to our production user
USER memberdb
CMD ./run.sh
