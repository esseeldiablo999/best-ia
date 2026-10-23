"""
ai_client.py - Cliente avanzado para DeepSeek API
Con sistema de personalidades y funciones mejoradas
"""

import openai
import httpx
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..config.settings import settings

class AIClient:
    """Cliente avanzado para DeepSeek API con personalidades"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEFAULT_AI_MODEL
        self.base_url = "https://api.deepseek.com/v1"
        self.client = None
        self._initialize_client()
        self.history = []
        self.personality = "helpful"  # Personalidad por defecto
        self.user_name = "Usuario"
        
        # Estadísticas
        self.stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "start_time": datetime.now()
        }
    
    def _initialize_client(self):
        """Inicializa el cliente OpenAI compatible"""
        if self.api_key and not self.api_key.startswith("tu_clave"):
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                http_client=httpx.Client(timeout=30.0)
            )
        else:
            self.client = None  # Modo demo
    
    # ==================== PERSONALIDADES ====================
    
    PERSONALITIES = {
        "helpful": {
            "name": "Asistente Útil",
            "system_prompt": "Eres BEST-IA, un asistente de IA útil, amable y detallado. Responde en español de manera clara y completa.",
            "greeting": "¡Hola! Soy BEST-IA, tu asistente personal. ¿En qué puedo ayudarte hoy? 😊",
            "style": "formal",
            "emoji_set": ["🤗", "🌟", "💡", "✨", "🎯"]
        },
        "friendly": {
            "name": "Amigable",
            "system_prompt": "Eres BEST-IA, un amigo conversacional. Habla en español coloquial, sé cálido y usa emojis apropiados.",
            "greeting": "¡Hey! ✨ Soy BEST-IA, ¿cómo estás? Cuéntame, ¿qué pasa? 💬",
            "style": "casual",
            "emoji_set": ["😊", "👋", "💬", "🎉", "🤝"]
        },
        "technical": {
            "name": "Técnico",
            "system_prompt": "Eres BEST-IA, experto técnico. Da explicaciones detalladas, incluye ejemplos de código cuando sea relevante.",
            "greeting": "Buen día. Soy BEST-IA, especialista técnico. Listo para analizar problemas y ofrecer soluciones precisas. ⚙️",
            "style": "professional",
            "emoji_set": ["⚙️", "🔧", "💻", "📊", "🔍"]
        },
        "funny": {
            "name": "Divertido",
            "system_prompt": "Eres BEST-IA, el asistente más divertido. Usa humor, chistes apropiados y mantén el ánimo alto.",
            "greeting": "¡Saludos terrestres! 👽 Soy BEST-IA, tu robot favorito. ¿Listo para reír y aprender? 😄",
            "style": "humorous",
            "emoji_set": ["😂", "🤣", "🎭", "🤪", "😆"]
        },
        "creative": {
            "name": "Creativo",
            "system_prompt": "Eres BEST-IA, artista digital. Sé poético, metafórico y estimula la imaginación.",
            "greeting": "✨ Hola, soy BEST-IA, tu musa digital. Las ideas fluyen como ríos de bits. ¿Qué crearemos hoy? 🎨",
            "style": "poetic",
            "emoji_set": ["🎨", "✨", "🌌", "📝", "🎭"]
        },
        "brief": {
            "name": "Conciso",
            "system_prompt": "Eres BEST-IA, directo al punto. Da respuestas cortas, claras y sin rodeos.",
            "greeting": "Hola. BEST-IA aquí. ¿Pregunta?",
            "style": "concise",
            "emoji_set": ["✅", "⚡", "🎯", "📌", "✓"]
        }
    }
    
    def set_personality(self, personality_name: str) -> bool:
        """Cambia la personalidad de BEST-IA"""
        if personality_name in self.PERSONALITIES:
            self.personality = personality_name
            return True
        return False
    
    def set_user_name(self, name: str):
        """Establece el nombre del usuario"""
        self.user_name = name
    
    def get_current_personality(self) -> Dict:
        """Obtiene la personalidad actual"""
        return self.PERSONALITIES.get(self.personality, self.PERSONALITIES["helpful"])
    
    # ==================== CHAT PRINCIPAL ====================
    
    def chat(self, message: str, temperature: float = 0.7) -> Dict[str, Any]:
        """Chat principal con personalidad"""
        self.stats["total_requests"] += 1
        
        if not self.client:
            return self._demo_response(message)
        
        try:
            messages = self._prepare_messages(message)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=settings.AI_MAX_TOKENS,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            answer = response.choices[0].message.content
            self._save_to_history(message, answer)
            
            # Actualizar estadísticas
            if response.usage:
                self.stats["total_tokens"] += response.usage.total_tokens
            
            return {
                "success": True,
                "answer": answer,
                "model": response.model,
                "tokens": response.usage.total_tokens if response.usage else 0,
                "personality": self.personality
            }
            
        except Exception as e:
            return {
                "success": False,
                "answer": f"Error: {str(e)}",
                "error": str(e)
            }
    def analyze_document(self, document_text: str, question: str, temperature: float = 0.5) -> dict:
        """Analiza un documento largo basándose en una pregunta"""
        if not self.client:
            return self._demo_response("Análisis de documento (Modo Demo)")

        try:
            safe_text = document_text[:15000]
            
            prompt = f"""
            El usuario ha subido un documento. Aquí está su contenido:
            ---
            {safe_text}
            ---
            
            Basándote EXCLUSIVAMENTE en el texto anterior, responde a esta pregunta:
            {question}
            """

            messages = [
                {"role": "system", "content": "Eres BEST-IA, un asistente experto en analizar documentos."},
                {"role": "user", "content": prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=settings.AI_MAX_TOKENS
            )

            return {
                "success": True,
                "answer": response.choices[0].message.content,
                "tokens": response.usage.total_tokens if response.usage else 0
            }
        except Exception as e:
            return {"success": False, "answer": f"Error analizando documento: {str(e)}"}

    def chat_with_custom_prompt(self, message: str, custom_prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        """Chat con prompt personalizado"""
        messages = [
            {"role": "system", "content": custom_prompt},
            {"role": "user", "content": message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=settings.AI_MAX_TOKENS
            )
            
            return {
                "success": True,
                "answer": response.choices[0].message.content,
                "model": response.model
            }
        except Exception as e:
            return {
                "success": False,
                "answer": f"Error: {str(e)}"
            }
    
    def _prepare_messages(self, new_message: str) -> List[Dict]:
        """Prepara mensajes con personalidad"""
        personality = self.get_current_personality()
        
        messages = [
            {"role": "system", "content": personality["system_prompt"]}
        ]
        
        # Agregar historial reciente (personalizado)
        for msg in self.history[-4:]:  # Menos historial para dejar espacio a la personalidad
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Mensaje actual con contexto de usuario
        personalized_message = f"{self.user_name}: {new_message}"
        messages.append({
            "role": "user",
            "content": personalized_message
        })
        
        return messages
    
    def _save_to_history(self, question: str, answer: str):
        """Guarda conversación en historial"""
        self.history.append({
            "role": "user",
            "content": question,
            "timestamp": time.time(),
            "personality": self.personality
        })
        
        self.history.append({
            "role": "assistant",
            "content": answer,
            "timestamp": time.time(),
            "personality": self.personality
        })
        
        # Mantener solo últimos 30 mensajes
        if len(self.history) > 30:
            self.history = self.history[-30:]
    
    def _demo_response(self, message: str) -> Dict[str, Any]:
        """Respuesta de demostración"""
        time.sleep(0.5)
        
        personality = self.get_current_personality()
        greetings = [
            f"{personality['greeting']}",
            f"Modo: {personality['name']}. Mensaje: '{message[:50]}...'",
            f"💡 Con API Key real, respondería como: {personality['name']}",
            f"🎭 Personalidad '{personality['name']}' activa. Configura API Key."
        ]
        
        return {
            "success": True,
            "answer": random.choice(greetings),
            "model": "demo-mode",
            "tokens": 0,
            "personality": self.personality
        }
    
    # ==================== FUNCIONES ESPECIALES ====================
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analiza sentimiento del texto"""
        prompt = f"""Analiza el sentimiento de este texto y devuelve JSON con:
        - sentiment: "positive", "negative", "neutral", "mixed"
        - confidence: 0-1
        - keywords: lista de palabras clave
        - emotion: emoción principal
        
        Texto: {text}"""
        
        response = self.chat_with_custom_prompt(prompt, "Eres un analista de sentimientos experto.")
        return response
    
    def summarize_text(self, text: str, max_length: int = 200) -> Dict[str, Any]:
        """Resume texto largo"""
        prompt = f"""Resume este texto en máximo {max_length} caracteres manteniendo la idea principal:
        
        {text}"""
        
        response = self.chat_with_custom_prompt(prompt, "Eres un experto en resumir información.")
        return response
    
    def translate_text(self, text: str, target_language: str = "inglés") -> Dict[str, Any]:
        """Traduce texto"""
        prompt = f"""Traduce este texto al {target_language} manteniendo el tono y significado:
        
        {text}"""
        
        response = self.chat_with_custom_prompt(prompt, "Eres un traductor profesional bilingüe.")
        return response
    
    # ==================== UTILIDADES ====================
    
    def clear_history(self):
        """Limpia el historial"""
        self.history = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas"""
        elapsed = datetime.now() - self.stats["start_time"]
        
        return {
            "total_requests": self.stats["total_requests"],
            "total_tokens": self.stats["total_tokens"],
            "uptime_hours": round(elapsed.total_seconds() / 3600, 2),
            "current_personality": self.personality,
            "history_size": len(self.history),
            "user_name": self.user_name
        }
    
    def get_personality_options(self) -> List[Dict[str, str]]:
        """Obtiene lista de personalidades disponibles"""
        return [
            {"id": key, "name": value["name"], "description": value["system_prompt"][:100] + "..."}
            for key, value in self.PERSONALITIES.items()
        ]

# Instancia global
ai_client = AIClient()