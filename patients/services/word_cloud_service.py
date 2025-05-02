from patients.models import WordCloud, Note
from patients.services.text_analysis_service import TextAnalysisService

class WordCloudService:
    def __init__(self):
        self.text_analysis = TextAnalysisService()

    def update_word_clouds(self, patient, text):
        """
        Actualiza las nubes de palabras para un paciente específico y la nube global
        """
        # Procesar el texto
        frequencies = self.text_analysis.process_text(text)
        
        # Verificar si hay palabras significativas
        if not frequencies:
            print("No se encontraron palabras significativas para la nube de palabras")
            return
        
        # Actualizar nube individual del paciente
        self._update_cloud(patient, frequencies, 'individual')
        
        # Actualizar nube global
        self._update_global_cloud(frequencies)

    def _update_cloud(self, patient, frequencies, cloud_type):
        """
        Actualiza o crea una nube de palabras específica
        """
        try:
            # Si no hay frecuencias y es una nube individual, eliminar la nube existente
            if not frequencies and cloud_type == 'individual':
                WordCloud.objects.filter(patient=patient, cloud_type=cloud_type).delete()
                return

            # Generar imagen de nube de palabras
            image_content = self.text_analysis.generate_wordcloud(frequencies)
            
            # Actualizar o crear nube de palabras
            cloud, created = WordCloud.objects.get_or_create(
                patient=patient if cloud_type == 'individual' else None,
                cloud_type=cloud_type,
                defaults={'data': frequencies}
            )
            
            if not created:
                # Combinar frecuencias existentes con nuevas
                existing_data = cloud.data
                for word, freq in frequencies.items():
                    existing_data[word] = existing_data.get(word, 0) + freq
                cloud.data = existing_data
            
            # Guardar nueva imagen
            cloud.image.save(
                f'wordcloud_{cloud_type}_{patient.id if patient else "global"}.png',
                image_content,
                save=True
            )
        except Exception as e:
            print(f"Error al actualizar la nube de palabras: {str(e)}")
            # No propagar el error para que no afecte el guardado de la nota

    def _update_global_cloud(self, frequencies):
        """
        Actualiza la nube de palabras global
        """
        try:
            # Verificar si hay notas en el sistema
            if Note.objects.exists():
                self._update_cloud(None, frequencies, 'global')
            else:
                # Si no hay notas, eliminar la nube global
                WordCloud.objects.filter(cloud_type='global').delete()
        except Exception as e:
            print(f"Error al actualizar la nube de palabras global: {str(e)}")
            # No propagar el error para que no afecte el guardado de la nota