from app.app import app
from app.settings import engine
import flask
from sqlalchemy.orm import sessionmaker
from app.index import *

@app.route('/hello')
def main():
    return "Hello World!"

    
@app.route('/')
def root():
    return flask.redirect(flask.url_for('main'))

@app.route('/controller')
def controller():
    student_add('bb','cc')
    return ''
    
@app.route('/tasklist')
def tasklist():
    tasks = [
        {'subject':'線形代数', 'taskname':'課題1', 'status':'未完了', 'time_left':'30', 'deadline':'0930'},
        {'subject':'線形代数', 'taskname':'課題1', 'status':'未完了', 'time_left':'30', 'deadline':'0930'},
        {'subject':'線形代数', 'taskname':'課題1', 'status':'未完了', 'time_left':'30', 'deadline':'0930'},
        {'subject':'線形代数', 'taskname':'課題1', 'status':'未完了', 'time_left':'30', 'deadline':'0930'},
        {'subject':'線形代数', 'taskname':'課題1', 'status':'未完了', 'time_left':'30', 'deadline':'0930'},
        {'subject':'線形代数', 'taskname':'課題1', 'status':'未完了', 'time_left':'30', 'deadline':'0930'}           
        ]
    return flask.render_template('tasklist.htm',tasks=tasks)


if __name__ =='__main__':
    app.run(debug=True)