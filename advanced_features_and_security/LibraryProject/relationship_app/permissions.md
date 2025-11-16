Permissions and Groups Setup

This project defines custom permissions for the `Book` model and demonstrates how to use groups and permissions to control access.

Model permissions
- `relationship_app.Book` defines these custom permissions (in `models.py`):
  - `can_view`  — Permission to view book details or lists
  - `can_create` — Permission to create new books
  - `can_edit`  — Permission to edit existing books
  - `can_delete` — Permission to delete books

Groups to create (recommended)
- Editors: `can_create`, `can_edit`, `can_view`
- Viewers: `can_view`
- Admins: all permissions (Django superuser already has all)

How to create groups and assign permissions (Django admin)
1. Start the development server and log in to the Django admin as a superuser:
   ```bash
   python manage.py runserver
   # Visit http://127.0.0.1:8000/admin/
   ```
2. Choose "Groups" in the admin. Create a group (e.g., Editors).
3. In the group's permissions, add the appropriate `Book` permissions (look for permissions named "Can view book", "Can create book", "Can edit book", "Can delete book").
4. Assign users to groups via the Users page in admin or programmatically.

How permissions are enforced in views
- The add, edit, and delete views are decorated with `permission_required` using the permission names:
  - `@permission_required('relationship_app.can_create', raise_exception=True)` — protects the add view
  - `@permission_required('relationship_app.can_edit', raise_exception=True)` — protects the edit view
  - `@permission_required('relationship_app.can_delete', raise_exception=True)` — protects the delete view

Testing permissions manually
1. Create test users and assign them to groups via admin.
2. Log in as each user and try to access the pages for adding, editing, and deleting books.
   - Users in Viewers should get a permission denied response when trying to add/edit/delete.
   - Editors should be able to create and edit if assigned.

Programmatic group/permission creation (optional)
You can also create groups and assign permissions in a small script or migration. Example snippet (use in Django shell or a data migration):

```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from relationship_app.models import Book

content_type = ContentType.objects.get_for_model(Book)
can_view = Permission.objects.get(codename='can_view', content_type=content_type)
can_create = Permission.objects.get(codename='can_create', content_type=content_type)
can_edit = Permission.objects.get(codename='can_edit', content_type=content_type)
can_delete = Permission.objects.get(codename='can_delete', content_type=content_type)

editors, _ = Group.objects.get_or_create(name='Editors')
viewers, _ = Group.objects.get_or_create(name='Viewers')
admins, _ = Group.objects.get_or_create(name='Admins')

editors.permissions.set([can_view, can_create, can_edit])
viewers.permissions.set([can_view])
admins.permissions.set([can_view, can_create, can_edit, can_delete])
```

Notes
- If you add or change permissions, run `python manage.py makemigrations` and `python manage.py migrate` so Django registers the new permission records.
- Superusers bypass permission checks by default.
- The `permission_required` decorator will raise a PermissionDenied exception (HTTP 403) when `raise_exception=True`.
