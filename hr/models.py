import os
from decimal import Decimal

from django.db import models
from django.db.models import F, Q
from django.core.validators import MinValueValidator


# ---------------------------------------------------------------------------
# 1. users
# ---------------------------------------------------------------------------
class User(models.Model):
    """Authentication / account / role table."""

    class Role(models.TextChoices):
        EMPLOYEE = 'EMPLOYEE'
        HR = 'HR'
        ADMIN = 'ADMIN'

    id = models.BigAutoField(primary_key=True)
    employee_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.TextField()
    role = models.CharField(max_length=20, choices=Role.choices)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email'], name='idx_users_email'),
            models.Index(fields=['employee_id'], name='idx_users_employee_id'),
            models.Index(fields=['role'], name='idx_users_role'),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(role__in=['EMPLOYEE', 'HR', 'ADMIN']),
                name='users_role_valid',
            ),
        ]

    def __str__(self):
        return f"{self.employee_id} ({self.email})"


# ---------------------------------------------------------------------------
# 2. departments
# ---------------------------------------------------------------------------
class Department(models.Model):
    """Company department."""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'departments'

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# 3. employee_profiles
# ---------------------------------------------------------------------------
class EmployeeProfile(models.Model):
    """Personal and job information — one‑to‑one with User."""

    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile',
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_picture = models.TextField(null=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='employees',
    )
    designation = models.CharField(max_length=100, null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'employee_profiles'
        indexes = [
            models.Index(fields=['department'], name='idx_ep_department'),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ---------------------------------------------------------------------------
# 4. attendance
# ---------------------------------------------------------------------------
class Attendance(models.Model):
    """Daily employee attendance record."""

    class Status(models.TextChoices):
        PRESENT = 'PRESENT'
        ABSENT = 'ABSENT'
        HALF_DAY = 'HALF_DAY'
        LEAVE = 'LEAVE'

    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    attendance_date = models.DateField()
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices)
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance'
        unique_together = ('employee', 'attendance_date')
        indexes = [
            models.Index(fields=['attendance_date'], name='idx_att_date'),
            models.Index(fields=['status'], name='idx_att_status'),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(status__in=['PRESENT', 'ABSENT', 'HALF_DAY', 'LEAVE']),
                name='attendance_status_valid',
            ),
        ]

    def __str__(self):
        return f"{self.employee} — {self.attendance_date}"


# ---------------------------------------------------------------------------
# 5. leave_requests
# ---------------------------------------------------------------------------
class LeaveRequest(models.Model):
    """Employee leave application with HR / Admin approval."""

    class LeaveType(models.TextChoices):
        PAID = 'PAID'
        SICK = 'SICK'
        UNPAID = 'UNPAID'

    class Status(models.TextChoices):
        PENDING = 'PENDING'
        APPROVED = 'APPROVED'
        REJECTED = 'REJECTED'

    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE,
        related_name='leave_requests',
    )
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default='PENDING',
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_leaves',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leave_requests'
        indexes = [
            models.Index(fields=['status'], name='idx_lr_status'),
            models.Index(fields=['leave_type'], name='idx_lr_leave_type'),
            models.Index(fields=['start_date'], name='idx_lr_start_date'),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(end_date__gte=F('start_date')),
                name='leave_dates_valid',
            ),
            models.CheckConstraint(
                check=Q(leave_type__in=['PAID', 'SICK', 'UNPAID']),
                name='leave_type_valid',
            ),
            models.CheckConstraint(
                check=Q(status__in=['PENDING', 'APPROVED', 'REJECTED']),
                name='leave_status_valid',
            ),
        ]

    def __str__(self):
        return f"{self.employee} — {self.leave_type} ({self.start_date} → {self.end_date})"


# ---------------------------------------------------------------------------
# 6. payroll
# ---------------------------------------------------------------------------
class Payroll(models.Model):
    """Employee salary structure. net_salary is computed server‑side."""

    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE,
        related_name='payrolls',
    )
    basic_salary = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
    )
    allowances = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
    )
    deductions = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
    )
    net_salary = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
    )
    effective_from = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payroll'
        indexes = [
            models.Index(fields=['effective_from'], name='idx_payroll_eff'),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(basic_salary__gte=Decimal('0')),
                name='payroll_basic_salary_gte_0',
            ),
            models.CheckConstraint(
                check=Q(allowances__gte=Decimal('0')),
                name='payroll_allowances_gte_0',
            ),
            models.CheckConstraint(
                check=Q(deductions__gte=Decimal('0')),
                name='payroll_deductions_gte_0',
            ),
            models.CheckConstraint(
                check=Q(net_salary__gte=Decimal('0')),
                name='payroll_net_salary_gte_0',
            ),
        ]

    def save(self, *args, **kwargs):
        """Always compute net_salary server‑side: basic + allowances − deductions."""
        self.net_salary = self.basic_salary + self.allowances - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payroll for {self.employee} effective {self.effective_from}"


# ---------------------------------------------------------------------------
# 7. documents
# ---------------------------------------------------------------------------
class Document(models.Model):
    """Employee‑uploaded documents."""

    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE,
        related_name='documents',
    )
    document_type = models.CharField(max_length=50)
    document_name = models.CharField(max_length=255)
    file_url = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documents'
        indexes = [
            models.Index(fields=['document_type'], name='idx_doc_type'),
        ]

    def __str__(self):
        return f"{self.document_type}: {self.document_name}"


# ---------------------------------------------------------------------------
# 8. notifications
# ---------------------------------------------------------------------------
class Notification(models.Model):
    """Application notifications (optional for MVP)."""

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['is_read'], name='idx_notif_is_read'),
            models.Index(fields=['created_at'], name='idx_notif_created'),
        ]

    def __str__(self):
        return f"{self.title} → {self.user}"
