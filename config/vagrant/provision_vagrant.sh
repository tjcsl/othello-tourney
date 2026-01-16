#!/bin/bash

set -e

apt update
apt -y upgrade
apt -y autoremove

timedatectl set-timezone America/New_York

# Install utilities
apt -y install htop net-tools curl libssl-dev

# Install Python 3.8
curl -LsSf https://astral.sh/uv/install.sh | sh
ln -s /root/.local/bin/uv /usr/local/bin/uv

# Install firejail
apt install -y firejail

# Install Redis
apt install -y redis-server
systemctl enable --now redis-server

# PostsgreSQL
apt -y install postgresql
apt -y install postgresql-contrib
apt -y install libpq-dev

sqlcmd(){
    sudo -u postgres psql -U postgres -d postgres -c "$@"
}
sqlcmd "CREATE DATABASE othello;" || echo Database already exists
sqlcmd "CREATE USER othello PASSWORD 'pwd';" || echo Database user already exists
sed -Ei "s/(^local +all +all +)peer$/\1md5/g" /etc/postgresql/12/main/pg_hba.conf
service postgresql restart

# Setup Project
cd othello
uv sync
cp -n othello/settings/secret.sample.py othello/settings/secret.py

# Setup Django DB Tables
uv run manage.py migrate
uv run manage.py collectstatic --noinput
