from .models import student
from .settings import session


def student_add(studentid, fullname):
    students = session.query(student.Student).all()
    for st in students:
        if st.StudentID == studentid:
            continue
        else:
            new_student = student.Student()
            new_student.StudentID = studentid
            new_student.FullName = fullname

            session.add(new_student)
            session.commit()
            return


