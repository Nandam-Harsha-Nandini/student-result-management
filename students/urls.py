from django.urls import path
from . import views

urlpatterns = [
    # Core navigation modules
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("transcript/<str:roll_number>/", views.transcript, name="transcript"),
    path("history/", views.history, name="history"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("calculator/", views.calculator, name="calculator"),
    path("notices/", views.notices_view, name="notices"),
    path("reevaluation/", views.reevaluation_view, name="reevaluation"),

    # Student Result Management (CRUD)
    path("student/add/", views.student_add, name="student_add"),
    path("student/edit/<int:student_id>/", views.student_edit, name="student_edit"),
    path("student/delete/<int:student_id>/", views.student_delete, name="student_delete"),
    path("export-csv/", views.export_csv, name="export_csv"),

    # User Authentication & Role Management
    path("login/", views.user_login, name="login"),
    path("signup/", views.user_signup, name="signup"),
    path("logout/", views.user_logout, name="logout"),

    # Instant Roll Number Search API
    path("api/quick-search/", views.quick_search_api, name="quick_search_api"),
]