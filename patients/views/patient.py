from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.urls import reverse_lazy
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

from patients.models import Patient
from patients.forms.patient import PatientForm
from patients.services.patient_form_handler import PatientFormHandler

class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'

    def get_queryset(self):
        return Patient.objects.filter(psychologist=self.request.user)

class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'
    success_url = reverse_lazy('patient_list')

    def form_valid(self, form):
        form.instance.psychologist = self.request.user
        response = super().form_valid(form)
        handler = PatientFormHandler(self.request, self.object)
        handler.handle_medical_history()
        handler.handle_family_members()
        return response

class PatientDetailView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'

    def get_queryset(self):
        return Patient.objects.filter(psychologist=self.request.user)

class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            # Convertir el historial médico a diccionario si existe
            medical_history = None
            if hasattr(self.object, 'medical_history'):
                medical_history = model_to_dict(
                    self.object.medical_history,
                    exclude=['id', 'patient']
                )

            # Preparar datos existentes
            context['existing_data'] = {
                'medical_history': medical_history,
                'parents': [
                    model_to_dict(parent, exclude=['id', 'patient']) 
                    for parent in self.object.parents.all()
                ],
                'siblings': [
                    model_to_dict(sibling, exclude=['id', 'patient']) 
                    for sibling in self.object.siblings.all()
                ],
                'household_members': [
                    model_to_dict(member, exclude=['id', 'patient']) 
                    for member in self.object.household_members.all()
                ]
            }
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        handler = PatientFormHandler(self.request, self.object)
        handler.handle_medical_history()
        handler.handle_family_members()
        return response

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.object.pk})