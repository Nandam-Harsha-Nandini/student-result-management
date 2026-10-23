from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    DEPARTMENT_CHOICES = [
        ("Computer Science & Engineering", "Computer Science & Engineering"),
        ("Information Technology", "Information Technology"),
        ("Electronics & Communication", "Electronics & Communication"),
        ("Mechanical Engineering", "Mechanical Engineering"),
        ("Civil Engineering", "Civil Engineering"),
        ("Business Administration", "Business Administration"),
    ]

    SEMESTER_CHOICES = [
        ("Semester 1", "Semester 1"),
        ("Semester 2", "Semester 2"),
        ("Semester 3", "Semester 3"),
        ("Semester 4", "Semester 4"),
        ("Semester 5", "Semester 5"),
        ("Semester 6", "Semester 6"),
        ("Semester 7", "Semester 7"),
        ("Semester 8", "Semester 8"),
    ]

    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,
        default="Computer Science & Engineering",
    )
    semester = models.CharField(
        max_length=20,
        choices=SEMESTER_CHOICES,
        default="Semester 4",
    )
    academic_year = models.CharField(max_length=20, default="2025-2026")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    python_marks = models.FloatField()
    java_marks = models.FloatField()
    dbms_marks = models.FloatField()
    maths_marks = models.FloatField()
    english_marks = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} ({self.roll_number})"

    @property
    def total(self):
        return (
            self.python_marks
            + self.java_marks
            + self.dbms_marks
            + self.maths_marks
            + self.english_marks
        )

    @property
    def percentage(self):
        return round(self.total / 5.0, 2)

    @staticmethod
    def get_subject_grade(marks):
        if marks >= 90:
            return "A+", 10.0
        elif marks >= 80:
            return "A", 9.0
        elif marks >= 70:
            return "B+", 8.0
        elif marks >= 60:
            return "B", 7.0
        elif marks >= 50:
            return "C", 6.0
        elif marks >= 35:
            return "D", 5.0
        else:
            return "F", 0.0

    @property
    def is_passed(self):
        return all(
            m >= 35
            for m in [
                self.python_marks,
                self.java_marks,
                self.dbms_marks,
                self.maths_marks,
                self.english_marks,
            ]
        )

    @property
    def result_status(self):
        return "Pass" if self.is_passed else "Fail"

    @property
    def grade(self):
        if not self.is_passed:
            return "F"
        p = self.percentage
        if p >= 90:
            return "A+"
        elif p >= 80:
            return "A"
        elif p >= 70:
            return "B+"
        elif p >= 60:
            return "B"
        elif p >= 50:
            return "C"
        else:
            return "D"

    @property
    def gpa(self):
        if not self.is_passed:
            return 0.0
        # Average grade points out of 10
        gp_list = [
            self.get_subject_grade(self.python_marks)[1],
            self.get_subject_grade(self.java_marks)[1],
            self.get_subject_grade(self.dbms_marks)[1],
            self.get_subject_grade(self.maths_marks)[1],
            self.get_subject_grade(self.english_marks)[1],
        ]
        return round(sum(gp_list) / 5.0, 2)

    @property
    def division(self):
        if not self.is_passed:
            return "Arrear / Needs Improvement"
        p = self.percentage
        if p >= 75:
            return "First Class with Distinction"
        elif p >= 60:
            return "First Class"
        elif p >= 50:
            return "Second Class"
        else:
            return "Pass Class"

    @property
    def subjects_list(self):
        subjects = [
            {"code": "CS401", "name": "Python Programming", "marks": self.python_marks, "credits": 4},
            {"code": "CS402", "name": "Java Architecture", "marks": self.java_marks, "credits": 4},
            {"code": "CS403", "name": "Database Management (DBMS)", "marks": self.dbms_marks, "credits": 3},
            {"code": "MA404", "name": "Discrete Mathematics", "marks": self.maths_marks, "credits": 4},
            {"code": "HS405", "name": "Technical English", "marks": self.english_marks, "credits": 3},
        ]
        for sub in subjects:
            grd, gp = self.get_subject_grade(sub["marks"])
            sub["grade"] = grd
            sub["grade_point"] = gp
            sub["passed"] = sub["marks"] >= 35
        return subjects


class AcademicNotice(models.Model):
    CATEGORY_CHOICES = [
        ("Exam", "Examination"),
        ("Result", "Result Declaration"),
        ("Reval", "Re-evaluation"),
        ("General", "General Notice"),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="General")
    content = models.TextField()
    published_date = models.DateField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)
    author = models.CharField(max_length=100, default="Examination Cell")

    class Meta:
        ordering = ["-is_pinned", "-published_date", "-id"]

    def __str__(self):
        return self.title


class ReEvaluationRequest(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending Review"),
        ("In Review", "In Review"),
        ("Approved", "Score Revised"),
        ("Rejected", "No Change (Verified)"),
    ]

    student_name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    subject = models.CharField(max_length=100)
    current_marks = models.FloatField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.roll_number} - {self.subject} ({self.status})"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("faculty", "Faculty / Examiner"),
        ("student", "Student"),
        ("admin", "College Management"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    roll_number = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
