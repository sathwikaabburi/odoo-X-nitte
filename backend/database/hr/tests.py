"""
Dayflow HRMS — API Tests

Covers authentication, authorization, attendance, leave, payroll.
"""
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from hr.models import (
    User, Department, EmployeeProfile, Attendance,
    LeaveRequest, Payroll, Notification,
)


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'hr.authentication.DayflowSessionAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ],
    }
)
class DayflowTestBase(TestCase):
    """Shared setup: creates users, profiles, departments."""

    def setUp(self):
        self.client = APIClient()

        self.dept = Department.objects.create(name='Engineering')

        self.admin_user = User.objects.create(
            employee_id='T001', email='admin@test.io',
            password_hash=make_password('Admin@123'),
            role='ADMIN', is_verified=True,
        )
        self.admin_profile = EmployeeProfile.objects.create(
            user=self.admin_user, first_name='Admin', last_name='User',
            department=self.dept,
        )

        self.hr_user = User.objects.create(
            employee_id='T002', email='hr@test.io',
            password_hash=make_password('Hr@1234'),
            role='HR', is_verified=True,
        )
        self.hr_profile = EmployeeProfile.objects.create(
            user=self.hr_user, first_name='HR', last_name='User',
            department=self.dept,
        )

        self.emp_user = User.objects.create(
            employee_id='T003', email='emp@test.io',
            password_hash=make_password('Emp@1234'),
            role='EMPLOYEE', is_verified=True,
        )
        self.emp_profile = EmployeeProfile.objects.create(
            user=self.emp_user, first_name='Employee', last_name='One',
            department=self.dept,
        )

        self.emp2_user = User.objects.create(
            employee_id='T004', email='emp2@test.io',
            password_hash=make_password('Emp2@123'),
            role='EMPLOYEE', is_verified=True,
        )
        self.emp2_profile = EmployeeProfile.objects.create(
            user=self.emp2_user, first_name='Employee', last_name='Two',
            department=self.dept,
        )

    def _login(self, email, password):
        return self.client.post('/api/auth/login/', {
            'email': email, 'password': password,
        }, format='json')

    def _login_admin(self):
        self._login('admin@test.io', 'Admin@123')

    def _login_hr(self):
        self._login('hr@test.io', 'Hr@1234')

    def _login_emp(self):
        self._login('emp@test.io', 'Emp@1234')

    def _login_emp2(self):
        self._login('emp2@test.io', 'Emp2@123')


# ── Authentication ────────────────────────────────────────────────────────

class AuthTests(DayflowTestBase):

    def test_signup_success(self):
        r = self.client.post('/api/auth/signup/', {
            'employee_id': 'NEW01',
            'email': 'new@test.io',
            'password': 'NewPass@1',
            'role': 'EMPLOYEE',
            'first_name': 'New',
            'last_name': 'Person',
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertNotIn('password_hash', r.data['user'])

    def test_signup_duplicate_email(self):
        r = self.client.post('/api/auth/signup/', {
            'employee_id': 'NEW02',
            'email': 'emp@test.io',  # already exists
            'password': 'NewPass@1',
            'role': 'EMPLOYEE',
            'first_name': 'Dup', 'last_name': 'Email',
        }, format='json')
        self.assertEqual(r.status_code, 400)

    def test_signup_duplicate_employee_id(self):
        r = self.client.post('/api/auth/signup/', {
            'employee_id': 'T003',  # already exists
            'email': 'unique@test.io',
            'password': 'NewPass@1',
            'role': 'EMPLOYEE',
            'first_name': 'Dup', 'last_name': 'ID',
        }, format='json')
        self.assertEqual(r.status_code, 400)

    def test_login_success(self):
        r = self._login('emp@test.io', 'Emp@1234')
        self.assertEqual(r.status_code, 200)
        self.assertIn('user', r.data)

    def test_login_wrong_password(self):
        r = self._login('emp@test.io', 'WrongPass')
        self.assertEqual(r.status_code, 401)

    def test_login_inactive_user(self):
        self.emp_user.is_active = False
        self.emp_user.save()
        r = self._login('emp@test.io', 'Emp@1234')
        self.assertEqual(r.status_code, 401)

    def test_me_authenticated(self):
        self._login_emp()
        r = self.client.get('/api/auth/me/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['employee_id'], 'T003')

    def test_me_unauthenticated(self):
        r = self.client.get('/api/auth/me/')
        self.assertEqual(r.status_code, 403)

    def test_logout(self):
        self._login_emp()
        r = self.client.post('/api/auth/logout/')
        self.assertEqual(r.status_code, 200)
        # After logout, /me/ should fail
        r2 = self.client.get('/api/auth/me/')
        self.assertEqual(r2.status_code, 403)


# ── Authorization ─────────────────────────────────────────────────────────

class AuthorizationTests(DayflowTestBase):

    def test_employee_cannot_see_other_profile(self):
        self._login_emp()
        r = self.client.get(f'/api/employees/{self.emp2_profile.pk}/')
        self.assertEqual(r.status_code, 403)

    def test_employee_cannot_approve_leave(self):
        leave = LeaveRequest.objects.create(
            employee=self.emp2_profile, leave_type='PAID',
            start_date='2026-09-01', end_date='2026-09-02', status='PENDING',
        )
        self._login_emp()
        r = self.client.patch(f'/api/leaves/{leave.pk}/approve/', {}, format='json')
        self.assertEqual(r.status_code, 403)

    def test_employee_cannot_update_payroll(self):
        payroll = Payroll(
            employee=self.emp_profile, basic_salary=Decimal('50000'),
            allowances=Decimal('5000'), deductions=Decimal('3000'),
            net_salary=Decimal('0'), effective_from='2026-01-01',
        )
        payroll.save()
        self._login_emp()
        r = self.client.put(f'/api/payroll/{payroll.pk}/', {
            'basic_salary': '99999',
        }, format='json')
        self.assertEqual(r.status_code, 403)

    def test_admin_can_see_all_employees(self):
        self._login_admin()
        r = self.client.get('/api/employees/')
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.data), 2)


# ── Attendance ────────────────────────────────────────────────────────────

class AttendanceTests(DayflowTestBase):

    def test_check_in(self):
        self._login_emp()
        r = self.client.post('/api/attendance/check-in/')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['status'], 'PRESENT')

    def test_duplicate_check_in_blocked(self):
        self._login_emp()
        self.client.post('/api/attendance/check-in/')
        r = self.client.post('/api/attendance/check-in/')
        self.assertEqual(r.status_code, 409)

    def test_check_out(self):
        self._login_emp()
        self.client.post('/api/attendance/check-in/')
        r = self.client.post('/api/attendance/check-out/')
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(r.data['check_out'])

    def test_check_out_without_check_in(self):
        self._login_emp()
        r = self.client.post('/api/attendance/check-out/')
        self.assertEqual(r.status_code, 400)

    def test_employee_sees_own_attendance_only(self):
        self._login_emp()
        self.client.post('/api/attendance/check-in/')
        self._login_emp2()
        r = self.client.get('/api/attendance/')
        # emp2 has no attendance
        self.assertEqual(len(r.data), 0)

    def test_admin_sees_all_attendance(self):
        self._login_emp()
        self.client.post('/api/attendance/check-in/')
        self._login_admin()
        r = self.client.get('/api/attendance/')
        self.assertGreaterEqual(len(r.data), 1)


# ── Leave ─────────────────────────────────────────────────────────────────

class LeaveTests(DayflowTestBase):

    def test_submit_leave(self):
        self._login_emp()
        r = self.client.post('/api/leaves/', {
            'leave_type': 'PAID',
            'start_date': '2026-10-01',
            'end_date': '2026-10-03',
            'remarks': 'Family event',
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['status'], 'PENDING')

    def test_invalid_leave_dates(self):
        self._login_emp()
        r = self.client.post('/api/leaves/', {
            'leave_type': 'PAID',
            'start_date': '2026-10-05',
            'end_date': '2026-10-01',
        }, format='json')
        self.assertEqual(r.status_code, 400)

    def test_invalid_leave_type(self):
        self._login_emp()
        r = self.client.post('/api/leaves/', {
            'leave_type': 'VACATION',
            'start_date': '2026-10-01',
            'end_date': '2026-10-02',
        }, format='json')
        self.assertEqual(r.status_code, 400)

    def test_approve_leave(self):
        self._login_emp()
        r = self.client.post('/api/leaves/', {
            'leave_type': 'SICK',
            'start_date': '2026-11-01',
            'end_date': '2026-11-02',
        }, format='json')
        leave_id = r.data['id']

        self._login_admin()
        r = self.client.patch(f'/api/leaves/{leave_id}/approve/', {
            'admin_comment': 'Take care.',
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['status'], 'APPROVED')
        self.assertIsNotNone(r.data['reviewed_by'])

    def test_reject_leave(self):
        self._login_emp()
        r = self.client.post('/api/leaves/', {
            'leave_type': 'UNPAID',
            'start_date': '2026-12-01',
            'end_date': '2026-12-03',
        }, format='json')
        leave_id = r.data['id']

        self._login_hr()
        r = self.client.patch(f'/api/leaves/{leave_id}/reject/', {
            'admin_comment': 'Not enough notice.',
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['status'], 'REJECTED')

    def test_employee_sees_own_leaves(self):
        self._login_emp()
        self.client.post('/api/leaves/', {
            'leave_type': 'PAID', 'start_date': '2026-09-01', 'end_date': '2026-09-02',
        }, format='json')
        self._login_emp2()
        r = self.client.get('/api/leaves/')
        self.assertEqual(len(r.data), 0)


# ── Payroll ───────────────────────────────────────────────────────────────

class PayrollTests(DayflowTestBase):

    def setUp(self):
        super().setUp()
        self.payroll = Payroll(
            employee=self.emp_profile,
            basic_salary=Decimal('50000'),
            allowances=Decimal('5000'),
            deductions=Decimal('3000'),
            net_salary=Decimal('0'),
            effective_from='2026-01-01',
        )
        self.payroll.save()

    def test_employee_read_own_payroll(self):
        self._login_emp()
        r = self.client.get('/api/payroll/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)

    def test_employee_cannot_update_payroll(self):
        self._login_emp()
        r = self.client.put(f'/api/payroll/{self.payroll.pk}/', {
            'basic_salary': '99999',
        }, format='json')
        self.assertEqual(r.status_code, 403)

    def test_admin_can_update_payroll(self):
        self._login_admin()
        r = self.client.put(f'/api/payroll/{self.payroll.pk}/', {
            'basic_salary': '60000',
            'allowances': '8000',
            'deductions': '4000',
            'effective_from': '2026-06-01',
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['net_salary'], '64000.00')

    def test_net_salary_calculated_server_side(self):
        self._login_admin()
        r = self.client.put(f'/api/payroll/{self.payroll.pk}/', {
            'basic_salary': '100000',
            'allowances': '20000',
            'deductions': '15000',
            'effective_from': '2026-07-01',
        }, format='json')
        self.assertEqual(r.data['net_salary'], '105000.00')


# ── Documents ─────────────────────────────────────────────────────────────

class DocumentTests(DayflowTestBase):

    def test_upload_and_list_documents(self):
        self._login_emp()
        r = self.client.post('/api/documents/', {
            'document_type': 'ID_PROOF',
            'document_name': 'Passport',
            'file_url': 'https://example.com/passport.pdf',
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['document_name'], 'Passport')

        r_list = self.client.get('/api/documents/')
        self.assertEqual(r_list.status_code, 200)
        self.assertEqual(len(r_list.data), 1)

    def test_delete_document(self):
        self._login_emp()
        r = self.client.post('/api/documents/', {
            'document_type': 'RESUME',
            'document_name': 'MyResume',
            'file_url': 'https://example.com/resume.pdf',
        }, format='json')
        doc_id = r.data['id']

        r_del = self.client.delete(f'/api/documents/{doc_id}/')
        self.assertEqual(r_del.status_code, 204)


# ── Notifications ─────────────────────────────────────────────────────────

class NotificationTests(DayflowTestBase):

    def setUp(self):
        super().setUp()
        self.notif = Notification.objects.create(
            user=self.emp_user,
            title='Test Alert',
            message='You have an update.',
            notification_type='SYSTEM',
        )

    def test_get_notifications(self):
        self._login_emp()
        r = self.client.get('/api/notifications/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)
        self.assertFalse(r.data[0]['is_read'])

    def test_mark_notification_read(self):
        self._login_emp()
        r = self.client.patch(f'/api/notifications/{self.notif.pk}/read/')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data['is_read'])


# ── Dashboard ─────────────────────────────────────────────────────────────

class DashboardTests(DayflowTestBase):

    def test_employee_dashboard(self):
        self._login_emp()
        r = self.client.get('/api/dashboard/employee/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('profile', r.data)
        self.assertIn('today_attendance', r.data)
        self.assertIn('recent_leaves', r.data)
        self.assertIn('unread_notifications', r.data)

    def test_admin_dashboard_allowed(self):
        self._login_admin()
        r = self.client.get('/api/dashboard/admin/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('total_employees', r.data)
        self.assertIn('today_attendance', r.data)
        self.assertIn('department_summary', r.data)

    def test_admin_dashboard_forbidden_for_employee(self):
        self._login_emp()
        r = self.client.get('/api/dashboard/admin/')
        self.assertEqual(r.status_code, 403)


# ── Departments ───────────────────────────────────────────────────────────

class DepartmentTests(DayflowTestBase):

    def test_list_departments(self):
        self._login_emp()
        r = self.client.get('/api/departments/')
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.data), 1)
        self.assertEqual(r.data[0]['name'], 'Engineering')
