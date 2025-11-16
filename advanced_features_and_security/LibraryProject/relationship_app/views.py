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
    """Function-based view that renders an HTML list of books and their authors."""
    books = Book.objects.select_related('author').all()
    return render(request, 'relationship_app/book_list.html', {'books': books})


class LibraryBooksView(ListView):
    """Class-based view that lists books for a specific library using a template.

    URL expects a `pk` argument for the Library primary key.
    """
    model = Book
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'books'

    def get_queryset(self):
        library_pk = self.kwargs.get('pk')
        return Book.objects.select_related('author').filter(libraries__pk=library_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        library_pk = self.kwargs.get('pk')
        context['library'] = get_object_or_404(Library, pk=library_pk)
        return context

def register(request):
    """Simple user registration view using Django's UserCreationForm.

    On successful registration the user is logged in and redirected to the
    login redirect URL.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
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


@permission_required('relationship_app.can_create', raise_exception=True)
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            return redirect('relationship_app:book-list')
    else:
        form = BookForm()
    return render(request, 'relationship_app/book_form.html', {'form': form, 'action': 'Add'})


@permission_required('relationship_app.can_edit', raise_exception=True)
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('relationship_app:book-list')
    else:
        form = BookForm(instance=book)
    return render(request, 'relationship_app/book_form.html', {'form': form, 'action': 'Edit'})


@permission_required('relationship_app.can_delete', raise_exception=True)
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('relationship_app:book-list')
    return render(request, 'relationship_app/book_confirm_delete.html', {'book': book})
