# README #

==Quick Start==

1. Create VM/VPS and update. I use Ubuntu 14.04 x64.

* apt-get update && apt-get upgrade
* reboot

2. Install dependencies:

* apt-get install vim git python-virtualenv python-dev python-mysqldb gcc

Optional: apt-get install apache2 libapache2-mod-wsgi php5 mysql-server php5-mysql

3. Clone and install websitemixer-app-base:

* git clone https://github.com/bderstine/WebsiteMixer-App-Base testapp
* cd testapp
* ./setup.sh

4. And follow instructions.

5. To run, use ./run.py to use port 5000 test server.
