# Othello

[![CI](https://github.com/tjcsl/othello-tourney/actions/workflows/ci.yml/badge.svg?branch=master&event=push)](https://github.com/tjcsl/othello-tourney/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/tjcsl/othello-tourney/badge.svg?branch=master)](https://coveralls.io/github/tjcsl/othello-tourney?branch=master)

## Getting Started

The Othello server models require a PostgreSQL database and will not work with SQLite.
Celery and the channels layer also require a redis server running.

There are two ways to develop for Othello:
  1) Docker (recommended, easy)
  2) Vagrant (not recommended, less easy)


NOTE: If you are using windows, make sure you are using WSL 2. Run all shell commands in the WSL and if you are using docker make sure the docker backend is WSL 2.0

Start by cloning this repository:
`git clone https://github.com/tjcsl/othello-tourney.git`


### Docker

To start the services(postgres, redis):
  * `cd config/docker`
  * `docker-compose up -d`

You can also run the services individually:
  * `./config/docker/postgres.sh`
  * `./config/docker/redis.sh`

You only need to start the services once (either with `docker-compose` or the shell scripts) and both ways will handle all the necessary configuration(passwords, port forwarding, etc.)

* Note: The postgres docker service will create a volume on the host machine so that data persists between runs


### Vagrant

The recommended VM provider is [Virtualbox](https://www.virtualbox.org/wiki/Downloads). However, the process describe below assumes you are using Virtualbox as the provider

You will need the Virtualbox Guest Additions for Vagrant, install them by running:
  * `vagrant plugin install vagrant-vbguest` (may differ for Windows users)

Afterwards, start the VM by running:
  * `vagrant up`

The VM may take a long time to boot and provision, do not interrupt this process (unless it takes more than 15-20 minutes).



### Ion OAuth

The Othello server uses Ion OAuth, you will need to register an application [here](https://ion.tjhsst.edu/oauth)
  * Redirect url is `http://<host>:8000/oauth/complete/ion/`
  * Acceptable hosts can be found in the `ALLOWED_HOSTS` list in `othello/settings/__init__.py`
  * url must be inputted exactly or OAuth will fail

If you are using `docker` to host the Othello services, you will have to manually copy `othello/settings/secret.py.sample` to `othello/settings/secret.py`. If you are using `vagrant`, this is automatically done for you.

After registering an OAuth application enter the key and secret in the `SOCIAL_AUTH_ION_KEY` and `SOCIAL_AUTH_ION_SECRET` variables in `secret.py`


### Running the Othello server

After you have setup your dev environment and configured Ion OAuth, you will need to install the project dependencies.

This project uses [Pipenv](https://pipenv.pypa.io/en/latest/) to manage dependencies, to install the dependencies run:
  * `pipenv install --dev`

After installing the dependencies, run the model migrations
  * `pipenv run python3 manage.py migrate`

Note: Failure to do this will cause the game code to fail.


You can run the django server by running:
  * `pipenv run python3 manage.py runserver <host>:<port>`

Note: If you are using `vagrant`, host should be `0.0.0.0` and port should be `8000`. Vagrant on Linux has some issues forwarding traffic if the host is `127.0.0.1` or `localhost`, so `0.0.0.0` will have the most success. The only port forwarded from the vagrant VM is `8000` so no other port will work (unless you change the Vagrant config).

Note: If you are using `docker`, you can use any host/port combination as long as :
  1) You can access the host and port
  2) The resultant url is registered in the Ion OAuth application

Afterwards, open the resultant url in a browser and you should see the Othello site.


### Running the celery worker

The Othello server uses [celery](https://docs.celeryproject.org/en/stable/getting-started/introduction.html) to run games and tournaments. If you try to play a game without starting the celery worker, the game will just hang.


Start the celery worker by running:

  * `pipenv run celery --app=othello worker --loglevel=INFO -B`

Note: You will need to keep this command running in the foreground until you need to restart it

Note: If using `vagrant` this command must be run inside the Vagrant VM.



## Formatting

Keep the code pretty :)

Run this command before committing or CI checks will fail

  * `pipenv run ./scripts/format.sh`
