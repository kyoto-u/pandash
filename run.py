from app.app import app
import flask

@app.route('/hello')
def main():
    return "Hello World!"

    
@app.route('/')
def root():
    return flask.redirect(flask.url_for('main'))



if __name__ =='__main__':
    app.run(debug=True)