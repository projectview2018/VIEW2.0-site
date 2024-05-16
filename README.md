# VIEW-Prototype

## Link to VIEW 2.0 Website

Website Link: www.blindzonesafety.org

## How to Run Website Locally on Computer

### Set up a Virtual Environment

1. Create a virtual environment using the command below.

```bash
python -m venv /path/to/environment_name
```

2. Activate virtual environment. Navigate to directory where enviroment is
   located.

```bash
source environment_name/bin/activate
```

### Set up the Repository

3. Clone this repository and deploy the main branch.

4. Navigate into the repository project folder.

5. In terminal, run the line of code below to install all necessary packages.
   Make sure you are in your virtual environment.

```bash
pip install -r requirements.txt
```

6. Create a file called _.env_ and place in root directory of project folder.
   Copy in secret environment variables and add to .gitignore if not already
   there. **For security, this file should never be committed or pushed to
   GitHub.**

7. Add your device IP address to the Digital Ocean database trusted sources.

   a. Log in to Digital Ocean using sign in with gmail.

   b. On the left side panel, click on **Databases**.

   c. Click on the database called **db-postgresql-nyc3-27521**.

   d. Click on the **Settings** tab, scroll down to **Trusted Sources**, and
   click **Edit**.

   e. Enter your device IP address and click **Save**. Typically, once you click
   into the input field, your IP address will show up automatically as a
   suggested IP.

### Launching the Website

7. To launch the local server, run the line below in the root directory of the
   project.

```bash
python manage.py runserver
```

## Commands to Make Changes

### Editing static files

When editing any static files, such as javascript files (.js) or CSS files
(.css), your changes will not automatically show up on the local site or on the
production site. Run the command below to push changes to the website storage on
Digital Ocean where static files are stored. This must be done whether making
changes to the local or production site.

```bash
python manage.py collectstatic --noinput
```

### Editing other files

Changes made to the other files will be updated on the locally run website
immediately upon refreshing. However, when ready to make changes to the
production website, changes must be committed then pushed to the branch that the
production website is sourcing (right now it is the main branch). After changes
are pushed, Digital Ocean rebuilds and deploys the site, which can take anywhere
from 4-8 minutes.

### How to Access PostgresSQL in Terminal

Navigate to the command line and type in the following command, replacing the
sections in `<>` with the correct values.

```bash
psql -h <REMOTE HOST> -p <REMOTE PORT> -U <DB_USER> <DB_NAME>
```
