from application import app

@app.route('/slack-invite/')
def slackinvite():
    return 'It worked!'

