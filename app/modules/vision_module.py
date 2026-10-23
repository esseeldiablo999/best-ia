import google.generativeai as genai
from app.config.settings import settings
from PIL import Image
import io

def analyze_image(uploaded_file, prompt):
    """Analiza una imagen usando la visión de Gemini"""
    try:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return "⚠️ Falta configurar la API Key de Gemini en los Secrets."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        # Leer la imagen subida
        img = Image.open(io.BytesIO(uploaded_file.getvalue()))
        
        # Enviar a Gemini
        response = model.generate_content([prompt, img])
        return response.text
    except Exception as e:
        return f"❌ Error analizando la imagen: {str(e)}"