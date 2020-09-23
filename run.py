from app.app import app
from app.settings import engine
import flask
from sqlalchemy.orm import sessionmaker

@app.route('/hello')
def main():
    return "Hello World!"

    
@app.route('/')
def root():
    return flask.redirect(flask.url_for('main'))

@app.route('/controller')
def controller():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    


if __name__ =='__main__':
    app.run(debug=True)