#!/bin/sh
export FLASK_APP=websitemixer
export FLASK_ENV=development

#flask init-db
flask run --host=0.0.0.0
