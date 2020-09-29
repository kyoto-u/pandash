from .models import student, assignment, course, enrollment, instructor
from .settings import session


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

def add_enrollment(enrollmentid, assignmentid, \
                    studentid, courseid, status):
    enrollments = session.query(enrollment.Enrollment).all()
    isExist = False
    for i in enrollments:
        i_str = str(i)
        i_str = i_str.replace('(','')
        i_str = i_str.replace(')','')
        i_str = i_str.replace('\'','')
        i_str = i_str.replace(',','')
        if i_str == enrollmentid:
            isExist = True

    if isExist == False:
        new_enrollment = enrollment.Enrollment()
        new_enrollment.enrollmentID = enrollmentid
        new_enrollment.assignmentID = assignmentid
        new_enrollment.StudentID = studentid
        new_enrollment.CourseID = courseid
        new_enrollment.Status = status

        session.add(new_student)
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