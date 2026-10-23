"""
file_processor.py - Procesador de archivos para BEST-IA
"""
import io
from pypdf import PdfReader
import docx2txt

class FileProcessor:
    """Extrae texto de documentos para que la IA los lea"""

    @staticmethod
    def extract_text(uploaded_file) -> str:
        """Extrae texto dependiendo de la extensión del archivo"""
        filename = uploaded_file.name.lower()
        
        try:
            if filename.endswith(".pdf"):
                return FileProcessor._read_pdf(uploaded_file)
            elif filename.endswith(".docx"):
                return FileProcessor._read_docx(uploaded_file)
            elif filename.endswith(".txt"):
                return uploaded_file.read().decode("utf-8")
            else:
                return "⚠️ Formato de archivo no soportado. Usa PDF, DOCX o TXT."
        except Exception as e:
            return f"❌ Error leyendo el archivo: {str(e)}"

    @staticmethod
    def _read_pdf(file) -> str:
        """Lee un archivo PDF"""
        reader = PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()

    @staticmethod
    def _read_docx(file) -> str:
        """Lee un archivo de Word (.docx)"""
        return docx2txt.process(io.BytesIO(file.read())).strip()