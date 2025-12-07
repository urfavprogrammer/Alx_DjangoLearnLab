from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment
from taggit.forms import TagField, TagWidget

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
    
class PostForm(forms.ModelForm):
    tags = TagField(widget=TagWidget(), required=False, help_text="Add tags separated by commas.")
    class Meta:
        model = Post
        fields = ['title', 'content', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        help_texts = {
            'content': 'Be respectful and constructive in your comments.',
        }
    
    def clean_content(self):
        content = self.cleaned_data['content'].strip()
        if len(content) < 10:
            raise forms.ValidationError("Comment is too short. Please provide more details.")
        return content
    