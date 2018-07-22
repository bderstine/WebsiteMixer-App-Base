WebsiteMixer
======

A Python/Flask alternative to WordPress and Drupal.

Run
---

::

    export FLASK_APP=websitemixer
    export FLASK_ENV=development
    flask init-db
    flask run

Or on Windows cmd::

    set FLASK_APP=websitemixer
    set FLASK_ENV=development
    flask init-db
    flask run

Open http://0.0.0.0:5000 in a browser.


Test
----

::

    pip install '.[test]'
    pytest

Run with coverage report::

    coverage run -m pytest
    coverage report
    coverage html  # open htmlcov/index.html in a browser
