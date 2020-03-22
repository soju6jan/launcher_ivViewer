#!/bin/sh
nginx -s stop
ps -ef | grep php-fpm7 | awk '{print $1}' | xargs kill -9
