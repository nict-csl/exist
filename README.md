# EXIST (EXternal Information aggregation System against cyber Threat)

EXIST is a web application for aggregating and analyzing threat intelligence.

- EXIST is written by the following software.
 - Python 3.5.1
 - Django 1.11.5

## Getting started

After that I assume the environment of CentOS 7. Please at your own when deploying to other environment.

### Install python modules

```
$ sudo pip install -r requirements.txt
```

### Install MariaDB

```
$ curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash
$ sudo yum install MariaDB-server MariaDB-client
```

### Run database

```
$ sudo systemctl start mariadb
$ sudo systemctl enable mariadb
```

### Database setting

- Create datebase and user.
- Create intelligence/settings.py in reference to [intelligence/settings.py.template](intelligence/settings.py.template). And edit according to your DB settings.

### Migrate database

```
$ python manage.py makemigrations exploit reputation threat threat_hunter twitter twitter_hunter
$ python manage.py migrate
```

### Install Redis server
Reputation tracker uses redis as the Celery cache server backend.

```
$ sudo yum install redis
$ sudo systemctl start redis
$ sudo systemctl enable redis
```

### Setup Celery
Reputation tracker uses Celery as an asynchronous task job queue.

- Create a celery config
/etc/sysconfig/celery

```
# Name of nodes to start
# here we have a single node
CELERYD_NODES="w1"
# or we could have three nodes:
#CELERYD_NODES="w1 w2 w3"

# Absolute or relative path to the 'celery' command:
CELERY_BIN="/path/to/your/celery"

# App instance to use
# comment out this line if you don't use an app
CELERY_APP="intelligence"
# or fully qualified:
#CELERY_APP="proj.tasks:app"

# How to call manage.py
CELERYD_MULTI="multi"

# Extra command-line arguments to the worker
CELERYD_OPTS="--time-limit=300 --concurrency=8"

# - %n will be replaced with the first part of the nodename.
# - %I will be replaced with the current child process index
# and is important when using the prefork pool to avoid race conditions.
CELERYD_PID_FILE="/var/run/celery/%n.pid"
CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_LOG_LEVEL="INFO"
```

- Create a celery service management script.
/etc/systemd/system/celery.service

```
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=YOUR_USER
Group=YOUR_GROUP
EnvironmentFile=/etc/sysconfig/celery
WorkingDirectory=/path/to/your/exist
ExecStart=/bin/sh -c '${CELERY_BIN} multi start ${CELERYD_NODES} \
-A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
--logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}'
ExecStop=/bin/sh -c '${CELERY_BIN} multi stopwait ${CELERYD_NODES} \
--pidfile=${CELERYD_PID_FILE}'
ExecReload=/bin/sh -c '${CELERY_BIN} multi restart ${CELERYD_NODES} \
-A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
--logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}'

[Install]
WantedBy=multi-user.target
```

- Create Celery log and run directories.

```
$ sudo mkdir /var/log/celery; sudo chown YOUR_USER:YOUR_GROUP /var/log/celery
$ sudo mkdir /var/run/celery; sudo chown YOUR_USER:YOUR_GROUP /var/run/celery
```

- Run Celery

```
$ sudo systemctl start celery.service
$ sudo systemctl enable celery.service
```

### Run web server

```
$ python manage.py runserver 0.0.0.0:8000
```

- Access to http://[YourWebServer]:8000 with your browser.
- WebAPI: http://[YourWebServer]:8000/api/

> **Note:** I recommend to use Nginx and uWSGI when running in production environment.

## Collect feed

Scripts for inserting feed into database are [scripts/insert2db](scripts/insert2db)/\*/insert2db.py.

### Configure insert2db

Configration files are [scripts/insert2db](scripts/insert2db)/\*/conf/insert2db.conf. Create them in reference to insert2db.conf.template.

### Run scripts

```
$ python scripts/insert2db/reputation/insert2db.py
```

> **Note:** To automate information collection, write them in your cron.

## Setting hunter

Configration files are [scripts/hunter](scripts/hunter)/\*/conf/\*.conf. Create them in reference to \*.conf.template.

## Other requirement tools

### GeoIP DB
Lookup IP / Domain uses [GeoLite2 Database](https://dev.maxmind.com/geoip/geoip2/geolite2/).

- Download GeoIP DB from http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz
- Write the path to GeoLite2-City.mmdb in your conf/geoip.conf.

### wkhtmltopdf and Xvfb
Lookup URL uses [wkhtmltopdf](https://wkhtmltopdf.org/) and Xvfb.

- Download and install wkhtmltopdf from https://wkhtmltopdf.org/downloads.html
- Install Xvfb.

```
$ sudo yum install xorg-x11-server-Xvfb
```

## Credits

This product includes GeoLite2 data created by MaxMind, available from [https://www.maxmind.com](https://www.maxmind.com).