from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from .models import Book, Library


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
