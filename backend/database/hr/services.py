"""
Reusable business-logic helpers for Dayflow HRMS.

Keep functions focused — only logic that is shared or non-trivial lives here.
"""
from datetime import date

from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.utils import timezone

from hr.models import (
    User, EmployeeProfile, Attendance, LeaveRequest,
    Payroll, Notification,
)


# ── Auth ──────────────────────────────────────────────────────────────────

def create_employee(*, employee_id, email, password, role, first_name, last_name):
    """
    Create a User + blank EmployeeProfile in one step.
    Returns (user, profile).
    Raises IntegrityError on duplicate employee_id/email.
    """
    user = User.objects.create(
        employee_id=employee_id,
        email=email,
        password_hash=make_password(password),
        role=role,
        is_verified=True,   # MVP: auto-verified
    )
    profile = EmployeeProfile.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
    )
    return user, profile


# ── Attendance ────────────────────────────────────────────────────────────

def check_in_employee(profile: EmployeeProfile):
    """
    Create today's attendance with check_in = now, status = PRESENT.
    Returns (attendance, created).
    Raises IntegrityError if already checked in today.
    """
    now = timezone.now()
    today = now.date()

    att, created = Attendance.objects.get_or_create(
        employee=profile,
        attendance_date=today,
        defaults={
            'check_in': now,
            'status': 'PRESENT',
        },
    )
    if not created:
        raise IntegrityError('Already checked in today.')
    return att, created


def check_out_employee(profile: EmployeeProfile):
    """
    Set check_out on today's attendance.
    Returns the updated attendance record.
    """
    today = date.today()
    try:
        att = Attendance.objects.get(employee=profile, attendance_date=today)
    except Attendance.DoesNotExist:
        raise ValueError('No check-in found for today.')

    if att.check_in is None:
        raise ValueError('Cannot check out without checking in first.')
    if att.check_out is not None:
        raise ValueError('Already checked out today.')

    att.check_out = timezone.now()
    att.save()
    return att


# ── Leave ─────────────────────────────────────────────────────────────────

def submit_leave_request(profile, *, leave_type, start_date, end_date, remarks=''):
    """Create a PENDING leave request for the employee."""
    leave = LeaveRequest.objects.create(
        employee=profile,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        remarks=remarks,
        status='PENDING',
    )
    return leave


def approve_leave_request(leave: LeaveRequest, reviewer: User, comment: str = ''):
    """Approve a PENDING leave request."""
    if leave.status != 'PENDING':
        raise ValueError(f'Cannot approve a leave request that is {leave.status}.')

    leave.status = 'APPROVED'
    leave.reviewed_by = reviewer
    leave.reviewed_at = timezone.now()
    leave.admin_comment = comment
    leave.save()

    # Notify the employee
    _create_notification(
        user_id=leave.employee.user_id,
        title='Leave Approved',
        message=f'Your {leave.leave_type} leave ({leave.start_date} to {leave.end_date}) has been approved.',
        notification_type='LEAVE',
    )
    return leave


def reject_leave_request(leave: LeaveRequest, reviewer: User, comment: str = ''):
    """Reject a PENDING leave request."""
    if leave.status != 'PENDING':
        raise ValueError(f'Cannot reject a leave request that is {leave.status}.')

    leave.status = 'REJECTED'
    leave.reviewed_by = reviewer
    leave.reviewed_at = timezone.now()
    leave.admin_comment = comment
    leave.save()

    _create_notification(
        user_id=leave.employee.user_id,
        title='Leave Rejected',
        message=f'Your {leave.leave_type} leave ({leave.start_date} to {leave.end_date}) has been rejected.',
        notification_type='LEAVE',
    )
    return leave


# ── Payroll ───────────────────────────────────────────────────────────────

def update_payroll(payroll: Payroll, *, basic_salary, allowances, deductions, effective_from):
    """Update salary structure — net_salary is computed in model save()."""
    payroll.basic_salary = basic_salary
    payroll.allowances = allowances
    payroll.deductions = deductions
    payroll.effective_from = effective_from
    payroll.save()  # triggers net_salary computation
    return payroll


# ── Helpers ───────────────────────────────────────────────────────────────

def _create_notification(*, user_id, title, message, notification_type='SYSTEM'):
    Notification.objects.create(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
    )
