from django import forms
from .models import Book


class ExampleForm(forms.ModelForm):
    """
    ModelForm for Book creation and editing.

    Security Features:
    - All fields are validated by Django forms (type checking, length constraints)
    - User input is automatically escaped in templates (auto-escaping is default)
    - Database queries use ORM (parameterized, prevents SQL injection)
    - CSRF token is required in template ({% csrf_token %})
    """

    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book title',
                'maxlength': '200',  # Match model field max_length
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter author name',
                'maxlength': '100',  # Match model field max_length
            }),
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY',
                'min': '1000',
                'max': '9999',
            }),
        }

    def clean_title(self):
        """Validate title field."""
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) == 0:
            raise forms.ValidationError('Title cannot be empty or whitespace only.')
        return title.strip() if title else title

    def clean_author(self):
        """Validate author field."""
        author = self.cleaned_data.get('author')
        if author and len(author.strip()) == 0:
            raise forms.ValidationError('Author cannot be empty or whitespace only.')
        return author.strip() if author else author

    def clean_publication_year(self):
        """Validate publication year."""
        year = self.cleaned_data.get('publication_year')
        if year:
            if year < 1000 or year > 9999:
                raise forms.ValidationError('Publication year must be between 1000 and 9999.')
        return year


class BookSearchForm(forms.Form):
    """
    Form for searching books by title or author.

    Security Features:
    - CharField with max_length prevents buffer overflow attacks
    - Form validation ensures safe input
    - Query uses Django ORM (parameterized, prevents SQL injection)
    - Never use raw SQL or string formatting with user input
    """

    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title or author...',
            'autocomplete': 'off',  # Prevent autocomplete of search history
        }),
        help_text='Enter a title or author name',
    )

    def clean_search_query(self):
        """Sanitize search query."""
        query = self.cleaned_data.get('search_query', '').strip()
        # Remove leading/trailing whitespace
        # Prevent empty searches (optional, adjust as needed)
        return query
