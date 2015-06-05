from application import app

@app.route('/test/')
def test():
    return 'It worked!'



