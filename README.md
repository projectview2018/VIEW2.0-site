# VIEW-Prototype

## Link to VIEW 2.0 Website
Website Link: www.blindzonesafety.org


## How to Run Website Locally on Computer

### Set up a Virtual Environment
1. Create a virtual environment using the command below.

```
python -m venv /path/to/environment_name
```
2. Activate virtual environment. Navigate to directory where enviroment is located
```
source environment_name/bin/activate
```
### Set up the Repository
3. Clone this repository and deploy the main branch.

4. Navigate into the repository project folder.

5. In terminal, run the line of code below to install all necessary packages. Make sure you are in your virtual environment.
```
pip install -r requirements.txt
```
6. Create a file called *.env* and place in root directory of project folder. Copy in secret environment variables and add to .gitignore if not already there. **For security, this file should never be committed or pushed to GitHub.**

### Launching the Website

7. To launch the local server, run the line below.
```
python manage.py runserver
```

## Commands to Make Changes
### Editing javascript files
When editing javascript files (.js), run the command below to push changes to the website storage on Digital Ocean where static files are stored. This must be done whether making changes to the local or production site.
```
python manage.py collectstatic
```
### Editing other files
Changes made to the other files will be updated on the locally run website immediately upon refreshing. However, when ready to make changes to the production website, changes must be committed then pushed to the branch that the production website is sourcing (right now it is the main branch). After changes are pushed, Digital Ocean rebuilds and deploys the site, which can take anywhere from 4-8 minutes.

### How to Access PostgresSQL in Terminal
1. Navigate to Digital Ocean and go to the Database page.
