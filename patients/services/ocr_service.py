from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch
from django.conf import settings
import os

class OCRService:
    def __init__(self):
        print("Inicializando OCR Service...")
        # Usar el modelo base multilingüe
        self.processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
        self.model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')
        print("Modelo cargado exitosamente")
        
        # Move to GPU if available
        if torch.cuda.is_available():
            self.model.to('cuda')
            print("Modelo movido a GPU")
        else:
            print("Usando CPU para el procesamiento")

    def process_image(self, image_path):
        try:
            print("\n=== Iniciando procesamiento de imagen ===")
            print(f"Ruta original: {image_path}")
            print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
            
            # Si image_path es un objeto FieldFile, obtener su nombre
            if hasattr(image_path, 'name'):
                print("image_path es un objeto FieldFile")
                image_path = image_path.name
            
            # Convertir la ruta relativa a absoluta usando MEDIA_ROOT
            absolute_path = os.path.join(settings.MEDIA_ROOT, str(image_path))
            print(f"Ruta absoluta: {absolute_path}")
            
            # Asegurarse de que la ruta existe
            if not os.path.exists(absolute_path):
                print(f"El archivo no existe en: {absolute_path}")
                # Intentar encontrar el archivo en la ruta original
                if os.path.exists(image_path):
                    print(f"El archivo existe en la ruta original: {image_path}")
                    absolute_path = image_path
                else:
                    raise FileNotFoundError(f"No se encontró el archivo en: {absolute_path}")
            
            print("Cargando imagen...")
            # Load and preprocess image
            image = Image.open(absolute_path).convert('RGB')
            print(f"Imagen cargada. Tamaño: {image.size}")
            
            print("Procesando imagen con el modelo...")
            pixel_values = self.processor(image, return_tensors="pt").pixel_values
            print("Imagen procesada exitosamente")
            
            if torch.cuda.is_available():
                pixel_values = pixel_values.to('cuda')
                print("Tensor movido a GPU")

            print("Generando texto...")
            # Generate text with Spanish-specific settings
            generated_ids = self.model.generate(
                pixel_values,
                max_length=128,
                num_beams=4,
                length_penalty=2.0,
                early_stopping=True
            )
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            print(f"Texto generado: {generated_text}")
            
            processed_text = self.postprocess_text(generated_text)
            print(f"Texto procesado final: {processed_text}")
            
            return processed_text
            
        except Exception as e:
            print(f"\n=== Error en OCR ===")
            print(f"Tipo de error: {type(e).__name__}")
            print(f"Mensaje de error: {str(e)}")
            print(f"Tipo de image_path: {type(image_path)}")
            return None

    def postprocess_text(self, text):
        """Clean and improve the recognized text for Spanish"""
        if not text:
            print("No hay texto para procesar")
            return None
            
        print("\n=== Iniciando post-procesamiento del texto ===")
        print(f"Texto original: {text}")
        
        # Remove unwanted characters
        text = ''.join(c for c in text if c.isprintable())
        print(f"Después de limpiar caracteres no imprimibles: {text}")
        
        # Fix common spacing issues
        text = ' '.join(text.split())
        print(f"Después de arreglar espacios: {text}")
        
        # Fix Spanish-specific punctuation
        text = text.replace(' ,', ',')
        text = text.replace(' .', '.')
        text = text.replace(' :', ':')
        text = text.replace(' ;', ';')
        text = text.replace(' ¿', '¿')
        text = text.replace(' !', '!')
        text = text.replace(' ¡', '¡')
        
        # Handle Spanish-specific characters
        text = text.replace('a~', 'ñ')
        text = text.replace('A~', 'Ñ')
        
        print(f"Después de arreglar puntuación: {text}")
        
        # Capitalize sentences (considering Spanish punctuation)
        sentences = []
        for sentence in text.split('. '):
            # También dividir por otros signos de puntuación que terminan oraciones en español
            for subsentence in sentence.split('! '):
                for final_sentence in subsentence.split('? '):
                    if final_sentence:
                        sentences.append(final_sentence.capitalize())
        
        text = '. '.join(sentences)
        print(f"Texto final: {text}")
        
        return text.strip()