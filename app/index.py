from .models import student, assignment, course, enrollment, instructor
from .settings import session


def student_add(studentid, fullname):
    students = session.query(student.Student.StudentID).all()
    isExist = False
    print(students)
    print(type(students))
    for st in students:
        st_str = str(st)
        st_str = st_str.replace('(','')
        st_str = st_str.replace(')','')
        st_str = st_str.replace('\'','')
        st_str = st_str.replace(',','')
        if st_str == studentid:
            isExist = True

    if isExist == False:
        new_student = student.Student()
        new_student.StudentID = studentid
        new_student.FullName = fullname

        session.add(new_student)
        session.commit()
    
    return
