WebsiteMixer
======

A Python/Flask alternative to WordPress and Drupal.

Tested with: Ubuntu 18.04, Flask 1.0.2, Python 3.6.7

Run
---

::

    ./run.sh

Which runs with the following options::

    export FLASK_APP=websitemixer
    export FLASK_ENV=development
    export FLASK_DEBUG=1

    flask run --host=0.0.0.0

And it should have output similar to::

    * Serving Flask app "websitemixer" (lazy loading)
    * Environment: development
    * Debug mode: on
    * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
    * Restarting with stat
    * Debugger is active!
    * Debugger PIN: XXX-XXX-XXX

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
