# Waterloo Jam League (wjl)
This repository is for the Waterloo Jam League. A fun little Kan Jam league due to most sports being closed for the time being. This app was a repository I created to allow people to submit their game scores and to keep track of schedule/standings. Also I got to try some new things out.

**Assumed Dependencies**:
* python
* npm

## Python Webapp
**TLDR**
```
    # install all python requirements
    pip install -r requirements.txt
    # export following if plan on testing locally
    export ARE_TESTING=True
    # allow for oauth from http
    export OAUTHLIB_INSECURE_TRANSPORT=1
    export OAUTHLIB_RELAX_TOKEN_SCOPE=1
    python runserver.py
```
This will use an in-memory database. To actually test with a PostGres database one just needs to setup the appropriate environment variables.

# Environment Variables
The following variables are used by wjl and the defaults are in brackets:
* DATABASE_URL: the database url to connect to ("sqlite://")
* SECRET_KEY:  the secret key for the app (random uuid1)
* GOOGLE_OAUTH_CLIENT_ID: the Google OAuth client id (default off)
* GOOGLE_OAUTH_CLIENT_SECRET:  the Google OAuth secret (default off)
* FACEBOOK_OAUTH_CLIENT_ID: the Facebook OAuth client id (default off)
* FACEBOOK_OAUTH_CLIENT_SECRET:  the Facebook OAuth client secret (default off)
* GITHUB_OAUTH_CLIENT_ID:  the Github OAuth client id (default off)
* GITHUB_OAUTH_CLIENT_SECRET:  the Github OAuth client secret (default off)
* ARE_TESTING:  True if testing using Cypress (default False)

The various OAuth providers are off by default and one has to setup the client/secret
for their local development.

## Database
One like wants persistence data for testing locally. First create a PSQL database and
set its URL in an environment variable
```
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/<DATABASE_NAME>
```
Now calling `python initDB.py` will create the database schema.

## Adding OAuth Provider
This can be a bit of a pain. The easiest one to setup is Github (good for local development).

### Github
Visit [here](https://github.com/settings/applications/new) to register an application on GitHub. You must set the application's authorization callback URL to http://localhost:5000/login/github/authorized.

Once you've registered your application on GitHub, GitHub will give you a client ID and client secret, which we'll can be set using
```
export GITHUB_OUATH_CLIENT_ID=<YOUR ID HERE>
export GITHUB_OUATH_CLIENT_SECRET=<YOUR SECRET HERE>
```

### Google
I was unable to get this working locally. See [here](https://github.com/singingwolfboy/flask-dance-google-sqla) for how it was setup in production.

### Facebook
I was unable to get this working locally. See [here](https://github.com/singingwolfboy/flask-dance-facebook-sqla) for how it was setup in production.


# Github Actions
When doing a pull-request to the master branch some checks are
executed using Github actions. These actions are to ensure
the changes in the PR do not break anything. The following is executed:
1. Check the Python code for any flake8 issues
2. Run the webapp
3. Run the Cypress tests against the webapp

## Cypress Testing Locally
**TLDR**
```
    cd cypress-testing
    # install all dependencies
    npm install
    # set application URL
    export CYPRESS_baseUrl=<Application URL: http://localhost:5000>
    # run the cypress app then choose test
    npm run open
    # run all tests
    npm run test
```
See the Readme in cypress-testing folder for more details.


# Additional Sources
## Python Resources
 * [Flask](https://flask.palletsprojects.com/en/1.1.x/) - documentation for Flask
 * [Flask-Login](https://flask-login.readthedocs.io/en/latest/) - documentation for login extension
 * [Flask-Dance](https://flask-dance.readthedocs.io/en/latest/) - documentation for handling OAuth providers 
 * [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) - dpocumentation for database flask extension
 * [Flake8](https://flake8.pycqa.org/en/latest/) - the python linter for the project

## JavaScript Resources
 * [jQuery](https://api.jquery.com/) - used for some basic pages
 * [Boostrap](https://getbootstrap.com/docs/4.5/getting-started/download/) - CSS framework
 * [Vue](https://vuejs.org/v2/guide/) - used for the score app and other more complex UI
 * [Cypress](https://docs.cypress.io/guides/overview/why-cypress.html#In-a-nutshell) - documentation for Cypress
 * [TypeScript](https://www.typescriptlang.org/) - a super set of JavaScript