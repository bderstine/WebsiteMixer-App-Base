from application import app

@app.route('/landing-test/')
def landingtest():
    return 'It worked!'
