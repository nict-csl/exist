#!/bin/bash

STATIC_DIR='/home/jingu/django/exist/static'

find ${STATIC_DIR}/webimg/ -mtime +0| grep -v gitkeep| xargs rm -f
find ${STATIC_DIR}/websrc/ -mtime +0| grep -v gitkeep| xargs rm -f

