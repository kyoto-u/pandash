from app.app import app
from app.settings import engine,app_url,app_login_url,cas_url,proxy_url,proxy_callback,api_url
from app.settings import cas_client
import flask
from sqlalchemy.orm import sessionmaker
from app.index import *
from pprint import pprint
from cas_client import CASClient
from flask import Flask, redirect, request, session, url_for
import logging
import requests
import time

logging.basicConfig(level=logging.DEBUG)
app.secret_key ='pandash'

global pgtids

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
                print(cas_response.data['proxyGrantingTicket'])
                pgtiou= cas_response.data['proxyGrantingTicket']
                return redirect(url_for('proxy', pgtiou=pgtiou))
        if "logged-in" in session and session["logged-in"]:
            del(session['logged-in'])
        cas_login_url = cas_client.get_login_url(service_url=app_login_url)
        return redirect(cas_login_url)
    elif request.method == 'POST':
        print('pgt=')
        pgt = request.form
        print(pgt)
        return ''

@app.route('/login/proxy/<pgtiou>', methods=['GET'])
def proxy(pgtiou=None):
    pgtid = pgtids[pgtiou]
    cas_response = cas_client.perform_proxy(proxy_ticket=pgtid)
    proxy_ticket = cas_response.data.get('proxyTicket')
    return redirect(url_for('proxyticket', ticket=proxy_ticket))

@app.route('/proxyticket', methods=["GET"])
def proxyticket():
    ticket = request.args.get('ticket')
    start_time = time.perf_counter()
    if ticket:
        ses = requests.Session()
        api_response = ses.get(f"{proxy_callback}?ticket={ticket}")
        if api_response.status_code == 200:
            now = now = floor(time.time())
            membership = ses.get(f"{api_url}membership.json")
            assignments = ses.get(f"{api_url}assignment/my.json")
            get_membership = get_course_id_from_api(membership.json())
            student_id = get_membership["student_id"]
            if student_id != "":
                get_assignments = get_assignments_from_api(assignments.json(), student_id)
                get_sites = {"courses":[],"student_courses":[]}
                get_resources = {"resources":[],"student_resources":[]}
                asyncio.set_event_loop(asyncio.SelectorEventLoop())
                loop = asyncio.get_event_loop()
                c_statements = []
                s_statements = []
                for courseid in get_membership["site_list"]:
                    c_statements.append(async_get_content(courseid, ses))
                    s_statements.append(async_get_site(courseid, ses))
                    # site = s.get(f"{api_url}site/{courseid}.json")
                    # resources = s.get(f"{api_url}content/site/{courseid}.json")
                    # get_site = get_course_from_api(site.json(), student_id)
                    # get_sites["courses"].append(get_site["course"])
                    # get_sites["student_courses"].append(get_site["student_course"])
                    # get_resource = get_resources_from_api(resources.json(),courseid,student_id)
                    # get_resources["resources"].append(get_resource["resources"])
                    # get_resources["student_resources"].append(get_resources["student_resources"])
                c_statements.extend(s_statements)
                tasks = asyncio.gather(*c_statements)
                content_site = loop.run_until_complete(tasks)
                content_site_len = int(len(content_site))
                contents = content_site[0:content_site_len//2]
                sites = content_site[content_site_len//2:content_site_len]
                index = 0
                for courseid in get_membership["site_list"]:
                    get_resource = get_resources_from_api(contents[index],courseid,student_id)
                    get_site = get_course_from_api(sites[index], student_id)
                    get_sites["courses"].append(get_site["course"])
                    get_sites["student_courses"].append(get_site["student_course"])
                    get_resources["resources"].extend(get_resource["resources"])
                    get_resources["student_resources"].extend(get_resource["student_resources"])
                    index += 1
                # student_id       student_id
                # get_membership   {"student_id": , "site_list": []}
                # get_assignments  {"assignments": [], student_assignments: []}
                # get_sites        {"courses": [], "student_courses": []}
                # get_resources    {"resources":[], "student_resources": []}
                sync_student_contents(student_id, get_sites, get_assignments, get_resources, now)
            print(time.perf_counter()-start_time)
        return redirect(url_for("root"))
    return redirect(url_for("root"))

@app.route('/logout')
def logout():
    del(session['logged-in'])
    cas_client = CASClient(cas_url, proxy_url=proxy_url)
    cas_logout_url = cas_client.get_logout_url(service_url=app_login_url)
    return redirect(cas_logout_url)

@app.route('/')
def root():
    if session.get('logged-in'):
        return flask.redirect(flask.url_for('tasklist',show_only_unfinished = 0,max_time_left = 3))
    else:
        return flask.render_template('welcome.htm')


@app.route('/hello')
def main():
    return "Hello World!"

@app.route('/help/<page>')
def help(page):
    return flask.render_template(f"FAQ_{page}.htm")


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
    return tasklist_day(day,0,3)

@app.route('/tasklist/course/<courseid>')
def tasklist_course_redirect(courseid):
    return tasklist_course(courseid,0,3)

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
    studentid = 'student1'
    data = setdefault_for_overview(studentid, mode="resourcelist")
    resource = get_resource_list(studentid, course_id=courseid)
    coursename = get_coursename(courseid)
    resource_html = resource_arrange(resource[courseid], coursename, courseid)
    return flask.render_template('resources_sample.htm', html=resource_html, data=data)

@app.route('/resourcelist/day/<day>')
def resource_day(day):
    studentid = 'student1'
    courses = get_courses_to_be_taken(studentid)
    data = setdefault_for_overview(studentid, mode="resourcelist")
    html = ""
    resource_list = get_resource_list(studentid, day=day)
    for c in courses:
        if resource_list[c.course_id] != []:
            html += resource_arrange(resource_list[c.course_id], c.coursename, c.course_id)
    data = setdefault_for_overview(studentid, mode='resourcelist')
    return flask.render_template('resources_sample.htm', html=html, data=data, day=day)

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

@app.route('/task_unfinish', methods=['POST'])
def task_unfinish():
    studentid = 'student1'
    task_id = request.json['task_id']
    update_task_status(studentid, task_id, mode=1)
    return 'success'

@app.route('/pgtCallback', methods=['GET', 'POST'])
def pgtCallback():
    if request.method == 'GET':
        pgtiou = request.args.get('pgtIou')
        pgtid = request.args.get('pgtId')
        pgtids[pgtiou] = pgtid
        return ''
    elif request.method == 'POST':
        pgt = request.form
        print(pgt)
        return ''


def tasklist_general(show_only_unfinished,max_time_left,day = None,courseid = None):
    studentid = "student1"
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

    data ={"others":[]}
    data = setdefault_for_overview(studentid)
    if courseid != None:
        search_condition = get_search_condition(show_only_unfinished, max_time_left, courseid=courseid)
    elif day != None:
        search_condition = get_search_condition(show_only_unfinished, max_time_left, day=day)
        return flask.render_template('tasklist.htm', tasks=tasks, data=data, day=day, search_condition=search_condition)
    else:
        search_condition = get_search_condition(show_only_unfinished, max_time_left)
    return flask.render_template('tasklist.htm', tasks=tasks, data=data, day='oth', search_condition=search_condition)


if __name__ == '__main__':
    pgtids={}
    app.run(debug=True, host='0.0.0.0', port=5000)
