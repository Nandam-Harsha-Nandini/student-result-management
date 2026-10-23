import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.contrib.auth.models import User
from students.models import Student, AcademicNotice, ReEvaluationRequest, UserProfile

def seed():
    print("Clearing and seeding demonstration records...")

    # Create faculty user
    faculty_user, created = User.objects.get_or_create(username="faculty", defaults={"email": "faculty@apexuniv.edu"})
    if created or not faculty_user.check_password("faculty123"):
        faculty_user.set_password("faculty123")
        faculty_user.first_name = "Dr. Rajesh"
        faculty_user.last_name = "Sharma"
        faculty_user.is_staff = True
        faculty_user.save()
    
    UserProfile.objects.update_or_create(
        user=faculty_user,
        defaults={
            "role": "faculty",
            "department": "Computer Science & Engineering",
            "phone": "+91 98765 43210"
        }
    )

    # Create student user
    student_user, created = User.objects.get_or_create(username="student", defaults={"email": "aarav.patel@student.edu"})
    if created or not student_user.check_password("student123"):
        student_user.set_password("student123")
        student_user.first_name = "Aarav"
        student_user.last_name = "Patel"
        student_user.save()

    UserProfile.objects.update_or_create(
        user=student_user,
        defaults={
            "role": "student",
            "roll_number": "2024CS01",
            "department": "Computer Science & Engineering",
            "phone": "+91 98111 22334"
        }
    )

    # Create admin user
    admin_user, created = User.objects.get_or_create(username="admin", defaults={"email": "admin@apexuniv.edu"})
    if created or not admin_user.check_password("admin123"):
        admin_user.set_password("admin123")
        admin_user.first_name = "University"
        admin_user.last_name = "Registrar"
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

    UserProfile.objects.update_or_create(
        user=admin_user,
        defaults={
            "role": "admin",
            "department": "Academic Affairs",
            "phone": "+91 99000 11223"
        }
    )

    # Seed students
    sample_students = [
        {
            "name": "Aarav Patel",
            "roll_number": "2024CS01",
            "department": "Computer Science & Engineering",
            "semester": "Semester 4",
            "academic_year": "2025-2026",
            "email": "aarav.patel@student.edu",
            "phone": "+91 98111 22334",
            "python_marks": 96.0,
            "java_marks": 92.5,
            "dbms_marks": 94.0,
            "maths_marks": 98.0,
            "english_marks": 89.0,
        },
        {
            "name": "Ananya Iyer",
            "roll_number": "2024CS02",
            "department": "Computer Science & Engineering",
            "semester": "Semester 4",
            "academic_year": "2025-2026",
            "email": "ananya.iyer@student.edu",
            "phone": "+91 98222 33445",
            "python_marks": 91.0,
            "java_marks": 88.0,
            "dbms_marks": 95.0,
            "maths_marks": 94.0,
            "english_marks": 92.0,
        },
        {
            "name": "Rohan Deshmukh",
            "roll_number": "2024CS03",
            "department": "Computer Science & Engineering",
            "semester": "Semester 4",
            "academic_year": "2025-2026",
            "email": "rohan.d@student.edu",
            "phone": "+91 98333 44556",
            "python_marks": 84.0,
            "java_marks": 79.0,
            "dbms_marks": 82.5,
            "maths_marks": 88.0,
            "english_marks": 81.0,
        },
        {
            "name": "Priya Nair",
            "roll_number": "2024IT01",
            "department": "Information Technology",
            "semester": "Semester 4",
            "academic_year": "2025-2026",
            "email": "priya.nair@student.edu",
            "phone": "+91 98444 55667",
            "python_marks": 89.0,
            "java_marks": 91.0,
            "dbms_marks": 86.0,
            "maths_marks": 75.0,
            "english_marks": 88.0,
        },
        {
            "name": "Kabir Verma",
            "roll_number": "2024IT02",
            "department": "Information Technology",
            "semester": "Semester 4",
            "academic_year": "2025-2026",
            "email": "kabir.v@student.edu",
            "phone": "+91 98555 66778",
            "python_marks": 72.0,
            "java_marks": 68.0,
            "dbms_marks": 74.0,
            "maths_marks": 65.0,
            "english_marks": 70.0,
        },
        {
            "name": "Sneha Kulkarni",
            "roll_number": "2024EC01",
            "department": "Electronics & Communication",
            "semester": "Semester 4",
            "academic_year": "2025-2026",
            "email": "sneha.k@student.edu",
            "phone": "+91 98666 77889",
            "python_marks": 80.0,
            "java_marks": 75.0,
            "dbms_marks": 78.0,
            "maths_marks": 90.0,
            "english_marks": 85.0,
        },
        {
            "name": "Vikram Singh",
            "roll_number": "2024ME01",
            "department": "Mechanical Engineering",
            "semester": "Semester 4",
            "academic_year": "2025-2026",
            "email": "vikram.s@student.edu",
            "phone": "+91 98777 88990",
            "python_marks": 58.0,
            "java_marks": 54.0,
            "dbms_marks": 62.0,
            "maths_marks": 50.0,
            "english_marks": 64.0,
        },
        {
            "name": "Devansh Gupta",
            "roll_number": "2024CS04",
            "department": "Computer Science & Engineering",
            "semester": "Semester 4",
            "academic_year": "2025-2026",
            "email": "devansh.g@student.edu",
            "phone": "+91 98888 99001",
            "python_marks": 45.0,
            "java_marks": 32.0,  # arrear in java
            "dbms_marks": 50.0,
            "maths_marks": 30.0,  # arrear in maths
            "english_marks": 55.0,
        },
    ]

    for item in sample_students:
        Student.objects.update_or_create(
            roll_number=item["roll_number"],
            defaults=item
        )

    # Seed Academic Notices
    notices = [
        {
            "title": "Spring Semester 2026 Examination Results Officially Published",
            "category": "Result",
            "content": "The Controller of Examinations has published the provisional results for B.Tech / BE Semester 4 examinations. Students can check their digital marksheet online and apply for revaluation before the deadline.",
            "is_pinned": True,
            "author": "Controller of Examinations"
        },
        {
            "title": "Application Window for Paper Re-evaluation and Retotaling",
            "category": "Reval",
            "content": "Students dissatisfied with their evaluation may submit a re-evaluation request through the student portal within 15 days of result publication. A non-refundable processing fee of ₹300 per subject applies.",
            "is_pinned": True,
            "author": "Academic Evaluation Cell"
        },
        {
            "title": "Annual Academic Excellence Awards & Merit List Announcement",
            "category": "Event",
            "content": "Congratulations to department toppers! The annual dean's medal and merit certificates ceremony will take place next month in the main auditorium. Top 5 students from each stream are requested to verify their records.",
            "is_pinned": False,
            "author": "Dean of Academic Affairs"
        },
        {
            "title": "Supplementary / Arrear Examination Schedule for Autumn Term",
            "category": "Exam",
            "content": "Students with backlogs or arrears are advised that supplementary examination timetables will be released shortly. Hall tickets can be downloaded starting next Monday.",
            "is_pinned": False,
            "author": "Exam Registration Office"
        }
    ]

    for n in notices:
        AcademicNotice.objects.get_or_create(title=n["title"], defaults=n)

    # Seed a sample re-evaluation request
    ReEvaluationRequest.objects.get_or_create(
        roll_number="2024CS04",
        subject="Java Architecture",
        defaults={
            "student_name": "Devansh Gupta",
            "current_marks": 32.0,
            "reason": "Submitted full answers for Section B question 4 and 5; requesting reassessment of practical and theoretical parts.",
            "status": "In Review"
        }
    )

    print("Database successfully seeded with realistic academic records, users, notices and requests!")

if __name__ == "__main__":
    seed()
