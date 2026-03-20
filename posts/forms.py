from posts.models import Comment, Post
from django import forms



class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['imagen', 'content']


class PostCommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Escribe un comentario...',
                    'class': 'form-control',
                }
            ),
        }