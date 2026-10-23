from django.contrib import admin
from .models import Student, AcademicNotice, ReEvaluationRequest, UserProfile


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "roll_number",
        "name",
        "department",
        "semester",
        "total",
        "percentage",
        "gpa",
        "grade",
        "result_status",
    )
    list_filter = ("department", "semester", "academic_year")
    search_fields = ("roll_number", "name", "email")
    ordering = ("-id",)


@admin.register(AcademicNotice)
class AcademicNoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "published_date", "is_pinned")
    list_filter = ("category", "is_pinned")
    search_fields = ("title", "content")


@admin.register(ReEvaluationRequest)
class ReEvaluationRequestAdmin(admin.ModelAdmin):
    list_display = ("roll_number", "student_name", "subject", "current_marks", "status", "submitted_at")
    list_filter = ("status", "subject")
    search_fields = ("roll_number", "student_name", "reason")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "roll_number", "department")
    list_filter = ("role", "department")
    search_fields = ("user__username", "roll_number")
