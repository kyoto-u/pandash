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
    # ex
    # add_student('student1','s_fullname1')
    # add_assignment('assignment1', 'https://panda...', '課題１', '2020-10-06T01:55:00Z', '<p>説明</p>')
    # add_course('course1', 'teacher1', 'コース１', '火5')
    # add_instructor('instructor1', 'i_fullname', 'i_mailadress')
    # add_enrollment('assignmentid', 'studentid', 'courseid', 'status')
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