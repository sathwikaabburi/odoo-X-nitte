"""
DRF serializers for all Dayflow HRMS models.

Rules:
- Never expose password_hash.
- Validate enums, dates, and money server-side.
- Employee-editable profile fields are restricted.
"""
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from hr.models import (
    User, Department, EmployeeProfile, Attendance,
    LeaveRequest, Payroll, Document, Notification,
)


# ── Auth ──────────────────────────────────────────────────────────────────

class SignupSerializer(serializers.Serializer):
    employee_id = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(min_length=8, write_only=True)
    role = serializers.ChoiceField(choices=User.Role.choices)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)

    def validate_employee_id(self, value):
        if User.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError('Employee ID already exists.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSafeSerializer(serializers.ModelSerializer):
    """Read-only user fields — never returns password_hash."""

    class Meta:
        model = User
        fields = [
            'id', 'employee_id', 'email', 'role',
            'is_verified', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


# ── Department ────────────────────────────────────────────────────────────

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


# ── Employee Profile ─────────────────────────────────────────────────────

class EmployeeProfileSerializer(serializers.ModelSerializer):
    """Full profile — used for HR/Admin views."""
    user = UserSafeSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department',
        write_only=True, required=False, allow_null=True,
    )

    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 'user', 'first_name', 'last_name', 'phone',
            'address', 'profile_picture', 'department', 'department_id',
            'designation', 'joining_date', 'date_of_birth', 'gender',
        ]
        read_only_fields = ['id', 'user']


class EmployeeProfileUpdateSerializer(serializers.ModelSerializer):
    """Employee self-edit: only phone, address, profile_picture."""

    class Meta:
        model = EmployeeProfile
        fields = ['phone', 'address', 'profile_picture']


# ── Attendance ────────────────────────────────────────────────────────────

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'attendance_date',
            'check_in', 'check_out', 'status', 'remarks',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'employee', 'employee_name', 'attendance_date',
            'check_in', 'check_out', 'status', 'created_at', 'updated_at',
        ]

    def get_employee_name(self, obj):
        return str(obj.employee)


# ── Leave Request ─────────────────────────────────────────────────────────

class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'remarks']

    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError(
                {'end_date': 'End date must be >= start date.'}
            )
        return data


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'leave_type',
            'start_date', 'end_date', 'remarks', 'status',
            'reviewed_by', 'reviewed_by_name', 'reviewed_at',
            'admin_comment', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        return str(obj.employee)

    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return str(obj.reviewed_by)
        return None


class LeaveReviewSerializer(serializers.Serializer):
    admin_comment = serializers.CharField(required=False, allow_blank=True, default='')


# ── Payroll ───────────────────────────────────────────────────────────────

class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_name', 'basic_salary',
            'allowances', 'deductions', 'net_salary',
            'effective_from', 'updated_at',
        ]
        read_only_fields = ['id', 'employee', 'employee_name', 'net_salary', 'updated_at']

    def get_employee_name(self, obj):
        return str(obj.employee)

    def validate_basic_salary(self, value):
        if value < Decimal('0'):
            raise serializers.ValidationError('Must be >= 0.')
        return value

    def validate_allowances(self, value):
        if value < Decimal('0'):
            raise serializers.ValidationError('Must be >= 0.')
        return value

    def validate_deductions(self, value):
        if value < Decimal('0'):
            raise serializers.ValidationError('Must be >= 0.')
        return value


# ── Document ──────────────────────────────────────────────────────────────

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id', 'employee', 'document_type', 'document_name',
            'file_url', 'uploaded_at',
        ]
        read_only_fields = ['id', 'employee', 'uploaded_at']


# ── Notification ──────────────────────────────────────────────────────────

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message',
            'notification_type', 'is_read', 'created_at',
        ]
        read_only_fields = fields
