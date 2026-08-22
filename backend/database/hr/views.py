"""
Dayflow HRMS — API Views

Phases 1-9 consolidated into a single views module.
Each section maps to an API route group.
"""
from datetime import date, timedelta

from django.db import IntegrityError
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from hr.authentication import authenticate_user, login_user, logout_user
from hr.models import (
    User, Department, EmployeeProfile, Attendance,
    LeaveRequest, Payroll, Document, Notification,
)
from hr.permissions import IsAuthenticated, IsHROrAdmin, IsOwnerOrHRAdmin
from hr.serializers import (
    SignupSerializer, LoginSerializer, UserSafeSerializer,
    EmployeeProfileSerializer, EmployeeProfileUpdateSerializer,
    AttendanceSerializer,
    LeaveRequestCreateSerializer, LeaveRequestSerializer, LeaveReviewSerializer,
    PayrollSerializer,
    DocumentSerializer,
    NotificationSerializer,
    DepartmentSerializer,
)
from hr.services import (
    create_employee, check_in_employee, check_out_employee,
    submit_leave_request, approve_leave_request, reject_leave_request,
    update_payroll,
)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1 — AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = SignupSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        try:
            user, profile = create_employee(
                employee_id=d['employee_id'],
                email=d['email'],
                password=d['password'],
                role=d['role'],
                first_name=d['first_name'],
                last_name=d['last_name'],
            )
        except IntegrityError:
            return Response(
                {'error': 'Employee ID or email already exists.'},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            {'message': 'Account created.', 'user': UserSafeSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = authenticate_user(ser.validated_data['email'], ser.validated_data['password'])
        if user is None:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_verified:
            return Response(
                {'error': 'Account not verified.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        login_user(request, user)
        return Response({
            'message': 'Login successful.',
            'user': UserSafeSerializer(user).data,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout_user(request)
        return Response({'message': 'Logged out.'})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserSafeSerializer(user).data
        try:
            profile = user.profile
            data['profile'] = EmployeeProfileSerializer(profile).data
        except EmployeeProfile.DoesNotExist:
            data['profile'] = None
        return Response(data)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3 — EMPLOYEE / PROFILE
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role in ('HR', 'ADMIN'):
            qs = EmployeeProfile.objects.select_related('user', 'department').all()
            # simple search by name
            search = request.query_params.get('search')
            if search:
                qs = qs.filter(
                    Q(first_name__icontains=search) | Q(last_name__icontains=search)
                )
            department = request.query_params.get('department')
            if department:
                qs = qs.filter(department_id=department)
        else:
            qs = EmployeeProfile.objects.select_related('user', 'department').filter(user=user)

        serializer = EmployeeProfileSerializer(qs, many=True)
        return Response(serializer.data)


class EmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            profile = EmployeeProfile.objects.select_related('user', 'department').get(pk=pk)
        except EmployeeProfile.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Employees can only see their own profile
        if request.user.role == 'EMPLOYEE' and profile.user_id != request.user.pk:
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        return Response(EmployeeProfileSerializer(profile).data)

    def put(self, request, pk):
        try:
            profile = EmployeeProfile.objects.select_related('user').get(pk=pk)
        except EmployeeProfile.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Employee can only edit own profile, and only limited fields
        if request.user.role == 'EMPLOYEE':
            if profile.user_id != request.user.pk:
                return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
            ser = EmployeeProfileUpdateSerializer(profile, data=request.data, partial=True)
        else:
            # HR / Admin — full edit
            ser = EmployeeProfileSerializer(profile, data=request.data, partial=True)

        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(EmployeeProfileSerializer(profile).data)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 4 — ATTENDANCE
# ═══════════════════════════════════════════════════════════════════════════

class CheckInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            profile = request.user.profile
        except EmployeeProfile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            att, _ = check_in_employee(profile)
        except IntegrityError:
            return Response(
                {'error': 'Already checked in today.'},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(AttendanceSerializer(att).data, status=status.HTTP_201_CREATED)


class CheckOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            profile = request.user.profile
        except EmployeeProfile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            att = check_out_employee(profile)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(AttendanceSerializer(att).data)


class AttendanceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role in ('HR', 'ADMIN'):
            qs = Attendance.objects.select_related('employee').all()
            employee_id = request.query_params.get('employee_id')
            if employee_id:
                qs = qs.filter(employee_id=employee_id)
        else:
            try:
                profile = user.profile
            except EmployeeProfile.DoesNotExist:
                return Response([])
            qs = Attendance.objects.filter(employee=profile)

        # Date filtering
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(attendance_date__gte=date_from)
        if date_to:
            qs = qs.filter(attendance_date__lte=date_to)

        qs = qs.order_by('-attendance_date')
        return Response(AttendanceSerializer(qs, many=True).data)


class AttendanceWeeklyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())  # Monday

        user = request.user
        if user.role in ('HR', 'ADMIN'):
            qs = Attendance.objects.select_related('employee').filter(
                attendance_date__gte=start_of_week,
                attendance_date__lte=today,
            )
        else:
            try:
                profile = user.profile
            except EmployeeProfile.DoesNotExist:
                return Response([])
            qs = Attendance.objects.filter(
                employee=profile,
                attendance_date__gte=start_of_week,
                attendance_date__lte=today,
            )

        qs = qs.order_by('attendance_date')
        return Response(AttendanceSerializer(qs, many=True).data)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 5 — LEAVE
# ═══════════════════════════════════════════════════════════════════════════

class LeaveListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role in ('HR', 'ADMIN'):
            qs = LeaveRequest.objects.select_related('employee', 'reviewed_by').all()
            status_filter = request.query_params.get('status')
            if status_filter:
                qs = qs.filter(status=status_filter.upper())
        else:
            try:
                profile = user.profile
            except EmployeeProfile.DoesNotExist:
                return Response([])
            qs = LeaveRequest.objects.filter(employee=profile)

        qs = qs.order_by('-created_at')
        return Response(LeaveRequestSerializer(qs, many=True).data)

    def post(self, request):
        user = request.user
        ser = LeaveRequestCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            profile = user.profile
        except EmployeeProfile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        leave = submit_leave_request(
            profile,
            leave_type=ser.validated_data['leave_type'],
            start_date=ser.validated_data['start_date'],
            end_date=ser.validated_data['end_date'],
            remarks=ser.validated_data.get('remarks', ''),
        )
        return Response(
            LeaveRequestSerializer(leave).data,
            status=status.HTTP_201_CREATED,
        )


class LeaveDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            leave = LeaveRequest.objects.select_related('employee', 'reviewed_by').get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'EMPLOYEE' and leave.employee.user_id != request.user.pk:
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        return Response(LeaveRequestSerializer(leave).data)


class LeaveApproveView(APIView):
    permission_classes = [IsAuthenticated, IsHROrAdmin]

    def patch(self, request, pk):
        try:
            leave = LeaveRequest.objects.select_related('employee').get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        ser = LeaveReviewSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            approve_leave_request(leave, request.user, ser.validated_data.get('admin_comment', ''))
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(LeaveRequestSerializer(leave).data)


class LeaveRejectView(APIView):
    permission_classes = [IsAuthenticated, IsHROrAdmin]

    def patch(self, request, pk):
        try:
            leave = LeaveRequest.objects.select_related('employee').get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        ser = LeaveReviewSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            reject_leave_request(leave, request.user, ser.validated_data.get('admin_comment', ''))
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(LeaveRequestSerializer(leave).data)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 6 — PAYROLL
# ═══════════════════════════════════════════════════════════════════════════

class PayrollListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role in ('HR', 'ADMIN'):
            qs = Payroll.objects.select_related('employee').all()
            employee_id = request.query_params.get('employee_id')
            if employee_id:
                qs = qs.filter(employee_id=employee_id)
        else:
            try:
                profile = user.profile
            except EmployeeProfile.DoesNotExist:
                return Response([])
            qs = Payroll.objects.filter(employee=profile)

        qs = qs.order_by('-effective_from')
        return Response(PayrollSerializer(qs, many=True).data)


class PayrollDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            payroll = Payroll.objects.select_related('employee').get(pk=pk)
        except Payroll.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'EMPLOYEE' and payroll.employee.user_id != request.user.pk:
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        return Response(PayrollSerializer(payroll).data)

    def put(self, request, pk):
        if request.user.role not in ('HR', 'ADMIN'):
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            payroll = Payroll.objects.get(pk=pk)
        except Payroll.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        ser = PayrollSerializer(payroll, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)

        update_payroll(
            payroll,
            basic_salary=ser.validated_data.get('basic_salary', payroll.basic_salary),
            allowances=ser.validated_data.get('allowances', payroll.allowances),
            deductions=ser.validated_data.get('deductions', payroll.deductions),
            effective_from=ser.validated_data.get('effective_from', payroll.effective_from),
        )
        return Response(PayrollSerializer(payroll).data)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 7 — DOCUMENTS
# ═══════════════════════════════════════════════════════════════════════════

class DocumentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role in ('HR', 'ADMIN'):
            qs = Document.objects.select_related('employee').all()
            employee_id = request.query_params.get('employee_id')
            if employee_id:
                qs = qs.filter(employee_id=employee_id)
        else:
            try:
                profile = user.profile
            except EmployeeProfile.DoesNotExist:
                return Response([])
            qs = Document.objects.filter(employee=profile)

        qs = qs.order_by('-uploaded_at')
        return Response(DocumentSerializer(qs, many=True).data)

    def post(self, request):
        user = request.user
        try:
            profile = user.profile
        except EmployeeProfile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        ser = DocumentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(employee=profile)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class DocumentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'EMPLOYEE' and doc.employee.user_id != request.user.pk:
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        doc.delete()
        return Response({'message': 'Deleted.'}, status=status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 8 — NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(user=request.user).order_by('-created_at')
        return Response(NotificationSerializer(qs, many=True).data)


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        notif.is_read = True
        notif.save()
        return Response(NotificationSerializer(notif).data)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 9 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            profile = user.profile
        except EmployeeProfile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        today = date.today()

        # Today's attendance
        today_att = Attendance.objects.filter(employee=profile, attendance_date=today).first()

        # Recent leave requests (last 5)
        recent_leaves = LeaveRequest.objects.filter(employee=profile).order_by('-created_at')[:5]

        # Payroll summary (latest)
        latest_payroll = Payroll.objects.filter(employee=profile).order_by('-effective_from').first()

        # Unread notifications count
        unread_count = Notification.objects.filter(user=user, is_read=False).count()

        return Response({
            'profile': EmployeeProfileSerializer(profile).data,
            'today_attendance': AttendanceSerializer(today_att).data if today_att else None,
            'recent_leaves': LeaveRequestSerializer(recent_leaves, many=True).data,
            'payroll': PayrollSerializer(latest_payroll).data if latest_payroll else None,
            'unread_notifications': unread_count,
        })


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsHROrAdmin]

    def get(self, request):
        today = date.today()

        total_employees = EmployeeProfile.objects.count()
        total_departments = Department.objects.count()

        # Today's attendance summary
        today_attendance = Attendance.objects.filter(attendance_date=today)
        present = today_attendance.filter(status='PRESENT').count()
        absent = today_attendance.filter(status='ABSENT').count()
        half_day = today_attendance.filter(status='HALF_DAY').count()
        on_leave = today_attendance.filter(status='LEAVE').count()

        # Pending leave count
        pending_leaves = LeaveRequest.objects.filter(status='PENDING').count()

        # Department-wise employee count
        dept_summary = list(
            Department.objects.annotate(
                employee_count=Count('employees')
            ).values('id', 'name', 'employee_count')
        )

        return Response({
            'total_employees': total_employees,
            'total_departments': total_departments,
            'today_attendance': {
                'present': present,
                'absent': absent,
                'half_day': half_day,
                'on_leave': on_leave,
                'total_checked_in': today_attendance.count(),
            },
            'pending_leaves': pending_leaves,
            'department_summary': dept_summary,
        })


# ═══════════════════════════════════════════════════════════════════════════
# DEPARTMENTS (bonus useful endpoint)
# ═══════════════════════════════════════════════════════════════════════════

class DepartmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Department.objects.all().order_by('name')
        return Response(DepartmentSerializer(qs, many=True).data)
