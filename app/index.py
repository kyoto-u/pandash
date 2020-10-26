from .models import student, assignment, course, enrollment, instructor, enrollmentR, resource, studentcourse, resource_attachment
from .settings import session
import re


def get_tasklist(studentid, mode=0):
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

    enrollments = session.query(enrollment.Enrollment).filter(
        enrollment.Enrollment.student_id == studentid).all()
    tasks = []
    for data in enrollments:
        task = {}
        task["status"] = data.status
        task["assignmentid"] = data.assignment_id
        assignmentdata = session.query(assignment.Assignment).filter(
            assignment.Assignment.assignment_id == data.assignment_id).all()
        task["taskname"] = assignmentdata[0].title
        task["deadline"] = assignmentdata[0].limit_at
        if mode == 0:
            task["time_left"] = remain_time(assignmentdata[0].time_ms)
        if mode == 1:
            task["instructions"] = assignmentdata[0].instructions
        coursedata = session.query(course.Course).filter(
            course.Course.course_id == data.course_id).all()
        task["subject"] = coursedata[0].coursename
        if mode == 1:
            task["classschedule"] = coursedata[0].classschedule
        tasks.append(task)
    return tasks

def get_courses_to_be_taken(studentid):
    data=[]
    courses = session.query(studentassignment.Student_Assignment).filter(
        studentassignment.Student_Assignment.student_id == studentid).all()
    for course in courses:
        if course.hide == 1:
            continue
        coursedata = session.query(course.Course).filter(
            course.Course.course_id == course.course_id).all()
        data.append(coursedata[0])
    return data

def setdefault_for_overview(data, studentid):
    days =["mon", "tue", "wed", "thu", "fri"]
    for day in days:
        for i in range(5):
            data.setdefault(day+str(i+1),{"subject": "", "shortname": "", "searchURL": "","tasks": []})
            data[day+str(i+1)]["tasks"] = sort_tasks(data[day+str(i+1)]["tasks"])
    data.setdefault("others",[])
    for subject in data["others"]:
        subject["tasks"] = sort_tasks(subject["tasks"])
    coursedata = get_courses_to_be_taken(studentid)
    for course in coursedata:
        add_in_others = False
        add_new_subject = False
        # 教科に時限情報がない場合
        if course.classschedule == "others":
            add_in_others = True
        else:
            if course.coursename != data[course.classschedule]["subject"] and course.coursename != "":
                add_in_others = True
            else:
                add_new_subject = True
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
                data["others"][index]["subject"] = course.coursename
                data["others"][index]["shortname"] = re.sub(
                    "\[.*\]", "", course.coursename)
                data["others"][index]["tasks"] = []

        elif add_new_subject == True:
            data[course.classschedule] = {}
            data[course.classschedule]["shorturl"] = ""
            data[course.classschedule]["subject"] = course.coursename
            data[course.classschedule]["shortname"] = re.sub(
                "\[.*\]", "", course.coursename)
            data[course.classschedule]["tasks"] = []
    return data


def task_arrange_for_overview(tasks):
    task_arranged = {"others": []}

    for task in tasks:
        # if task["status"] != "未":
        #     continue
        add_in_others = False
        add_new_subject = False
        # 教科に時限情報がない場合
        if task["classschedule"] == "others":
            add_in_others = True
        else:
            if task["classschedule"] in task_arranged.keys():
                if task["subject"] != task_arranged[task["classschedule"]]["subject"]:
                    add_in_others = True
            else:
                add_new_subject = True
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
                # 新しい教科を追加
                task_arranged["others"].append({})
                task_arranged["others"][index]["subject"] = task["subject"]
                task_arranged["others"][index]["shortname"] = re.sub(
                    "\[.*\]", "", task["subject"])
                task_arranged["others"][index]["tasks"] = [task]

        elif add_new_subject == True:
            task_arranged[task["classschedule"]] = {}
            task_arranged[task["classschedule"]]["shorturl"] = ""
            task_arranged[task["classschedule"]]["subject"] = task["subject"]
            task_arranged[task["classschedule"]]["shortname"] = re.sub(
                "\[.*\]", "", task["subject"])
            task_arranged[task["classschedule"]]["tasks"] = [task]
        else:
            task_arranged[task["classschedule"]]["tasks"].append(task)
    return task_arranged


def add_student(studentid, fullname):
    students = session.query(student.Student.StudentID).all()
    isExist = False
    for i in students:
        i_str = str(i)
        i_str = i_str.replace('(', '')
        i_str = i_str.replace(')', '')
        i_str = i_str.replace('\'', '')
        i_str = i_str.replace(',', '')
        if i_str == studentid:
            isExist = True

    if isExist == False:
        new_student = student.Student()
        new_student.StudentID = studentid
        new_student.FullName = fullname

        session.add(new_student)
        session.commit()

    return


def add_assignment(assignmentid, assignmenturl,
                   title, limit_at, instructions, time_ms):
    assignments = session.query(assignment.Assignment.AssignmentID).all()
    isExist = False
    for i in assignments:
        i_str = str(i)
        i_str = i_str.replace('(', '')
        i_str = i_str.replace(')', '')
        i_str = i_str.replace('\'', '')
        i_str = i_str.replace(',', '')
        if i_str == assignmentid:
            isExist = True

    if isExist == False:
        new_assignment = assignment.Assignment()
        new_assignment.AssignmentID = assignmentid
        new_assignment.AssignmentUrl = assignmenturl
        new_assignment.Title = title
        new_assignment.Limit_at = limit_at
        new_assignment.Time_ms = floor(time_ms/1000)

        session.add(new_assignment)
        session.commit()

    return

def add_course(courseid, instructorid, \
                    coursename, yearsemester, classschedule):
    courses = session.query(course.Course.CourseID).all()
    isExist = False
    for i in courses:
        i_str = str(i)
        i_str = i_str.replace('(', '')
        i_str = i_str.replace(')', '')
        i_str = i_str.replace('\'', '')
        i_str = i_str.replace(',', '')
        if i_str == courseid:
            isExist = True

    if isExist == False:
        new_course = course.Course()
        new_course.CourseID = courseid
        new_course.InstructorID = instructorid
        new_course.CourseName = coursename
        new_course.YearSemester = yearsemester
        new_course.ClassSchedule = classschedule

        session.add(new_course)
        session.commit()

    return


def add_enrollment(assignmentid,
                   studentid, courseid, status):
    enrollments_assignmentid = session.query(
        enrollment.Enrollment.AssignmentID).all()
    enrollments_studentid = session.query(
        enrollment.Enrollment.StudentID).all()
    isExist_assignmentid = False
    isExist_studentid = False
    for i in enrollments_assignmentid:
        i_str = str(i)
        i_str = i_str.replace('(', '')
        i_str = i_str.replace(')', '')
        i_str = i_str.replace('\'', '')
        i_str = i_str.replace(',', '')
        if i_str == assignmentid:
            isExist_assignmentid = True

    if isExist_assignmentid:
        for i in enrollments_studentid:
            i_str = str(i)
            i_str = i_str.replace('(', '')
            i_str = i_str.replace(')', '')
            i_str = i_str.replace('\'', '')
            i_str = i_str.replace(',', '')
            if i_str == studentid:
                isExist_studentid = True

    if isExist_studentid == False:
        new_enrollment = enrollment.Enrollment()
        # new_enrollment.enrollmentID = enrollmentid
        new_enrollment.AssignmentID = assignmentid
        new_enrollment.StudentID = studentid
        new_enrollment.CourseID = courseid
        new_enrollment.Status = status

        session.add(new_enrollment)
        session.commit()

    return


def add_instructor(instructorid, fullname, emailaddress):
    instructors = session.query(instructor.Instructor.InstructorID).all()
    isExist = False
    for i in instructors:
        i_str = str(i)
        i_str = i_str.replace('(', '')
        i_str = i_str.replace(')', '')
        i_str = i_str.replace('\'', '')
        i_str = i_str.replace(',', '')
        if i_str == instructorid:
            isExist = True

    if isExist == False:
        new_instructor = instructor.Instructor()
        new_instructor.InstructorID = instructorid
        new_instructor.FullName = fullname
        new_instructor.EmailAddress = emailaddress

        session.add(new_instructor)
        session.commit()

    return

def add_enrollmentR(resourceurl, studentid, courseid, status):
    enrollments_resourceurl = session.query(enrollmentR.EnrollmentR.ResourceUrl).all()
    enrollments_studentid = session.query(enrollmentR.EnrollmentR.StudentID).all()
    isExist_resourceurl = False
    isExist_studentid = False
    for i in enrollments_resourceurl:
        i_str = str(i)
        i_str = i_str.replace('(','')
        i_str = i_str.replace(')','')
        i_str = i_str.replace('\'','')
        i_str = i_str.replace(',','')
        if i_str == resourceurl:
            isExist_resourceurl = True
        
    if isExist_resourceurl:
        for i in enrollments_studentid:
            i_str = str(i)
            i_str = i_str.replace('(','')
            i_str = i_str.replace(')','')
            i_str = i_str.replace('\'','')
            i_str = i_str.replace(',','')
            if i_str == studentid:
                isExist_studentid = True

    if isExist_studentid == False:
        new_enrollment = enrollment.Enrollment()
        # new_enrollment.enrollmentID = enrollmentid
        new_enrollment.ResourceUrl = resourceurl
        new_enrollment.StudentID = studentid
        new_enrollment.CourseID = courseid
        new_enrollment.Status = status

        session.add(new_enrollment)
        session.commit()
    
    return


def add_resource(resourceid, resourceurl, title, container, modifieddate):
    resources = session.query(resource.Resource.ResourceUrl).all()
    isExist = False
    for i in resources:
        i_str = str(i)
        i_str = i_str.replace('(','')
        i_str = i_str.replace(')','')
        i_str = i_str.replace('\'','')
        i_str = i_str.replace(',','')
        if i_str == resourceurl:
            isExist = True
    if isExist == False:
        new_resource = resource.Resource()
        # new_resource.ResourceID = resourceid
        new_resource.ResourceUrl = resourceurl
        new_resource.Title = title
        new_resource.Container = container
        new_resource.ModifiedDate = modifieddate

    return

def sort_tasks(tasks, show_only_unfinished = False, max_time_left = 1):
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


def remain_time(time_ms):
    ato = 'あと'
    now = floor(time.time())
    seconds = time_ms - now
    minutes = seconds/60
    hours = minutes/60
    days = hours/24
    weeks = days/7
    months = weeks/4

    if seconds < 0:
        return ''
    elif minutes < 1:
        return '1分未満'
    elif hours < 1:
        return ato + str(floor(minutes)) + '分'
    elif days < 1:
        return ato + str(floor(hours)) + '時間'
    elif weeks < 1:
        return ato + str(floor(days)) + '日'
    elif months < 1:
        remain_days = floor(days) - floor(weeks)*7
        if remain_days == 0:
            return ato + str(floor(weeks)) + '週間'
        else:
            return ato + str(floor(weeks)) + '週と' + \
                str(remain_days) + '日'
    else:
        return ato + '4週間以上'
