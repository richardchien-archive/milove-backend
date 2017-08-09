FROM python:3.6
MAINTAINER Richard Chien <richardchienthebest@gmail.com>

# to get rid of the annoying "apt-utils" warning
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y apt-utils

WORKDIR /usr/src/app

# install requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# things for MySQL support
RUN apt-get install -y libmysqlclient-dev && pip install --no-cache-dir mysqlclient

# install gunicorn and related package
RUN pip install --no-cache-dir gunicorn gevent

COPY milove ./milove
COPY manage.py ./manage.py
RUN mkdir -p media static

# configure cron
RUN apt-get install -y cron
COPY crontab /etc/cron.d/backend-cron
RUN chmod 0644 /etc/cron.d/backend-cron
RUN touch /var/log/cron.log

# cleanup
RUN apt-get autoremove -y --purge && apt-get clean && apt-get autoclean

CMD python manage.py collectstatic --no-input --clear && gunicorn --config gunicorn_config.py milove.wsgi
