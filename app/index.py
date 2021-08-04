# 他ファイルの複数の関数を利用する関数、あるいはどれにも属さない関数

from math import *
from .settings import app_url
import re
from pprint import pprint
import copy
import asyncio
from .add import *
from .get import *
from .api import *

# 複合的な関数
def get_announcementlist(studentid, show_only_unchecked = False,courseid=None, day=None):
    """

    """
    announcements=get_announcements(studentid, show_only_unchecked,courseid, day)

    return announcements

def get_data_from_api_and_update(student_id,ses,now,last_update,need_to_update_sitelist):
    """
        ユーザーの履修科目を取得し、対象科目の課題、授業資料、テスト・クイズの情報を更新する

        need_to_update_sitelist:
        0 -> すでにデータベースに格納してあるユーザー履修状況をもとに対象科目を定める
        1 -> APIで履修科目を取得し、うちデータベースに格納していない科目のみを対象とする
    """
    membership = {"student_id": "", "site_list":[]}
    if need_to_update_sitelist == 0:                
        membership["student_id"] = student_id
        membership["site_list"] = get_courses_id_to_be_taken(student_id)
    else:
        # 時間かかる
        last_update = 0
        # membership.json 使用
        # membership = get_course_id_from_api(membership_json(ses))
        # site.json 使用
        membership = get_course_id_from_site_api(get_site_json(ses),student_id)
        already_known= get_courses_id_to_be_taken(student_id)
        # 新規のもののみを取り上げる
        membership["site_list"] = [i for i in membership["site_list"] if i not in already_known]
    if student_id != "":
        # get_assignments = get_assignments_from_api(assignments.json(), student_id)
        courses = {"courses":[],"student_courses":[]}
        resources = {"resources":[],"student_resources":[]}
        quizzes = {"quizzes":[], "student_quizzes":[]}
        asyncio.set_event_loop(asyncio.SelectorEventLoop())
        loop = asyncio.get_event_loop()
        content_statements = []
        site_statements = []
        quiz_statements = []
        page_statements = []
        for courseid in membership["site_list"]:
            content_statements.append(async_get_content(courseid, ses))
            site_statements.append(async_get_site(courseid, ses))
            page_statements.append(async_get_site_pages(courseid, ses))
            quiz_statements.append(async_get_quiz(courseid, ses))
        statements = [*content_statements,*page_statements,*quiz_statements,async_get_assignments(ses),async_get_user_info(ses),async_get_announcement(ses)]
        tasks = asyncio.gather(*statements)
        results = loop.run_until_complete(tasks)
        results_len = int(len(results))-3
        one_forth_results_len = results_len//4
        rslt_contents = results[0:one_forth_results_len]
        rslt_sites = results[one_forth_results_len:one_forth_results_len*2]
        rslt_pages = results[one_forth_results_len*2:one_forth_results_len*3]
        rslt_quizzes = results[one_forth_results_len*3:results_len]
        assignments = get_assignments_from_api(results[results_len],student_id)
        user_info = get_user_info_from_api(results[results_len+1])
        announcements = get_announcement_from_api(results[results_len+2])
        index = 0
        for courseid in membership["site_list"]:
            res = get_resources_from_api(rslt_contents[index],courseid,student_id)
            quiz = get_quizzes_from_api(rslt_quizzes[index],courseid,student_id)
            crs = get_course_from_api(rslt_sites[index], student_id)
            if crs:
                crs["course"]["page_id"] = get_page_from_api(rslt_pages[index]["page_id"])
                crs["course"]["announcement_page_id"] = get_page_from_api(rslt_pages[index]["announcement_page_id"])
                courses["courses"].append(crs["course"])
                courses["student_courses"].append(crs["student_course"])
                resources["resources"].extend(res["resources"])
                resources["student_resources"].extend(res["student_resources"])
                quizzes["quizzes"].extend(quiz["quiz"])
                quizzes["student_quizzes"].extend(quiz["student_quizzes"])
            index += 1
        # student_id   student_id
        # membership   {"student_id": , "site_list": []}
        # assignments  {"assignments": [], student_assignments: []}
        # courses      {"courses": [], "student_courses": []}
        # resources    {"resources":[], "student_resources": []}
        # quizzes      {"quizzes:[], "student_quizzes":[]}
        # user_info    {"student_id": , "fullname": }
        # quizzes      {"quizzes":[], "student_quizzes":[]}
        # announcements{"announcements":[], "studnet_announcements":[]}
        sync_student_contents(student_id, courses, assignments, resources, quizzes, announcements, now, last_update=last_update)

def get_data_from_api_and_update(student_id,access_param,ses,now,last_update):
    last_update = 0
    timetables = get_kulasis_lecture_and_department_no_from_timetable_api(get_timetable(ses,access_param),student_id)
    lectures = {"lectures":[], "student_lectreus":[]}
    # announcements = {"announcements":[], "student_announcements":[]}
    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    lecture_statements = []
    lecture_material_statements = []
    mail_list_statements = []
    for lecture in timetables["site_list"]:
        lecture_statements.append(get_lecture_detail(ses,access_param,lecture["department_no"],lecture["lecture_no"]))
        lecture_material_statements.append(get_lecture_material(ses,access_param,lecture["department_no"],lecture["lecture_no"]))
        mail_list_statements.append(get_mail_list(ses,access_param,lecture["department_no"],lecture["lecture_no"]))
    statements = [*lecture_statements,*lecture_material_statements,*mail_list_statements]
    tasks = asyncio.gather(*statements)
    results = loop.run_until_complete(tasks)
    results_len = int(len(results))
    one_third_results_len = results_len//3
    rslt_lecture_details = results[0:one_third_results_len]
    rslt_lecture_materials = results[one_third_results_len:one_third_results_len*2]
    rslt_mail_lists = results[one_third_results_len*2:results_len]
    index = 0
    lecture_details = {"lectures":[]}
    mail_lists = []
    for lecture in timetables["site_list"]:
        lecture_detail = get_lecture_detail_from_api(rslt_lecture_details[index])
        lecture_material = get_lecture_material_from_api(rslt_lecture_details[index])
        mail_list = get_mail_list_from_api(rslt_mail_lists[index])
        lecture_details["lectures"].append(lecture_detail)
        mail_lists.extend(mail_list)

    mail_detail_statements = []
    for mail in mail_lists:
        mail_detail_statements.extend(get_mail_detail(ses,access_param,mail['department_no'],mail['courseMailNo']))
    # 2度目の非同期処理, メール本文の取得
    task_mail = asyncio.gather(*mail_detail_statements)
    mail_detail_result = loop.run_until_complete(task_mail)
    # この後メールの本文取得，追加処理
        

def get_tasklist(studentid, show_only_unfinished = False,courseid=None, day=None, mode=0):
    """
        mode
        0:tasklist
        1:tasklist for overview
    """

    assignments=get_assignments(studentid, show_only_unfinished,courseid, day, mode)
    quizzes=get_quizzes(studentid, show_only_unfinished,courseid, day, mode)
    # assignmentsとquizzesを結合
    return assignments+quizzes

def sync_student_announcement(studentid, sa, anc): 
    # 追加、更新をする
    add_student_announcement(studentid, sa)
    add_announcement(studentid, anc)
    return 0

def sync_student_assignment(studentid, sa, asm,last_update): 
    # 追加、更新をする
    add_student_assignment(studentid,sa, last_update)
    add_assignment(studentid, asm, last_update)
    return 0

def sync_student_contents(studentid, crs, asm, res, qz, anc, now,last_update=0):
    # 以下主な方針
    #
    # studentテーブルにlast_updateを用意し、毎回update後に記録しておく
    # APIで課題全取得
    # これまでにないものはinsert
    # modifieddateがlast_updateよりあとのもののみupdate
    #

    # 更新をするのはstudent, student_assignment, student_course, student_resource, student_quiz
    # 加えて、assignment,course,resource,quizも同時に更新することにする。

    # courseが最初!!!
    sync_student_course(studentid, crs["student_courses"], crs["courses"], last_update)
    sync_student_assignment(studentid, asm["student_assignments"], asm["assignments"], last_update)
    sync_student_resource(studentid, res["student_resources"], res["resources"], last_update)
    sync_student_quiz(studentid, qz["student_quizzes"], qz["quizzes"], last_update)
    sync_student_announcement(studentid, anc["student_announcement", anc["announcements"]])

    return 0

def sync_student_course(studentid, sc, crs, last_update):
    # 追加、更新をする
    add_studentcourse(studentid, sc)
    add_course(studentid, crs, last_update)
    return 0

def sync_student_resource(studentid, sr, res, last_update):
    # 追加、更新をする
    add_student_resource(studentid, sr)
    add_resource(studentid, res, last_update)
    return 0

def sync_student_quiz(studentid, sq, quiz, last_update):
    add_student_quiz(studentid, sq, last_update)
    add_quiz(studentid, quiz, last_update)
    return 0


# formatter, sort

def day_to_str(day):
    if day == "mon":
        day_str="月曜"
    elif day == "tue":
        day_str="火曜"
    elif day == "wed":
        day_str="水曜"
    elif day == "thu":
        day_str="木曜"
    elif day == "fri":
        day_str="金曜"
    else: day_str="曜日設定がないもの"

    return day_str

def get_search_condition(show_only_unfinished ,max_time_left , course=None, day=None):
    condition=[]
    select3a_judge = 0
    if course != None:
        condition.append(f"{get_coursename(course)}のみ")
    elif day !=None:
        condition.append(f"{day_to_str(day)}のみ")
    if show_only_unfinished == 1:
        condition.append("未完了のみ")
        select3a_judge = 1
    if max_time_left == 0:
        condition.append("一時間以内")
        select3a_judge = 2
    elif max_time_left == 1:
        condition.append("二十四時間以内")
        select3a_judge = 3
    elif max_time_left == 2:
        condition.append("一週間以内")
        select3a_judge = 4
    if len(condition) != 0:       
        search_condition='・'.join(condition)
    else:
        search_condition="全て"
    return {"search_condition":search_condition, "select3a_judge":select3a_judge}

def order_status(status):
    if status == Status.NotYet.value:
        return 0
    elif status == Status.Done.value:
        return 1
    elif status == Status.AlreadyDue.value:
        return 2
    else:
        return 3

def resource_arrange(resource_list:list, coursename:str, courseid):
    course = {"folders":[],"files":[],"name":coursename}
    folderlist = []
    html = ""
    for r in resource_list:
        container = r['container']
        container_spilt = container.split('/')
        del container_spilt[-1]
        for i in range(3):
            del container_spilt[0]
        for folder in folderlist:
            if folder == container_spilt:
                break
        else:
            folderlist.append(container_spilt)
    for foldername in folderlist:
        list_f = course["folders"]
        str_place = 0
        folderindex = 1
        folder_num = 0
        for f in foldername:
            folder_num += 1
            index = 0
            isExist = False
            tag_class = "fas fa-folder-plus"
            if folder_num == 1:
                tag_class = "far fa-folder"
            for lf in list_f:
                if lf["name"] == f:
                    list_f = list_f[index]["folders"]
                    isExist = True
                    break
                index += 1
            if isExist:
                html_1 = re.search(f'><i class="fa.*">{f}</i><ul>', html[str_place:])
                if html_1:
                    str_place += html_1.end()
                folderindex += 1
                continue
            folder_id = '/'.join(foldername[:folderindex])
            html = html[:str_place] + f'''
            <li id="{folder_id}"><i class="{tag_class}">{f}</i><ul></ul></li>''' + html[str_place:]
            html_1 = re.search(f'><i class="fa.*">{f}</i><ul>', html[str_place:])
            if html_1:
                str_place += html_1.end()
            list_f.append({'folders':[],'files':[],'name':f})
            list_len = len(list_f)
            list_f = list_f[list_len-1]["folders"]
            folderindex += 1
    for r in resource_list:
        list_f = course["folders"]
        container = r['container']
        container_spilt = container.split('/')
        del container_spilt[-1]
        for i in range(3):
            del container_spilt[0]
        folder_id = '/'.join(container_spilt)
        folder = re.search(f'<li id="{folder_id}">',html)
        search_num = 0
        if folder:
            search_num = folder.end()
        folder_i = re.search(f'</i><ul>',html[search_num:])
        # target = "_self"
        target = "_blank"
        # if re.search(r'.*\.pdf' ,r["resource_url"]):
        #     target = "_blank"
        #2020/1/19 Shinji Akayama style = "poi"
        # checkbox あり
        # add_html = f"""
        # <li>
        #     <div class="form-check">
        #         <input class="form-check-input" type="checkbox" id="{r["resource_url"]}" value="0"/>
        #         <label class="form-check-label" for="{r["resource_url"]}"> 
        #             <a href="{r["resource_url"]}" target="{target}" download="{r["title"]}" name="{r["resource_url"]}"　style="pointer-events: none;">{r["title"]}</a>
        #         </label>
        #     </div>
        # </li>"""
        # if r['status'] == 1:
        #     add_html = f"""
        #     <li>
        #         <div class="d-inline-flex">
        #             <div class="form-check">
        #                 <input class="form-check-input" type="checkbox" id="{r["resource_url"]}" value="1" disabled checked/>
        #                 <label class="form-check-label" for="{r["resource_url"]}">
        #                         <a href="{r["resource_url"]}" download="{r["title"]}" data-container="body" data-toggle="tooltip" title="このファイルを再ダウンロードする" name="{r["resource_url"]}" target="{target}">{r["title"]}</a>                     
        #                 </label>
        #             </div>
        #         </div>
        #     </li>
        #     """
        # checkbox なし
        status_class = "undownloaded"
        resource_title = r["title"]
        if r["status"] == 1:
            status_class = "downloaded"
            resource_title = "このファイルを再ダウンロードする"
        add_html = f"""
            <li>
                <div class="d-inline-flex">
                    <div class="form-check">
                        <label class="form-check-label" for="{r["resource_url"]}">
                                <a href="{r["resource_url"]}" download="{r["title"]}" data-container="body" data-toggle="tooltip" title={resource_title} name="{r["resource_url"]}" target="{target}" class="resource {status_class}">{r["title"]}</a>                     
                        </label>
                    </div>
                </div>
            </li>
        """
        if folder_i:
            html = html[:folder_i.end()+search_num] + add_html + html[folder_i.end()+search_num:]
    # html = f"""<span><i class="far fa-folder" style="font-size:medium;">{coursename}</i></span>
    #         """ + html
    # html = f'<li class="list-group-item">{coursename}<ul>' + html + '</ul></li>'
    html = f"""
        <div class="card">
            <div class="card-body ressubs">
        <span><i class="far fa-folder">
            <a href="/resourcelist/course/{courseid}">{coursename}</a>
        </i><span>
        """ + html + "</div></div>"
    return html

def setdefault_for_overview(studentid, mode='tasklist',tasks_name="tasks"):
    """
        履修科目をデータベースから取得し、overviewで使用するdataの枠組みを作る
        data:
        {
            "mon1":{"subject": "", "shortname": "", "searchURL": "","tasks": []}
            "mon2":{"subject": "", "shortname": "", "searchURL": "","tasks": []}
            "mon3":{"subject": "", "shortname": "", "searchURL": "","tasks": []}
            "mon4":{"subject": "", "shortname": "", "searchURL": "","tasks": []}
            "mon5":{"subject": "", "shortname": "", "searchURL": "","tasks": []}
            "tue1":{"subject": "", "shortname": "", "searchURL": "","tasks": []}
            "tue2":{"subject": "", "shortname": "", "searchURL": "","tasks": []}
            .
            .
            .
            "fri5":
            "others":[{"subject": "", "shortname": "", "searchURL": "","tasks": []},{"subject": "", "shortname": "", "searchURL": "","tasks": []}]
        }
        - mon1からfri5に対して履修科目があればsubject,shortname,searchURLを追加(taskは空リスト)
        - 時限情報がない科目や、同じ時限に二科目入っていた場合はothersにリスト化して追加
    """
    data={}
    days =["mon", "tue", "wed", "thu", "fri"]
    default = {"subject": "", "shortname": "", "searchURL": "",tasks_name: []}
    for day in days:
        for i in range(5):
            data[day+str(i+1)]=copy.copy(default)
    data["others"]=[]
    coursedata = get_courses_to_be_taken(studentid)
    for course in coursedata:
        add_in_others = False
        add_subject = False
        # 教科に時限情報がない場合
        if course.classschedule == "others" or course.classschedule == "oth":
            add_in_others = True
        else:
            if data[course.classschedule]["subject"] != "":
                if course.coursename != data[course.classschedule]["subject"]:
                    # 本来の時限に既に別科目が入っている
                    add_in_others = True
            else:
                # 本来の時限に科目を入れられる
                add_subject = True

        if add_in_others == True:
            # othersは教科が複数あるので何番目の教科か判定する必要がある
            subject_exist = False
            index = 0
            for subject in data["others"]:
                if subject["subject"] == course.coursename:
                    subject_exist = True
                    break
                index += 1
            if subject_exist:
                continue
            else:
                # 新しい教科を追加
                data["others"].append({})
                data["others"][index]["searchURL"] = app_url+ f"/{mode}/course/"+course.course_id
                data["others"][index]["subject"] = course.coursename
                data["others"][index]["shortname"] = re.sub(
                    "\[.*\]", "", course.coursename)
                data["others"][index][tasks_name] = []

        elif add_subject == True:
            data[course.classschedule]["searchURL"] = app_url+ f"/{mode}/course/"+course.course_id
            data[course.classschedule]["subject"] = course.coursename
            data[course.classschedule]["shortname"] = re.sub(
                "\[.*\]", "", course.coursename)
            data[course.classschedule][tasks_name] = []
    return data

def sort_announcements(announcements,criterion,ascending):
    """
        
        criterion 並び替えの順
        0: 保存者 1: 公開日時 2: サイト名

        ascending 0: 降順 1: 昇順
    """
    

    keyname=""
    if criterion==0:
        keyname="publisher"
    elif criterion==1:
        keyname="time_ms"
    else:
        keyname="subject"
    # keynameの値で並べ変える。降順ならreverseをTrueにする
    new_announcements = sorted(announcements, key=lambda x: x[keyname],reverse=ascending==0)
    return new_announcements

def sort_tasks(tasks, show_only_unfinished = False, max_time_left = 3):
    """
        about max_time_left
        0:an hour
        1:a day
        2:a week
    """
    if show_only_unfinished == True:
        tasks = [task for task in tasks if task["status"] == Status.NotYet.value]
    if max_time_left in [0, 1, 2]:
        tasks = [task for task in tasks if timejudge(task, max_time_left)]
    
    for task in tasks:
        if task["time_left"] == "":
            task["status"]=Status.AlreadyDue.value

    
    new_tasks = sorted([i for i in tasks if i["status"] != Status.AlreadyDue.value], key=lambda x: x["deadline"])
    new_tasks.extend(sorted([i for i in tasks if i["status"] == Status.AlreadyDue.value], key=lambda x: x["deadline"],reverse=True))
    new_tasks = sorted(new_tasks, key=lambda x: order_status(x["status"]))
    return new_tasks

def task_arrange_for_overview(tasks,task_arranged,key_name="tasks"):

    for task in tasks:
        add_in_others = False
        # 教科に時限情報がない場合
        if task["classschedule"] == "others" or task["classschedule"] == "oth":
            add_in_others = True
        else:
            if task["classschedule"] in task_arranged.keys():
                if task["subject"] != task_arranged[task["classschedule"]]["subject"]:
                    add_in_others = True
            else:
                add_in_others = True
        if add_in_others == True:
            # othersは教科が複数あるので何番目の教科か判定する必要がある
            subject_exist = False
            index = 0
            for subject in task_arranged["others"]:
                if subject["subject"] == task["subject"]:
                    subject_exist = True
                    break
                index += 1
            if subject_exist:
                task_arranged["others"][index][key_name].append(task)
            else:
                # 新しい教科を追加(setdefault_for_overviewで型は作ってあるはずなので本来ここに到達することはない)
                task_arranged["others"].append({})
                task_arranged["others"][index]["searchURL"] = ""
                task_arranged["others"][index]["subject"] = task["subject"]
                task_arranged["others"][index]["shortname"] = re.sub(
                    "\[.*\]", "", task["subject"])
                task_arranged["others"][index][key_name] = [task]

        else:
            task_arranged[task["classschedule"]][key_name].append(task)
    return task_arranged

def timejudge(task, max_time_left):
    """
        taskの締め切りまでの残り時間から、taskが残り時間での絞り込みの範囲内かを判定する

        max_time_left
        0:一時間以内
        1:一日以内
        2:一週間以内
        (3:無期限　この場合はそもそもこの関数を呼ばないが、Trueを返しておく。)
    """
    if max_time_left==3:
        return True
    # ex あと10分
    time_left = task["time_left"]
    units = ["minute", "分", "hour", "時", "day", "日"]
    u_num = 0
    if max_time_left == 0:
        u_num = 2
    elif max_time_left == 1:
        u_num = 4
    else:
        u_num = 6
    for i in range(u_num):
        if units[i] in time_left:
            return True
    return False
