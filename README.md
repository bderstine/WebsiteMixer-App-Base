# WebsiteMixer [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-green.svg)](https://github.com/bderstine/WebsiteMixer-App-Base/pulls)

A Python/Flask alternative to WordPress and Drupal, with themes and plugins!<br> 
Tested on the latest Ubuntu 18.04, Flask 1.0.2, Python 3.6.7

## Install Dependencies

Start with Ubuntu 18.04, recommend using venv

```
sudo apt update && sudo apt upgrade
sudo apt-get install python3-venv
python3 -m venv www_env
source www_env/bin/activate
```

## Run

```
git clone https://github.com/bderstine/WebsiteMixer-App-Base
cd WebsiteMixer-App-Base
pip install -r requirements.txt
./run.sh
```

Which runs with the following options:

```
export FLASK_APP=websitemixer
export FLASK_ENV=development
export FLASK_DEBUG=1

flask run --host=0.0.0.0
```

And it should have output similar to:

```
Serving Flask app "websitemixer" (lazy loading)
Environment: development
Debug mode: on
Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
Restarting with stat
Debugger is active!
Debugger PIN: XXX-XXX-XXX
```

Open http://0.0.0.0:5000 in a browser.

## Test

These don't work... yet. I'm still working on the v0.4 upgrade! -Brad

```
pip install '.[test]'
pytest
```

Run with coverage report::

```
coverage run -m pytest
coverage report
coverage html  # open htmlcov/index.html in a browser
```

## Installation

NEW!! - This project now uses a web based installer/setup similar to WordPress!

## Why?

I love WordPress and Drupal, but they can definitely be frustrating and have their own drawbacks. I used Django and it was a great toolset, but seemed like overkill for just building a basic website and made cloning websites and code bases a bit more difficult. So as I've been learning and working with Python more, I stumbled upon Flask, and completely fell in love.

## ToDo

See the [issues page](https://github.com/bderstine/WebsiteMixer-App-Base/issues) if you are interested in contributing or helping!

Thanks for stopping by and visiting!

-Brad
