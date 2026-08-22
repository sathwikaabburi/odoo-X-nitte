"""
Management command to populate the DAYFLOW database with realistic demo data.

Usage:
    python manage.py seed_data
"""
from django.contrib.auth.hashers import make_password
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from backend.database.hr.models import (
    User, Department, EmployeeProfile, Attendance,
    LeaveRequest, Payroll, Document, Notification,
)


class Command(BaseCommand):
    help = 'Seed the DAYFLOW database with realistic demo data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding DAYFLOW database …'))

        # ------------------------------------------------------------------
        # 1. Departments
        # ------------------------------------------------------------------
        dept_data = [
            ('Engineering', 'Software development and infrastructure'),
            ('Human Resources', 'People management, hiring, and compliance'),
            ('Finance', 'Accounting, budgets, and payroll processing'),
            ('Marketing', 'Brand, campaigns, and digital outreach'),
        ]
        departments = {}
        for name, desc in dept_data:
            dept, created = Department.objects.get_or_create(
                name=name, defaults={'description': desc},
            )
            departments[name] = dept
            self._log(f'Department: {name}', created)

        # ------------------------------------------------------------------
        # 2. Users
        # ------------------------------------------------------------------
        def _hash(pw):
            return make_password(pw)

        user_data = [
            ('EMP001', 'admin@dayflow.io',    _hash('Admin@123'),    'ADMIN',    True),
            ('EMP002', 'hr@dayflow.io',       _hash('Hr@123'),       'HR',       True),
            ('EMP003', 'rahul@dayflow.io',    _hash('Rahul@123'),    'EMPLOYEE', True),
            ('EMP004', 'priya@dayflow.io',    _hash('Priya@123'),    'EMPLOYEE', True),
            ('EMP005', 'amit@dayflow.io',     _hash('Amit@123'),     'EMPLOYEE', True),
            ('EMP006', 'sneha@dayflow.io',    _hash('Sneha@123'),    'EMPLOYEE', False),
        ]
        users = {}
        for eid, email, pw, role, verified in user_data:
            user, created = User.objects.get_or_create(
                employee_id=eid,
                defaults={
                    'email': email,
                    'password_hash': pw,
                    'role': role,
                    'is_verified': verified,
                },
            )
            users[eid] = user
            self._log(f'User: {eid} ({role})', created)

        # ------------------------------------------------------------------
        # 3. Employee Profiles
        # ------------------------------------------------------------------
        profile_data = [
            ('EMP001', 'Arun',    'Kumar',   '9876543210', 'Engineering',       'CTO',               date(2022, 1, 15), date(1988, 5, 10), 'Male'),
            ('EMP002', 'Meera',   'Nair',    '9876543211', 'Human Resources',   'HR Manager',        date(2022, 3, 1),  date(1990, 8, 22), 'Female'),
            ('EMP003', 'Rahul',   'Sharma',  '9876543212', 'Engineering',       'Software Engineer', date(2023, 6, 10), date(1995, 2, 14), 'Male'),
            ('EMP004', 'Priya',   'Reddy',   '9876543213', 'Marketing',         'Marketing Lead',    date(2023, 9, 1),  date(1993, 11, 5), 'Female'),
            ('EMP005', 'Amit',    'Patel',   '9876543214', 'Finance',           'Accountant',        date(2024, 1, 15), date(1996, 7, 30), 'Male'),
            ('EMP006', 'Sneha',   'Gupta',   '9876543215', 'Engineering',       'Intern',            date(2024, 7, 1),  date(2001, 4, 18), 'Female'),
        ]
        profiles = {}
        for eid, fn, ln, phone, dept_name, desig, join, dob, gender in profile_data:
            profile, created = EmployeeProfile.objects.get_or_create(
                user=users[eid],
                defaults={
                    'first_name': fn,
                    'last_name': ln,
                    'phone': phone,
                    'department': departments[dept_name],
                    'designation': desig,
                    'joining_date': join,
                    'date_of_birth': dob,
                    'gender': gender,
                },
            )
            profiles[eid] = profile
            self._log(f'Profile: {fn} {ln}', created)

        # ------------------------------------------------------------------
        # 4. Attendance Records (last 5 working days for each employee)
        # ------------------------------------------------------------------
        today = date.today()
        statuses = ['PRESENT', 'PRESENT', 'PRESENT', 'HALF_DAY', 'PRESENT']
        for eid in ['EMP003', 'EMP004', 'EMP005']:
            for i, status in enumerate(statuses):
                att_date = today - timedelta(days=(5 - i))
                check_in_time = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0) - timedelta(days=(5 - i))
                check_out_time = check_in_time.replace(hour=17 if status == 'PRESENT' else 13)
                _, created = Attendance.objects.get_or_create(
                    employee=profiles[eid],
                    attendance_date=att_date,
                    defaults={
                        'check_in': check_in_time,
                        'check_out': check_out_time,
                        'status': status,
                    },
                )
                self._log(f'Attendance: {eid} on {att_date} → {status}', created)

        # ------------------------------------------------------------------
        # 5. Leave Requests (mix of statuses)
        # ------------------------------------------------------------------
        leave_data = [
            ('EMP003', 'PAID',   today + timedelta(days=5),  today + timedelta(days=7),  'Family function',     'PENDING',   None,     None),
            ('EMP004', 'SICK',   today - timedelta(days=10), today - timedelta(days=9),  'Fever',               'APPROVED',  'EMP002', 'Get well soon.'),
            ('EMP005', 'UNPAID', today - timedelta(days=3),  today - timedelta(days=1),  'Personal emergency',  'REJECTED',  'EMP001', 'Insufficient notice period.'),
        ]
        for eid, ltype, start, end, remark, status, reviewer_eid, comment in leave_data:
            defaults = {
                'leave_type': ltype,
                'start_date': start,
                'end_date': end,
                'remarks': remark,
                'status': status,
                'admin_comment': comment,
            }
            if reviewer_eid:
                defaults['reviewed_by'] = users[reviewer_eid]
                defaults['reviewed_at'] = timezone.now()
            _, created = LeaveRequest.objects.get_or_create(
                employee=profiles[eid],
                leave_type=ltype,
                start_date=start,
                defaults=defaults,
            )
            self._log(f'Leave: {eid} {ltype} {status}', created)

        # ------------------------------------------------------------------
        # 6. Payroll Records
        # ------------------------------------------------------------------
        payroll_data = [
            ('EMP001', Decimal('120000'), Decimal('20000'), Decimal('15000'), date(2022, 1, 1)),
            ('EMP002', Decimal('90000'),  Decimal('15000'), Decimal('10000'), date(2022, 3, 1)),
            ('EMP003', Decimal('60000'),  Decimal('10000'), Decimal('7000'),  date(2023, 6, 1)),
            ('EMP004', Decimal('70000'),  Decimal('12000'), Decimal('8000'),  date(2023, 9, 1)),
            ('EMP005', Decimal('55000'),  Decimal('8000'),  Decimal('5000'),  date(2024, 1, 1)),
            ('EMP006', Decimal('25000'),  Decimal('2000'),  Decimal('1500'),  date(2024, 7, 1)),
        ]
        for eid, basic, allow, deduct, eff in payroll_data:
            _, created = Payroll.objects.get_or_create(
                employee=profiles[eid],
                effective_from=eff,
                defaults={
                    'basic_salary': basic,
                    'allowances': allow,
                    'deductions': deduct,
                    'net_salary': Decimal('0'),  # save() will recompute
                },
            )
            self._log(f'Payroll: {eid} basic={basic}', created)

        # ------------------------------------------------------------------
        # 7. Documents
        # ------------------------------------------------------------------
        doc_data = [
            ('EMP003', 'ID Proof',   'Aadhaar Card',   '/media/docs/emp003_aadhaar.pdf'),
            ('EMP003', 'Resume',     'Resume_2023',    '/media/docs/emp003_resume.pdf'),
            ('EMP004', 'ID Proof',   'PAN Card',       '/media/docs/emp004_pan.pdf'),
        ]
        for eid, dtype, dname, url in doc_data:
            _, created = Document.objects.get_or_create(
                employee=profiles[eid],
                document_type=dtype,
                document_name=dname,
                defaults={'file_url': url},
            )
            self._log(f'Document: {eid} {dtype}', created)

        # ------------------------------------------------------------------
        # 8. Notifications
        # ------------------------------------------------------------------
        notif_data = [
            ('EMP003', 'Welcome to DAYFLOW!',          'Your account has been verified.',       'SYSTEM',  True),
            ('EMP002', 'New leave request',             'Rahul Sharma requested paid leave.',    'LEAVE',   False),
            ('EMP001', 'Payroll updated',               'Payroll for June has been processed.',  'PAYROLL', False),
        ]
        for eid, title, msg, ntype, read in notif_data:
            _, created = Notification.objects.get_or_create(
                user=users[eid],
                title=title,
                defaults={
                    'message': msg,
                    'notification_type': ntype,
                    'is_read': read,
                },
            )
            self._log(f'Notification: {title}', created)

        self.stdout.write(self.style.SUCCESS('[OK] Seed data complete!'))

    # helper
    def _log(self, label, created):
        tag = 'CREATED' if created else 'EXISTS'
        style = self.style.SUCCESS if created else self.style.WARNING
        self.stdout.write(style(f'  [{tag}] {label}'))
