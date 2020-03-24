#!/bin/sh
apk update
apk add nginx
mkdir /www
mkdir -p /run/nginx
mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.orig
mv /app/data/custom/launcher_ivViewer/files/nginx.conf /etc/nginx
apk add php7-fpm php7-mcrypt php7-soap php7-openssl php7-gmp php7-pdo_odbc php7-json php7-dom php7-pdo php7-zip php7-mysqli php7-sqlite3 php7-apcu php7-pdo_pgsql php7-bcmath php7-gd php7-odbc php7-pdo_mysql php7-pdo_sqlite php7-gettext php7-xmlreader php7-xmlrpc php7-bz2 php7-iconv php7-pdo_dblib php7-curl php7-ctype
apk add php7-mbstring php7-fileinfo php7-session
mv /app/data/custom/launcher_ivViewer/files/php.ini /etc/php7
cd /www
git clone https://github.com/tvj030728/ivViewer
mkdir /www/ivViewer/data
ln -s /app/data/ivViewer_metadata /www/ivViewer/metadata
chmod 777 -R /www/ivViewer