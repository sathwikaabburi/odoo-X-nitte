from django.contrib import admin
from .models import (
    User, Department, EmployeeProfile, Attendance,
    LeaveRequest, Payroll, Document, Notification,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'email', 'role', 'is_verified', 'is_active')
    list_filter = ('role', 'is_verified', 'is_active')
    search_fields = ('employee_id', 'email')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'department', 'designation', 'joining_date')
    list_filter = ('department', 'gender')
    search_fields = ('first_name', 'last_name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'attendance_date', 'status', 'check_in', 'check_out')
    list_filter = ('status', 'attendance_date')
    search_fields = ('employee__first_name', 'employee__last_name')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'reviewed_by')
    list_filter = ('status', 'leave_type')


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'basic_salary', 'allowances', 'deductions', 'net_salary', 'effective_from')
    search_fields = ('employee__first_name', 'employee__last_name')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'document_type', 'document_name', 'uploaded_at')
    list_filter = ('document_type',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'notification_type')
