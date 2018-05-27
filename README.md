# WebsiteMixer-App-Base
### A Python/Flask alternative to WordPress & Drupal

See the [Changelog](http://websitemixer.com/changelog/) for more details.   

## Quick Start (Ubuntu 18.04)
Tested on: Ubuntu 18.04, Python 3.6.5

$ sudo apt-get update && sudo apt-get upgrade

$ sudo apt-get install python3-pip

$ cd /srv

$ sudo git clone https://github.com/bderstine/WebsiteMixer-App-Base

$ sudo chown ubuntu:ubuntu WebsiteMixer-App-Base -R

$ cd WebsiteMixer-App-Base

$ sudo pip3 install -r requirements.txt

$ ./run.py
 * Serving Flask app "websitemixer" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: xxx-xxx-xxx

## Quick Start (Ubuntu 16.04)
Tested on: Ubuntu 16.04.3 LTS, Python  3.6.3

$ sudo apt-get update && sudo apt-get upgrade

#### For Ubuntu 16.04, need to add PPA for Python 3.6

$ sudo add-apt-repository ppa:jonathonf/python-3.6

$ sudo apt-get update

$ sudo apt-get install python3.6

#### Pip for Python 3.6 has to be installed manually, no package...

$ curl https://bootstrap.pypa.io/get-pip.py | sudo python3.6

#### Coming with Ubuntu 18.04, Python 3.6 will be the default!

$ cd /srv

$ sudo git clone https://github.com/bderstine/WebsiteMixer-App-Base

$ sudo chown ubuntu:ubuntu WebsiteMixer-App-Base -R

$ cd WebsiteMixer-App-Base

$ sudo pip3.6 install -r requirements.txt

$ ./run.py
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: xxx-xxx-xxx

## Quick Start (RHEL 7.4)
Tested on: RHEL 7.4, Python 3.6.3

$ sudo yum update

$ sudo yum install git wget

$ sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

$ sudo yum install https://centos7.iuscommunity.org/ius-release.rpm

$ sudo yum install python36u python36u-pip

$ cd /srv

$ sudo git clone https://github.com/bderstine/WebsiteMixer-App-Base

$ sudo chown ec2-user:ec2-user WebsiteMixer-App-Base -R

$ cd WebsiteMixer-App-Base/

$ sudo pip-3.6 install -r requirements.txt

$ ./run.py
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: xxx-xxx-xxx

## Quick Start (Linux AMI)
Tested on: Linux AMI 2017.09.1, Python 3.6.2

$ sudo yum update

$ sudo yum install python36 python36-pip git

$ cd /srv

$ sudo git clone https://github.com/bderstine/WebsiteMixer-App-Base

$ sudo chown ec2-user:ec2-user WebsiteMixer-App-Base/ -R

$ cd WebsiteMixer-App-Base

$ sudo pip-3.6 install -r requirements.txt

$ ./run.py
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: xxx-xxx-xxx

## Installation

NEW!! - This project now uses a web based installer/setup similar to WordPress! 

## Why?

I love WordPress and Drupal, but they can definitely be frustrating and have their own drawbacks. I used Django and it was a great toolset, but seemed like overkill for just building a basic website and made cloning websites and code bases a bit more difficult. So as I've been learning and working with Python more, I stumbled upon Flask, and completely fell in love.

## To do

See the [issues page](https://github.com/bderstine/WebsiteMixer-App-Base/issues) if you're interested in contributing or helping!

Thanks for stopping by and visiting! 

-Brad

