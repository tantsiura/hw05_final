from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')

    def clean_subject(self):
        data = self.cleaned_data['subject']

        if data == '':
            raise forms.ValidationError('А кто поле будет заполнять, Пушкин?')
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_subject(self):
        data = self.cleaned_data['subject']

        if data == '':
            raise forms.ValidationError('А кто поле будет заполнять, Пушкин?')
        return data
