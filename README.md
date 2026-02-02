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

To start all the services(postgres, redis):
  * `cd config/docker`
  * `docker compose up --build`

Once started, the docker configuration will handle everything from there, and there is no need to worry about configuration afterwards. Four services will be started up, namely the postgres, redis, django server, and celery worker containers. Once started, the django server will serve the website at [http://localhost:8000/](http://localhost:8000/).

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

If you are using `docker` to host the Othello services, you will have to manually copy `othello/settings/secret.sample.docker.py` to `othello/settings/secret.py`. Note that the `secret.sample.docker.py` file is slightly different from the `secret.sample.py` file in the regards that it runs its services from the docker container names instead of localhost. If you are using `vagrant`, this is automatically done for you.

After registering an OAuth application enter the key and secret in the `SOCIAL_AUTH_ION_KEY` and `SOCIAL_AUTH_ION_SECRET` variables in `secret.py`



## Formatting

Keep the code pretty :)

Run this command before committing or CI checks will fail

  * `uv run pre-commit run --all-files`
