# Othello

## Getting Started
This project uses [vagrant](https://www.vagrantup.com/downloads.html) as a development environment, with VirtualBox as the VM provider.
[VirtualBox](https://www.virtualbox.org/wiki/Downloads) is required in order to start the `vagrant` VM.

To get started:
  1) Clone the repo `git clone https://github.com/abagali1/othello-tourney.git`
  2) Navigate to the cloned repository directory
  3) VirtualBox Guest Additions for Vagrant is also required, install this plugin using:
  `vagrant plugin install vagrant-vbguest`
  4) Launch the `vagrant` VM: `vagrant up`, the VM may take a long time to boot be patient until vagrant finishes provisioning the VM
  5) Register an Ion OAuth application here: https://ion.tjhsst.edu/oauth
      * Redirect url is `http://<host>:8000/oauth/complete/ion/`
      * Acceptable hosts can be found in the `ALLOWED_HOSTS` variable in `settings/__init__.py`
      * url must be inputted exactly or authentication will fail
  6) After the VM has been provisioned the file `othello/settings/secret.py` will be created, copy your Ion OAuth credentials in the appropriate fields
  7) Run `./manage.py runserver <host>:8000` after running `vagrant ssh`
  8) Open the url in a browser on the host computer
  9) Run the celery worker using `celery --app=othello worker --loglevel=INFO`
      * Celery worker needs to be running or games will not be executed
