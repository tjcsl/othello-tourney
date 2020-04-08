#!/bin/bash

source /home/vagrant/.bashrc
export PATH="$HOME/.pyenv/bin:$PATH"


# Install Python 3.8
pyenv install 3.8.2
pyenv global 3.8.2
export PATH="$HOME/.pyenv/shims:$PATH"
pip install --user virtualenv virtualenvwrapper

# Setup Project
cd othello
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
cp othello/othello/settings/secret.sample.py othello/othello/settings/secret.py

# Setup Django DB Tables
cd othello
python3 manage.py migrate
python3 manage.py loaddata othello/models/yourself.json
python3 manage.py collectstatic --noinput
