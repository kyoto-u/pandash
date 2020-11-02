from app.app import app
from app.settings import engine
import flask
from sqlalchemy.orm import sessionmaker
from app.index import *
from pprint import pprint


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
    add_instructor('instructor1', 'i_fullname', 'i_mailadress')
    add_assignment("assignmentid1", "url","課題1", "2020-10-30T01:55:00Z", "<p>説明<p>", 11111111111, 1111, "course1" )
    add_assignment("assignmentid2", "ur2","課題2", "2020-10-30T01:50:00Z", "<p>説明<p>", 11111111111, 1111, "course4" )
    add_student_assignment('assignmentid1', 'student1', '未')
    add_student_assignment('assignmentid2', 'student1', '未')
    add_studentcourse("student1","course1")
    add_studentcourse("student1","course2")
    add_studentcourse("student1","course3")
    add_studentcourse("student1","course4")
    add_course('course1', 'teacher1', 'コース1', 20200, 'wed2')
    add_course('course2', 'teacher1', 'コース2', 20200, 'mon2')
    add_course('course3', 'teacher1', '[2020前期月1]線形代数学', 20200, 'mon1')
    add_course('course4', 'teacher1', '[2020前期月2]微分積分学', 20200, 'mon2')
    add_resource('url1', '資料１', '/content/group/2020-888-N150-017/演義/演義動画/', 111, 'course1')
    add_resource('url2', '資料２', '/content/group/2020-888-N150-017/演義/演義動画/', 222, 'course1')
    add_resource('url3', '資料３', '/content/group/2020-888-N150-017/演義/演義資料/', 222, 'course1')
    add_resource('url4', '資料４', '/content/group/2020-888-N150-017/演義/演義動画/詳細/', 222, 'course1')
    add_resource('url5', '資料５', '/content/group/2020-888-N150-017/講義/講義動画/', 222, 'course1')
    add_resource('url6', '資料６', '/content/group/2020-888-N150-017/講義/講義ノート/', 222, 'course1')
    add_resource('url7', '資料７', '/content/group/2020-888-N150-017/演義/演義動画/', 222, 'course2')
    add_student_resource('url1', 'student1', '未')
    add_student_resource('url2', 'student1', '未')
    add_student_resource('url3', 'student1', '未')
    add_student_resource('url4', 'student1', '未')
    add_student_resource('url5', 'student1', '未')
    add_student_resource('url6', 'student1', '未')
    add_student_resource('url7', 'student1', '未')


    pprint(resource_arrange(get_resource_list('student1', 'course1'), 'コース名'))
    # get_tasklist('student1')
    return ''

@app.route('/tasklist')
def tasklist_redirect():
    return flask.redirect(flask.url_for('tasklist',show_only_unfinished = 0,max_time_left = 3))

@app.route('/overview')
def overview():
    studentid = "student1"
    tasks = get_tasklist(studentid, mode=1)
    # tasks = [
    #     {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題1', 'status':'未', 'time_left': "あと50分", 'deadline':'2020-10-30T02:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題2', 'status':'未', 'time_left':'あと2時間', 'deadline':'2020-10-30T00:50:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題3', 'status':'終了', 'time_left':'', 'deadline':'2020-10-29T23:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期火1]英語リーディング', 'classschedule':'tue1','taskname':'課題4', 'status':'未', 'time_left':'あと3日', 'deadline':'2020-11-02T03:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題5', 'status':'済', 'time_left':'あと1時間', 'deadline':'2020-10-30T01:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月1]英語ライティングリスニング', 'classschedule':'mon1','taskname':'課題6', 'status':'済', 'time_left':'あと1日', 'deadline':'2020-10-31T02:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月1]英語ライティングリスニング', 'classschedule':'mon1','taskname':'課題7', 'status':'未', 'time_left':'あと1日', 'deadline':'2020-10-31T01:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月1]英語ライティングリスニング', 'classschedule':'mon1','taskname':'課題8', 'status':'未', 'time_left':'あと1日', 'deadline':'2020-10-31T00:00:00Z','instructions':'なし'}
    #     ]
    data = task_arrange_for_overview(tasks)
    data = setdefault_for_overview(data, studentid)
    
    
    return flask.render_template('overview.htm',data = data)

@app.route('/tasklist/day/<day>')
def tasklist_day_redirect(day):
    return flask.redirect(flask.url_for('tasklist_day', day = day,show_only_unfinished = 0,max_time_left = 3))

@app.route('/tasklist/course/<courseid>')
def tasklist_course_redirect(courseid):
    return flask.redirect(flask.url_for('tasklist_course', courseid = courseid,show_only_unfinished = 0,max_time_left = 3))

@app.route('/tasklist/day/<day>/<int:show_only_unfinished>/<int:max_time_left>')
def tasklist_day(day,show_only_unfinished,max_time_left):
    studentid = "student1"
    tasks = get_tasklist(studentid ,day = day)
    # tasks = [
    #     {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題1', 'status':'未', 'time_left': "あと50分", 'deadline':'2020-10-30T00:50:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題2', 'status':'未', 'time_left':'あと2時間', 'deadline':'2020-10-30T02:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題3', 'status':'終了', 'time_left':'', 'deadline':'2020-10-29T23:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期火1]英語リーディング', 'classschedule':'Tue1','taskname':'課題4', 'status':'未', 'time_left':'あと3日', 'deadline':'2020-11-02T03:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題5', 'status':'済', 'time_left':'あと1時間', 'deadline':'2020-10-30T01:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月1]英語ライティングリスニング', 'classschedule':'mon1','taskname':'課題6', 'status':'済', 'time_left':'あと1日', 'deadline':'2020-10-31T01:00:00Z','instructions':'なし'}
    #     ]
    tasks = sort_tasks(tasks, show_only_unfinished = show_only_unfinished, max_time_left = max_time_left)
    data ={"others":[]}
    data = setdefault_for_overview(data,studentid)
    return flask.render_template('tasklist.htm', tasks=tasks, data=data)


@app.route('/tasklist/course/<courseid>/<int:show_only_unfinished>/<int:max_time_left>')
def tasklist_course(courseid,show_only_unfinished,max_time_left):
    studentid = "student1"
    tasks = get_tasklist(studentid ,courseid = courseid)
    # tasks = [
    #     {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題1', 'status':'未', 'time_left': "あと50分", 'deadline':'2020-10-30T00:50:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題2', 'status':'未', 'time_left':'あと2時間', 'deadline':'2020-10-30T02:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題3', 'status':'終了', 'time_left':'', 'deadline':'2020-10-29T23:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期火1]英語リーディング', 'classschedule':'Tue1','taskname':'課題4', 'status':'未', 'time_left':'あと3日', 'deadline':'2020-11-02T03:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題5', 'status':'済', 'time_left':'あと1時間', 'deadline':'2020-10-30T01:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月1]英語ライティングリスニング', 'classschedule':'mon1','taskname':'課題6', 'status':'済', 'time_left':'あと1日', 'deadline':'2020-10-31T01:00:00Z','instructions':'なし'}
    #     ]
    tasks = sort_tasks(tasks, show_only_unfinished = show_only_unfinished, max_time_left = max_time_left)

    data ={"others":[]}
    data = setdefault_for_overview(data,studentid)
    return flask.render_template('tasklist.htm', tasks=tasks, data=data)

@app.route('/tasklist/<int:show_only_unfinished>/<int:max_time_left>')
def tasklist(show_only_unfinished,max_time_left):
    studentid = "student1"
    tasks = get_tasklist(studentid)
    # tasks = [
    #     {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題1', 'status':'未', 'time_left': "あと50分", 'deadline':'2020-10-30T00:50:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題2', 'status':'未', 'time_left':'あと2時間', 'deadline':'2020-10-30T02:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題3', 'status':'終了', 'time_left':'', 'deadline':'2020-10-29T23:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期火1]英語リーディング', 'classschedule':'Tue1','taskname':'課題4', 'status':'未', 'time_left':'あと3日', 'deadline':'2020-11-02T03:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題5', 'status':'済', 'time_left':'あと1時間', 'deadline':'2020-10-30T01:00:00Z','instructions':'なし'},
    #     {'subject':'[2020前期月1]英語ライティングリスニング', 'classschedule':'mon1','taskname':'課題6', 'status':'済', 'time_left':'あと1日', 'deadline':'2020-10-31T01:00:00Z','instructions':'なし'}
    #     ]
    tasks = sort_tasks(tasks, show_only_unfinished = show_only_unfinished, max_time_left = max_time_left)

    data ={"others":[]}
    data = setdefault_for_overview(data,studentid)
    return flask.render_template('tasklist.htm', tasks=tasks, data=data)


if __name__ == '__main__':
    app.run(debug=True)
