from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Create test users and assign them to Admins, Editors, and Viewers groups'

    def handle(self, *args, **options):
        User = get_user_model()

        users = [
            ('admin_user', 'admin@example.com', 'password123', 'Admins'),
            ('editor_user', 'editor@example.com', 'password123', 'Editors'),
            ('viewer_user', 'viewer@example.com', 'password123', 'Viewers'),
        ]

        for username, email, pwd, group_name in users:
            user, created = User.objects.get_or_create(username=username, defaults={'email': email})
            if created:
                user.set_password(pwd)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {username} already exists'))

            try:
                group = Group.objects.get(name=group_name)
                user.groups.clear()
                user.groups.add(group)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Assigned {username} to group {group_name}'))
            except Group.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Group {group_name} does not exist. Run create_groups first.'))

        self.stdout.write(self.style.SUCCESS('Test users creation complete.'))
