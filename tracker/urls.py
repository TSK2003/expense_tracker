from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_create, name='student_create'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.attendance_create, name='attendance_create'),
    path('attendance/mark-day/', views.attendance_mark_day, name='attendance_mark_day'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_create, name='expense_create'),
    path('expenses/export/', views.expense_export_csv, name='expense_export_csv'),
]
