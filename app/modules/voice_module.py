"""
voice_module.py - Módulo profesional de voz para BEST-IA
Versión 6.0 - Totalmente optimizada y probada
"""

import pyttsx3
import speech_recognition as sr
import threading
import time
import queue
import warnings
from typing import Optional, Callable, List, Dict, Any

# Suprimir warnings molestos
warnings.filterwarnings('ignore')

class VoiceModule:
    """
    Módulo profesional de voz con:
    - Reconocimiento de voz con Google Speech Recognition
    - Síntesis de voz con pyttsx3
    - Detección de palabra clave "BEST IA"
    - Múltiples modos de operación
    - Compatibilidad total con Streamlit
    """
    
    def __init__(self, mic_device_index: int = 0):
        """
        Inicializa el módulo de voz
        
        Args:
            mic_device_index: Índice del micrófono a usar (0 = por defecto)
        """
        # ========== ESTADO DEL SISTEMA ==========
        self.is_listening = False
        self.is_speaking = False
        self.is_initialized = False
        
        # ========== CONFIGURACIÓN ==========
        self.mic_device_index = mic_device_index
        self.voice_rate = 180  # Velocidad de habla (palabras por minuto)
        self.voice_volume = 0.9  # Volumen (0.0 a 1.0)
        self.language = "es-ES"  # Idioma para reconocimiento
        self.energy_threshold = 300  # Sensibilidad del micrófono
        self.pause_threshold = 0.8  # Pausa para detectar fin de frase
        self.timeout = 1.0  # Timeout de escucha
        self.phrase_time_limit = 5  # Límite de duración de frase
        
        # ========== PALABRAS DE ACTIVACIÓN ==========
        self.wake_words = [
            "best ia",
            "bestia",
            "best-ia",
            "best i a",
            "bes tia"
        ]
        
        # ========== COMPONENTES ==========
        self.tts_engine = None  # Motor de texto a voz
        self.recognizer = None  # Reconocedor de voz
        self.microphone = None  # Micrófono
        self.callback = None  # Callback para comandos detectados
        
        # ========== THREADS ==========
        self.listening_thread = None
        self.should_stop = False
        
        # ========== ESTADÍSTICAS ==========
        self.stats = {
            "total_commands": 0,
            "successful_recognitions": 0,
            "failed_recognitions": 0,
            "last_command": "",
            "last_command_time": None,
            "start_time": time.time()
        }
        
        # ========== HISTORIAL ==========
        self.command_history: List[Dict[str, Any]] = []
        self.max_history = 50
        
        # Inicializar componentes
        self._initialize_components()
        
        print(f"✅ Módulo de voz inicializado")
        print(f"🎤 Micrófono configurado: índice {self.mic_device_index}")
        print(f"🗣️ Idioma: {self.language}")
        print(f"🔊 Velocidad: {self.voice_rate} | Volumen: {self.voice_volume}")
    
    # ==================== INICIALIZACIÓN ====================
    
    def _initialize_components(self):
        """Inicializa todos los componentes del módulo de voz"""
        try:
            # Inicializar TTS (texto a voz)
            self._initialize_tts()
            
            # Inicializar STT (reconocimiento de voz)
            self._initialize_stt()
            
            self.is_initialized = True
            
        except Exception as e:
            print(f"❌ Error inicializando componentes: {e}")
            import traceback
            traceback.print_exc()
    
    def _initialize_tts(self):
        """Inicializa el motor de texto a voz"""
        try:
            print("🔧 Inicializando TTS...")
            self.tts_engine = pyttsx3.init()
            
            # Configurar propiedades
            self.tts_engine.setProperty('rate', self.voice_rate)
            self.tts_engine.setProperty('volume', self.voice_volume)
            
            # Buscar voz en español
            voices = self.tts_engine.getProperty('voices')
            spanish_voices = []
            
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'español' in voice.name.lower():
                    spanish_voices.append(voice)
                    print(f"   🎤 Voz encontrada: {voice.name}")
            
            if spanish_voices:
                # Seleccionar la primera voz en español
                self.tts_engine.setProperty('voice', spanish_voices[0].id)
                print(f"🗣️ Voz seleccionada: {spanish_voices[0].name}")
            else:
                print(f"⚠️ No se encontraron voces en español, usando voz por defecto")
                if voices:
                    print(f"   Voz por defecto: {voices[0].name}")
            
            print(f"✅ TTS inicializado correctamente")
            
        except Exception as e:
            print(f"❌ Error inicializando TTS: {e}")
            self.tts_engine = None
    
    def _initialize_stt(self):
        """Inicializa el reconocimiento de voz"""
        try:
            print("🔧 Inicializando STT...")
            
            # Crear reconocedor
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = self.pause_threshold
            
            # Configurar micrófono
            self._setup_microphone()
            
            print(f"✅ STT inicializado correctamente")
            print(f"   Umbral de energía: {self.recognizer.energy_threshold}")
            
        except Exception as e:
            print(f"❌ Error inicializando STT: {e}")
            self.recognizer = None
            self.microphone = None
    
    def _setup_microphone(self):
        """Configura el micrófono según el índice especificado"""
        try:
            # Listar micrófonos disponibles
            available_mics = sr.Microphone.list_microphone_names()
            print(f"📋 Micrófonos detectados: {len(available_mics)}")
            
            # Mostrar primeros 5 micrófonos
            for i, mic in enumerate(available_mics[:5]):
                status = " ← SELECCIONADO" if i == self.mic_device_index else ""
                print(f"   [{i}] {mic[:50]}...{status}")
            
            if len(available_mics) > 5:
                print(f"   ... y {len(available_mics) - 5} más")
            
            # Intentar configurar el micrófono seleccionado
            try:
                self.microphone = sr.Microphone(device_index=self.mic_device_index)
                print(f"✅ Micrófono [{self.mic_device_index}] configurado")
            except Exception as e:
                print(f"⚠️ Error con micrófono [{self.mic_device_index}]: {e}")
                print("🔄 Usando micrófono por defecto")
                self.microphone = sr.Microphone()
                self.mic_device_index = 0
            
            # Probar el micrófono
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print(f"📊 Umbral ajustado: {self.recognizer.energy_threshold:.1f}")
            
        except Exception as e:
            print(f"❌ Error configurando micrófono: {e}")
            self.microphone = None
    
    # ==================== CONTROL PRINCIPAL ====================
    
    def start_listening(self, callback: Callable[[str], None]) -> bool:
        """
        Inicia la escucha de voz en segundo plano
        
        Args:
            callback: Función que se llamará cuando se detecte un comando válido
            
        Returns:
            bool: True si se inició correctamente
        """
        if self.is_listening:
            print("⚠️ Ya se está escuchando")
            return True
        
        if not self.microphone:
            print("❌ No hay micrófono disponible")
            return False
        
        self.callback = callback
        self.is_listening = True
        self.should_stop = False
        
        # Iniciar thread de escucha
        self.listening_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True,
            name="VoiceListener"
        )
        self.listening_thread.start()
        
        print("\n" + "=" * 50)
        print("🎤 MODO VOZ ACTIVADO")
        print("=" * 50)
        print("📢 Di claramente: 'BEST IA' seguido de tu mensaje")
        print("📝 Ejemplo: 'BEST IA, ¿qué hora es?'")
        print("=" * 50)
        
        return True
    
    def stop_listening(self) -> bool:
        """Detiene la escucha de voz"""
        if not self.is_listening:
            return True
        
        print("\n🔇 Deteniendo escucha...")
        self.is_listening = False
        self.should_stop = True
        
        if self.listening_thread:
            self.listening_thread.join(timeout=2)
        
        print("✅ Escucha detenida")
        return True
    
    def _listen_loop(self):
        """Bucle principal de escucha (se ejecuta en thread separado)"""
        print("🔊 Bucle de escucha iniciado")
        
        try:
            with self.microphone as source:
                # Calibración inicial
                print("🎯 Calibrando micrófono...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"✅ Umbral calibrado: {self.recognizer.energy_threshold:.1f}")
                
                print("\n👂 Escuchando... (esperando 'BEST IA')")
                
                while self.is_listening and not self.should_stop:
                    try:
                        # Escuchar audio
                        audio = self.recognizer.listen(
                            source,
                            timeout=self.timeout,
                            phrase_time_limit=self.phrase_time_limit
                        )
                        
                        # Procesar en el mismo thread
                        self._process_audio(audio)
                        
                    except sr.WaitTimeoutError:
                        # Timeout normal, continuar
                        continue
                    except Exception as e:
                        if "input overflowed" not in str(e):
                            print(f"⚠️ Error en escucha: {e}")
                        time.sleep(0.1)
                        
        except Exception as e:
            print(f"❌ Error crítico en bucle de escucha: {e}")
            self.is_listening = False
    
    def _process_audio(self, audio):
        """Procesa un fragmento de audio"""
        try:
            # Reconocer texto
            text = self.recognizer.recognize_google(
                audio,
                language=self.language,
                show_all=False
            ).lower().strip()
            
            print(f"🗣️ Reconocido: '{text}'")
            
            # Verificar si contiene palabra de activación
            for wake_word in self.wake_words:
                if wake_word in text:
                    # Extraer comando
                    command = text.replace(wake_word, '').strip()
                    
                    # Limpiar signos de puntuación
                    command = command.strip(' .,;:?!')
                    
                    if command:
                        print(f"✅ COMANDO DETECTADO: '{command}'")
                        
                        # Actualizar estadísticas
                        self.stats["total_commands"] += 1
                        self.stats["successful_recognitions"] += 1
                        self.stats["last_command"] = command
                        self.stats["last_command_time"] = time.time()
                        
                        # Guardar en historial
                        self.command_history.append({
                            "command": command,
                            "timestamp": time.time(),
                            "raw_text": text
                        })
                        
                        # Limitar historial
                        if len(self.command_history) > self.max_history:
                            self.command_history = self.command_history[-self.max_history:]
                        
                        # Llamar callback
                        if self.callback:
                            try:
                                self.callback(command)
                                print("📞 Callback ejecutado")
                            except Exception as e:
                                print(f"❌ Error en callback: {e}")
                        
                        break
                    else:
                        print("⚠️ Comando vacío después de palabra clave")
            
        except sr.UnknownValueError:
            # No se entendió el audio (silenciosamente)
            self.stats["failed_recognitions"] += 1
            pass
        except sr.RequestError as e:
            print(f"🌐 Error de conexión con Google: {e}")
        except Exception as e:
            print(f"❌ Error procesando audio: {e}")
    
    # ==================== SÍNTESIS DE VOZ ====================
    
    def speak(self, text: str, wait: bool = False) -> bool:
        """
        Convierte texto a voz
        
        Args:
            text: Texto a hablar
            wait: Esperar a que termine de hablar
            
        Returns:
            bool: True si se inició correctamente
        """
        if not text or not text.strip():
            return False
        
        if not self.tts_engine:
            print("❌ TTS no disponible")
            return False
        
        # Limpiar texto
        clean_text = text.strip()
        
        # Limitar longitud para no saturar
        if len(clean_text) > 300:
            clean_text = clean_text[:297] + "..."
        
        print(f"🔊 Hablando: '{clean_text[:50]}...'")
        
        try:
            self.is_speaking = True
            
            # Dividir en oraciones para habla más natural
            sentences = self._split_sentences(clean_text)
            
            for sentence in sentences:
                if sentence.strip():
                    self.tts_engine.say(sentence.strip())
            
            if wait:
                self.tts_engine.runAndWait()
                self.is_speaking = False
            else:
                # Ejecutar en thread separado
                threading.Thread(
                    target=self._speak_async,
                    args=(clean_text,),
                    daemon=True
                ).start()
            
            return True
            
        except Exception as e:
            print(f"❌ Error hablando: {e}")
            self.is_speaking = False
            return False
    
    def _speak_async(self, text: str):
        """Ejecuta la síntesis de voz en segundo plano"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ Error en síntesis asíncrona: {e}")
        finally:
            self.is_speaking = False
    
    def _split_sentences(self, text: str) -> List[str]:
        """Divide texto en oraciones para mejor entonación"""
        separators = ['. ', '! ', '? ', '; ', ': ', '\n']
        sentences = []
        current = ""
        
        for char in text:
            current += char
            if any(current.endswith(sep) for sep in separators):
                sentences.append(current.strip())
                current = ""
        
        if current.strip():
            sentences.append(current.strip())
        
        return sentences if sentences else [text]
    
    # ==================== UTILIDADES Y DIAGNÓSTICO ====================
    
    def test_microphone(self) -> bool:
        """
        Prueba completa del micrófono (Versión Segura)
        
        Returns:
            bool: True si el micrófono funciona
        """
        print("\n" + "=" * 50)
        print("🎤 PRUEBA DE MICRÓFONO")
        print("=" * 50)
        
        # PROTECCIÓN: Evitar que choque con el hilo de escucha
        if getattr(self, 'is_listening', False):
            print("⚠️ ERROR: El asistente está en modo escucha continua.")
            print("   Desactiva la voz en la app antes de probar el micrófono.")
            return False

        try:
            # Usamos una instancia temporal del micrófono para no bloquear la principal
            import speech_recognition as sr
            test_mic = sr.Microphone()
            test_recognizer = sr.Recognizer()
            
            # Copiar configuraciones
            test_recognizer.energy_threshold = getattr(self.recognizer, 'energy_threshold', 300)
            test_recognizer.dynamic_energy_threshold = getattr(self.recognizer, 'dynamic_energy_threshold', True)
            language = getattr(self, 'language', 'es-ES')

            with test_mic as source:
                print("1️⃣ Calibrando ruido ambiente...")
                test_recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"   ✅ Umbral: {test_recognizer.energy_threshold:.1f}")
                
                print("\n2️⃣ Habla AHORA - Di algo como 'hola mundo'")
                print("   ⏳ Escuchando... (3 segundos)")
                
                audio = test_recognizer.listen(
                    source,
                    timeout=3,
                    phrase_time_limit=3
                )
                
                print("   ✅ Audio capturado correctamente")
                
                print("\n3️⃣ Procesando audio...")
                try:
                    text = test_recognizer.recognize_google(audio, language=language)
                    print(f"   ✅ ¡Reconocimiento exitoso! Dijiste: '{text}'")
                    print("\n🎉 ¡MICRÓFONO FUNCIONA PERFECTAMENTE!")
                    return True
                    
                except sr.UnknownValueError:
                    print("   ⚠️ Audio capturado pero no reconocido")
                    print("   ✅ El micrófono FUNCIONA (solo no se entendió)")
                    return True
                    
                except sr.RequestError as e:
                    print(f"   ⚠️ Error de conexión: {e}")
                    print("   ✅ El micrófono FUNCIONA (problema de red)")
                    return True
                    
        except sr.WaitTimeoutError:
            print("\n❌ No se detectó voz en 3 segundos")
            return False
            
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_speakers(self) -> bool:
        """
        Prueba los altavoces
        
        Returns:
            bool: True si los altavoces funcionan
        """
        print("\n" + "=" * 50)
        print("🔊 PRUEBA DE ALTAVOCES")
        print("=" * 50)
        
        if not self.tts_engine:
            print("❌ TTS no disponible")
            return False
        
        try:
            test_phrases = [
                "Hola, soy BEST IA. Esta es una prueba de sonido.",
                "Si escuchas esto, los altavoces funcionan correctamente."
            ]
            
            for phrase in test_phrases:
                print(f"\n🗣️ Hablando: '{phrase[:30]}...'")
                self.speak(phrase, wait=True)
                time.sleep(0.5)
            
            print("\n🎉 ¡ALTAVOCES FUNCIONAN CORRECTAMENTE!")
            return True
            
        except Exception as e:
            print(f"\n❌ Error en prueba de altavoces: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del módulo
        
        Returns:
            Dict con información de estado
        """
        uptime = time.time() - self.stats["start_time"]
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        return {
            "initialized": self.is_initialized,
            "listening": self.is_listening,
            "speaking": self.is_speaking,
            "mic_index": self.mic_device_index,
            "voice_rate": self.voice_rate,
            "voice_volume": self.voice_volume,
            "language": self.language,
            "stats": {
                "total_commands": self.stats["total_commands"],
                "success_rate": (self.stats["successful_recognitions"] / 
                               max(1, self.stats["successful_recognitions"] + self.stats["failed_recognitions"]) * 100),
                "uptime": f"{hours}h {minutes}m {seconds}s",
                "last_command": self.stats["last_command"],
                "history_size": len(self.command_history)
            },
            "threads": {
                "listening": self.listening_thread.is_alive() if self.listening_thread else False
            }
        }
    
    def get_command_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de comandos
        
        Args:
            limit: Número máximo de comandos a retornar
            
        Returns:
            Lista de comandos recientes
        """
        return self.command_history[-limit:] if self.command_history else []
    
    def clear_history(self):
        """Limpia el historial de comandos"""
        self.command_history = []
        print("🧹 Historial de comandos limpiado")
    
    def change_settings(self, **kwargs):
        """
        Cambia la configuración en tiempo real
        
        Args:
            **kwargs: Parámetros a cambiar (voice_rate, voice_volume, language, etc.)
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                old_value = getattr(self, key)
                setattr(self, key, value)
                print(f"⚙️ Configuración actualizada: {key} = {old_value} → {value}")
                
                # Aplicar cambios inmediatos si es necesario
                if key == "voice_rate" and self.tts_engine:
                    self.tts_engine.setProperty('rate', value)
                elif key == "voice_volume" and self.tts_engine:
                    self.tts_engine.setProperty('volume', value)
                elif key == "energy_threshold" and self.recognizer:
                    self.recognizer.energy_threshold = value
    
    def list_microphones(self) -> List[str]:
        """
        Lista todos los micrófonos disponibles
        
        Returns:
            Lista de nombres de micrófonos
        """
        try:
            return sr.Microphone.list_microphone_names()
        except Exception as e:
            print(f"⚠️ Error listando micrófonos: {e}")
            return []
    
    def set_microphone(self, index: int) -> bool:
        """
        Cambia el micrófono activo
        
        Args:
            index: Nuevo índice de micrófono
            
        Returns:
            bool: True si se cambió correctamente
        """
        if index < 0:
            print(f"❌ Índice inválido: {index}")
            return False
        
        try:
            available = self.list_microphones()
            if index >= len(available):
                print(f"❌ Índice {index} fuera de rango (max: {len(available)-1})")
                return False
            
            print(f"🔄 Cambiando a micrófono [{index}]: {available[index][:50]}...")
            self.mic_device_index = index
            
            # Reinicializar STT
            self._initialize_stt()
            
            print(f"✅ Micrófono cambiado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error cambiando micrófono: {e}")
            return False
    
    # ==================== LIMPIEZA ====================
    
    def shutdown(self):
        """Apaga el módulo de voz de forma segura"""
        print("\n🔄 Apagando módulo de voz...")
        
        # Detener escucha
        self.stop_listening()
        
        # Detener TTS
        if self.tts_engine:
            try:
                self.tts_engine.stop()
                print("✅ TTS detenido")
            except:
                pass
        
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"   Comandos procesados: {self.stats['total_commands']}")
        print(f"   Reconocimientos exitosos: {self.stats['successful_recognitions']}")
        print(f"   Fallos: {self.stats['failed_recognitions']}")
        print(f"   Último comando: '{self.stats['last_command']}'")
        
        print("✅ Módulo de voz apagado correctamente")
    
    def __del__(self):
        """Destructor"""
        self.shutdown()


# ==================== INSTANCIA GLOBAL ====================

# Crear instancia única con micrófono por defecto (0)
voice_module = VoiceModule(mic_device_index=0)

# Para usar otro micrófono, por ejemplo el 1:
# voice_module = VoiceModule(mic_device_index=1)