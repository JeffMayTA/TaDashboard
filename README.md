# Ten Adams Dashboard project

This is a python / flask framework dashboard for Ten Adams

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

## Prerequisites

To run this project, you need to have Python 3 installed on your machine. You can download it from the official website: [https://www.python.org/downloads/]

## Installing

* Clone the repository to your local machine
* Suggest code editor is VS Code
* go to the project folder and open in terminal
* Setup a virtual environment
`python3 -m venv venv`
* then run
`source venv/bin/activate`
* Once activated, you should see the name of your virtual environment in the terminal prompt. You can now install packages and dependencies within this virtual environment without affecting the rest of your system.
* in the terminal - Navigate to the project directory:
`pip3 install -r requirements.txt`
* NOTE: To exit the virtual environment, run the `deactivate` command

## Authenticating with Google

Request the proper authentication JSON Keyfile from Ten Adams

add to your .zshrc file (activate hidden files to view)

```text
# set the bigquery and dashboard Google Creds 
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
```

Replace /path/to/your/keyfile.json with the actual file path to your JSON key file for Google BigQuery on your Mac. Remember to replace the placeholders with the actual values for your setup.

## Running the App

To run the app locally, use the following command:

In the terminal on first run, or first launch, run this command

copy code
`export FLASK_APP=main.py` or `flask --app main.py --debug run`

then run
`flask run` or `flask run --reload`

CTRL - C to exit

You will have to exit and re-run app on any changes to code to see in local - refresh doesn't pull in updated code.

* Open your web browser and go to [http://localhost:5000/] to view the app.

## Deployment

This project is currently deployed to Google App Engine

more instructions to come - merging to master will not currently deplopy to app engine. deployment happens locally via gcloud app deploy once the SDK in installed locally and properly setup

## Static markup

### Ten Adams

* Utilization - /markup/utilization.html (for example <http://127.0.0.1:5000/markup/utilization.html>)
* Login - /markup/login.html (<http://127.0.0.1:5000/markup/login.html>)
* 404 page - /markup/404.html  (<http://127.0.0.1:5000/markup/404.html>)
* Welcome page = /markup/index.html (<http://127.0.0.1:5000/markup/index.html>)

### Nuvance

* Nuvance - Index - /markup/nuvance/index.html (<http://127.0.0.1:5000/markup/nuvance/index.html>)
