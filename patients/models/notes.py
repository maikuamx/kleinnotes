from django.db import models
from django.core.files.storage import FileSystemStorage
from patients.models import Patient

class Note(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField(verbose_name='Contenido de la nota')
    image = models.ImageField(upload_to='notes_images/', blank=True, null=True, verbose_name='Imagen de la nota')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Nota de {self.patient} - {self.created_at.strftime('%d/%m/%Y')}"

class WordCloud(models.Model):
    CLOUD_TYPES = [
        ('individual', 'Individual'),
        ('global', 'Global'),
    ]
    
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='word_clouds',
        null=True, 
        blank=True
    )
    cloud_type = models.CharField(max_length=10, choices=CLOUD_TYPES)
    image = models.ImageField(upload_to='word_clouds/')
    data = models.JSONField(default=dict)  # Almacena frecuencias de palabras
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['patient', 'cloud_type']]

    def __str__(self):
        if self.patient:
            return f"Nube de palabras {self.get_cloud_type_display()} - {self.patient}"
        return f"Nube de palabras {self.get_cloud_type_display()}"