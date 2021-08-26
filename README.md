![run-tests](https://github.com/molinitomario/feynman-it/actions/workflows/django.yml/badge.svg)

## Description
The name given to this web application is "FeynmanIt" because it was inspired by Richard Feynman's learning technique. FeynmanIt utilizes the following stack: Django (backend), Python, JS, HTML, and CSS. Once a user signs up they are given certain permissions to create notes and folders. Each note has much thought put into its structure, this structure was inspired by the infamous learning technique "The Feynman Technique" which was, as the name suggests, made popular by Richard Feynman. Sought as the most efficient learning technique as it forces the learner to explain the topic in simple terms instead of tricking themselves into thinking they understand the topic by being complex. A folder can be created to store notes, organizing different learnings by subject, by default, there are two folders created called: "All", and "Deleted". 

## Motivation
I have been know of Richard Feynman's learning technique for quite a while, but always wanted a web application that utilized it. I never found a web application that has utilized it, therefore I thought it would be nice to have for not only me but for others to utilize too. I thought of how great an application like this can be for multiple uses such as classroom teaching, individuals, and parents. Of course the idea of helping others really motivated me to start this project, therefore with my limited knowledge of Django I thought I would give it a try. Hopefully in the future more advanced features can be implemented such as: sharing notes and having a forum where existing notes can be referenced as answers to questions for others to learn.

## Application is hosted at:
```
http://feynman-it.herokuapp.com
```

## Setting up the database
1. This application uses Postgres as the backend engine, therefore it is important to have Postgres installed on the machine it's running on.
```
for windows: 
    https://www.postgresqltutorial.com/install-postgresql/
for linux: 
    https://www.postgresqltutorial.com/install-postgresql-linux/
for max: 
    https://www.postgresqltutorial.com/install-postgresql-macos/
```
2. sign in to Postgres CLI:
```
sudo -u postgres -i
```
3. Type the following once in Postgres CLI:
```
psql
createdb feynman;
CREATE USER temp WITH password '1234';
``` 
4. Exit from psql, and then from Postgres cli:
```
\q
exit
```

## Database Models
There are only two custom models named: Folder, and Note. Folder is the simplest of the two, meanwhile, Note contains a bit more fields of which I will describe here:
- title: Stores title of the note
- step_one_iterations, step_two_iterations, links: Stores an array of iterations
- understand: Stores a boolean
- owner: Stores who owns the note
- folder: Stores the foreign key of the folder under 

## Setting up the virtual environment (optional)
It is advised to set up a virtual environment when running this application
1. Make sure to have the venv package installed
```
pip3 install venv
```
2. Create a virtual environment in the projects root directory
```
python3 -m venv feynman_venv
```
3. Activate the virtual environment
```
source feynman_venv/bin/activate
```

## Running setup.sh
File connects user to local Postgres server instead of production. 
```
source setup.sh
```

## Installing requirements
To run this application you need to have the requirements that are listed in the requirements.txt file:
```
pip3 install -r requirements.txt
```

## Running the local development server
By default, environment variables are attempted to access but if not set then default fallback values are used. So you don't have to worry about setting external variables as long as you followed the steps above the application should run fine.
```
python3 manage.py runserver
```

## Running tests
```
python3 manage.py test
```

## Explaining files
### CSS
All of my stylings were exported into separate files to reduce clutter in HTML files. 
- index.css: included in ('home/') route, contains styling needed for the home page of the site 
- item-styling.css: included in following routes ('notes/', 'folders/'), contains styling for items seen when visiting folders, or notes route (styles note/folder items).
- layout.css: included in all routes excluding('home/'), general styling such as root colors are placed here
- media.css: included in all routes, styling used to keep page responsive is stored here
- note-syyling.css: included in following routes ('view_note/', 'edit_note/'), styles note such as font size of labels and positioning of table data
- table-styles.css: included in ('edit_note/'), this styles inputs and anything related to the table
### JS
- add-item.js: included in following routes('notes/', 'foders'/), and is used to provide functionality of adding new items
- edit-note.js: included in the ('edit_note/') route, provides many individual methods that are vital in the functionality of editing a note such as formatting inputs before the form is submitted and moving edit form around when editing iterations.
- note-animation.js: included in following routes ('edit_note/', 'view_note/'), has functionality of hovering over labels and consecutive flashing on load of document.
- item-animation.js: included in following routes ('notes/', 'folders/'), has functionality of clicking on new item button and causing animation to occur to reveal/hide form
### Python
- views.py: contains code for backend server code
- models.py: stores models
- urls.py: stores URLs that are available in the project
### Dockerfile
Since I am using a CI/CD workflow with the help of Github Actions. I need this file in order to build/push a new release to Heroku after a push to the main branch on this Github repo is performed. All it does is use an existing docker image to set up python3, copy data in the current working directory to ```/usr/src/app```, and then change the working directory to ```/usr/src/app```. Install the necessary dependencies for the project to run. Finally, it starts the server by running ```gunicorn feynmanit.wsgi```. 
### Layout Tags
In this file is where I register custom filters and tags for me to use in Django templating engine. 

## Todo:
- Make style much more modern
- Add forums
- ... 
