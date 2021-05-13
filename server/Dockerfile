# Python version
FROM python:3.9
ENV PYTHONUNBUFFERED=1

WORKDIR /code/server

# Install gettext to compile tranlations
RUN apt-get update && apt-get install gettext -y

# Install pipenv
RUN pip install --upgrade pip && pip install pipenv

# Copy pipfile and install it as a system packages
COPY ./Pipfile ./Pipfile.lock /code/server/

# No need in virtualenv as we are already inside container
RUN pipenv install --dev --system

# Copy project files only here, because we don't want to reinstall
# requirements each time file is changed.
COPY ./ /code/server/
