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
Reputation tracker uses redis as the cache server.

```
$ sudo yum install redis
$ sudo systemctl start redis
$ sudo systemctl enable redis
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

### wkhtmltopdf
Lookup URL uses [wkhtmltopdf](https://wkhtmltopdf.org/).

- Download and install wkhtmltopdf from https://wkhtmltopdf.org/downloads.html

## Credits

This product includes GeoLite2 data created by MaxMind, available from [https://www.maxmind.com](https://www.maxmind.com).