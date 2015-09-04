from application import app
from application.functions import *

@app.route('/landing-test/')
def landingtest():
    s = getSettings()
    return s['landing-test']

