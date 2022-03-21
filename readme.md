# Folder Structure

- `db_directory` has the sqlite DB. It can be anywhere on the machine. Adjust the path in ``application/config.py`. Repo ships with one required for testing.
- `application` is where our application code is
- `static` - default `static` files folder. It serves at '/static' path. More about it is [here](https://flask.palletsprojects.com/en/2.0.x/tutorial/static/).
- `templates` - Default flask templates folder


```
├── application
│   ├── config.py
│   ├── controllers.py
│   ├── database.py
│   ├── __init__.py
│   ├── models.py
│   └── __pycache__
│       ├── config.cpython-39.pyc
│       ├── controllers.cpython-39.pyc
│       ├── database.cpython-39.pyc
│       ├── __init__.cpython-39.pyc
│       ├── models.cpython-39.pyc
├── __pycache__
|   ├──app.cpython-39.pyc 
├── db_directory
│   └── database.sqlite3
├── app.py
├── readme.md
├── static
    └──images
    │   └── 1.png
    │   └── 7.png
    │   └── login.png
    │   └── signup.png
    └──css
    │   └── dashboard.css
    │   └── login.css
└── templates
    ├── signup.html
    └── index.html
    └── login.html
    └── welcome.html
    └── add_tracker.html
    └── add_logs.html
    └── notfound.html
    └── tracker.html
    └── update_logs.html
    └── update_tracker.html
```
