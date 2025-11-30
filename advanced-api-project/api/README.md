API Views for `api` app

This README explains how each view in `api/views.py` is configured, what
custom hooks or settings are present, and how to extend or modify the
behaviour.

Files referenced:
- `api/views.py` - class-based DRF views for `Book` model
- `api/serializers.py` - serializers used by the views
- `api/models.py` - model definitions (Author, Book)

Views
-----

ListView (class: `ListView`)
- Purpose: Return a list of `Book` instances.
- Base class: `generics.ListAPIView`.
- Queryset: `Book.objects.all()` by default.
- Serializer: `BookSerializer`.
- Permission: `permissions.AllowAny` (readable by unauthenticated users).
- Filtering hook: `get_queryset()` supports these query parameters:
  - `author=<id>` filters by `author_id`.
  - `year=<int>` filters by `publication_year`.
  - `title=<str>` performs a case-insensitive containment search on `title`.
- Extension points: replace `get_queryset()` with DjangoFilterBackend for
  more advanced filtering, or add ordering/pagination classes.

DetailView (class: `DetailView`)
- Purpose: Retrieve a single `Book` by ID.
- Base class: `generics.RetrieveAPIView`.
- Permission: `permissions.AllowAny` (readable by unauthenticated users).

CreateView (class: `CreateView`)
- Purpose: Create new `Book` instances.
- Base class: `generics.CreateAPIView`.
- Parsers: `JSONParser`, `FormParser`, `MultiPartParser` — accepts JSON
  requests, HTML form submissions, and multipart file uploads.
- Permission: `permissions.IsAuthenticated` — only authenticated users may
  create books. Change to `IsAdminUser` or a custom permission for stricter
  control.
- Validation & hooks:
  - `create()` overrides the default to explicitly call
    `serializer.is_valid(raise_exception=True)` and `self.perform_create()`.
  - Database `IntegrityError` exceptions are caught and returned as a
    `400 Bad Request` JSON response with an `error` detail.
  - Serializer `ValidationError`s are handled by DRF as usual.
- Extension points: perform extra actions in `perform_create()` (e.g. set
  an `owner` field, send signals or emails) or replace parser classes.

UpdateView (class: `UpdateView`)
- Purpose: Update existing `Book` instances.
- Base class: `generics.UpdateAPIView`.
- Parsers: `JSONParser`, `FormParser`, `MultiPartParser`.
- Permission: `permissions.IsAuthenticated` — only authenticated users may
  update. For owner-only updates create `IsOwnerOrReadOnly` permission.
- Validation & hooks:
  - `update()` is overridden to call `serializer.is_valid(raise_exception=True)`
    and `self.perform_update(serializer)`; `IntegrityError` is caught and
    returned as a `400` response.
- Extension points: support partial updates by calling the endpoint with
  `PATCH` or by invoking `update(..., partial=True)`. Add custom logic in
  `perform_update()` to handle side effects.

DeleteView (class: `DeleteView`)
- Purpose: Delete a `Book` instance.
- Base class: `generics.DestroyAPIView`.
- Permission: `permissions.IsAuthenticated` — only authenticated users may
  delete. Replace with a custom permission (e.g. staff-only) if desired.

Custom permission example (in `views.py`)
- `IsStaffOrReadOnly`: an example `permissions.BasePermission` implementation
  that allows safe methods to everyone but restricts write operations to
  staff users (`request.user.is_staff`). Swap this into `permission_classes`
  for stricter controls.

Notes & Recommendations
- For production APIs, consider using `django-filter` and DRF's
  `DjangoFilterBackend` for robust filtering, and `IsAdminUser` or a
  custom permission for sensitive endpoints.
- If you need owner-based permissions, add an `owner`/`created_by` FK to
  `Book`, set it in `perform_create()`, then implement `IsOwnerOrReadOnly`.
- The views catch `IntegrityError` to provide friendlier DB error messages.
  You can customize the error payload or log the exception as needed.

Quick checks
------------
Run these locally to verify syntax and basic Django checks:

```bash
python3 -m py_compile api/views.py api/serializers.py api/models.py
python3 manage.py check
```

If you want, I can:
- Add `IsOwnerOrReadOnly` and an `owner` field to `Book` and wire it up.
- Replace the simple `get_queryset()` filters with `django-filter` configuration.
- Add tests demonstrating permission enforcement and create/update behavior.

Filtering, Search & Ordering Examples
------------------------------------
The `ListView` supports the following query parameters once `django-filter`
and DRF filter backends are enabled in the project:

- Filter by exact fields:
  - `GET /api/books/?author=1` — returns books whose `author` FK equals `1`.
  - `GET /api/books/?publication_year=2020` — books published in 2020.
  - `GET /api/books/?title=Python` — exact match filtering on `title` (useful for equality checks).

- Search (text search across fields):
  - `GET /api/books/?search=django` — performs a case-insensitive search across `title` and `author__name`.

- Ordering (sort results):
  - `GET /api/books/?ordering=title` — order by title ascending.
  - `GET /api/books/?ordering=-publication_year` — order by publication_year descending.

Combine parameters:
  - `GET /api/books/?author=2&search=api&ordering=-publication_year`

Notes:
  - Ensure `django-filter` is installed and added to `INSTALLED_APPS` (`'django_filters'`).
  - Enable DRF filter backends in `settings.py` for global behavior, or use the view-level
    `filter_backends` as shown in `views.py`.
  - Example settings snippet to add in `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}
```

If you'd like, I can add `django-filter` to a `requirements.txt` and wire up a project-level configuration automatically.
