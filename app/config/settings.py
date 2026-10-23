import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    """Configuración principal de BEST-IA"""
    
    # 🏷️ Información de la aplicación
    APP_NAME: str = os.getenv("APP_NAME", "BEST-IA")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.0.0")
    APP_ENV: str = os.getenv("APP_ENVIRONMENT", "development")
    
    # 🔐 API Keys
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    
    # 🎨 Configuración de tema
    PRIMARY_COLOR: str = os.getenv("PRIMARY_COLOR", "#6E44FF")
    SECONDARY_COLOR: str = os.getenv("SECONDARY_COLOR", "#00D4AA")
    ACCENT_COLOR: str = os.getenv("ACCENT_COLOR", "#FF6B9D")
    DARK_BACKGROUND: str = os.getenv("DARK_BACKGROUND", "#0F0F1E")
    DARK_CARD: str = os.getenv("DARK_CARD", "#1A1A2E")
    
    # 🤖 Configuración de IA
    DEFAULT_AI_MODEL: str = os.getenv("DEFAULT_AI_MODEL", "deepseek-chat")
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "2000"))
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    
    # 📁 Rutas
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    ASSETS_DIR: Path = BASE_DIR / "assets"
    
    # 🚀 Métodos de utilidad
    @classmethod
    def is_development(cls) -> bool:
        """Verifica si está en modo desarrollo"""
        return cls.APP_ENV == "development"
    
    @classmethod
    def get_colors(cls) -> dict:
        """Obtiene diccionario de colores"""
        return {
            "primary": cls.PRIMARY_COLOR,
            "secondary": cls.SECONDARY_COLOR,
            "accent": cls.ACCENT_COLOR,
            "dark_bg": cls.DARK_BACKGROUND,
            "dark_card": cls.DARK_CARD,
        }

# Instancia global de configuración
settings = Settings()