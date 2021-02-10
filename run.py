from app.app import app
from app.settings import engine,app_url,app_logout_url,app_login_url,cas_url,proxy_url,proxy_callback,api_url
from app.settings import cas_client
import flask
from sqlalchemy.orm import sessionmaker
from app.index import *
from pprint import pprint
from cas_client import CASClient
from flask import Flask, redirect, request, session, url_for
import logging
import requests
import datetime
import time

logging.basicConfig(level=logging.INFO)
app.secret_key ='pandash'

global pgtids
global redirect_pages

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
                pgtiou= cas_response.data['proxyGrantingTicket']
                return redirect(url_for('proxy', pgtiou=pgtiou))
        if "logged-in" in session and session["logged-in"]:
            del(session['logged-in'])
        if "student_id" in session:
            # ログイン後のページを指定しておく
            redirect_page = request.args.get('page')
            if not redirect_page:
                redirect_page =""
            redirect_pages[session['student_id']] = redirect_page
        cas_login_url = cas_client.get_login_url(service_url=app_login_url)
        return redirect(cas_login_url)
    elif request.method == 'POST':
        pgt = request.form
        return ''

@app.route('/login/proxy/<pgtiou>', methods=['GET'])
def proxy(pgtiou=None):
    pgtid = pgtids[pgtiou]
    del(pgtids[pgtiou])
    cas_response = cas_client.perform_proxy(proxy_ticket=pgtid)
    proxy_ticket = cas_response.data.get('proxyTicket')
    # return redirect(url_for('proxyticket', ticket=proxy_ticket))
    # 時間かかる通知を行う
    return flask.render_template('loading.htm', ticket=proxy_ticket)

@app.route('/proxyticket', methods=["GET"])
def proxyticket():
    ticket = request.args.get('ticket')
    start_time = time.perf_counter()
    show_only_unfinished = 0
    if ticket:
        ses = requests.Session()
        api_response = ses.get(f"{proxy_callback}?ticket={ticket}")
        if api_response.status_code == 200:
            user=get_user_json(ses)
            student_id = user.get('id')
            fullname = user.get('displayName')
            session["student_id"] = student_id
            now = now = floor(time.time())
            studentdata = get_student(student_id)
            need_to_update_sitelist = 1
            if studentdata:
                if studentdata.show_already_due==0:show_only_unfinished=1
                need_to_update_sitelist = studentdata.need_to_update_sitelist
                last_update = studentdata.last_update
                if need_to_update_sitelist:
                    add_student(student_id, fullname,last_update= now, last_update_subject= now, language = studentdata.language)
                else:
                    add_student(student_id, fullname,last_update= now, last_update_subject= studentdata.last_update_subject, language = studentdata.language)
            else:
                last_update = 0
                add_student(student_id, fullname,last_update= now, last_update_subject= now)
            get_data_from_api_and_update(student_id,ses,now,last_update,0)
            if need_to_update_sitelist == 1:
                get_data_from_api_and_update(student_id,ses,now,0,1)
            if student_id !="":
                update_student_needs_to_update_sitelist(student_id)
            logging.info(f"TIME {student_id}:{time.perf_counter()-start_time}")
    
    if 'student_id' in session and session['student_id'] in redirect_pages:
        redirect_page = redirect_pages[session['student_id']]
        redirect_page = app_url + "/" + redirect_page
        if re.match(app_login_url,redirect_page):
            logging.info(f"Requested redirect '{redirect_page}' is invalid because it is login page")
        elif redirect_page == app_url + "/":
            logging.info(f"Requested redirect '{redirect_page}' is invalid because it is portal page")
        else:
            return flask.redirect(redirect_page)
    return flask.redirect(flask.url_for('tasklist',show_only_unfinished=show_only_unfinished,max_time_left = 3))

@app.route('/logout')
def logout():
    if "logged-in" in session and session["logged-in"]:
        del(session['logged-in'])
    if "student_id" in session and session["student_id"]:
        del(session['student_id'])
    cas_logout_url = cas_client.get_logout_url(service_url=app_logout_url)
    return redirect(cas_logout_url)

@app.route('/')
def root():
    if session.get('logged-in'):
        return redirect(url_for("login"))
    else:
        return flask.render_template('welcome.htm')


@app.route('/hello')
def main():
    return "Hello World!"

@app.route('/faq')
def faq():
    return flask.render_template("faq.htm")

@app.route('/updatelog')
def update():
    return flask.render_template("update.htm")

@app.route('/tutrial')
def tutrial():
    return flask.render_template("_tutrial.htm")


@app.route('/help/<page>')
def help(page):
    #2021/01/14 Shinji Akayama: 参照するhtmlが間違っていたので修正しました。FAQ_{page}は完全なhtmlではありません
    return flask.render_template(f"_flexible_help_{page}.htm")

@app.route('/option', methods=['GET'])
def option():
    studentid = session.get('student_id')
    if studentid:
        data ={"others":[]}
        studentdata = get_student(studentid)
        data = setdefault_for_overview(studentid)
        return flask.render_template(f"option.htm",data=data, show_already_due=studentdata.show_already_due)
    else:
        return redirect(url_for('login'))

@app.route('/update_subject')
def update_subject():
    studentid = session.get('student_id')
    if studentid:
        update_student_needs_to_update_sitelist(studentid,need_to_update_sitelist=1)
        return redirect(url_for('login',page='option'))
    else:
        return redirect(url_for('login'))



# @app.route('/')
# def root():
#     return flask.redirect(flask.url_for('main'))


@app.route('/controller')
def controller():
    # 現行のバージョンでは使えなくなりました
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
    crs_data=[]
    asm_data=[]
    res_data=[]
    for i in range(30):
        sc_data.append({"student_id":studentid,"course_id":f"dummy{i}"})
        crs_data.append({"course_id":f"dummy{i}","instructor_id":"instructor1", "coursename":f'[2020前期他他]ダミー{i}', "yearsemester":20200, "classschedule":f'thu{(i%5)+1}'})
        for j in range(10):
            sa_data.append({"sa_id":f"{studentid}:dummyassignment{i}-{j}", "assignment_id":f'dummyassignment{i}-{j}', "student_id":studentid, "status":'未'})
            asm_data.append({"assignment_id":f'dummyassignment{i}-{j}', "url":"url","title":f"課題{i}-{j}", "limit_at":"2020-10-30T01:50:00Z", "instructions":"<p>説明<p>", "time_ms":11111111111, "modifieddate":1111, "course_id":f"dummy{i}"})
            sr_data.append({"resource_url":f"resource{i}-{j}","student_id":studentid,"status":0})
            res_data.append({"resource_url":f"resource{i}-{j}", "title":f'資料{i}-{j}', "container":'/content/group/2020-888-N150-017/演義/', "modifieddate":222, "course_id":f"dummy{i}"})
    add_studentcourse(studentid,sc_data)
    add_student_assignment(studentid,sa_data, 0)
    add_student_resource(studentid, sr_data)
    add_course(studentid, crs_data, 0)
    add_assignment(studentid, asm_data, 0)
    add_resource(studentid, res_data, 0)
    return ''
    


@app.route('/tasklist')
def tasklist_redirect():
    return flask.redirect(flask.url_for('tasklist',show_only_unfinished = 0,max_time_left = 3))

@app.route('/overview')
def overview():
    studentid = session.get('student_id')
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
    if studentid:
        # 課題の最終更新時間を取得
        studentdata = get_student(studentid)
        if studentdata == None:
            # なければstudentの記録がないことになるので一度ログインへ
            return redirect(url_for('login'))
        last_update= str(datetime.datetime.fromtimestamp(studentdata.last_update,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
        logging.debug(f"last update = {last_update}\npage = overview")
        data = setdefault_for_overview(studentid)
        tasks = get_tasklist(studentid, show_only_unfinished=1, mode=1)
        data = task_arrange_for_overview(tasks,data)

        days =["mon", "tue", "wed", "thu", "fri"]
        for day in days:
            for i in range(5):
                data[day+str(i+1)]["tasks"] = sort_tasks(data[day+str(i+1)]["tasks"],show_only_unfinished = 1)
        data.setdefault("others",[])
        for i in range(len(data["others"])):
            data["others"][i]["tasks"] = sort_tasks(data["others"][i]["tasks"],show_only_unfinished = 1)
        return flask.render_template('overview.htm',data = data,last_update=last_update)
    else:
        return redirect(url_for('login'))

@app.route('/tasklist/day/<day>')
def tasklist_day_redirect(day):
    return flask.redirect(flask.url_for('tasklist_day', day=day, show_only_unfinished = 0,max_time_left = 3))

@app.route('/tasklist/course/<courseid>')
def tasklist_course_redirect(courseid):
    return flask.redirect(flask.url_for('tasklist_course', courseid=courseid, show_only_unfinished = 0,max_time_left = 3))

@app.route('/tasklist/day/<day>/<int:show_only_unfinished>/<int:max_time_left>')
def tasklist_day(day,show_only_unfinished,max_time_left):
    return tasklist_general(show_only_unfinished,max_time_left, day=day)


@app.route('/tasklist/course/<courseid>/<int:show_only_unfinished>/<int:max_time_left>')
def tasklist_course(courseid,show_only_unfinished,max_time_left):
    return tasklist_general(show_only_unfinished,max_time_left, courseid = courseid)

@app.route('/tasklist/<int:show_only_unfinished>/<int:max_time_left>')
def tasklist(show_only_unfinished,max_time_left):
    return tasklist_general(show_only_unfinished,max_time_left)

@app.route('/resourcelist/course/<courseid>')
def resource_course(courseid):
    return resourcelist_general(courseid = courseid)

@app.route('/resourcelist/day/<day>')
def resource_day(day):
    return resourcelist_general(day = day)

@app.route('/resourcelist')
def resources_sample():
    return resourcelist_general()

@app.route('/ical')
def ical():
    studentid = session.get('student_id')
    data = setdefault_for_overview(studentid)
    return flask.render_template('coming_soon.htm',data=data)


# 資料ページのダウンロード時のstatus変更
@app.route('/checkedclick')
def checkedclick():
    return 'checkedclick'

@app.route('/allclick')
def allclick():
    return 'allclick'

@app.route('/r_status_change', methods=['POST'])
def r_status_change():
    studentid = session.get('student_id')
    if studentid:
        r_links = request.json['r_links']
        update_resource_status(studentid, r_links)
        return 'success'
    else:
        return 'failed'

@app.route('/task_finish', methods=['POST'])
def task_finish():
    studentid = session.get('student_id')
    if studentid:
        task_id = request.json['task_id']
        update_task_status(studentid, task_id)
        return 'success'
    else:
        return 'failed'

@app.route('/task_unfinish', methods=['POST'])
def task_unfinish():
    studentid = session.get('student_id')
    if studentid:
        task_id = request.json['task_id']
        update_task_status(studentid, task_id, mode=1)
        return 'success'
    else:
        return 'failed'

@app.route('/task_clicked', methods=['POST'])
def task_clicked():
    studentid = session.get('student_id')
    if studentid:
        task_ids = request.json['task_ids']
        update_task_clicked_status(studentid, task_ids)
        return 'success'
    else:
        return 'failed'

@app.route('/settings_change', methods=['POST'])
def settings_change():
    studentid = session.get('student_id')
    if studentid:
        show_already_due = request.json['show_already_due']
        update_student_show_already_due(show_already_due)
        return 'success'
    else:
        return 'failed'

@app.route('/pgtCallback', methods=['GET', 'POST'])
def pgtCallback():
    if request.method == 'GET':
        pgtiou = request.args.get('pgtIou')
        pgtid = request.args.get('pgtId')
        pgtids[pgtiou] = pgtid
        return ''
    elif request.method == 'POST':
        pgt = request.form
        return ''


def resourcelist_general(day = None,courseid = None):
    studentid = session.get('student_id')
    if studentid:
        # 課題の最終更新時間を取得
        studentdata = get_student(studentid)
        if studentdata == None:
            # なければstudentの記録がないことになるので一度ログインへ
            return redirect(url_for('login'))
        last_update= str(datetime.datetime.fromtimestamp(studentdata.last_update,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
        logging.debug(f"last update = {last_update}\npage = resourcelist")
        numofcourses = 0
        courses = get_courses_to_be_taken(studentid)
        html = ""
        resource_list = get_resource_list(studentid, course_id = courseid, day=day)
        for c in courses:
            if resource_list[c.course_id] != []:
                numofcourses += 1
                html += resource_arrange(resource_list[c.course_id], c.coursename, c.course_id)
        data = setdefault_for_overview(studentid, mode='resourcelist')

        if courseid != None:
            return flask.render_template('resources_sample.htm', html=html, data=data, numofcourses=1, last_update=last_update)
        if day != None:
            return flask.render_template('resources_sample.htm', html=html, data=data, day=day, numofcourses=numofcourses, last_update=last_update)
        else:
            return flask.render_template('resources_sample.htm', html=html, data=data, numofcourses=numofcourses, last_update=last_update)
    else:
        return redirect(url_for('login'))

def tasklist_general(show_only_unfinished,max_time_left,day = None,courseid = None):
    studentid = session.get('student_id')
    if studentid:
        # 課題の最終更新時間を取得
        studentdata = get_student(studentid)
        if studentdata == None:
            # なければstudentの記録がないことになるので一度ログインへ
            return redirect(url_for('login'))
        last_update= str(datetime.datetime.fromtimestamp(studentdata.last_update,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
        logging.debug(f"last update = {last_update}\npage = tasklist")
        if courseid != None:
            tasks = get_tasklist(studentid,courseid=courseid)
        elif day != None:
            tasks = get_tasklist(studentid,day=day)
        else:
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
        unfinished_task_num=sum((i["status"] == "未" for i in tasks))
        logging.info(f"studentid={studentid}の未完了課題:{unfinished_task_num}個")
        data ={"others":[]}
        data = setdefault_for_overview(studentid)
        if courseid != None:
            search_condition = get_search_condition(show_only_unfinished, max_time_left, course=courseid)
        elif day != None:
            search_condition = get_search_condition(show_only_unfinished, max_time_left, day=day)
            return flask.render_template(
                'tasklist.htm',
                tasks = tasks,
                data = data,
                day = day,
                search_condition = search_condition,
                unfinished_task_num = unfinished_task_num,
                last_update = last_update)
        else:
            search_condition = get_search_condition(show_only_unfinished, max_time_left)
        return flask.render_template(
            'tasklist.htm',
            tasks = tasks,
            data = data,
            day = 'oth',
            search_condition = search_condition,
            unfinished_task_num = unfinished_task_num,
            last_update = last_update)
    else:
        return redirect(url_for('login'))


@app.route('/ContactUs', methods=['GET', 'POST'])
def forum():
    studentid = session.get('student_id')
    if studentid:
        data = setdefault_for_overview(studentid)
        if request.method == 'GET':
            return flask.render_template('ContactUs.htm', error=False, data=data)
        elif request.method == 'POST':
            try:
                title = request.form["title"]
                contents = request.form["contents"]
                # msg = f"""---FORUM---
                #     STUDENT: {studentid},
                #     TITLE: {title},
                #     CONTENTS: {contents}
                #     --------------"""
                msg = add_forum(studentid,title,contents)
                logging.info(msg)
                return flask.render_template('Contacted.htm', data=data)
            except:
                logging.info(f"FORUM STUDENT:{studentid} sending failed")
                return flask.render_template('ContactUs.htm', error=True, data=data)
    else:
        return redirect('/login')

# HTTP error 処理 debag=Trueとすると無効になる
@app.errorhandler(500)
def internal_server_error(error):
    msg = "---INTERNAL SERVER ERROR---\n"
    try:
        msg += f'description:{error.description},\nmessage:{error.message},\
            \nresponse:{error.response},\nwrap:{error.wrap}'
    except:
        msg += 'failed to get the details of the error'
    logging.error(msg)    
    return flask.render_template('error_500.htm'),500

@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template('error_404.htm'),404

# MySQL server has gone away の対策
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool

@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        raise exc.DisconnectionError()
    cursor.close()

import os
@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path,'static/images'),'favicon.ico',mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    pgtids={}
    redirect_pages={}
    app.run(debug=True, host='0.0.0.0', port=5000)
