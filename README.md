# EXIST (EXternal Information aggregation System against cyber Threat)

EXIST is a web application for aggregating and analyzing threat intelligence.

- EXIST is written by the following software.
 - Python 3.5.1
 - Django 1.11.5

## Getting started

After that I assume the environment of CentOS 7.

### Install python modules

```
$ pip install -r requirements.txt
```

### Install MariaDB

```
$ curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash
$ sudo yum install MariaDB-server MariaDB-client
```

### Database setting

- Create datebase and user.
- Create intelligence/settings.py in reference to [intelligence/settings.py.template](intelligence/settings.py.template). And edit according to your DB settings.

### Run database

```
$ sudo systemctl start mariadb
$ sudo systemctl enable mariadb
```

### Migrate database

```
$ python manage.py makemigrations exploit reputation threat threat_hunter twitter twitter_hunter
$ python manage.py migrate
```

### Run web server

```
$ python manage.py runserver 0.0.0.0:8000
```

- Access to http://[YourWebServer]:8000 with your browser.

> **Note:** I recommend to use Nginx and uWSGI when running in production environment.

## Collect feed

Scripts for inserting feed into database are [scripts/insert2db](scripts/insert2db)/\*/insert2db.py.

### Configure insert2db

Configration files are [scripts/insert2db](scripts/insert2db)/\*/conf/insert2db.conf. Create them in reference to insert2db.conf.template.

### Install Redis server
insert2db uses redis as the cache server.

```
$ sudo yum install redis
$ sudo systemctl start redis
$ sudo systemctl enable redis
```

### Run scripts

```
$ python scripts/insert2db/reputation/insert2db.py
```

> **Note:** To automate information collection, write them in your cron.

## Setting hunter

Configration files are [scripts/hunter](scripts/hunter)/\*/conf/\*.conf. Create them in reference to \*.conf.template.
