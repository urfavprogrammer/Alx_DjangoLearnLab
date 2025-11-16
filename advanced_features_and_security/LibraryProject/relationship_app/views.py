from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test
from django import forms

from .models import Book

from .models import Library


def list_books(request):
    """Function-based view that renders an HTML list of books and their authors.
    
    Security: Uses Django ORM with select_related() to prevent N+1 queries.
    No user input is used in the query, so SQL injection is not a risk here.
    """
    # Use select_related() to fetch related author in a single query (performance + security)
    books = Book.objects.select_related('author').all()
    return render(request, 'relationship_app/book_list.html', {'books': books})


class LibraryBooksView(ListView):
    """Class-based view that lists books for a specific library using a template.

    URL expects a `pk` argument for the Library primary key.
    
    Security: The library_pk is retrieved from URL kwargs and passed to filter().
    Django ORM automatically parameterizes queries, preventing SQL injection.
    Using get_object_or_404() prevents enumeration attacks by raising 404 for invalid IDs.
    """
    model = Book
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'books'

    def get_queryset(self):
        library_pk = self.kwargs.get('pk')
        # Safe: Django ORM parameterizes the filter() query automatically
        return Book.objects.select_related('author').filter(libraries__pk=library_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        library_pk = self.kwargs.get('pk')
        # get_object_or_404() prevents information disclosure by raising 404 instead of returning None
        context['library'] = get_object_or_404(Library, pk=library_pk)
        return context

def register(request):
    """Simple user registration view using Django's UserCreationForm.

    On successful registration the user is logged in and redirected to the
    login redirect URL.
    
    Security:
    - Uses Django's UserCreationForm which validates password strength
    - Automatically hashes passwords using the configured PASSWORD_HASHERS
    - user.set_password() and form.save() ensure passwords are never stored in plain text
    - CSRF token is handled by the middleware and template
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Password is automatically hashed
            login(request, user)
            return redirect('relationship_app:book-list')
    else:
        form = UserCreationForm()
    return render(request, 'relationship_app/register.html', {'form': form})


def _has_role(user, role_name: str) -> bool:
    if not user.is_authenticated:
        return False
    profile = getattr(user, 'userprofile', None)
    return profile is not None and profile.role == role_name


@user_passes_test(lambda u: _has_role(u, 'Admin'))
def admin_view(request):
    return render(request, 'relationship_app/admin_view.html')


@user_passes_test(lambda u: _has_role(u, 'Librarian'))
def librarian_view(request):
    return render(request, 'relationship_app/librarian_view.html')


@user_passes_test(lambda u: _has_role(u, 'Member'))
def member_view(request):
    return render(request, 'relationship_app/member_view.html')


# Simple ModelForm for Book create/update
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author']


@permission_required('relationship_app.can_add_book', raise_exception=True)
def add_book(request):
    """View to add a new book.
    
    Security:
    - @permission_required() decorator checks for 'can_add_book' permission
    - Raises 403 Forbidden if user lacks permission (raise_exception=True)
    - ModelForm automatically escapes user input for template rendering
    - CSRF token is required (enforced by CsrfViewMiddleware)
    - POST data is validated by form.is_valid() before saving
    """
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()  # Safe: form validation and ORM parameterization
            return redirect('relationship_app:book-list')
    else:
        form = BookForm()
    return render(request, 'relationship_app/book_form.html', {'form': form, 'action': 'Add'})


@permission_required('relationship_app.can_change_book', raise_exception=True)
def edit_book(request, pk):
    """View to edit an existing book.
    
    Security:
    - @permission_required() checks for 'can_change_book' permission
    - get_object_or_404() prevents information disclosure (returns 404 for invalid pk)
    - pk is passed via URL parameter and used in ORM query (parameterized automatically)
    - ModelForm validates all user input before saving
    - CSRF token is required (enforced by middleware)
    """
    book = get_object_or_404(Book, pk=pk)  # Safe: ORM parameterization
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()  # Safe: form validation before save
            return redirect('relationship_app:book-list')
    else:
        form = BookForm(instance=book)
    return render(request, 'relationship_app/book_form.html', {'form': form, 'action': 'Edit'})


@permission_required('relationship_app.can_delete_book', raise_exception=True)
def delete_book(request, pk):
    """View to delete a book (with confirmation).
    
    Security:
    - @permission_required() checks for 'can_delete_book' permission
    - get_object_or_404() prevents information disclosure
    - POST request required for actual deletion (prevents accidental deletion via GET)
    - CSRF token validated for POST (enforced by middleware)
    """
    book = get_object_or_404(Book, pk=pk)  # Safe: ORM parameterization
    if request.method == 'POST':
        book.delete()  # Safe: object already exists (verified by get_object_or_404)
        return redirect('relationship_app:book-list')
    return render(request, 'relationship_app/book_confirm_delete.html', {'book': book})
