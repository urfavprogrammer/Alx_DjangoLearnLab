from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Create default groups (Admins, Editors, Viewers) and assign Book permissions'

    def handle(self, *args, **options):
        # Import here to avoid app-loading issues during Django startup
        from bookshelf.models import Book

        ct = ContentType.objects.get_for_model(Book)

        # Map of codename -> Permission
        perms = {}
        for codename in ('can_view', 'can_create', 'can_edit', 'can_delete'):
            try:
                perms[codename] = Permission.objects.get(codename=codename, content_type=ct)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Permission {codename} does not exist yet. Run migrate first.'))

        # Create groups
        groups = {
            'Admins': ['can_view', 'can_create', 'can_edit', 'can_delete'],
            'Editors': ['can_view', 'can_create', 'can_edit'],
            'Viewers': ['can_view'],
        }

        for group_name, group_perms in groups.items():
            group, created = Group.objects.get_or_create(name=group_name)
            # assign permissions that exist
            to_assign = [perms[p] for p in group_perms if p in perms]
            group.permissions.set(to_assign)
            group.save()
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {group_name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated group: {group_name}'))

        self.stdout.write(self.style.SUCCESS('Groups and permissions setup complete.'))
