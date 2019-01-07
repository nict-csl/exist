#!/bin/bash

source $(cd $(dirname $0); pwd)/url.conf

find ${STATIC_DIR}/webimg/ -mtime +0 -type f| grep -v gitkeep| xargs rm -f
find ${STATIC_DIR}/websrc/ -mtime +0 -type f| grep -v gitkeep| xargs rm -f

