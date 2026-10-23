"""
themes.py - Sistema de temas para BEST-IA
"""

class ThemeManager:
    """Gestor de temas personalizados"""
    
    def __init__(self):
        """Inicializa el gestor de temas"""
        self.colors = {
            "primary": "#6E44FF",
            "secondary": "#00D4AA",
            "accent": "#FF6B9D",
            "dark_bg": "#0F0F1E",
            "dark_card": "#1A1A2E",
            "text_primary": "#FFFFFF",
            "text_secondary": "#B0B0D0"
        }
        self.current_theme = "neon_future"
    
    def get_css(self):
        """Genera CSS personalizado para BEST-IA"""
        colors = self.colors
        
        return f"""
        <style>
        :root {{
            --primary: {colors['primary']};
            --secondary: {colors['secondary']};
            --accent: {colors['accent']};
            --dark-bg: {colors['dark_bg']};
            --dark-card: {colors['dark_card']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
        }}
        
        .stApp {{
            background: linear-gradient(135deg, var(--dark-bg) 0%, #1a1a2e 100%);
            color: var(--text-primary);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        h1, h2, h3 {{
            color: var(--primary) !important;
        }}
        
        .stButton > button {{
            background: linear-gradient(90deg, var(--primary), var(--accent));
            color: white;
            border: none;
            border-radius: 25px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(110, 68, 255, 0.4);
        }}
        
        [data-testid="stChatMessage"][aria-label="user"] > div {{
            background: linear-gradient(90deg, var(--primary), #8A6CFF);
            color: white;
            border-radius: 20px 20px 5px 20px;
        }}
        
        [data-testid="stChatMessage"][aria-label="assistant"] > div {{
            background: var(--dark-card);
            color: var(--text-primary);
            border-radius: 20px 20px 20px 5px;
            border-left: 4px solid var(--secondary);
        }}
        
        section[data-testid="stSidebar"] > div {{
            background: var(--dark-card);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .stChatInput > div > input {{
            background: rgba(30, 30, 60, 0.8);
            color: var(--text-primary);
            border: 2px solid var(--primary);
            border-radius: 25px;
            padding: 12px 20px;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        [data-testid="stChatMessage"] {{
            animation: fadeIn 0.5s ease;
        }}
        </style>
        """
    
    def set_theme(self, theme_name):
        """Cambia el tema actual"""
        themes = {
            "neon_future": {
                "primary": "#6E44FF",
                "secondary": "#00D4AA",
                "accent": "#FF6B9D"
            },
            "midnight_purple": {
                "primary": "#8A2BE2",
                "secondary": "#9370DB",
                "accent": "#DA70D6"
            }
        }
        
        if theme_name in themes:
            self.colors.update(themes[theme_name])
            self.current_theme = theme_name
            return True
        return False

# Instancia global del gestor de temas
theme_manager = ThemeManager()