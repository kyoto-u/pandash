from app.app import app
from app.settings import engine, app_url,app_login_url, cas_url, proxy_url
# from app.settings import cas_client
import flask
from sqlalchemy.orm import sessionmaker
from app.index import *
from pprint import pprint
from cas_client import CASClient
from flask import Flask, redirect, request, session, url_for
import logging
import requests

logging.basicConfig(level=logging.DEBUG)
app.secret_key ='pandash'


# url list
# 
# "/login" ログイン画面
# "/logout" ログアウト画面
# "/tasklist" 課題の一覧を取得
# "/tasklist/day/<str:day>" 曜日で絞り込み <day>にはmon,tue,wed,thu,friのいずれかが入る
# "/tasklist/course/<str:courceid>" 教科で絞り込み <courceid>にはデータベースで登録した教科idが入る
# "/"
# tasklistについては、末尾に　"/<int>/<int>"を追加すると課題の取り組み状況、締め切りまでの残り時間で絞り込み
# 詳細は関数参照
# 
# "/overview" 時間割表示
# 
# "/resourcelist" 授業資料一覧を取得
# "/resourcelist/course/<str:courseid>" 教科で絞り込み <courceid>にはデータベースで登録した教科idが入る
# 


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        ticket = request.args.get('ticket')
        cas_client = CASClient(cas_url, auth_prefix='')
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
                return redirect(url_for('proxy', ticket=ticket))
        if "logged-in" in session and session["logged-in"]:
            del(session['logged-in'])
        cas_login_url = cas_client.get_login_url(service_url=app_login_url)
        return redirect(cas_login_url)
    elif request.method == 'POST':
        print('pgt=')
        pgt = request.form
        print(pgt)
        return ''

@app.route('/login/proxy', methods=['GET'])
def proxy():
    s_ticket = request.args.get('ticket')
    cas_client = CASClient(cas_url,auth_prefix='',proxy_url=proxy_url)
    # cas_response = cas_client.perform_service_validate(
    #     ticket=s_ticket,
    #     service_url=app_login_url
    #     )
    # print(cas_response.data)
    return redirect(url_for('root'))

@app.route('/logout')
def logout():
    del(session['logged-in'])
    cas_client = CASClient(cas_url, proxy_url=proxy_url)
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
            add_resource(f'resource{i}-{j}','teacher1','/content/group/2020-888-N150-017/演義/',111,f'dummy{i}')
    
    
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
    sc_data=[]
    sa_data=[]
    sr_data=[]
    sa_data.append({'assignment_id':'assignmentid1', 'student_id':studentid, 'status':'未'})
    sa_data.append({'assignment_id':'assignmentid2', 'student_id':studentid, 'status':'未'})
    sa_data.append({'assignment_id':'assignmentid3', 'student_id':studentid, 'status':'未'})
    sa_data.append({'assignment_id':'assignmentid4', 'student_id':studentid, 'status':'未'})
    sa_data.append({'assignment_id':'assignmentid5', 'student_id':studentid, 'status':'未'})
    sa_data.append({'assignment_id':'assignmentid6', 'student_id':studentid, 'status':'未'})
    sa_data.append({'assignment_id':'assignmentid7', 'student_id':studentid, 'status':'未'})
    sc_data.append({"student_id":studentid,"course_id":"course1"})
    sc_data.append({"student_id":studentid,"course_id":"course2"})
    sc_data.append({"student_id":studentid,"course_id":"course3"})
    sc_data.append({"student_id":studentid,"course_id":"course4"})
    for i in range(30):
        sc_data.append({"student_id":studentid,"course_id":f"dummy{i}"})
        for j in range(10):
            sa_data.append({"assignment_id":f'dummyassignment{i}-{j}', "student_id":studentid, "status":'未'})
            sr_data.append({"resource_url":f"resource{i}-{j}","student_id":studentid,"status":0})
    sr_data.append({"resource_url":'url1', "student_id":studentid, "status":0})
    sr_data.append({"resource_url":'url2', "student_id":studentid, "status":0})
    sr_data.append({"resource_url":'url3', "student_id":studentid, "status":0})
    sr_data.append({"resource_url":'url4', "student_id":studentid, "status":0})
    sr_data.append({"resource_url":'url5', "student_id":studentid, "status":0})
    sr_data.append({"resource_url":'url6', "student_id":studentid, "status":0})
    sr_data.append({"resource_url":'url7', "student_id":studentid, "status":0})
    add_studentcourse(studentid,sc_data)
    add_student_assignment(studentid,sa_data)
    add_student_resource(studentid, sr_data)
    return ''
    


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
    search_condition = get_search_condition(show_only_unfinished, max_time_left, day=day)
    return flask.render_template('tasklist.htm', tasks=tasks, data=data, day=day, search_condition=search_condition)


@app.route('/tasklist/course/<courseid>/<int:show_only_unfinished>/<int:max_time_left>')
def tasklist_course(courseid,show_only_unfinished,max_time_left):
    studentid = "student1"
    tasks = get_tasklist(studentid ,courseid = courseid)
    tasks = sort_tasks(tasks, show_only_unfinished = show_only_unfinished, max_time_left = max_time_left)

    data ={"others":[]}
    data = setdefault_for_overview(studentid)
    search_condition = get_search_condition(show_only_unfinished, max_time_left, course=courseid)
    return flask.render_template('tasklist.htm', tasks=tasks, data=data, day='oth', search_condition=search_condition)

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
    search_condition = get_search_condition(show_only_unfinished, max_time_left)
    return flask.render_template('tasklist.htm', tasks=tasks, data=data, day='oth', search_condition=search_condition)

@app.route('/resourcelist/course/<courseid>')
def resource_course(courseid):
    studentid = 'student1'
    data = setdefault_for_overview(studentid, mode="resourcelist")
    resource = get_resource_list(studentid, course_id=courseid)
    coursename = get_coursename(courseid)
    resource_html = resource_arrange(resource[courseid], coursename, courseid)
    return flask.render_template('resources_sample.htm', html=resource_html, data=data)

@app.route('/resourcelist')
def resources_sample():
    studentid = "student1"
    courses = get_courses_to_be_taken(studentid)
    html = ""
    resource_list = get_resource_list(studentid, None)
    for c in courses:
        
        if resource_list[c.course_id] != []:
            html += resource_arrange(resource_list[c.course_id], c.coursename, c.course_id)
    data = setdefault_for_overview(studentid, mode='resourcelist')
    return flask.render_template('resources_sample.htm', html=html, data=data)

# 資料ページのダウンロード時のstatus変更
@app.route('/checkedclick')
def checkedclick():
    return 'checkedclick'

@app.route('/allclick')
def allclick():
    return 'allclick'

@app.route('/r_status_change', methods=['POST'])
def r_status_change():
    studentid = 'student1'
    r_links = request.json['r_links']
    update_resource_status(studentid, r_links)
    return 'success'

@app.route('/task_finish', methods=['POST'])
def task_finish():
    studentid = 'student1'
    task_id = request.json['task_id']
    update_task_status(studentid, task_id)
    return 'success'


@app.route('/pgtCallback', methods=['GET', 'POST'])
def pgtCallback():
    if request.method == 'GET':
        print(pgtCallback)
        pgtiou = request.args.get('pgtIou')
        pgtid = request.args.get('pgtid')
        print(pgtid)
        return redirect(url_for('root'))
    elif request.method == 'POST':
        pgt = request.form
        print(pgt)
        return ''


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
