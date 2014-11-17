from flask import Flask, request, redirect, abort, render_template, jsonify
from app import app

@app.route('/')
def home():
    return render_template('index.html')

#######################################################################
# Error handlers

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

