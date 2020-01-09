# create a build stage
FROM python:3.8-slim AS build

RUN pip install poetry

WORKDIR /home/memberdb/

# copy relevant files
COPY pyproject.toml poetry.lock ./
COPY database database

# install production dependencies
RUN poetry install --no-dev
# this is our production server
# on top, for production we use postgresql, which needs psycopg2 and
# pg_config
RUN poetry add gunicorn psycopg2-binary

# the app directory needs to match the project name
RUN mv database member_database
# this will create a wheel file that contains all dependencies
RUN poetry build


# start building the production container
FROM python:3.8-slim

# everything should run as the memberdb user (not root, best practice)
RUN useradd --system --user-group memberdb

WORKDIR /home/memberdb

# this will be our startup script
COPY run.sh .
# migrations are needed at startup
COPY migrations migrations
# only the wheel distribution from the build stage is needed for the
# deployed container
COPY --from=build /home/memberdb/dist/*.whl ./wheel/

# we need the pg_dump executable for auto backups
RUN apt-get update && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache ./wheel/*

# we always want to serve the member_database app
ENV FLASK_APP=member_database
ENV PORT=5000

# switch to our production user
USER memberdb
CMD ./run.sh
