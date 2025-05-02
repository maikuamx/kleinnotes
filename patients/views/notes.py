from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from patients.models import Patient, Note
from patients.forms.notes import NoteForm
from patients.services.word_cloud_service import WordCloudService

class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'patients/notes/list.html'
    context_object_name = 'notes'

    def get_queryset(self):
        self.patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        return Note.objects.filter(patient=self.patient)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.patient
        return context

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'patients/notes/create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = get_object_or_404(Patient, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        note = form.save(commit=False)
        note.patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        note.save()
        
        try:
            # Update word clouds
            word_cloud_service = WordCloudService()
            word_cloud_service.update_word_clouds(note.patient, note.content)
            messages.success(self.request, 'Nota creada exitosamente')
        except ValueError as e:
            messages.warning(self.request, 'Nota guardada, pero no se pudo generar la nube de palabras')
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('patient_notes', kwargs={'pk': self.kwargs['pk']})

class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'patients/notes/edit.html'

    def get_success_url(self):
        return reverse_lazy('patient_notes', kwargs={'pk': self.object.patient.pk})

class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    template_name = 'patients/notes/delete.html'

    def get_success_url(self):
        return reverse_lazy('patient_notes', kwargs={'pk': self.object.patient.pk})