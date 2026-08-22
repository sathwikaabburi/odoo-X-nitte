"""
Custom authentication backend for the Dayflow HRMS.

The project uses a CUSTOM User model (hr.User) stored in the 'users' table
— NOT Django's built-in auth_user.  This module bridges DRF's session auth
with our custom model so login/logout work via Django sessions while the
User table stays untouched.
"""
from django.contrib.auth.hashers import check_password
from rest_framework.authentication import SessionAuthentication

from hr.models import User


class DayflowSessionAuthentication(SessionAuthentication):
    """
    Wraps Django's session auth but resolves the session's user_id
    against hr.User instead of auth.User.
    """

    def authenticate(self, request):
        user_id = request.session.get('_dayflow_user_id')
        if user_id is None:
            return None
        try:
            user = User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return None
        # Skip CSRF enforcement for API-only usage during dev;
        # session cookie SameSite=Lax already mitigates CSRF.
        return (user, None)


def authenticate_user(email: str, password: str) -> User | None:
    """
    Locate a user by email and verify their password using Django's
    check_password (PBKDF2 by default).
    Returns the User instance or None.
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None

    if not check_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


def login_user(request, user: User) -> None:
    """Persist user identity into the Django session."""
    request.session['_dayflow_user_id'] = user.pk
    request.session.save()


def logout_user(request) -> None:
    """Clear the session."""
    request.session.flush()
