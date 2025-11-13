from django.core.management.base import BaseCommand
from users.models import Permission, Role, User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Seed initial data for users app'

    def handle(self, *args, **options):

        for permission in Permission.ALL_PERMISSIONS:
            _, created = Permission.objects.get_or_create(name=permission)
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Permission "{permission}" created successfully.'))
            else:
                self.stdout.write(
                    f'Permission "{permission}" already exists.')

        for role_name, permission_names in Permission.ROLE_DEFAULT_PERMISSIONS.items():
            role, created = Role.objects.get_or_create(name=role_name)
            permissions = Permission.objects.filter(
                name__in=permission_names)

            if permissions.exists():
                role.permissions.set(permissions)

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Role "{role_name}" created successfully.'))
            else:
                self.stdout.write(f'Role "{role_name}" already exists.')

        full_name = 'Admin User'
        email = 'admin@example.com'
        password = 'adminpassword'
        admin_role = Role.objects.get(name=Role.ADMIN_ROLE)

        user, created = User.objects.get_or_create(
            full_name=full_name,
            email=email,
            defaults={
                'password': make_password(password),
                'role': admin_role,
            }
        )

        user.permissions.set(admin_role.permissions.all())
