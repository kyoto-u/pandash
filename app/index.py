from .models import student
from .settings import session


student = student.Student()
student.StudentID = '0000'
student.FullName = 'kita'

session.add(student)
session.commit()



