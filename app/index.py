from .models import student, assignment, course, enrollment, instructor
from .settings import session



def get_tasklist(studentid):
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

    enrollments = session.query(enrollment.Enrollment).filter(enrollment.Enrollment.StudentID == studentid).all()
    tasks=[]
    for data in enrollments:
        task={}
        task["status"]=data.Status
        assignmentdata = session.query(assignment.Assignment).filter(assignment.Assignment.AssignmentID == data.AssignmentID).all()
        task["taskname"] = assignmentdata[0].Title
        task["deadline"] = assignmentdata[0].Limit_at
        task["time_left"] = remain_time(assignmentdata[0].Time_ms)
        coursedata = session.query(course.Course).filter(course.Course.CourseID == data.CourseID).all()
        task["subject"] = coursedata[0].CourseName
        tasks.append(task)
    return tasks


def add_student(studentid, fullname):
    students = session.query(student.Student.StudentID).all()
    isExist = False
    for i in students:
        i_str = str(i)
        i_str = i_str.replace('(','')
        i_str = i_str.replace(')','')
        i_str = i_str.replace('\'','')
        i_str = i_str.replace(',','')
        if i_str == studentid:
            isExist = True

    if isExist == False:
        new_student = student.Student()
        new_student.StudentID = studentid
        new_student.FullName = fullname

        session.add(new_student)
        session.commit()

    return

def add_assignment(assignmentid, assignmenturl, \
                    title, limit_at, instructions):
    assignments = session.query(assignment.Assignment.AssignmentID).all()
    isExist = False
    for i in assignments:
        i_str = str(i)
        i_str = i_str.replace('(','')
        i_str = i_str.replace(')','')
        i_str = i_str.replace('\'','')
        i_str = i_str.replace(',','')
        if i_str == assignmentid:
            isExist = True

    if isExist == False:
        new_assignment = assignment.Assignment()
        new_assignment.AssignmentID = assignmentid
        new_assignment.AssignmentUrl = assignmenturl
        new_assignment.Title = title
        new_assignment.Limit_at = limit_at

        session.add(new_assignment)
        session.commit()
    
    return

def add_course(courseid, instructorid, \
                    coursename, classschedule):
    courses = session.query(course.Course.CourseID).all()
    isExist = False
    for i in courses:
        i_str = str(i)
        i_str = i_str.replace('(','')
        i_str = i_str.replace(')','')
        i_str = i_str.replace('\'','')
        i_str = i_str.replace(',','')
        if i_str == courseid:
            isExist = True

    if isExist == False:
        new_course = course.Course()
        new_course.CourseID = courseid
        new_course.InstructorID = instructorid
        new_course.CourseName = coursename
        new_course.ClassSchedule = classschedule

        session.add(new_course)
        session.commit()
    
    return

def add_enrollment(assignmentid, \
                    studentid, courseid, status):
    enrollments_assignmentid = session.query(enrollment.Enrollment.AssignmentID).all()
    enrollments_studentid = session.query(enrollment.Enrollment.StudentID).all()
    isExist_assignmentid = False
    isExist_studentid = False
    for i in enrollments_assignmentid:
        i_str = str(i)
        i_str = i_str.replace('(','')
        i_str = i_str.replace(')','')
        i_str = i_str.replace('\'','')
        i_str = i_str.replace(',','')
        if i_str == assignmentid:
            isExist_assignmentid = True
        
    if isExist_assignmentid:
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
        i_str = i_str.replace('(','')
        i_str = i_str.replace(')','')
        i_str = i_str.replace('\'','')
        i_str = i_str.replace(',','')
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

def sort_tasks(tasks, show_only_unfinished = False, max_time_left = 1):
    """
        about max_time_left
        0:an hour
        1:a day
        2:a week
    """
    if show_only_unfinished == True:
        tasks = [task for task in tasks if task["status"] == "未"]     
    if max_time_left in [0,1,2]:
        tasks = [task for task in tasks if timejudge(task,max_time_left)]
    tasks = sorted(tasks, key=lambda x: x["deadline"])
    tasks = sorted(tasks, key=lambda x: order_status(x["status"]))
    return tasks

def timejudge(task,max_time_left):
    # ex あと10分
    time_left = task["time_left"]
    units = ["minute","分","hour","時","day","日"]
    u_num=0
    if max_time_left == 0:
        u_num =2
    elif max_time_left == 1:
        u_num =4
    else:
        u_num =6
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

from math import *
def remain_time(time_ms):
    ato = 'あと'
    seconds = time_ms/1000
    minutes = seconds/60
    hours = minutes/60
    days = hours/24
    weeks = days/7
    months = weeks/4

    if minutes < 1:
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
