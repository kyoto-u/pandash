from app.app import app
from app.settings import engine, app_login_url, cas_url
from app.settings import cas_client
import flask
from sqlalchemy.orm import sessionmaker
from app.index import *
from pprint import pprint
from cas_client import CASClient
from flask import Flask, redirect, request, session, url_for

app.secret_key ='pandash'


@app.route('/login')
def login():
    ticket = request.args.get('ticket')
    print(ticket)
    if ticket:
        try:
            cas_response = cas_client.perform_service_validate(
                ticket=ticket,
                service_url=app_login_url,
                )
        except:
            # CAS server is currently broken, try again later.
            return redirect(url_for('root'))
        if cas_response and cas_response.success:
            session['logged-in'] = True
            return redirect(url_for('root'))
    if "logged-in" in session and session["logged-in"]:
        del(session['logged-in'])
    cas_login_url = cas_client.get_login_url(service_url=app_login_url)
    return redirect(cas_login_url)

@app.route('/logout')
def logout():
    del(session['logged-in'])
    cas_logout_url = cas_client.get_logout_url(service_url=app_login_url)
    return redirect(cas_logout_url)

@app.route('/')
def root():
    if session.get('logged-in'):
        return 'You Are Logged In'
    else:
        return 'You Are Not Logged In'


@app.route('/hello')
def main():
    return "Hello World!"


# @app.route('/')
# def root():
#     return flask.redirect(flask.url_for('main'))


@app.route('/controller')
def controller():
    # ex
    add_instructor('instructor1', 'i_fullname', 'i_mailadress')
    add_assignment("assignmentid1", "url","課題1", "2020-10-30T01:55:00Z", "<p>説明<p>", 11111111111, 1111, "course1" )
    add_assignment("assignmentid2", "ur2","課題2", "2020-10-30T01:50:00Z", "<p>説明<p>", 11111111111, 1111, "course4" )
    add_assignment("assignmentid3", "ur3","課題3", "2020-11-01T01:52:00Z", "<p>説明<p>", 11111111111, 1111, "course4" )
    add_assignment("assignmentid4", "ur4","課題4", "2020-10-30T01:51:00Z", "<p>説明<p>", 11111111111, 1111, "course4" )
    add_assignment("assignmentid5", "ur5","課題5", "2020-10-30T01:53:00Z", "<p>説明<p>", 11111111111, 1111, "course2" )
    add_assignment("assignmentid6", "ur6","課題6", "2020-10-30T01:53:00Z", "<p>説明<p>", 11111111111, 1111, "course4" )
    add_assignment("assignmentid7", "ur7","課題7", "2020-10-30T01:53:00Z", "<p>説明<p>", 11111111111, 1111, "course4" )
    for i in range(30):
        add_course(f'dummy{i}', 'teacher1', f'[2020前期他他]ダミー{i}', 20200, f'thu{(i%5)+1}')
        for j in range(10):
            add_assignment(f"dummyassignment{i}-{j}", "url",f"課題{i}-{j}", "2020-10-30T01:53:00Z", "<p>説明<p>", 11111111111, 1111, f"dummy{i}" )
    
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

    return ''

@app.route('/controller_for_students/<studentid>')
def controller_for_students(studentid):
    add_student(studentid,'s_fullname')
    add_student_assignment(studentid,{'assignment_id':'assignmentid1', 'student_id':studentid, 'status':'未'})
    add_student_assignment(studentid,{'assignment_id':'assignmentid2', 'student_id':studentid, 'status':'未'})
    add_student_assignment(studentid,{'assignment_id':'assignmentid3', 'student_id':studentid, 'status':'未'})
    add_student_assignment(studentid,{'assignment_id':'assignmentid4', 'student_id':studentid, 'status':'未'})
    add_student_assignment(studentid,{'assignment_id':'assignmentid5', 'student_id':studentid, 'status':'未'})
    add_student_assignment(studentid,{'assignment_id':'assignmentid6', 'student_id':studentid, 'status':'未'})
    add_student_assignment(studentid,{'assignment_id':'assignmentid7', 'student_id':studentid, 'status':'未'})
    add_studentcourse(studentid, {"student_id":studentid,"course_id":"course1"})
    add_studentcourse(studentid, {"student_id":studentid,"course_id":"course2"})
    add_studentcourse(studentid, {"student_id":studentid,"course_id":"course3"})
    add_studentcourse(studentid, {"student_id":studentid,"course_id":"course4"})
    for i in range(30):
        add_studentcourse(studentid,f"dummy{i}")
        for j in range(10):
            add_student_assignment(f'dummyassignment{i}-{j}', studentid, '未')
    add_student_resource(studentid, {"resourceurl":'url1', "student_id":studentid, "status":'0'})
    add_student_resource(studentid, {"resourceurl":'url2', "student_id":studentid, "status":'0'})
    add_student_resource(studentid, {"resourceurl":'url3', "student_id":studentid, "status":'0'})
    add_student_resource(studentid, {"resourceurl":'url4', "student_id":studentid, "status":'0'})
    add_student_resource(studentid, {"resourceurl":'url5', "student_id":studentid, "status":'0'})
    add_student_resource(studentid, {"resourceurl":'url6', "student_id":studentid, "status":'0'})
    add_student_resource(studentid, {"resourceurl":'url7', "student_id":studentid, "status":'0'})
    


@app.route('/tasklist')
def tasklist_redirect():
    return flask.redirect(flask.url_for('tasklist',show_only_unfinished = 0,max_time_left = 3))

@app.route('/overview')
def overview():
    studentid = "student1"
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
    data = setdefault_for_overview(studentid)
    tasks = get_tasklist(studentid, mode=1)
    data = task_arrange_for_overview(tasks,data)

    days =["mon", "tue", "wed", "thu", "fri"]
    for day in days:
        for i in range(5):
            data[day+str(i+1)]["tasks"] = sort_tasks(data[day+str(i+1)]["tasks"],show_only_unfinished = 1)
    data.setdefault("others",[])
    for i in range(len(data["others"])):
        data["others"][i]["tasks"] = sort_tasks(data["others"][i]["tasks"],show_only_unfinished = 1)
    
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
    tasks = sort_tasks(tasks, show_only_unfinished = show_only_unfinished, max_time_left = max_time_left)
    data ={"others":[]}
    data = setdefault_for_overview(studentid)
    return flask.render_template('tasklist.htm', tasks=tasks, data=data)


@app.route('/tasklist/course/<courseid>/<int:show_only_unfinished>/<int:max_time_left>')
def tasklist_course(courseid,show_only_unfinished,max_time_left):
    studentid = "student1"
    tasks = get_tasklist(studentid ,courseid = courseid)
    tasks = sort_tasks(tasks, show_only_unfinished = show_only_unfinished, max_time_left = max_time_left)

    data ={"others":[]}
    data = setdefault_for_overview(studentid)
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
    data = setdefault_for_overview(studentid)
    return flask.render_template('tasklist.htm', tasks=tasks, data=data)

@app.route('/resourcelist/course/<courseid>')
def resource_course(courseid):
    studentid = 'student1'
    data = setdefault_for_overview(studentid, mode="resourcelist")
    resource = get_resource_list(studentid, course_id=courseid)
    coursename = get_coursename(courseid)
    resource_html = resource_arrange(resource, coursename)
    return flask.render_template('resources_sample.htm', html=resource_html, data=data)

@app.route('/resourcelist')
def resources_sample():
    studentid = "student1"
    course_ids = get_courseids(studentid)
    html = ""
    for c_id in course_ids:
        html = html + resource_arrange(get_resource_list(studentid, c_id[0]), get_coursename(c_id[0]))
    data = setdefault_for_overview(studentid, mode='resourcelist')
    return flask.render_template('resources_sample.htm', html=html, data=data)


if __name__ == '__main__':
    app.run(debug=True)
