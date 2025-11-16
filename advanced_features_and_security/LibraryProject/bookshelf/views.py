from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from django import forms

from .models import Book


# Simple ModelForm for Book create/update
class BookForm(forms.ModelForm):
	class Meta:
		model = Book
		fields = ['title', 'author', 'publication_year']


@permission_required('bookshelf.can_create', raise_exception=True)
def add_book(request):
	if request.method == 'POST':
		form = BookForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('relationship_app:book_list')
	else:
		form = BookForm()
	return render(request, 'relationship_app/book_form.html', {'form': form, 'action': 'Add'})


@permission_required('bookshelf.can_edit', raise_exception=True)
def edit_book(request, pk):
	book = get_object_or_404(Book, pk=pk)
	if request.method == 'POST':
		form = BookForm(request.POST, instance=book)
		if form.is_valid():
			form.save()
			return redirect('relationship_app:book_list')
	else:
		form = BookForm(instance=book)
	return render(request, 'relationship_app/book_form.html', {'form': form, 'action': 'Edit'})


@permission_required('bookshelf.can_delete', raise_exception=True)
def delete_book(request, pk):
	book = get_object_or_404(Book, pk=pk)
	if request.method == 'POST':
		book.delete()
		return redirect('relationship_app:book_list')
	return render(request, 'relationship_app/book_confirm_delete.html', {'book': book})
