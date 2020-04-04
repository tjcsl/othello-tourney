#!/bin/bash

set -e

apt update
apt -y upgrade

timedatectl set-timezone America/New_York

# Install Python
apt -y install python3
apt -y install python3-pip
pip3 install -U virtualenv virtualenvwrapper

# PostsgreSQL
apt -y install postgresql
apt -y install postgresql-contrib
apt -y install libpq-dev

sqlcmd(){
    sudo -u postgres psql -U postgres -d postgres -c "$@"
}
sqlcmd "CREATE DATABASE othello;" || echo Database already exists
sqlcmd "CREATE USER othello PASSWORD 'pwd';" || echo Database user already exists
sed -Ei "s/(^local +all +all +)peer$/\1md5/g" /etc/postgresql/10/main/pg_hba.conf
service postgresql restart

cd othello
virtualenv -p "$(command -v python3)" --always-copy venv
source ./venv/bin/activate
pip3 install -r requirements.txt
cd othello
python3 manage.py collectstatic --noinput
