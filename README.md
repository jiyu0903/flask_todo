Simple Flask Todo App using SQLAlchemy and SQLite database.
Updated with full REST API feature.

For styling, [semantic-ui](https://semantic-ui.com/) was used on the original version of the repository. 
To lessen the workload of browsing into semantic-ui.com, I just made the styles inside the Base.html using CSS in this new repository. 


### New Feature (Full REST API)
The new feature allows the Todo list to be used not just through the HTML interface, but also programmatically—via API calls.
This means other apps, JavaScript front-ends, or even mobile apps can now create, read, update, and delete todos.
It adds flexibility and modern integration potential, making the app much more powerful and scalable.


### Setup
Create project with virtual environment

```console
$ mkdir myproject
$ cd myproject
$ python3 -m venv venv
```

Activate it
```console
$ . venv/bin/activate
```

or on Windows
```console
venv\Scripts\activate
```

Install Flask
```console
$ pip install Flask
$ pip install Flask-SQLAlchemy
```

Set environment variables in terminal
```console
$ export FLASK_APP=app.py
$ export FLASK_ENV=development
```

or on Windows
```console
$ set FLASK_APP=app.py
$ set FLASK_ENV=development
```

Run the app
```console
$ flask run
```
