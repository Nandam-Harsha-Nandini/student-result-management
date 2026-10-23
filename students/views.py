import csv
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Q
from .models import Student, AcademicNotice, ReEvaluationRequest, UserProfile


def get_current_user_profile(user):
    if user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={"role": "faculty" if user.is_staff else "student"}
        )
        return profile
    return None


def home(request):
    """
    Public landing page for students, faculty, and institutional visitors.
    Includes quick roll number search, key statistics, grading scheme, and notices.
    """
    search_roll = request.GET.get("roll_number", "").strip()
    searched_student = None
    search_error = None

    if search_roll:
        try:
            searched_student = Student.objects.get(roll_number__iexact=search_roll)
        except Student.DoesNotExist:
            search_error = f"No student record found with Roll Number '{search_roll}'."

    total_students = Student.objects.count()
    all_students = list(Student.objects.all())

    pass_count = sum(1 for s in all_students if s.is_passed)
    pass_percentage = round((pass_count / total_students * 100), 1) if total_students > 0 else 0
    avg_percentage = round(sum(s.percentage for s in all_students) / total_students, 2) if total_students > 0 else 0
    top_score = max((s.percentage for s in all_students), default=0)
    distinction_count = sum(1 for s in all_students if s.is_passed and s.percentage >= 75)

    # Top 3 performers for preview podium
    top_students = sorted(all_students, key=lambda s: s.total, reverse=True)[:3]

    # Recent notices
    recent_notices = AcademicNotice.objects.all()[:4]

    context = {
        "total_students": total_students,
        "pass_count": pass_count,
        "pass_percentage": pass_percentage,
        "avg_percentage": avg_percentage,
        "top_score": top_score,
        "distinction_count": distinction_count,
        "top_students": top_students,
        "recent_notices": recent_notices,
        "searched_student": searched_student,
        "search_error": search_error,
        "search_roll": search_roll,
        "current_profile": get_current_user_profile(request.user),
    }
    return render(request, "students/home.html", context)


def dashboard(request):
    """
    Comprehensive analytics and management dashboard.
    Supports filtering by department, semester, result status, and search query.
    Shows Chart.js charts and student records with quick-action buttons.
    """
    query = request.GET.get("search", "").strip()
    dept_filter = request.GET.get("department", "").strip()
    sem_filter = request.GET.get("semester", "").strip()
    status_filter = request.GET.get("status", "").strip()

    students = Student.objects.all()

    if query:
        students = students.filter(
            Q(name__icontains=query) | Q(roll_number__icontains=query)
        )

    if dept_filter:
        students = students.filter(department=dept_filter)

    if sem_filter:
        students = students.filter(semester=sem_filter)

    all_students = list(Student.objects.all())
    total_count = len(all_students)

    passed_list = [s for s in all_students if s.is_passed]
    failed_list = [s for s in all_students if not s.is_passed]
    distinction_list = [s for s in passed_list if s.percentage >= 75]

    pass_rate = round((len(passed_list) / total_count * 100), 1) if total_count > 0 else 0
    avg_score = round(sum(s.percentage for s in all_students) / total_count, 2) if total_count > 0 else 0
    topper = max(all_students, key=lambda s: s.total) if all_students else None

    # Filter status in query set if specified
    student_list = list(students)
    if status_filter == "pass":
        student_list = [s for s in student_list if s.is_passed]
    elif status_filter == "fail":
        student_list = [s for s in student_list if not s.is_passed]
    elif status_filter == "distinction":
        student_list = [s for s in student_list if s.is_passed and s.percentage >= 75]

    # Chart data: Grade distribution
    grade_counts = {"A+": 0, "A": 0, "B+": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for s in all_students:
        g = s.grade
        if g in grade_counts:
            grade_counts[g] += 1
        else:
            grade_counts["F"] += 1

    # Subject averages
    sub_averages = {
        "Python": round(sum(s.python_marks for s in all_students) / total_count, 1) if total_count else 0,
        "Java": round(sum(s.java_marks for s in all_students) / total_count, 1) if total_count else 0,
        "DBMS": round(sum(s.dbms_marks for s in all_students) / total_count, 1) if total_count else 0,
        "Maths": round(sum(s.maths_marks for s in all_students) / total_count, 1) if total_count else 0,
        "English": round(sum(s.english_marks for s in all_students) / total_count, 1) if total_count else 0,
    }

    # If logged in user is a student, find their specific record
    student_record = None
    if request.user.is_authenticated:
        profile = get_current_user_profile(request.user)
        if profile and profile.roll_number:
            student_record = Student.objects.filter(roll_number__iexact=profile.roll_number).first()

    context = {
        "students": student_list,
        "total_students": total_count,
        "pass_count": len(passed_list),
        "fail_count": len(failed_list),
        "pass_rate": pass_rate,
        "avg_score": avg_score,
        "distinction_count": len(distinction_list),
        "topper": topper,
        "departments": Student.DEPARTMENT_CHOICES,
        "semesters": Student.SEMESTER_CHOICES,
        "selected_dept": dept_filter,
        "selected_sem": sem_filter,
        "selected_status": status_filter,
        "search_query": query,
        "grade_chart_labels": json.dumps(list(grade_counts.keys())),
        "grade_chart_data": json.dumps(list(grade_counts.values())),
        "subject_chart_labels": json.dumps(list(sub_averages.keys())),
        "subject_chart_data": json.dumps(list(sub_averages.values())),
        "student_record": student_record,
        "current_profile": get_current_user_profile(request.user),
    }
    return render(request, "students/dashboard.html", context)


def transcript(request, roll_number):
    """
    Official institutional transcript / digital marksheet view.
    Print-ready layout with university crest, subject breakdown, GPA, and validation seal.
    """
    student = get_object_or_404(Student, roll_number__iexact=roll_number)
    
    # Calculate rank among all students
    all_students_sorted = sorted(Student.objects.all(), key=lambda s: s.total, reverse=True)
    rank = 1
    for idx, s in enumerate(all_students_sorted):
        if s.id == student.id:
            rank = idx + 1
            break

    context = {
        "student": student,
        "rank": rank,
        "total_students": len(all_students_sorted),
        "subjects": student.subjects_list,
        "current_profile": get_current_user_profile(request.user),
    }
    return render(request, "students/transcript.html", context)


def history(request):
    """
    Examination History, batch archives, and past semester trends.
    """
    query = request.GET.get("search", "").strip()
    academic_year = request.GET.get("year", "2025-2026")
    semester = request.GET.get("semester", "")

    students = Student.objects.filter(academic_year=academic_year)
    if semester:
        students = students.filter(semester=semester)
    if query:
        students = students.filter(Q(name__icontains=query) | Q(roll_number__icontains=query))

    # Historical batch summaries
    all_years = ["2025-2026", "2024-2025", "2023-2024"]

    context = {
        "students": students,
        "all_years": all_years,
        "selected_year": academic_year,
        "selected_semester": semester,
        "search_query": query,
        "semesters": Student.SEMESTER_CHOICES,
        "total_batch_count": students.count(),
        "current_profile": get_current_user_profile(request.user),
    }
    return render(request, "students/history.html", context)


def leaderboard(request):
    """
    Academic Leaderboard & Merit List.
    Honors top performers with gold, silver, bronze medals and full rank list.
    """
    students = sorted(Student.objects.all(), key=lambda s: s.total, reverse=True)
    
    top_3 = students[:3] if len(students) >= 3 else students
    remaining = students[3:] if len(students) > 3 else []

    context = {
        "top_3": top_3,
        "remaining": remaining,
        "total_students": len(students),
        "current_profile": get_current_user_profile(request.user),
    }
    return render(request, "students/leaderboard.html", context)


def calculator(request):
    """
    Interactive GPA / CGPA Calculator and Target Simulator.
    """
    return render(request, "students/calculator.html", {
        "current_profile": get_current_user_profile(request.user)
    })


def notices_view(request):
    """
    Academic circulars and examination notifications board.
    Faculty can publish notices.
    """
    category = request.GET.get("category", "")
    notices = AcademicNotice.objects.all()

    if category:
        notices = notices.filter(category=category)

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Please log in as faculty to publish circulars.")
            return redirect("login")

        title = request.POST.get("title", "").strip()
        cat = request.POST.get("category", "General")
        content = request.POST.get("content", "").strip()
        is_pinned = "is_pinned" in request.POST

        if title and content:
            author_name = request.user.get_full_name() or request.user.username
            AcademicNotice.objects.create(
                title=title,
                category=cat,
                content=content,
                is_pinned=is_pinned,
                author=f"{author_name} (Faculty)"
            )
            messages.success(request, "Academic notice published successfully.")
            return redirect("notices")
        else:
            messages.error(request, "Please provide both title and description for the notice.")

    context = {
        "notices": notices,
        "selected_category": category,
        "categories": AcademicNotice.CATEGORY_CHOICES,
        "current_profile": get_current_user_profile(request.user),
    }
    return render(request, "students/notices.html", context)


def reevaluation_view(request):
    """
    Student re-evaluation and paper review request management.
    """
    if request.method == "POST":
        name = request.POST.get("student_name", "").strip()
        roll = request.POST.get("roll_number", "").strip()
        subject = request.POST.get("subject", "").strip()
        marks_str = request.POST.get("current_marks", "").strip()
        reason = request.POST.get("reason", "").strip()

        try:
            current_marks = float(marks_str)
            if not name or not roll or not subject or not reason:
                raise ValueError("All fields are mandatory.")
            
            ReEvaluationRequest.objects.create(
                student_name=name,
                roll_number=roll,
                subject=subject,
                current_marks=current_marks,
                reason=reason,
                status="Pending"
            )
            messages.success(request, f"Re-evaluation request for {subject} submitted successfully! Your tracking ID is recorded.")
            return redirect("reevaluation")
        except ValueError as e:
            messages.error(request, f"Invalid input: {e}")

    requests_list = ReEvaluationRequest.objects.all()
    context = {
        "requests": requests_list,
        "current_profile": get_current_user_profile(request.user),
    }
    return render(request, "students/reevaluation.html", context)


def student_add(request):
    """
    Add a new student result with validation.
    """
    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            roll_number = request.POST.get("roll_number", "").strip()
            department = request.POST.get("department", "Computer Science & Engineering")
            semester = request.POST.get("semester", "Semester 4")
            academic_year = request.POST.get("academic_year", "2025-2026")
            email = request.POST.get("email", "").strip()
            phone = request.POST.get("phone", "").strip()

            subjects = ["python_marks", "java_marks", "dbms_marks", "maths_marks", "english_marks"]
            marks = {}
            for sub in subjects:
                val = float(request.POST.get(sub, 0))
                if val < 0 or val > 100:
                    raise ValueError(f"Marks for {sub.replace('_', ' ')} must be between 0 and 100.")
                marks[sub] = val

            if not name or not roll_number:
                raise ValueError("Student Name and Roll Number are required.")

            if Student.objects.filter(roll_number__iexact=roll_number).exists():
                raise ValueError(f"Student with Roll Number '{roll_number}' already exists.")

            student = Student.objects.create(
                name=name,
                roll_number=roll_number,
                department=department,
                semester=semester,
                academic_year=academic_year,
                email=email,
                phone=phone,
                **marks
            )
            messages.success(request, f"Result for {student.name} ({student.roll_number}) added successfully!")
            return redirect("dashboard")

        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            messages.error(request, f"Unable to save record: {e}")

    return render(request, "students/student_form.html", {
        "action": "Add",
        "departments": Student.DEPARTMENT_CHOICES,
        "semesters": Student.SEMESTER_CHOICES,
        "current_profile": get_current_user_profile(request.user),
    })


def student_edit(request, student_id):
    """
    Edit marks and details for an existing student.
    """
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            department = request.POST.get("department", student.department)
            semester = request.POST.get("semester", student.semester)
            email = request.POST.get("email", "").strip()
            phone = request.POST.get("phone", "").strip()

            subjects = ["python_marks", "java_marks", "dbms_marks", "maths_marks", "english_marks"]
            for sub in subjects:
                val = float(request.POST.get(sub, getattr(student, sub)))
                if val < 0 or val > 100:
                    raise ValueError(f"Marks must be between 0 and 100.")
                setattr(student, sub, val)

            if not name:
                raise ValueError("Name cannot be blank.")

            student.name = name
            student.department = department
            student.semester = semester
            student.email = email
            student.phone = phone
            student.save()

            messages.success(request, f"Student {student.name} ({student.roll_number}) updated successfully!")
            return redirect("dashboard")

        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            messages.error(request, f"Error saving update: {e}")

    return render(request, "students/student_form.html", {
        "action": "Edit",
        "student": student,
        "departments": Student.DEPARTMENT_CHOICES,
        "semesters": Student.SEMESTER_CHOICES,
        "current_profile": get_current_user_profile(request.user),
    })


def student_delete(request, student_id):
    """
    Delete student record with confirmation.
    """
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        name = student.name
        roll = student.roll_number
        student.delete()
        messages.success(request, f"Student record {name} ({roll}) has been deleted.")
    return redirect("dashboard")


def export_csv(request):
    """
    Export all student results as a downloadable CSV report.
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Apex_University_Student_Results.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Roll Number", "Student Name", "Department", "Semester", "Academic Year",
        "Python", "Java", "DBMS", "Maths", "English",
        "Total (500)", "Percentage (%)", "SGPA", "Grade", "Result Status", "Division"
    ])

    for s in Student.objects.all():
        writer.writerow([
            s.roll_number,
            s.name,
            s.department,
            s.semester,
            s.academic_year,
            s.python_marks,
            s.java_marks,
            s.dbms_marks,
            s.maths_marks,
            s.english_marks,
            s.total,
            s.percentage,
            s.gpa,
            s.grade,
            s.result_status,
            s.division
        ])

    return response


def user_login(request):
    """
    Login page with support for student and faculty roles, plus 1-click demo login.
    """
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        role_type = request.POST.get("role_type", "faculty")
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            profile, _ = UserProfile.objects.get_or_create(user=user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}! Logged in as {profile.get_role_display()}.")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password. Try the 1-click Demo accounts below!")

    return render(request, "students/login.html")


def user_signup(request):
    """
    Registration page allowing students and faculty to create portal accounts.
    """
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        role = request.POST.get("role", "student")
        roll_number = request.POST.get("roll_number", "").strip()
        department = request.POST.get("department", "Computer Science & Engineering")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "students/signup.html", {"departments": Student.DEPARTMENT_CHOICES})

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return render(request, "students/signup.html", {"departments": Student.DEPARTMENT_CHOICES})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        if role == "faculty":
            user.is_staff = True
            user.save()

        UserProfile.objects.create(
            user=user,
            role=role,
            roll_number=roll_number if role == "student" else "",
            department=department
        )

        login(request, user)
        messages.success(request, f"Account created successfully! Welcome to EduMatrix, {user.username}.")
        return redirect("dashboard")

    return render(request, "students/signup.html", {
        "departments": Student.DEPARTMENT_CHOICES
    })


def user_logout(request):
    """
    Log out user and redirect to home.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("home")


def quick_search_api(request):
    """
    Instant JSON search API for the roll number search box.
    """
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"results": []})

    results = []
    students = Student.objects.filter(
        Q(roll_number__icontains=query) | Q(name__icontains=query)
    )[:5]

    for s in students:
        results.append({
            "name": s.name,
            "roll_number": s.roll_number,
            "percentage": s.percentage,
            "grade": s.grade,
            "status": s.result_status,
            "department": s.department,
            "url": f"/transcript/{s.roll_number}/"
        })

    return JsonResponse({"results": results})