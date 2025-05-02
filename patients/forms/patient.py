from django import forms
from patients.models import Patient, Parent, Sibling, MedicalHistory, HouseholdMember
from django.core.exceptions import ValidationError

class PatientForm(forms.ModelForm):
    # Campos adicionales para validación
    parent_name = forms.CharField(required=False)
    parent_birth_date = forms.DateField(required=False)
    parent_education_level = forms.CharField(required=False)
    parent_occupation = forms.CharField(required=False)
    parent_pathological_history = forms.CharField(required=False)

    sibling_name = forms.CharField(required=False)
    sibling_birth_date = forms.DateField(required=False)
    sibling_education_level = forms.CharField(required=False)
    sibling_has_addictions = forms.BooleanField(required=False)
    sibling_pathological_history = forms.CharField(required=False)

    household_name = forms.CharField(required=False)
    household_relationship = forms.CharField(required=False)
    household_medical_history = forms.CharField(required=False)

    class Meta:
        model = Patient
        exclude = ['psychologist', 'created_at', 'updated_at']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'marital_status': forms.Select(attrs={'class': 'form-input'}),
            'voluntary_assistance': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.FileInput)):
                field.widget.attrs['class'] = 'form-input'
            
        # Personalizar etiquetas
        self.fields['photo'].label = 'Foto del paciente'
        self.fields['first_name'].label = 'Nombre(s)'
        self.fields['last_name'].label = 'Apellidos'
        self.fields['birth_date'].label = 'Fecha de nacimiento'
        self.fields['gender'].label = 'Género'
        self.fields['birthplace'].label = 'Lugar de nacimiento'
        self.fields['education_level'].label = 'Escolaridad'
        self.fields['marital_status'].label = 'Estado civil'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['phone'].label = 'Teléfono'
        self.fields['address'].label = 'Dirección'
        self.fields['religion'].label = 'Religión'
        self.fields['voluntary_assistance'].label = '¿Acude voluntariamente?'

        # Campos requeridos
        required_fields = ['first_name', 'last_name', 'birth_date', 'gender', 
                         'birthplace', 'education_level', 'marital_status', 
                         'phone', 'address']
        for field_name in required_fields:
            self.fields[field_name].required = True

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que al menos un padre sea ingresado
        parent_names = self.data.getlist('parent_name[]')
        if not any(name.strip() for name in parent_names):
            raise ValidationError('Debe ingresar al menos un padre o tutor.')

        # Validar fechas de nacimiento de familiares
        for i, birth_date in enumerate(self.data.getlist('parent_birth_date[]')):
            if birth_date and parent_names[i].strip():
                try:
                    forms.DateField().clean(birth_date)
                except ValidationError:
                    raise ValidationError(f'Fecha de nacimiento inválida para el padre/tutor {i+1}')

        for i, birth_date in enumerate(self.data.getlist('sibling_birth_date[]')):
            if birth_date and self.data.getlist('sibling_name[]')[i].strip():
                try:
                    forms.DateField().clean(birth_date)
                except ValidationError:
                    raise ValidationError(f'Fecha de nacimiento inválida para el hermano {i+1}')

        return cleaned_data
