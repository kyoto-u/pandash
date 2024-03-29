from app.login import kulasis_login_get_api_keys
from flask.templating import render_template
from app.app import app
from app.settings import app_url,app_logout_url,app_login_url,proxy_callback
from app.settings import cas_client
import flask
from app.index import *
from app.decorators import check_oa, login_required, check_admin
from pprint import pprint
from flask import redirect, request, session, url_for
import logging
import requests
import datetime
import time
from app.accesscount import check_and_insert_all_accesses, get_access_logs

logging.basicConfig(level=logging.INFO)
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

@app.route('/login', methods=['GET'])
def login():
    ticket = request.args.get('ticket')
    if ticket:
        # ticketのvalidateを行う
        try:
            cas_response = cas_client.perform_service_validate(
                ticket=ticket,
                service_url=app_login_url,
                )              
        except:
            # CAS server is currently broken, try again later.
            return flask.redirect(url_for('login_failed',description='CAS server is broken'))
        if cas_response and cas_response.success:
            session['logged-in'] = True
            pgtiou= cas_response.data['proxyGrantingTicket']
            return redirect(url_for('proxy', pgtiou=pgtiou))
    if "logged-in" in session and session["logged-in"]:
        del(session['logged-in'])
    if "student_id" in session:
        # student_idがセッションにありかつログインページへ来るのは
        # 長時間放置での接続切れまたは意図的な移動
        # ログイン後のページとして遷移元ページを指定しておく
        redirect_page = request.args.get('page')
        if not redirect_page:
            redirect_page =""
        session['redirect_page'] = redirect_page
    cas_login_url = cas_client.get_login_url(service_url=app_login_url)
    return redirect(cas_login_url)


def count_accesses(student_id):
    with open_db_ses() as db_ses:
        check_and_insert_all_accesses(student_id,datetime.datetime.today(),db_ses)
    return ''

@app.route('/login/proxy/<pgtiou>', methods=['GET'])
def proxy(pgtiou=None):
    if pgtiou==None:
        return flask.redirect(url_for('login_failed',description='no pgtiou'))
    if not pgtids.get(pgtiou):
        return flask.redirect(url_for('login_failed',description='failed to get pgtid from pgtiou'))
    pgtid = pgtids[pgtiou]
    del(pgtids[pgtiou])
    cas_response = cas_client.perform_proxy(proxy_ticket=pgtid)
    if not cas_response.success:
        description=""
        for error in cas_response.error.keys():
            description+=error
        return flask.redirect(url_for('login_failed',description=description))
    proxy_ticket = cas_response.data.get('proxyTicket')
    if not proxy_ticket:
        return flask.redirect(url_for('login_failed',description='failed to get proxy ticket from CAS'))

    # return redirect(url_for('proxyticket', ticket=proxy_ticket))
    # 時間かかる通知を行う
    return flask.render_template('loading.htm', ticket=proxy_ticket)

@app.route('/proxyticket', methods=["GET"])
def proxyticket():
    ticket = request.args.get('ticket')
    if ticket:
        # ticketがあるのでPandAのAPIを利用できる
        ses = requests.Session()
        api_response = ses.get(f"{proxy_callback}?ticket={ticket}", verify=False)
        if api_response.status_code == 200:
            return login_successful(ses)
        return flask.redirect(url_for('login_failed',description='failed to use ticket at PandA'))
    return flask.redirect(url_for('login_failed',description='no ticket is given'))

def login_successful(ses):
    """
    proxyticket()で認証に成功した際に実行する。課題の取得・更新が主
    args
    'session':認証に成功したsession
    """
    start_time = time.perf_counter()
    user = get_user_json(ses)
    student_id = user.get('id')
    count_accesses(student_id)

    email = user.get('email')
    # trial_release ではここで認証済みユーザーのアクセスだけを許可する
    f = open('users.txt', 'r', encoding='UTF-8')
    auth_users = f.readlines()
    f.close()
    authenticated = False
    for auth_user in auth_users:
        if auth_user == f'{email}\n'or auth_user == email:
            authenticated = True
            break
    
    if authenticated == False:
        return flask.redirect(url_for('not_authenticated'))

    fullname = user.get('displayName')
    session["student_id"] = student_id
    now = floor(time.time() * 1000) #millisecond
    with open_db_ses() as db_ses:
        studentdata = get_student(student_id,db_ses)
        show_only_unfinished = 0
        need_to_update_sitelist = 1
        last_update=0
        last_update_subject=0
        language='ja'
        if studentdata:
            if studentdata.show_already_due == 0:
                # ユーザーが期限の過ぎた課題は表示しないように設定しているので、適用する
                show_only_unfinished = 1
            need_to_update_sitelist = studentdata.need_to_update_sitelist
            # ここで、履修状況について前回の更新から1週間以上経過している場合は履修状況を更新する
            if (now - studentdata.last_update_subject) >= 1*7*24*60*60*1000:
                need_to_update_sitelist = 1
            
            last_update = studentdata.last_update
            last_update_subject = studentdata.last_update_subject
            
        else:
            add_student(student_id, fullname, db_ses, last_update = 0, last_update_subject = 0,language='ja')
        
        if need_to_update_sitelist == 1:
            get_data_from_api_and_update(student_id, ses, now,  1, db_ses)
        else:
            get_data_from_api_and_update(student_id, ses, now,  0, db_ses)
        if student_id != "":
            update_student_needs_to_update_sitelist(student_id, db_ses)

        if need_to_update_sitelist:
            add_student(student_id, fullname, db_ses, last_update = now, last_update_subject = now, language = language)
        else:
            add_student(student_id, fullname, db_ses, last_update = now, last_update_subject = last_update_subject, language = language)
        logging.info(f"TIME {student_id}: {time.perf_counter() - start_time}")
        
    # リダイレクト先を決める
    if 'student_id' in session:
        redirect_page=session.get('redirect_page')
        if not 'redirect_page' in session:
            redirect_page=""
        if redirect_page in ['tasklist_redirect','overview','announcement_list','announcement_overview','resources_sample']:
            del(session['redirect_page'])
            return flask.redirect(url_for(redirect_page))
        # 前回情報がない場合のdefaultページ
        return flask.redirect(flask.url_for('tasklist', show_only_unfinished = show_only_unfinished, max_time_left = 3))
    # PGTなどが入手できたにもかかわらずstudent_idがないのは不具合であるのでエラー画面に飛ばす
    return flask.redirect(url_for('login_failed',description='no student_id (unexpected situation)'))

# @app.route('/kulasis/login', methods=['GET', 'POST'])
# def kulasis_login():
#     if request.method == 'GET':
#         return render_template('kulasis_login.htm')
#     elif request.method == 'POST':
#         try:
#             ecs_id = request.form["ecs_id"]
#             password = request.form["password"]
#             params = kulasis_login_get_api_keys(ecs_id, password)
#             if params != {}:
#                 session["access_param"] = params
#                 return url_for('kulasis_login_successful')
#             else:
#                 return url_for('kulasis_login_faild')
#         except:
#             return url_for('kulasis_login_faild')

# @app.route('/kulasis/login/failed')
# def kulasis_login_failed():
#     return render_template('kulasis_login_failed.htm')

# @app.route('/kulasis/login/successful')
# def kulasis_login_successful():
#     studentid = session.get('studentid')
#     param = session.get('access_param')
#     if studentid and param:
#         ses = requests.Session()
        



@app.route('/_logout')
def logout():
    if "logged-in" in session and session["logged-in"]:
        del(session['logged-in'])
    if "student_id" in session and session["student_id"]:
        del(session['student_id'])
    cas_logout_url = cas_client.get_logout_url(service_url=app_url)
    return redirect(cas_logout_url)

@app.route('/')
def root():
    if session.get('logged-in') and session.get('student_id'):
        return redirect(url_for("login"))
    else:
        return flask.render_template('welcome.htm')

@app.route('/welcome')
def welcome():
    return flask.redirect(url_for('root'))

# @app.route('/hello')
# def main():
#     return "Hello World!"

@app.route('/faq')
def faq():
    return flask.render_template("faq.htm")

@app.route('/update')
def update():
    with open_db_ses() as db_ses: 
        dashboard = get_access_logs(db_ses)
    return flask.render_template("update.htm",dashboard = dashboard)

@app.route('/privacypolicy')
def privacypolicy():
    return flask.render_template("privacypolicy.htm")

@app.route('/what_is_pandash')
def what_is_pandash():
    return flask.render_template("what_is_pandash.htm")

@app.route('/_tutorial')
def tutorial():
    return flask.render_template("_tutorial.htm")


@app.route('/help/<page>')
def help(page):
    #2021/01/14 Shinji Akayama: 参照するhtmlが間違っていたので修正しました。FAQ_{page}は完全なhtmlではありません
    return flask.render_template(f"_flexible_help_{page}.htm")

@app.route('/option', methods=['GET'])
def option():
    studentid = session.get('student_id')
    data ={"others":[]}
    show_already_due=0
    last_update_subject=0
    courses_to_be_taken = []
    with open_db_ses() as db_ses:
        studentdata = get_student(studentid,db_ses)
        scsdata = get_courses_to_be_taken(studentid, db_ses, mode=1, return_data='student_course')
        coursesdata = get_courses_to_be_taken(studentid, db_ses, mode=1, return_data='course')
        for i in range(len(scsdata)):
            course_id = scsdata[i].course_id
            hide = scsdata[i].hide
            coursename = coursesdata[i].coursename
            yearsemester = coursesdata[i].yearsemester
            classschedule = coursesdata[i].classschedule
            courses_to_be_taken.append({'course_id':course_id,'coursename':coursename,'yearsemester':yearsemester,'classschedule':classschedule,'hide':hide})
        courses_to_be_taken=sort_courses(courses_to_be_taken)
        show_already_due = studentdata.show_already_due
        data = setdefault_for_overview(studentid, db_ses)
        last_update_subject= str(datetime.datetime.fromtimestamp(studentdata.last_update_subject//1000,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
    return flask.render_template(f"option.htm",data=data, show_already_due=show_already_due, last_update_subject = last_update_subject, courses_to_be_taken=courses_to_be_taken)

@app.route('/update_subject')
def update_subject():
    studentid = session.get('student_id')
    with open_db_ses() as db_ses:
        update_student_needs_to_update_sitelist(studentid,db_ses, need_to_update_sitelist=1)
    return redirect(url_for('login',page='option'))

# 旧バージョンの機能・デバッグ機能のためコメントアウト

# @app.route('/')
# def root():
#     return flask.redirect(flask.url_for('main'))


# @app.route('/controller')
# def controller():
#     # 現行のバージョンでは使えなくなりました
#     # ex
#     add_instructor('instructor1', 'i_fullname', 'i_mailadress')
#     add_assignment("assignmentid1", "url","課題1", "2020-10-30T01:55:00Z", "<p>説明<p>", 11111111111, 1111, "course1" )
#     add_assignment("assignmentid2", "ur2","課題2", "2020-10-30T01:50:00Z", "<p>説明<p>", 11111111111, 1111, "course4" )
#     add_assignment("assignmentid3", "ur3","課題3", "2020-11-01T01:52:00Z", "<p>説明<p>", 11111111111, 1111, "course4" )
#     add_assignment("assignmentid4", "ur4","課題4", "2020-10-30T01:51:00Z", "<p>説明<p>", 11111111111, 1111, "course4" )
#     add_assignment("assignmentid5", "ur5","課題5", "2020-10-30T01:53:00Z", "<p>説明<p>", 11111111111, 1111, "course2" )
#     add_assignment("assignmentid6", "ur6","課題6", "2020-10-30T01:53:00Z", "<p>説明<p>", 11111111111, 1111, "course4" )
#     add_assignment("assignmentid7", "ur7","課題7", "2020-10-30T01:53:00Z", "<p>説明<p>", 11111111111, 1111, "course4" )
#     for i in range(30):
#         add_course(f'dummy{i}', 'teacher1', f'[2020前期他他]ダミー{i}', 20200, f'thu{(i%5)+1}')
#         for j in range(10):
#             add_assignment(f"dummyassignment{i}-{j}", "url",f"課題{i}-{j}", "2020-10-30T01:53:00Z", "<p>説明<p>", 11111111111, 1111, f"dummy{i}" )
#             add_resource(f'resource{i}-{j}','teacher1','/content/group/2020-888-N150-017/演義/',111,f'dummy{i}')
#     
#     
#     add_course('course1', 'teacher1', 'コース1', 20200, 'wed2')
#     add_course('course2', 'teacher1', 'コース2', 20200, 'mon2')
#     add_course('course3', 'teacher1', '[2020前期月1]線形代数学', 20200, 'mon1')
#     add_course('course4', 'teacher1', '[2020前期月2]微分積分学', 20200, 'mon2')
#     add_resource('url1', '資料１', '/content/group/2020-888-N150-017/演義/演義動画/', 111, 'course1')
#     add_resource('url2', '資料２', '/content/group/2020-888-N150-017/演義/演義動画/', 222, 'course1')
#     add_resource('url3', '資料３', '/content/group/2020-888-N150-017/演義/演義資料/', 222, 'course1')
#     add_resource('url4', '資料４', '/content/group/2020-888-N150-017/演義/演義動画/詳細/', 222, 'course1')
#     add_resource('url5', '資料５', '/content/group/2020-888-N150-017/講義/講義動画/', 222, 'course1')
#     add_resource('url6', '資料６', '/content/group/2020-888-N150-017/講義/講義ノート/', 222, 'course1')
#     add_resource('url7', '資料７', '/content/group/2020-888-N150-017/演義/演義動画/', 222, 'course2')
#     return ''

# @app.route('/controller_for_students/<studentid>')
# def controller_for_students(studentid):
#     add_student(studentid,'s_fullname')
#     sc_data=[]
#     sa_data=[]
#     sr_data=[]
#     crs_data=[]
#     asm_data=[]
#     res_data=[]
#     for i in range(30):
#         sc_data.append({"student_id":studentid,"course_id":f"dummy{i}"})
#         crs_data.append({"course_id":f"dummy{i}","instructor_id":"instructor1", "coursename":f'[2020前期他他]ダミー{i}', "yearsemester":20200, "classschedule":f'thu{(i%5)+1}'})
#         for j in range(10):
#             sa_data.append({"sa_id":f"{studentid}:dummyassignment{i}-{j}", "assignment_id":f'dummyassignment{i}-{j}', "student_id":studentid, "status":'未'})
#             asm_data.append({"assignment_id":f'dummyassignment{i}-{j}', "url":"url","title":f"課題{i}-{j}", "limit_at":"2020-10-30T01:50:00Z", "instructions":"<p>説明<p>", "time_ms":11111111111, "modifieddate":1111, "course_id":f"dummy{i}"})
#             sr_data.append({"resource_url":f"resource{i}-{j}","student_id":studentid,"status":0})
#             res_data.append({"resource_url":f"resource{i}-{j}", "title":f'資料{i}-{j}', "container":'/content/group/2020-888-N150-017/演義/', "modifieddate":222, "course_id":f"dummy{i}"})
#     add_studentcourse(studentid,sc_data)
#     add_student_assignment(studentid,sa_data, 0)
#     add_student_resource(studentid, sr_data)
#     add_course(studentid, crs_data, 0)
#     add_assignment(studentid, asm_data, 0)
#     add_resource(studentid, res_data, 0)
#     return ''
    


@app.route('/tasklist')
def tasklist_redirect():
    studentid = session.get('student_id')
    show_only_unfinished = 0
    with open_db_ses() as db_ses:
        studentdata=get_student(studentid, db_ses)
        show_already_due = studentdata.show_already_due
        if show_already_due==0:
            show_only_unfinished=1
    return flask.redirect(flask.url_for('tasklist',show_only_unfinished=show_only_unfinished,max_time_left = 3))

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

    # 課題の最終更新時間を取得
    with open_db_ses() as db_ses:
        studentdata = get_student(studentid,db_ses)
        last_update= str(datetime.datetime.fromtimestamp(studentdata.last_update//1000,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
        logging.debug(f"last update = {last_update}\npage = overview")
        data = setdefault_for_overview(studentid,db_ses)
        tasks = get_tasklist(studentid, db_ses, show_only_unfinished=1, mode=1)
    data = task_arrange_for_overview(tasks,data)

    days =["mon", "tue", "wed", "thu", "fri"]
    for day in days:
        for i in range(5):
            data[day+str(i+1)]["tasks"] = sort_tasks(data[day+str(i+1)]["tasks"],show_only_unfinished = 1)
    data.setdefault("others",[])
    for i in range(len(data["others"])):
        data["others"][i]["tasks"] = sort_tasks(data["others"][i]["tasks"],show_only_unfinished = 1)
    return flask.render_template('overview.htm',data = data,last_update=last_update)

# chat 一覧（暫定）
# @app.route('/chat/overview')
# def chat_overview():
#     studentid = session.get('student_id')
#     if studentid:
#         chatrooms = get_chatrooms(studentid)
#         data = setdefault_for_overview(studentid)
#         return flask.render_template('chat.htm', chatrooms=chatrooms, data=data)
#     else:
#         return redirect(url_for('login'))

@app.route('/tasklist/day/<day>')
def tasklist_day_redirect(day):
    studentid = session.get('student_id')
    show_only_unfinished = 0
    with open_db_ses() as db_ses:
        studentdata=get_student(studentid,db_ses)
        show_already_due = studentdata.show_already_due
        if show_already_due==0:
            show_only_unfinished=1
    return flask.redirect(flask.url_for('tasklist_day',day=day, show_only_unfinished=show_only_unfinished,max_time_left = 3))

@app.route('/tasklist/course/<courseid>')
def tasklist_course_redirect(courseid):
    studentid = session.get('student_id')
    show_only_unfinished = 0
    with open_db_ses() as db_ses:
        studentdata=get_student(studentid,db_ses)
        show_already_due = studentdata.show_already_due
        if show_already_due==0:
            show_only_unfinished=1
    return flask.redirect(flask.url_for('tasklist_course',courseid=courseid,show_only_unfinished=show_only_unfinished,max_time_left = 3))


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

# コメントを取得/表示
# @app.route('/chat/course/<courseid>')
# def chat_course(courseid):
#     studentid = session.get('student_id')
#     if studentid:
#         studentdata = get_student(studentid)
#         if studentdata == None:
#             return redirect(url_for('login'))
#         last_update = str(datetime.datetime.fromtimestamp(studentdata.last_update//1000,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
#         return comment_general(courseid)
#     else:
#         return redirect(url_for('login'))

@app.route('/announcement/overview')
def announcement_overview():
    studentid = session.get('student_id')
    # 課題の最終更新時間を取得
    with open_db_ses() as db_ses:
        studentdata = get_student(studentid,db_ses)
        last_update= str(datetime.datetime.fromtimestamp(studentdata.last_update//1000,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
        logging.debug(f"last update = {last_update}\npage = announcement")
        data = setdefault_for_overview(studentid, db_ses, mode="announcement",tasks_name="announcements")
        announcements = get_announcementlist(studentid, db_ses)
    data = task_arrange_for_overview(announcements,data,key_name="announcements")

    days =["mon", "tue", "wed", "thu", "fri"]
    for day in days:
        for i in range(5):
            data[day+str(i+1)]["announcements"] = sort_announcements(data[day+str(i+1)]["announcements"],1,0)
    data.setdefault("others",[])
    for i in range(len(data["others"])):
        data["others"][i]["announcements"] = sort_announcements(data["others"][i]["announcements"],1,0)
    # TODO: 適切なテンプレートを選択する
    return flask.render_template('announcement_overview.htm',data = data,announcements=data,last_update=last_update)

@app.route('/announcement/list')
def announcement_list():
    per_page=20
    studentid = session.get('student_id')
    with open_db_ses() as db_ses:
        # 課題の最終更新時間を取得
        studentdata = get_student(studentid,db_ses)
        last_update= str(datetime.datetime.fromtimestamp(studentdata.last_update//1000,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
        logging.debug(f"last update = {last_update}\npage = announcement_list")
        data = setdefault_for_overview(studentid, db_ses)
        announcements = get_announcementlist(studentid, db_ses)
    announcements = sort_announcements(announcements,1,0)
    num=len(announcements)
    return flask.render_template('announcement_pagenation.htm',data = data,announcements=announcements,num=num,per_page=per_page,last_update=last_update)

@app.route('/announcement/content/<announcement_id>')
def announcement_content(announcement_id):
    with open_db_ses() as db_ses:
        studentid = session.get('student_id')
        update_task_clicked_status(studentid, [announcement_id],db_ses=db_ses ,mode="anc")
        data = setdefault_for_overview(studentid, db_ses, mode="announcement",tasks_name="announcements")
        announce = get_announcement(studentid,announcement_id,db_ses)
    return render_template('announcement_content.htm', announce=announce, data=data)


@app.route('/announcement/course/<courseid>/<criterion>/<ascending>')
def announcementlist_general(courseid,criterion,ascending):
    studentid = session.get('student_id')
    with open_db_ses() as db_ses:
        # 課題の最終更新時間を取得
        studentdata = get_student(studentid,db_ses)
        
        last_update= str(datetime.datetime.fromtimestamp(studentdata.last_update//1000,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
        logging.debug(f"last update = {last_update}\npage = announcementlist")
        announcements = get_announcementlist(studentid, db_ses, courseid=courseid)
        unchecked_announcement_num=sum((i["checked"] == 0 for i in announcements))
        data = setdefault_for_overview(studentid, db_ses, mode="announcement",tasks_name="announcements")
    announcements = sort_announcements(announcements,criterion=criterion,ascending=ascending)
    logging.info(f"studentid={studentid}の未確認のお知らせ:{unchecked_announcement_num}個")
    
    sort_condition = {"criterion":criterion,"ascending":ascending==1}
    return flask.render_template(
        'announcement.htm',
        announcements = announcements,
        data = data,
        sort_condition = sort_condition,
        unchecked_task_num = unchecked_announcement_num,
        last_update = last_update)

@app.route('/ical')
def ical():
    studentid = session.get('student_id')
    with open_db_ses() as db_ses:
        data = setdefault_for_overview(studentid, db_ses)
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
        with open_db_ses() as db_ses:
            update_resource_status(studentid, r_links, db_ses)
        return 'success'
    else:
        return 'failed'

@app.route('/task_finish', methods=['POST'])
def task_finish():
    studentid = session.get('student_id')
    if studentid:
        task_id = request.json['task_id']
        with open_db_ses() as db_ses:
            update_task_status(studentid, task_id, db_ses)
        return 'success'
    else:
        return 'failed'

@app.route('/task_unfinish', methods=['POST'])
def task_unfinish():
    studentid = session.get('student_id')
    if studentid:
        task_id = request.json['task_id']
        with open_db_ses() as db_ses:
            update_task_status(studentid, task_id, db_ses, mode=1)
        return 'success'
    else:
        return 'failed'

@app.route('/quiz_finish', methods=['POST'])
def quiz_finish():
    studentid = session.get('student_id')
    if studentid:
        task_id = request.json['task_id']
        with open_db_ses() as db_ses:
            update_task_status(studentid, task_id, db_ses, mode=0, taskmode="quiz")
        return 'success'
    else:
        return 'failed'

@app.route('/quiz_unfinish', methods=['POST'])
def quiz_unfinish():
    studentid = session.get('student_id')
    if studentid:
        task_id = request.json['task_id']
        with open_db_ses() as db_ses:
            update_task_status(studentid, task_id, db_ses, mode=1, taskmode="quiz")
        return 'success'
    else:
        return 'failed'

@app.route('/task_clicked', methods=['POST'])
def task_clicked():
    studentid = session.get('student_id')
    if studentid:
        task_ids = request.json['task_ids']
        with open_db_ses() as db_ses:
            update_task_clicked_status(studentid, task_ids, db_ses, mode="task")
        return 'success'
    else:
        return 'failed'

@app.route('/quiz_clicked', methods=['POST'])
def quiz_clicked():
    studentid = session.get('student_id')
    if studentid:
        task_ids = request.json['task_ids']
        with open_db_ses() as db_ses:
            update_task_clicked_status(studentid, task_ids, db_ses, mode="quiz")
        return 'success'
    else:
        return 'failed'

@app.route('/announcement_clicked', methods=['POST'])
def announcement_clicked():
    studentid = session.get('student_id')
    if studentid:
        announcement_ids = request.json['announcement_ids']
        with open_db_ses() as db_ses:
            update_task_clicked_status(studentid, announcement_ids,db_ses, mode="anc")
        return 'success'
    else:
        return 'failed'

        
@app.route('/announcement_all_clicked', methods=['POST'])
def annoucnement_all_clicked():
    studentid = session.get('student_id')
    if studentid:
        with open_db_ses() as db_ses:
            update_all_tasks_clicked_status(studentid, db_ses, mode="anc")
        return 'success'
    else:
        return 'failed'

@app.route('/course_hide', methods=['POST'])
def course_hide():
    studentid = session.get('student_id')
    if studentid:
        course_list = request.json['course_list']
        hide = request.json['hide']
        with open_db_ses() as db_ses:
            update_student_course_hide(studentid,course_list,hide, db_ses)
        return 'success'
    else:
        return 'failed'

@app.route('/show_already_due', methods=['POST'])
def show_already_due():
    studentid = session.get('student_id')
    if studentid:
        show_already_due = request.json['show_already_due']
        with open_db_ses() as db_ses:
            update_student_show_already_due(studentid, db_ses,show_already_due)
        return 'success'
    else:
        return 'failed'

# コメントを追加 post
# @app.route('/add_comment', methods=['POST'])
# def add_comment():
#     studentid = session.get('studentid')
#     if studentid:
#         courseid = request.json['courseid']
#         content = request.json['content']
#         reply_to = request.json['reply_to']
#         commentid = add_comment(studentid,reply_to,content)
#         have_auth = add_coursecomment(studentid,commentid,courseid)
#         update_comment_unchecked(courseid)
#         # 自分の未読チェックは外す
#         update_comment_checked(studentid,courseid)
#         if have_auth:
#             return 'success'
#         else:
#             return 'failed'
#     else:
#         return 'error'                


@app.route('/pgtCallback', methods=['GET'])
def pgtCallback():
    pgtiou = request.args.get('pgtIou')
    pgtid = request.args.get('pgtId')
    pgtids[pgtiou] = pgtid
    return ''


def resourcelist_general(day = None,courseid = None):
    studentid = session.get('student_id')

    with open_db_ses() as db_ses:
        # 課題の最終更新時間を取得
        studentdata = get_student(studentid,db_ses)
        last_update= str(datetime.datetime.fromtimestamp(studentdata.last_update//1000,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
        logging.debug(f"last update = {last_update}\npage = resourcelist")
        numofcourses = 0
        courses = sort_courses_by_classschedule(get_courses_to_be_taken(studentid,db_ses),mode='course_id_name')
        html = ""
        resource_list = get_resource_list(studentid, db_ses, course_id = courseid, day=day)
        for c in courses:
            if resource_list[c[0]] != []:
                numofcourses += 1
                html += resource_arrange(resource_list[c[0]], c[1], c[0])
        data = setdefault_for_overview(studentid, db_ses, mode='resourcelist')

    if courseid != None:
        return flask.render_template('resources_sample.htm', html=html, data=data, numofcourses=1, last_update=last_update)
    if day != None:
        return flask.render_template('resources_sample.htm', html=html, data=data, day=day, numofcourses=numofcourses, last_update=last_update)
    else:
        return flask.render_template('resources_sample.htm', html=html, data=data, numofcourses=numofcourses, last_update=last_update)

def tasklist_general(show_only_unfinished,max_time_left,day = None,courseid = None):
    studentid = session.get('student_id')

    with open_db_ses() as db_ses:
        # 課題の最終更新時間を取得
        studentdata = get_student(studentid,db_ses)
        last_update= str(datetime.datetime.fromtimestamp(studentdata.last_update//1000,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
        logging.debug(f"last update = {last_update}\npage = tasklist")
        if courseid != None:
            tasks = get_tasklist(studentid, db_ses, courseid=courseid)
        elif day != None:
            tasks = get_tasklist(studentid, db_ses, day=day)
        else:
            tasks = get_tasklist(studentid, db_ses)
        # tasks = [
        #     {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題1', 'status':'未', 'time_left': "あと50分", 'deadline':'2020-10-30T00:50:00Z','instructions':'なし'},
        #     {'subject':'[2020前期月1]線形代数学', 'classschedule':'mon1','taskname':'課題2', 'status':'未', 'time_left':'あと2時間', 'deadline':'2020-10-30T02:00:00Z','instructions':'なし'},
        #     {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題3', 'status':'終了', 'time_left':'', 'deadline':'2020-10-29T23:00:00Z','instructions':'なし'},
        #     {'subject':'[2020前期火1]英語リーディング', 'classschedule':'Tue1','taskname':'課題4', 'status':'未', 'time_left':'あと3日', 'deadline':'2020-11-02T03:00:00Z','instructions':'なし'},
        #     {'subject':'[2020前期月2]微分積分学', 'classschedule':'mon2','taskname':'課題5', 'status':'済', 'time_left':'あと1時間', 'deadline':'2020-10-30T01:00:00Z','instructions':'なし'},
        #     {'subject':'[2020前期月1]英語ライティングリスニング', 'classschedule':'mon1','taskname':'課題6', 'status':'済', 'time_left':'あと1日', 'deadline':'2020-10-31T01:00:00Z','instructions':'なし'}
        #     ]
        tasks = sort_tasks(tasks, show_only_unfinished = show_only_unfinished, max_time_left = max_time_left)
        unfinished_task_num=sum((i["status"] == Status.NotYet.value for i in tasks))
        logging.info(f"studentid={studentid}の未完了課題:{unfinished_task_num}個")
        data ={"others":[]}
        data = setdefault_for_overview(studentid, db_ses)
    if courseid != None:
        search_condition = get_search_condition(show_only_unfinished, max_time_left, db_ses, course=courseid)
    elif day != None:
        search_condition = get_search_condition(show_only_unfinished, max_time_left, db_ses, day=day)
        return flask.render_template(
            'tasklist.htm',
            tasks = tasks,
            data = data,
            day = day,
            search_condition = search_condition,
            unfinished_task_num = unfinished_task_num,
            last_update = last_update)
    else:
        search_condition = get_search_condition(show_only_unfinished, max_time_left, db_ses)
    return flask.render_template(
        'tasklist.htm',
        tasks = tasks,
        data = data,
        day = 'oth',
        search_condition = search_condition,
        unfinished_task_num = unfinished_task_num,
        last_update = last_update)


def comment_general(courseid = None):
    studentid = session.get('studentid')
    with open_db_ses() as db_ses:
        studentdata = get_student(studentid,db_ses)
        last_update = str(datetime.datetime.fromtimestamp(studentdata.last_update//1000,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
        data = setdefault_for_overview(studentid,db_ses)
        all_comments = get_comments(studentid, courseid, db_ses)
        if len(all_comments) == 1:
            return flask.render_template(
                'comment.htm',
                comments = all_comments[0]["comments"],
                roomname = all_comments[0]["roomname"],
                data = data)
        else:
            return flask.render_template(
                'chatroom.htm',
                # commnets: [{roomname:"", comments:[]}, ..]
                comments = all_comments,
                data = data
            )

@app.route('/ContactUs', methods=['GET', 'POST'])
def forum():
    student_id = session.get('student_id')
    with open_db_ses() as db_ses:
        data = setdefault_for_overview(student_id, db_ses)
        if request.method == 'GET':
            frms=get_forums(student_id,True,db_ses)
            return flask.render_template('ContactUs.htm', error=False, data=data,frms=frms)
        elif request.method == 'POST':
            try:
                title = request.form["title"]
                contents = request.form["contents"]
                # msg = f"""---FORUM---
                #     STUDENT: {studentid},
                #     TITLE: {title},
                #     CONTENTS: {contents}
                #     --------------"""
                msg = add_forum(student_id,title,contents, db_ses)
                logging.info(msg)
                return flask.render_template('Contacted.htm', data=data)
            except:
                logging.info(f"FORUM STUDENT:{student_id} sending failed")
                return flask.render_template('ContactUs.htm', error=True, data=data)

# 管理画面
@app.route('/manage/admin')
@check_admin
def manage_admin():
    return "manage pandash!"

@app.route('/manage/oa')
@check_oa
def manage_oa():
    # !dashboardの情報
    log = ""
    try:
        with open("DEBUG_LOG.log") as f:
            log = f.read()
    except:
        log = ""
    log_list = log.split("\n")
    with open_db_ses() as db_ses: 
        dashboard = get_access_logs(db_ses)
        frms=get_forums("",False,db_ses,all=True)
    return flask.render_template('manage_oa.htm', dashboard = dashboard, frms = frms, year_sems = {}, log = log_list)

# oa 管理ページに/manage/year_semesterのリンクを設置
@app.route('/manage/year_semester_update')
@check_oa
def manage_year_semester_update():
    dt = datetime.date.today()
    year_sems = auto_collect_year_semester(dt=dt)
    # json ファイルにsemester情報を格納
    with open('year_semester.json', 'w') as f:
        json.dump(year_sems,f)
    
    with open_db_ses() as db_ses: 
        dashboard = get_access_logs(db_ses)
        frms=get_forums("",False,db_ses,all=True)

    # 更新したデータを表示
    return flask.render_template('manage_oa.htm', dashboard=dashboard,frms=frms,year_sems=year_sems)
    


@app.route('/manage_reply', methods=['POST'])
def manage_reply():
    student_id = session.get('student_id')
    with open_db_ses() as db_ses:
        reply_content = request.json['reply_content']
        form_id = request.json['form_id']
        update_reply_content(student_id, form_id, reply_content,db_ses)
    return 'success'

# 403
@app.errorhandler(403)
@app.route('/forbidden')
def forbidden(error):
    return flask.render_template('error_403.htm'),403

@app.route('/loginfailed')
def login_failed():
    description=request.args.get('description')
    if not description:
        description="no description"
    # ログイン情報を初期化
    if "logged-in" in session and session["logged-in"]:
        del(session['logged-in'])
    if "student_id" in session and session["student_id"]:
        del(session['student_id'])
    return flask.render_template('login_failed.htm',description=description)

#trial_releaseでは認証済みでないユーザーのアクセスを制限する
@app.route('/access-restriction')
def not_authenticated():
    return flask.render_template('access_restriction.htm')

# HTTP error 処理 debag=Trueとすると無効になる
@app.errorhandler(500)
def internal_server_error(error):
    msg = "---INTERNAL SERVER ERROR---\n"
    try:
        msg += f'description:{error.description},\nname:{error.name},\
            \nresponse:{error.response}'
    except:
        msg += 'failed to get the details of the error'
    logging.error(msg)    
    return flask.render_template('error_500.htm',msg=msg),500

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

@app.before_request
def before_request():
    pages_open=['login','logout','login_failed','not_authenticated','proxy','proxyticket','static','favicon','welcome','root','welcome','faq','update','tutorial','help','what_is_pandash','privacypolicy','page_not_found','internal_server_error','pgtCallback']
    
    # リクエストのたびにセッションの寿命を更新する
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes = 30)
    session.modified = True
    logged_in=True
    studentid = session.get('student_id')
    if studentid:
        with open_db_ses() as db_ses:
            studentdata = get_student(studentid,db_ses)
            if studentdata == None:
                logged_in=False
            now = floor(time.time() * 1000)
            if (now - studentdata.last_update) >= 30*60*1000:
                logged_in=False
    else:
        logged_in=False
    if (not logged_in) and request.endpoint not in pages_open:
        return redirect(url_for('login'))


if __name__ == '__main__':
    log_handler = logging.FileHandler("DEBUG_LOG.log")
    log_handler.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(log_handler)
    pgtids={}
    app.run(debug=True, host='0.0.0.0', port=5000)
