from math import *
import time
from .models import student, assignment, course, studentassignment, instructor, studentcourse, resource, studentresource, assignment_attachment
from .settings import session, app_url
import re
from pprint import pprint
import copy

class TimeLeft():
    time_ms:int
    language:str

    def __init__(self, time_ms, language = 'en'):
        self.time_ms = time_ms
        self.language = language
    
    def add_ato(self, msg):
        if self.language == 'ja':
            msg = f'あと{msg}'
        else:
            msg = f'{msg} left'
        return msg

    def add_ijyou(self, msg):
        if self.language == 'ja':
            msg = f'{msg}以上'
        else:
            msg = f'more than {msg}'
        return msg
    
    def add_miman(self, msg):
        if self.language == 'ja':
            msg = f'{msg}未満'
        else:
            msg = f'less than {msg}'
        return msg

    def time_left_to_str(self):
        to = {'ja':'と','en':' and '}
        unit_minute_single = {'ja':'分', 'en':' minute'}
        unit_minute = {'ja':'分', 'en':' minutes'}
        unit_hour_single = {'ja':'時間', 'en':' hour'}
        unit_hour = {'ja':'時間', 'en':' hours'}
        unit_day_single = {'ja':'日', 'en':' day'}
        unit_day = {'ja':'日', 'en':' days'}
        unit_week_single = {'ja':'週間', 'en':' week'}
        unit_week = {'ja':'週間', 'en':' weeks'}
        now = floor(time.time())
        seconds = self.time_ms - now
        minutes = seconds/60
        hours = minutes/60
        days = hours/24
        weeks = days/7
        months = weeks/4

        msg =''

        if seconds < 0:
            return ''
        elif minutes < 1:
            # 一分未満
            msg = self.add_miman('1'+ unit_minute_single[self.language])
        elif hours < 1:
            # 一時間未満
            if floor(minutes) == 1:
                msg = str(floor(minutes)) + unit_minute_single[self.language]
            else:
                msg = str(floor(minutes)) + unit_minute[self.language]
        elif days < 1:
            # 一日未満
            if floor(minutes) == 1:
                msg = str(floor(hours)) + unit_hour_single[self.language]
            else:
                msg = str(floor(hours)) + unit_hour[self.language]
        elif weeks < 1:
            # 一週間未満
            if floor(days) == 1:
                msg = str(floor(days)) + unit_day_single[self.language]
            else:
                msg = str(floor(days)) + unit_day[self.language]
        elif months < 1:
            # 一か月(4週間)未満
            if floor(weeks) == 1:
                msg = str(floor(weeks)) + unit_week_single[self.language]
            else:
                msg = str(floor(weeks)) + unit_week[self.language]

            remain_days = floor(days) - floor(weeks)*7

            if remain_days != 0:
                if remain_days ==1:
                    msg += to[self.language] + str(remain_days) + unit_day_single[self.language]
                else:
                    msg += to[self.language] + str(remain_days) + unit_day[self.language]
        else:
            # 一か月以上
            msg = self.add_ijyou('4' + unit_week[self.language])
        
        return self.add_ato(msg)

def sync_student_contents(studentid):

    # 更新をするのはstudent, student_assignment, student_course, student_resource
    sync_student(studentid)
    sync_student_assignment(studentid)
    sync_student_course(studentid)
    sync_student_resource(studentid)

    return 0

def sync_student_assignment(studentid):
    # 以下主な方針
    #
    # 1　確実だが処理時間は厳しい
    # APIで全課題を取得
    # studentidとassignmentid を使って全書き換え
    # 難点　うまくinsert, update を分けないと時間がかかる
    #
    #
    # 2 1よりは早い
    #
    # studentテーブルにlast_updateを用意し、毎回update後に記録しておく
    # APIで課題全取得
    # opendateがlast_updateより後のもののみinsert
    # modifieddateがlast_updateよりあとのもののみupdate
    # 
    return 0

def sync_student_course(studentid):
    return 0

def sync_student_resource(studentid):
    return 0

def sync_student(studentid):
    return 0

def get_tasklist(studentid, show_only_unfinished = False,courseid=None, day=None, mode=0):
    """
        mode
        0:tasklist
        1:tasklist for overview
    """
    # new_student = enrollment.enrollment()
    # new_student.enrollmentID = "2"
    # new_student.assignmentID = "kadai"
    # new_student.StudentID = "guest"
    # new_student.Status = "finished"
    # new_student.CourseID = "courseA"

    # new_student = assignment.Assignment()
    # new_student.AssignmentID = "kadai"
    # new_student.Title = "kadai"

    # session.add(new_student)

    # new_student = course.Course()
    # new_student.CourseID = "courseA"
    # new_student.CourseName = "PandAsh"
    # session.add(new_student)
    # session.commit()

    if show_only_unfinished == False:
        enrollments = session.query(studentassignment.Student_Assignment).filter(
            studentassignment.Student_Assignment.student_id == studentid).all()
    else:
        enrollments = session.query(studentassignment.Student_Assignment).filter(
            studentassignment.Student_Assignment.student_id == studentid).filter(
                studentassignment.Student_Assignment.status == "未").all()
    assignmentids =[i.assignment_id for i in enrollments]
    course_to_be_taken=get_courses_to_be_taken(studentid)
    courseids = [i.course_id for i in course_to_be_taken]
    assignmentdata = session.query(assignment.Assignment).filter(
        assignment.Assignment.assignment_id.in_(assignmentids)).all()
    
    coursedata = session.query(course.Course).filter(
            course.Course.course_id.in_(courseids)).all()
    
    tasks = []
    for data in enrollments:
        asmdata = [i for i in assignmentdata if i.assignment_id == data.assignment_id]
        crsdata = [i for i in coursedata if i.course_id == asmdata[0].course_id]
        
        if courseid != None:
            if courseid != asmdata[0].course_id:
                continue
        if day != None:
            if day not in crsdata[0].classschedule:
                continue
        if asmdata[0].course_id not in courseids:
            continue
        
        task = {}
        task["status"] = data.status
        task["taskname"] = asmdata[0].title
        task["assignmentid"] = data.assignment_id
        task["deadline"] = asmdata[0].limit_at
        task["time_left"] = TimeLeft(asmdata[0].time_ms).time_left_to_str()
        if mode == 1:
            # overviewのtooltipsに使用
            task["instructions"] = asmdata[0].instructions

        task["subject"] = crsdata[0].coursename
        if mode == 1:
            task["classschedule"] = crsdata[0].classschedule

        tasks.append(task)
    return tasks

def get_courses_to_be_taken(studentid):
    data=[]
    courses = session.query(studentcourse.Studentcourse).filter(
        studentcourse.Studentcourse.student_id == studentid).all()
    for i in courses:
        # if course.hide == 1:
        #     continue
        coursedata = session.query(course.Course).filter(
            course.Course.course_id == i.course_id).all()
        data.append(coursedata[0])
    return data

def setdefault_for_overview(studentid, mode='tasklist'):
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
        if course.classschedule == "others":
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


def task_arrange_for_overview(tasks,task_arranged):

    for task in tasks:
        add_in_others = False
        # 教科に時限情報がない場合
        if task["classschedule"] == "others":
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
                # 新しい教科を追加(本来ここに到達することはない)
                task_arranged["others"].append({})
                task_arranged["others"][index]["searchURL"] = ""
                task_arranged["others"][index]["subject"] = task["subject"]
                task_arranged["others"][index]["shortname"] = re.sub(
                    "\[.*\]", "", task["subject"])
                task_arranged["others"][index]["tasks"] = [task]

        else:
            task_arranged[task["classschedule"]]["tasks"].append(task)
    return task_arranged


def get_resource_list(studentid, course_id=None, day=None):
    srs = session.query(studentresource.Student_Resource).filter(
        studentresource.Student_Resource.student_id == studentid).all()
    
    resource_urls = [i.resource_url for i in srs]
    
    resourcedata = session.query(resource.Resource).filter(
        resource.Resource.resource_url.in_(resource_urls)).all()
    course_to_be_taken=get_courses_to_be_taken(studentid)
    courseids = [i.course_id for i in course_to_be_taken]
    coursedata = session.query(course.Course).filter(
        course.Course.course_id.in_(courseids)).all()
    resource_list={i:[] for i in courseids}

    for data in srs:
        rscdata = [i for i in resourcedata if i.resource_url == data.resource_url]
        crsdata = [i for i in coursedata if i.course_id == rscdata[0].course_id]
        
        if course_id != None:
            if course_id != rscdata[0].course_id:
                continue
        if day !=None:
            if day not in crsdata[0].classschedule:
                continue
        resource_dict = {}
        resource_dict["resource_url"] = data.resource_url
        resource_dict["title"] = rscdata[0].title
        resource_dict["container"] = rscdata[0].container
        resource_dict["modifieddate"] = rscdata[0].modifieddate
        resource_dict["status"] = data.status
        resource_list[rscdata[0].course_id].append(resource_dict)
    return resource_list


def resource_arrange(resource_list:list, coursename:str, courseid):
    course = {"folders":[],"files":[],"name":coursename}
    folderlist = []
    html = ""
    for r in resource_list:
        container = r['container']
        container_spilt = container.split('/')
        del container_spilt[-1]
        for i in range(4):
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
                html_1 = re.search(f'><i class="{tag_class}">{f}</i><ul>', html[str_place:])
                str_place += html_1.end()
                folderindex += 1
                continue
            folder_id = '/'.join(foldername[:folderindex])
            html = html[:str_place] + f'''
            <li id="{folder_id}"><i class="{tag_class}">{f}</i><ul></ul></li>''' + html[str_place:]
            html_1 = re.search(f'><i class="{tag_class}">{f}</i><ul>', html[str_place:])
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
        for i in range(4):
            del container_spilt[0]
        folder_id = '/'.join(container_spilt)
        folder = re.search(f'<li id="{folder_id}">',html)
        search_num = folder.end()
        folder_i = re.search(f'</i><ul>',html[search_num:])
        add_html = f"""
        <li>
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="{r["resource_url"]}" value="0"/>
                <label class="form-check-label" for="{r["resource_url"]}">
                    <a href="{r["resource_url"]}" target="_self" download="{r["title"]}" name="{r["resource_url"]}">{r["title"]}</a>
                </label>
            </div>
        </li>"""
        if r['status'] == 1:
            add_html = f"""
            <li>
                <div class="d-inline-flex">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="{r["resource_url"]}" value="1" disabled checked/>
                        <label class="form-check-label" for="{r["resource_url"]}">
                                <a href="{r["resource_url"]}" download="{r["title"]}" data-container="body" data-toggle="tooltip" title="このファイルを再ダウンロードする" name="{r["resource_url"]}">{r["title"]}</a>                     
                        </label>
                    </div>
                </div>
            </li>
            """
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

def get_coursename(courseid):
    coursename = session.query(course.Course.coursename).filter(course.Course.course_id==courseid).first()
    return coursename[0]

def get_courseids(studentid):
    course_ids = session.query(studentcourse.Studentcourse.course_id).filter(studentcourse.Studentcourse.student_id==studentid).all()
    return list(course_ids)

def add_student(studentid, fullname):
    students = session.query(student.Student.student_id).all()
    isExist = False
    for i in students:
        if list(i)[0] == studentid:
            isExist = True
            break
    if isExist == False:
        new_student = student.Student(student_id=studentid, fullname=fullname)
        session.add(new_student)
        session.commit()
    return

def add_assignment_attachment(url, title, assignment_id):
    assignments = session.query(assignment_attachment.Assignment_attachment.assignment_url).all()
    isExist = False
    for i in assignments:
        if list(i)[0] == url:
            isExist = True
            break
    if isExist == False:
        new_assignment_attachment = assignment_attachment.Assignment_attachment(assignment_url=url, title=title, assignment_id=assignment_id)
        session.add(new_assignment_attachment)
        session.commit()
    return

def add_assignment(assignmentid, url,
                   title, limit_at, instructions, time_ms, modifieddate, courseid):
    assignments = session.query(assignment.Assignment.assignment_id).all()
    isExist = False
    need_update = False
    for i in assignments:
        if list(i)[0] == assignmentid:
            isExist = True
            assignment_md = session.query(assignment.Assignment.modifieddate).filter(
                assignment.Assignment.assignment_id == assignmentid).all()
            if list(assignment_md[0])[0] != modifieddate:
                need_update = True
            break
    if isExist == False:
        new_assignment = assignment.Assignment(assignment_id=assignmentid, url=url, title=title, \
                                               limit_at=limit_at, instructions=instructions, time_ms=time_ms/1000, modifieddate=modifieddate, course_id=courseid)
        session.add(new_assignment)
        session.commit()
    elif need_update:
        old_assignment = session.query(assignment.Assignment).filter(assignment.Assignment.assignment_id==assignmentid).first()
        old_assignment.url = url
        old_assignment.title = title
        old_assignment.limit_at = limit_at
        old_assignment.time_ms = time_ms
        old_assignment.modifieddate = modifieddate
        session.add(old_assignment)
        session.commit()
    return

def add_course(courseid, instructorid, \
               coursename, yearsemester, classschedule):
    courses = session.query(course.Course.course_id).all()
    isExist = False
    for i in courses:
        if list(i)[0] == courseid:
            isExist = True
            break
    if isExist == False:
        new_course = course.Course(course_id=courseid, instructor_id=instructorid, \
                                   coursename=coursename, yearsemester=yearsemester, classschedule=classschedule)
        session.add(new_course)
        session.commit()
    return


def add_student_assignment(studentid, data):
    """
        data:assignment_id, student_id, status
    """
    sa = session.query(
        studentassignment.Student_Assignment.assignment_id).filter(studentassignment.Student_Assignment.student_id == studentid).all()
    assignment_exist = False
    new_sa = []
    for item in data:
        for i in sa:
            if i.assignment_id == item["assignment_id"]:
                assignment_exist = True
                break
        if assignment_exist == False:
            new_sa.append(item)
    session.execute(studentassignment.Student_Assignment.__table__.insert(),new_sa)
    session.commit()
    return


def add_instructor(instructorid, fullname, emailaddress):
    instructors = session.query(instructor.Instructor.instructor_id).all()
    isExist = False
    for i in instructors:
        if list(i)[0] == instructorid:
            isExist = True
            break
    if isExist == False:
        new_instructor = instructor.Instructor(instructor_id=instructorid, fullname=fullname, emailaddress=emailaddress)
        session.add(new_instructor)
        session.commit()
    return

def add_student_resource(studentid,data):
    """
        data: resourceurl, studentid, status
    """
    resource_exist = False
    sr = session.query(studentresource.Student_Resource).filter(studentresource.Student_Resource.student_id ==studentid).all()
    new_sr = []
    for item in data:
        for i in sr:
            if i.resource_url == item["resource_url"]:
                resource_exist = True
                break
        if resource_exist == False:
            new_sr.append(item)
    session.execute(studentresource.Student_Resource.__table__.insert(),new_sr)
    session.commit()
    return


def add_resource(resourceurl, title, container, modifieddate, course_id):
    resources = session.query(resource.Resource.resource_url).all()
    isExist = False
    need_update = False
    for i in resources:
        if list(i)[0] == resourceurl:
            isExist = True
            resource_md = session.query(resource.Resource.modifieddate).filter(
                resource.Resource.resource_url==resourceurl)
            if list(resource_md[0])[0] != modifieddate:
                need_update = True
            break
    if isExist == False:
        new_resource = resource.Resource(resource_url=resourceurl, title=title, container=container, modifieddate=modifieddate, course_id=course_id)
        session.add(new_resource)
        session.commit()
    elif need_update:
        old_resource = session.query(resource.Resource).filter(
            resource.Resource.resource_url==resourceurl).first()
        old_resource.title = title
        old_resource.container = container
        old_resource.modifieddate = modifieddate
        old_resource.course_id = course_id
        session.add(old_resource)
        need_student_resource = session.query(studentresource.Student_Resource).filter(
            studentresource.Student_Resource.resource_url==resourceurl).all()
        for sr in need_student_resource:
            sr.status = 0
            session.add(sr)
        session.commit()
    return

def update_resource_status(studentid, resourceids: list):
    srs = session.query(studentresource.Student_Resource.resource_url, studentresource.Student_Resource.sr_id).filter(
        studentresource.Student_Resource.student_id == studentid).all()
    update_list = []
    for r_id in resourceids:
        for i in srs:
            if i.resource_url == r_id:
                update_list.append({"sr_id":i.sr_id, "status":1})
                break
    session.bulk_update_mappings(studentresource.Student_Resource, update_list)
    session.commit()
    return

def update_task_status(studentid, taskids: list, mode=0):
    sas = session.query(studentassignment.Student_Assignment.assignment_id, studentassignment.Student_Assignment.sa_id).filter(
        studentassignment.Student_Assignment.student_id == studentid).all()
    update_list = []
    status = "未"
    if mode==0:
        status = "済"
    for t_id in taskids:
        for i in sas:
            if i.assignment_id == t_id:
                update_list.append({"sa_id":i.sa_id, "status":status})
                break
    session.bulk_update_mappings(studentassignment.Student_Assignment, update_list)
    session.commit()
    return

def add_studentcourse(studentid, data):
    """
        data:[{student_id:"", course_id:""},{}]
    """
    sc = session.query(studentcourse.Studentcourse).filter(studentcourse.Studentcourse.student_id == studentid).all()
    course_exist = False
    new_sc = []
    for item in data:
        for i in sc:
            if i.course_id == item["course_id"]:
                course_exist = True
                break
        if course_exist == False:
            new_sc.append(item)
    session.execute(studentcourse.Studentcourse.__table__.insert(),new_sc)
    session.commit()
    return

def sort_tasks(tasks, show_only_unfinished = False, max_time_left = 3):
    """
        about max_time_left
        0:an hour
        1:a day
        2:a week
    """
    if show_only_unfinished == True:
        tasks = [task for task in tasks if task["status"] == "未"]
    if max_time_left in [0, 1, 2]:
        tasks = [task for task in tasks if timejudge(task, max_time_left)]
    tasks = sorted(tasks, key=lambda x: x["deadline"])
    tasks = sorted(tasks, key=lambda x: order_status(x["status"]))
    return tasks


def timejudge(task, max_time_left):
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


def order_status(status):
    if status == "未":
        return 0
    elif status == "済":
        return 1
    elif status == "期限切れ":
        return 2
    else:
        return 3


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
