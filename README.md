uetopia-metagame
======================

Sample application for using uetopia metagame functionality

## Setup

Download the source: https://github.com/uetopia/metagame
create a new google project
https://console.cloud.google.com
Create a firebase project (Be careful! you need to select the REALTIME database type!)
https://firebase.google.com/
Turn on the datastore in test mode.
Enable auth. Enable google, (twitter, github, facebook if you want) auth. NOT EMAIL. NOT PHONE. NOT ANONYMOUS.
Add appengine domain:  yourproject.appspot.com
Copy firebase credentials into the static/index.html, configuration.py and app.yaml files


https://console.cloud.google.com
create an apikey and an oath2 key from the console - copy these into configuration.py
Change the apiurl inside static/app/js/app.js to match the appengine project name
Uetopia.com
Copy Game key/secret from uetopia.com developer game credentials page into the configuration.py file
Add a game mode for metagame
Update game details page. Enable matchmaker. Enable MetaGame.
Copy your numeric gameID into the static/app/partials/uetopia_connect.html file (in the iframe)
Deploy the appengine project (including app.yaml index.yaml queue.yaml)
gcloud app deploy -v1 app.yaml queue.yaml index.yaml
View the metagame website by going to yourproject.appspot.com login. connect your uetopia account.
view the datastore admin inside cloud.google.com find your user record, edit. enable admin go to appengeine > memcache. clear cache, confirm.
Manually advance the phase by hitting the task URL
https://yourproject.appspot.com/task/season/stage_change


## Video Demo

https://www.youtube.com/watch?v=pyXIBXg-vAM

## Video Walkthrough

https://www.youtube.com/watch?v=VWE2IBveQ9A

## Live Demo

https://ue4topia-metagame.appspot.com

## Directory Layout

- lib/: Python library files not included in the standard runtime environment.
- apps/model/: Python NDB class definitions. NDB is the schemaless object datastore
  on App Engine.
- apps/controllers/: Datastore accessors
- service/: Python Cloud Endpoints definitions. Defines the API backend classes.
- static/: Client side HTML, JavaScript, and other static files.
- app.yaml: App Engine configuration file. Defines paths and Python handlers.
- fix_path.py: Python file to set up our standard project include path.
- services.py: Python handler for the Cloud Endpoints. Choose which API service
  classes are active.
- configuration.py: Settings, and keys for this particular instance.


## Known Issues
- None
