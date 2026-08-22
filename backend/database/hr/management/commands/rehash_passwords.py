"""
Re-hash existing user passwords using Django's make_password (PBKDF2).

Existing seeded users have known passwords — this command updates their
password_hash to use Django's secure hasher so check_password() works.

Usage:
    python manage.py rehash_passwords
"""
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from hr.models import User


# Map of employee_id → known password for seeded users
SEED_PASSWORDS = {
    'EMP001': 'Admin@123',
    'EMP002': 'Hr@123',
    'EMP003': 'Rahul@123',
    'EMP004': 'Priya@123',
    'EMP005': 'Amit@123',
    'EMP006': 'Sneha@123',
}


class Command(BaseCommand):
    help = 'Re-hash seeded user passwords with Django PBKDF2.'

    def handle(self, *args, **options):
        for eid, plain in SEED_PASSWORDS.items():
            try:
                user = User.objects.get(employee_id=eid)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  [SKIP] {eid} not found'))
                continue

            user.password_hash = make_password(plain)
            user.save(update_fields=['password_hash'])
            self.stdout.write(self.style.SUCCESS(f'  [OK] {eid} password re-hashed'))

        self.stdout.write(self.style.SUCCESS('Done.'))
