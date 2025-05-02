from django import forms
from patients.models import Note

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 10,
                'placeholder': 'Escribe o dicta tus notas aquí...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*',
                'style': 'display: none;'
            })
        }