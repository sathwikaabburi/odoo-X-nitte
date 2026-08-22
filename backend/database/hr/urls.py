"""
HR app URL configuration — all /api/ routes.
"""
from django.urls import path

from hr.views import (
    # Auth
    SignupView, LoginView, LogoutView, MeView,
    # Employee
    EmployeeListView, EmployeeDetailView,
    # Attendance
    CheckInView, CheckOutView, AttendanceListView, AttendanceWeeklyView,
    # Leave
    LeaveListCreateView, LeaveDetailView, LeaveApproveView, LeaveRejectView,
    # Payroll
    PayrollListView, PayrollDetailView,
    # Documents
    DocumentListCreateView, DocumentDeleteView,
    # Notifications
    NotificationListView, NotificationReadView,
    # Dashboard
    EmployeeDashboardView, AdminDashboardView,
    # Departments
    DepartmentListView,
)

urlpatterns = [
    # ── Auth ──
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', MeView.as_view(), name='me'),

    # ── Employees ──
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),

    # ── Attendance ──
    path('attendance/check-in/', CheckInView.as_view(), name='check-in'),
    path('attendance/check-out/', CheckOutView.as_view(), name='check-out'),
    path('attendance/', AttendanceListView.as_view(), name='attendance-list'),
    path('attendance/weekly/', AttendanceWeeklyView.as_view(), name='attendance-weekly'),

    # ── Leave ──
    path('leaves/', LeaveListCreateView.as_view(), name='leave-list-create'),
    path('leaves/<int:pk>/', LeaveDetailView.as_view(), name='leave-detail'),
    path('leaves/<int:pk>/approve/', LeaveApproveView.as_view(), name='leave-approve'),
    path('leaves/<int:pk>/reject/', LeaveRejectView.as_view(), name='leave-reject'),

    # ── Payroll ──
    path('payroll/', PayrollListView.as_view(), name='payroll-list'),
    path('payroll/<int:pk>/', PayrollDetailView.as_view(), name='payroll-detail'),

    # ── Documents ──
    path('documents/', DocumentListCreateView.as_view(), name='document-list-create'),
    path('documents/<int:pk>/', DocumentDeleteView.as_view(), name='document-delete'),

    # ── Notifications ──
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', NotificationReadView.as_view(), name='notification-read'),

    # ── Dashboard ──
    path('dashboard/employee/', EmployeeDashboardView.as_view(), name='dashboard-employee'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='dashboard-admin'),

    # ── Departments ──
    path('departments/', DepartmentListView.as_view(), name='department-list'),
]
