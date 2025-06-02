from django import forms
from publications.models import Publication, Commentary


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ('title', 'body', 'image', 'is_free')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_free': forms.CheckboxInput(),
        }


class CommentaryForm(forms.ModelForm):
    class Meta:
        model = Commentary
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ваш комментарий...'
            }),
        }
        labels = {
            'body': 'Комментарий',
        }
