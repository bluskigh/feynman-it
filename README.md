## Description
The name given to this web application is "FeynmanIt" because it was inspired by Richard Feynman's learning technique. FeynmanIt utilizes the following stack: Django (backend), Python, JS, HTML, and CSS. Once a user signs up they are given certain permissions to create notes and folders. Each note has much thought put into its structure, this structure was inspired by the infamous learning technique "The Feynman Technique" that was, as the name suggests, made popular by Richard Feynman. Sought as the most efficient learning techniques as it forces the learner to explain the topic in simple terms instead of trickign themselves into thinking they undersatnd the topic by being complex. A folder can be created to store notes, organizing different learnings by subject, by default there are two folders created called: "All", and "Deleted". Progress of learning is available to view as a heatmap in the profile section. 

## Motivation
I have been know of Richard Feynman's learning technique for quite a while, but always wanted a web application that utilized it. I never found a web application that has utilized it, therefore I thought it would be nice to have for not only me but for others to utilize too. I thought of how great an application like this can be for multiple uses such as: classroom teaching, individuals, and parents. Of course the idea of helping others really motivated me to start this project, therefore with my limited knowledge on Django I thought I would give it a try. Hopefully in the future more advanced features can be implemnted such as: sharing notes and having a forum where existing notes can be referenced as answers to questions for others to learn.

## Distinctiveness and Complexity 
This web application is distinct from the projects done in cs50 because it does not fall under these subjects: mailing, commerce, and encyclopedia. Instead this application is a note taking platform greatly differs from any past project. No further explanation is required here because it should not be suspected that this project is related to past projects, as they are not. 

## Application is hosted at:
```
http://feynman-it.herokuapp.com
```

## Setting up the database
1. This application uses postgres as the backend engine, therefore it is important to have postgres installed on the machine its runnng on.
```
for windows: 
    https://www.postgresqltutorial.com/install-postgresql/
for linux: 
    https://www.postgresqltutorial.com/install-postgresql-linux/
for max: 
    https://www.postgresqltutorial.com/install-postgresql-macos/
```
2. sign into postgres cli:
```
sudo -u postgres -i
```
3. Type the following once in postgres cli:
```
psql
createdb feynman;
CREATE USER temp WITH password '1234';
``` 
4. Exit from psql, and then from postgres cli:
```
\q
exit
```

## Database Models
There are only two custom models named: Folder, and Note. Folder is the simplest of the two, meanwhile Note conains a bit more fields of which I will describe here:
- title: Stores title of note
- step_one_iterations, step_two_iterations, links: Stores an array of iterations
- understand: Stores a boolean
- owner: Stores who owns the note
- folder: Stores the foreign key of the folder its under 

## Running the local development server
By default evironment variables are attempted to access but if not set then default fallback values are used. So you don't have to worry about setting external variables as long as you followed the steps above the application should run fine.
```
python3 manage.py runserver
```

## Running tests
```
python3 manage.py test
```

## Explaning files
### CSS
All of my styling was exported into separate files to reduce clutter in html files. 
- index.css: included in ('home/') route, contains styling needed for the home page of the site 
- item-styling.css: included in following routes ('notes/', 'folders/'), contains styling for items seen when visiting folders, or notes route (styles note/folder items).
- layout.css: included in all routes excluding('home/'), general styling such as root colors are placed here
- media.css: included in all routes, styling used to keep page responsive is stored here
- note-syyling.css: included in following routes ('view_note/', 'edit_note/'), styles note such as font size of labels and positioning of table data
- table-styles.css: included in ('edit_note/'), this styles inputs and anything related to the table
### JS
- add-item.js: included in following routes('notes/', 'foders'/), and is used to provide functionality of adding new items
- edit-note.js: included in ('edit_note/') route, provides many individual methods that are vital in the funcitonality of editing a note such as: formatting inputs before form is submitted, and moving edit form around when editing iterations.
- note-animation.js: included in following routes ('edit_note/', 'view_note/'), has functionality of hovering over labels and consecutive flashing on load of document.
- item-animation.js: included in following routes ('notes/', 'folders/'), has functionality of clicking on new item button and causing animation to occur to reveal/hide form
### Python
- views.py: contains code for backend server code
- models.py: stores models
- urls.py: stores urls that are available in project
