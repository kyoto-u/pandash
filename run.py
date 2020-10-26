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
    add_student('student1','s_fullname1')
    add_assignment('assignment3', 'https://panda...', '課題3', '2020-10-06T01:55:00Z', '<p>説明</p>', 11111111111)
    add_course('course1', 'teacher1', 'コース１', '火5')
    # add_instrucstor('instructor1', 'i_fullname', 'i_mailadress')
    add_enrollment('assignment3', 'student1', 'course1', '未')
    return ''

@app.route('/tasklist')
def tasklist_all():
    return flask.redirect(flask.url_for('tasklist',show_only_unfinished = 0,max_time_left = 3))

@app.route('/overview')
def overview():
    tasks = [
        {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題1', 'status':'未', 'time_left': "あと50分", 'deadline':'2020-10-30T02:00:00Z','instructions':'なし'},
        {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題2', 'status':'未', 'time_left':'あと2時間', 'deadline':'2020-10-30T00:50:00Z','instructions':'なし'},
        {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題3', 'status':'終了', 'time_left':'', 'deadline':'2020-10-29T23:00:00Z','instructions':'なし'},
        {'subject':'[2020前期火1]英語リーディング', 'classschedule':'tue1','taskname':'課題4', 'status':'未', 'time_left':'あと3日', 'deadline':'2020-11-02T03:00:00Z','instructions':'なし'},
        {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題5', 'status':'済', 'time_left':'あと1時間', 'deadline':'2020-10-30T01:00:00Z','instructions':'なし'},
        {'subject':'[2020前期月1]英語ライティングリスニング', 'classschedule':'mon1','taskname':'課題6', 'status':'済', 'time_left':'あと1日', 'deadline':'2020-10-31T02:00:00Z','instructions':'なし'},
        {'subject':'[2020前期月1]英語ライティングリスニング', 'classschedule':'mon1','taskname':'課題7', 'status':'未', 'time_left':'あと1日', 'deadline':'2020-10-31T01:00:00Z','instructions':'なし'},
        {'subject':'[2020前期月1]英語ライティングリスニング', 'classschedule':'mon1','taskname':'課題8', 'status':'未', 'time_left':'あと1日', 'deadline':'2020-10-31T00:00:00Z','instructions':'なし'}
        ]
    data = task_arrange_for_overview(tasks)
    days =["mon", "tue", "wed", "thu", "fri"]
    for day in days:
        for i in range(5):
            data.setdefault(day+str(i+1),{"subject": "", "shortname": "", "searchURL": "","tasks": []})
            data[day+str(i+1)]["tasks"] = sort_tasks(data[day+str(i+1)]["tasks"])
    data.setdefault("others",[])
    for subject in data["others"]:
        subject["tasks"] = sort_tasks(subject["tasks"])
    
    
    return flask.render_template('overview.htm')

@app.route('/tasklist/<int:show_only_unfinished>/<int:max_time_left>')
def tasklist(show_only_unfinished,max_time_left):
    studentid = "student1"
    tasks = get_tasklist(studentid)
    tasks = [
        {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題1', 'status':'未', 'time_left': "あと50分", 'deadline':'2020-10-30T00:50:00Z','instructions':'なし'},
        {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題2', 'status':'未', 'time_left':'あと2時間', 'deadline':'2020-10-30T02:00:00Z','instructions':'なし'},
        {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題3', 'status':'終了', 'time_left':'', 'deadline':'2020-10-29T23:00:00Z','instructions':'なし'},
        {'subject':'[2020前期火1]英語リーディング', 'classschedule':'Tue1','taskname':'課題4', 'status':'未', 'time_left':'あと3日', 'deadline':'2020-11-02T03:00:00Z','instructions':'なし'},
        {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題5', 'status':'済', 'time_left':'あと1時間', 'deadline':'2020-10-30T01:00:00Z','instructions':'なし'},
        {'subject':'[2020前期月1]英語ライティングリスニング', 'classschedule':'mon1','taskname':'課題6', 'status':'済', 'time_left':'あと1日', 'deadline':'2020-10-31T01:00:00Z','instructions':'なし'}
        ]
    task_arrange_for_overview(tasks)
    tasks = sort_tasks(tasks, show_only_unfinished = show_only_unfinished, max_time_left = max_time_left)

    return flask.render_template('tasklist.htm', tasks=tasks)


if __name__ == '__main__':
    app.run(debug=True)
