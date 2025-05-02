import cv2
import pytesseract
import numpy as np
from PIL import Image

class TrOCRService:
    def __init__(self):
        # Configurar Tesseract para español
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.config = r'--oem 3 --psm 6 -l spa'

    def preprocess_image(self, image):
        """
        Preprocesa la imagen para mejorar el reconocimiento de texto manuscrito
        """
        # Convertir a array numpy
        img_array = np.array(image)
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Binarización adaptativa
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 21, 10
        )
        
        # Reducción de ruido
        denoised = cv2.fastNlMeansDenoising(binary)
        
        # Dilatación para conectar componentes
        kernel = np.ones((2,2), np.uint8)
        dilated = cv2.dilate(denoised, kernel, iterations=1)
        
        return Image.fromarray(dilated)

    def process_image(self, image_path):
        """
        Procesa una imagen usando Tesseract con preprocesamiento
        """
        try:
            # Cargar y preprocesar la imagen
            image = Image.open(image_path).convert('RGB')
            processed_image = self.preprocess_image(image)
            
            # Realizar OCR
            text = pytesseract.image_to_string(
                processed_image,
                config=self.config
            )
            
            return self.postprocess_text(text)
            
        except Exception as e:
            print(f"Error en OCR: {str(e)}")
            return ""

    def postprocess_text(self, text):
        """
        Limpia y mejora el texto reconocido
        """
        # Eliminar caracteres no deseados
        text = ''.join(c for c in text if c.isprintable())
        
        # Eliminar espacios múltiples
        text = ' '.join(text.split())
        
        # Corregir puntuación común
        text = text.replace(' ,', ',')
        text = text.replace(' .', '.')
        text = text.replace(' :', ':')
        
        # Asegurar que las oraciones empiecen con mayúscula
        sentences = text.split('. ')
        sentences = [s.capitalize() for s in sentences]
        text = '. '.join(sentences)
        
        return text.strip()