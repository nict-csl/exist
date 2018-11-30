#!/bin/bash

source $(cd $(dirname $0); pwd)/url.conf

QUERY='delete from django_celery_results_taskresult
    where not exists(
        select * from(
            select * from django_celery_results_taskresult T2
            order by date_done desc limit 6
            ) T3
        where django_celery_results_taskresult.id = T3.id
    );'
/usr/bin/mysql -u${USER} -p${PASS} -D${DB} -e "${QUERY}"
