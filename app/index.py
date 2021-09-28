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
def get_data_from_api_and_update(student_id,ses,now,last_update,need_to_update_sitelist):
    """
        ユーザーの履修科目を取得し、対象科目の課題、授業資料、テスト・クイズの情報を更新する

        need_to_update_sitelist:
        0 -> すでにデータベースに格納してあるユーザー履修状況をもとに対象科目を定める
        1 -> APIで履修科目を取得し、うちデータベースに格納していない科目のみを対象とする
    """
    get_membership = {"student_id": "", "site_list":[]}
    if need_to_update_sitelist == 0:                
        get_membership["student_id"] = student_id
        get_membership["site_list"] = get_courses_id_to_be_taken(student_id)
    else:
        # 時間かかる
        last_update = 0
        # membership.json 使用
        # get_membership = get_course_id_from_api(get_membership_json(ses))
        # site.json 使用
        get_membership = get_course_id_from_site_api(get_site_json(ses),student_id)
        already_known= get_courses_id_to_be_taken(student_id)
        # 新規のもののみを取り上げる
        get_membership["site_list"] = [i for i in get_membership["site_list"] if i not in already_known]
    if student_id != "":
        # get_assignments = get_assignments_from_api(assignments.json(), student_id)
        get_sites = {"courses":[],"student_courses":[]}
        get_resources = {"resources":[],"student_resources":[]}
        get_quizzes = {"quizzes":[], "student_quizzes":[]}
        asyncio.set_event_loop(asyncio.SelectorEventLoop())
        loop = asyncio.get_event_loop()
        c_statements = []
        s_statements = []
        q_statements = []
        p_statements = []
        for courseid in get_membership["site_list"]:
            c_statements.append(async_get_content(courseid, ses))
            s_statements.append(async_get_site(courseid, ses))
            p_statements.append(async_get_site_pages(courseid, ses))
            q_statements.append(async_get_quiz(courseid, ses))
            # site = s.get(f"{api_url}site/{courseid}.json")
            # resources = s.get(f"{api_url}content/site/{courseid}.json")
            # get_site = get_course_from_api(site.json(), student_id)
            # get_sites["courses"].append(get_site["course"])
            # get_sites["student_courses"].append(get_site["student_course"])
            # get_resource = get_resources_from_api(resources.json(),courseid,student_id)
            # get_resources["resources"].append(get_resource["resources"])
            # get_resources["student_resources"].append(get_resources["student_resources"])
        c_statements.extend(s_statements)
        c_statements.extend(p_statements)
        c_statements.extend(q_statements)
        c_statements.extend([async_get_assignments(ses),async_get_user_info(ses)])
        tasks = asyncio.gather(*c_statements)
        content_site = loop.run_until_complete(tasks)
        content_site_len = int(len(content_site))-2
        one_forrth_content_site_len = content_site_len//4
        contents = content_site[0:one_forrth_content_site_len]
        sites = content_site[one_forrth_content_site_len:one_forrth_content_site_len*2]
        pages = content_site[one_forrth_content_site_len*2:one_forrth_content_site_len*3]
        quizzes = content_site[one_forrth_content_site_len*3:content_site_len]
        get_assignments = get_assignments_from_api(content_site[content_site_len],student_id)
        user_info = get_user_info_from_api(content_site[content_site_len+1])
        index = 0
        for courseid in get_membership["site_list"]:
            get_resource = get_resources_from_api(contents[index],courseid,student_id)
            get_quiz = get_quizzes_from_api(quizzes[index],courseid,student_id)
            get_site = get_course_from_api(sites[index], student_id)
            if get_site:
                get_site["course"]["page_id"] = get_page_from_api(pages[index],"assignment")
                get_site["course"]["quiz_page_id"] = get_page_from_api(pages[index],"quiz")
                get_sites["courses"].append(get_site["course"])
                get_sites["student_courses"].append(get_site["student_course"])
                get_resources["resources"].extend(get_resource["resources"])
                get_resources["student_resources"].extend(get_resource["student_resources"])
                get_quizzes["quizzes"].extend(get_quiz["quizzes"])
                get_quizzes["student_quizzes"].extend(get_quiz["student_quizzes"])
            index += 1
        # student_id       student_id
        # get_membership   {"student_id": , "site_list": []}
        # get_assignments  {"assignments": [], student_assignments: []}
        # get_sites        {"courses": [], "student_courses": []}
        # get_resources    {"resources":[], "student_resources": []}
        # student_quizzes  {"quizzes:[], "student_quizzes":[]}
        # user_info        {"student_id": , "fullname": }
        # + get_quizzes 
        sync_student_contents(student_id, get_sites, get_assignments, get_resources, get_quizzes, now, last_update=last_update)

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

def sync_student_assignment(studentid, sa, asm,last_update): 
    # 追加、更新をする
    add_student_assignment(studentid,sa, last_update)
    add_assignment(studentid, asm, last_update)
    return 0

def sync_student_contents(studentid, crs, asm, res, qz, now,last_update=0):
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

def split_container(container):
    container_splited = container.split('/')
    del container_splited[-1]
    for i in range(3):
        del container_splited[0]
    return container_splited

def resource_arrange(resource_list:list, coursename:str, courseid):
    course = {"folders":[],"files":[],"name":coursename}
    folderlist = []
    html = ""
    for r in resource_list:
        container_splited = split_container(r['container'])
        for folder in folderlist:
            if folder == container_splited:
                break
        else:
            folderlist.append(container_splited)
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
        container_splited = split_container(r['container'])
        folder_id = '/'.join(container_splited)
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

def setdefault_for_overview(studentid, mode='tasklist'):
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
    default = {"subject": "", "shortname": "", "searchURL": "","tasks": []}
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
                data["others"][index]["tasks"] = []

        elif add_subject == True:
            data[course.classschedule]["searchURL"] = app_url+ f"/{mode}/course/"+course.course_id
            data[course.classschedule]["subject"] = course.coursename
            data[course.classschedule]["shortname"] = re.sub(
                "\[.*\]", "", course.coursename)
            data[course.classschedule]["tasks"] = []
    return data

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

def task_arrange_for_overview(tasks,task_arranged):

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
                task_arranged["others"][index]["tasks"].append(task)
            else:
                # 新しい教科を追加(setdefault_for_overviewで型は作ってあるはずなので本来ここに到達することはない)
                task_arranged["others"].append({})
                task_arranged["others"][index]["searchURL"] = ""
                task_arranged["others"][index]["subject"] = task["subject"]
                task_arranged["others"][index]["shortname"] = re.sub(
                    "\[.*\]", "", task["subject"])
                task_arranged["others"][index]["tasks"] = [task]

        else:
            task_arranged[task["classschedule"]]["tasks"].append(task)
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
        if units[i] in time_left["msg"]:
            return True
    return False
