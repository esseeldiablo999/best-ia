"""
app.py - Aplicación principal de BEST-IA
Versión 5.0 - Sistema de voz optimizado para Streamlit
"""

import streamlit as st
import time
import sys
import traceback
from datetime import datetime
from typing import Optional, Any

# Importaciones locales
from app.config.settings import settings
from app.core.ai_client import ai_client
from app.config.themes import theme_manager

# ==================== INICIALIZACIÓN DE SESSION STATE ====================

def initialize_session_state() -> None:
    """Inicializa todas las variables de session_state"""
    
    session_defaults = {
        # Configuración general
        'current_temperature': 0.7,
        'selected_model': 'deepseek-chat',
        'selected_personality': 'helpful',
        'user_name': 'Usuario',
        'first_visit': True,
        
        # Chat
        'messages': [],
        'chat_history_size': 0,
        
        # Voz - CRÍTICAS
        'voice_enabled': False,
        'new_voice_input': False,
        'last_voice_input': '',
        'voice_history': [],
        'voice_module_available': False,
        
        # UI/Estado
        'sidebar_collapsed': False,
        'dark_mode': True,
        'current_page': 'chat',
        
        # Estadísticas
        'total_requests': 0,
        'total_tokens': 0,
        'session_start_time': time.time()
    }
    
    # Inicializar solo las que no existen
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    print("✅ Session_state inicializado")

# ==================== FUNCIONES DE VOZ ====================

def load_voice_module():
    """Carga el módulo de voz de forma segura"""
    try:
        import os
        # Si estamos en Windows (tu PC), cargamos la voz. Si es Linux (la nube), la ignoramos.
        if os.name == 'nt':
            from app.modules.voice_module import voice_module
        else:
            voice_module = None

        # Si es None (estamos en la nube), no hacemos nada más y salimos
        if voice_module is None:
            st.session_state.voice_module_available = False
            return None
        
        # Verificar métodos esenciales (solo si estamos en Windows)
        required_methods = ['start_listening', 'stop_listening', 'speak', 'test_microphone']
        for method in required_methods:
            if not hasattr(voice_module, method):
                raise AttributeError(f"Módulo de voz no tiene método {method}")
        
        st.session_state.voice_module_available = True
        return voice_module
        
    except ImportError as e:
        st.session_state.voice_module_available = False
        print(f"⚠️ No se pudo importar voice_module: {e}")
        return None
    except Exception as e:
        st.session_state.voice_module_available = False
        print(f"⚠️ Error cargando voice_module: {e}")
        return None
    
def process_voice_input() -> bool:
    """
    Procesa la entrada de voz - VERSIÓN OPTIMIZADA
    Returns: True si se procesó voz
    """
    
    # Obtener entrada de voz
    voice_text = st.session_state.get('last_voice_input', '')
    
    # Debug
    if voice_text:
        print(f"🎯 [VOZ] Procesando: '{voice_text}'")
    
    if not voice_text:
        return False
    
    try:
        # 1. LIMPIAR INMEDIATAMENTE para evitar procesamiento duplicado
        st.session_state.last_voice_input = ""
        st.session_state.new_voice_input = False
        
        # 2. MOSTRAR EN CHAT
        with st.chat_message("user"):
            st.markdown(f"🎤 **{voice_text}**")
        
        # 3. GUARDAR EN HISTORIAL
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        st.session_state.messages.append({
            "role": "user",
            "content": voice_text,
            "voice_input": True,
            "timestamp": time.time(),
            "user_name": st.session_state.user_name
        })
        
        # 4. OBTENER RESPUESTA DE IA
        current_temp = st.session_state.get("current_temperature", 0.7)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 Procesando voz..."):
                respuesta = ai_client.chat(voice_text, current_temp)
                
                if respuesta.get("success"):
                    st.markdown(respuesta["answer"])
                    
                    # Guardar respuesta
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": respuesta["answer"],
                        "timestamp": time.time(),
                        "metadata": {
                            "personality": st.session_state.selected_personality,
                            "model": respuesta.get("model", st.session_state.selected_model),
                            "tokens": respuesta.get("tokens", 0)
                        }
                    })
                    
                    # Actualizar estadísticas
                    st.session_state.total_requests += 1
                    st.session_state.total_tokens += respuesta.get("tokens", 0)
                    
                    # Responder por voz si está activado
                    if st.session_state.get('voice_enabled', False):
                        try:
                            from app.modules.voice_module import voice_module
                            # Limitar longitud para voz
                            voice_response = respuesta["answer"][:200]
                            if len(respuesta["answer"]) > 200:
                                voice_response += "..."
                            voice_module.speak(voice_response, wait=False)
                            print("🔊 Respuesta por voz enviada")
                        except Exception as e:
                            print(f"⚠️ Error en respuesta por voz: {e}")
                else:
                    st.error(f"Error: {respuesta.get('answer', 'Error desconocido')}")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: {respuesta.get('answer', 'Error')}",
                        "error": True,
                        "timestamp": time.time()
                    })
        
        # 5. FORZAR ACTUALIZACIÓN
        print("🔄 [VOZ] Forzando rerun...")
        time.sleep(0.1)
        st.rerun()
        
        return True
        
    except Exception as e:
        print(f"❌ [VOZ] Error crítico: {e}")
        traceback.print_exc()
        return False

def emergency_voice_handler():
    """Manejador de emergencia para voz - MUESTRA BOTONES MANUALES"""
    
    last_command = st.session_state.get('last_voice_input', '')
    
    if last_command:
        st.markdown("---")
        st.warning("⚠️ **Voz detectada - Acción requerida**")
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.code(last_command, language="text")
        
        with col2:
            if st.button("🔄 **Procesar**", key="emergency_process", use_container_width=True):
                st.session_state.new_voice_input = True
                st.success("Procesando...")
                time.sleep(0.3)
                st.rerun()
        
        with col3:
            if st.button("🗑️ **Limpiar**", key="emergency_clear", use_container_width=True):
                st.session_state.last_voice_input = ""
                st.success("Comando limpiado")
                time.sleep(0.3)
                st.rerun()

# ==================== FUNCIONES DE RENDERIZADO ====================

def render_header() -> None:
    """Renderiza el encabezado de la aplicación"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style='text-align: center;'>
            <h1 style='color: {settings.PRIMARY_COLOR}; 
                       font-size: 3.5rem; 
                       margin-bottom: 0.5rem;
                       text-shadow: 0 2px 10px rgba(110, 68, 255, 0.3);'>
                🚀 {settings.APP_NAME}
            </h1>
            <p style='color: #888; font-size: 1.1rem;'>
                v{settings.APP_VERSION} | ThinkPad T480s | 16GB RAM
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_voice_section() -> None:
    """Renderiza la sección de configuración de voz - VERSIÓN OPTIMIZADA"""
    st.divider()
    st.subheader("🎤 CONFIGURACIÓN DE VOZ")
    
    # Cargar módulo de voz si no está cargado
    if 'voice_module' not in st.session_state:
        voice_module = load_voice_module()
        if voice_module:
            st.session_state.voice_module = voice_module
            st.success("✅ Módulo de voz cargado")
        else:
            st.error("❌ No se pudo cargar el módulo de voz")
            st.info("""
            **Para instalar las dependencias:**
            ```
            pip install SpeechRecognition pyttsx3 pyaudio
            ```
            En Windows: `pip install pipwin && pipwin install pyaudio`
            """)
            return
    
    voice_module = st.session_state.voice_module
    
    # Estado actual
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.voice_enabled:
            st.success("🎤 **ESCUCHANDO**")
        else:
            st.info("🔇 **EN PAUSA**")
    
    with col2:
        if st.button("🎤 **Probar Mic**", use_container_width=True, key="test_mic"):
            with st.spinner("Probando micrófono..."):
                if voice_module.test_microphone():
                    st.success("✅ Micrófono OK")
                else:
                    st.error("❌ Error - ¿Micrófono conectado?")
    
    # Botones de control
    col3, col4 = st.columns(2)
    
    with col3:
        if st.session_state.voice_enabled:
            if st.button("🔴 **Desactivar Voz**", use_container_width=True, type="secondary"):
                voice_module.stop_listening()
                st.session_state.voice_enabled = False
                st.success("Voz desactivada")
                time.sleep(0.3)
                st.rerun()
        else:
            if st.button("🟢 **Activar Voz**", use_container_width=True, type="primary"):
                
                # DEFINIR CALLBACK - GUARDA EN SESSION STATE
                def on_voice_detected(text):
                    if text and text.strip():
                        print(f"🎤 Callback recibido: '{text}'")
                        st.session_state.last_voice_input = text.strip()
                        st.session_state.new_voice_input = True
                
                # INICIAR ESCUCHA
                if voice_module.start_listening(on_voice_detected):
                    st.session_state.voice_enabled = True
                    st.success("✅ Voz activada")
                    st.info("""
                    **Instrucciones:**
                    1. Habla claramente
                    2. Di: **"BEST IA"** seguido de tu mensaje
                    3. Ejemplo: *"BEST IA, ¿qué hora es?"*
                    """)
                    time.sleep(0.3)
                    st.rerun()
                else:
                    st.error("❌ No se pudo activar la voz")
    
    with col4:
        if st.button("🔊 **Probar Voz**", use_container_width=True, key="test_voice"):
            voice_module.speak("Hola, soy BEST IA. Sistema de voz funcionando.")
            st.success("Voz probada")
    
    # Configuración básica
    with st.expander("⚙️ Ajustes de voz"):
        new_rate = st.slider(
            "Velocidad de voz",
            100, 300,
            voice_module.voice_rate if hasattr(voice_module, 'voice_rate') else 180,
            10,
            help="Palabras por minuto"
        )
        
        new_volume = st.slider(
            "Volumen",
            0.0, 1.0,
            voice_module.voice_volume if hasattr(voice_module, 'voice_volume') else 0.9,
            0.1,
            help="Volumen de la voz"
        )
        
        if st.button("💾 Aplicar cambios", use_container_width=True):
            voice_module.change_voice_settings(rate=new_rate, volume=new_volume)
            st.success("✅ Configuración aplicada")
    
    # Mostrar último comando detectado
    if st.session_state.get('last_voice_input'):
        st.info(f"📝 **Último comando:** _{st.session_state.last_voice_input}_")

def render_api_status() -> None:
    """Renderiza el estado de la API"""
    st.divider()
    st.subheader("🔑 ESTADO API")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if hasattr(ai_client, 'client') and ai_client.client:
            st.success("✅")
        else:
            st.error("❌")
    
    with col2:
        if hasattr(ai_client, 'api_key') and ai_client.api_key:
            masked_key = f"...{ai_client.api_key[-8:]}" if len(ai_client.api_key) > 10 else "Configurada"
            st.success(f"API Key: `{masked_key}`")
        else:
            st.error("API Key no configurada")
            st.markdown("[🔗 Obtener API Key](https://platform.deepseek.com)")

def render_ai_configuration() -> None:
    """Renderiza la configuración de IA"""
    st.divider()
    st.subheader("⚙️ CONFIGURACIÓN IA")
    
    # Temperatura
    col1, col2 = st.columns([3, 1])
    with col1:
        new_temp = st.slider(
            "Temperatura",
            0.0, 2.0,
            st.session_state.current_temperature,
            0.1,
            help="0.0 = Preciso | 0.7 = Balanceado | 1.0+ = Creativo"
        )
    with col2:
        st.metric("Valor", f"{new_temp:.1f}")
    
    st.session_state.current_temperature = new_temp
    
    # Modelo
    model_options = ["deepseek-chat", "deepseek-coder"]
    selected_model = st.selectbox(
        "Modelo",
        model_options,
        index=model_options.index(st.session_state.selected_model) 
        if st.session_state.selected_model in model_options else 0
    )
    
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        if hasattr(ai_client, 'model'):
            ai_client.model = selected_model

def render_personality_section() -> None:
    """Renderiza la sección de personalidades"""
    st.divider()
    st.subheader("🎭 PERSONALIDAD")
    
    personalities = {
        "helpful": "🤗 Útil y Detallado",
        "friendly": "👋 Amigable y Cercano",
        "technical": "⚙️ Técnico y Preciso",
        "funny": "😄 Divertido y Ocurrente",
        "creative": "🎨 Creativo y Poético",
        "brief": "⚡ Conciso y Directo"
    }
    
    selected = st.selectbox(
        "Elige personalidad:",
        options=list(personalities.keys()),
        format_func=lambda x: personalities[x],
        index=list(personalities.keys()).index(st.session_state.selected_personality)
    )
    
    if selected != st.session_state.selected_personality:
        st.session_state.selected_personality = selected
        if hasattr(ai_client, 'set_personality'):
            ai_client.set_personality(selected)
            st.success(f"Personalidad cambiada a: {personalities[selected]}")

def render_user_profile() -> None:
    """Renderiza el perfil de usuario"""
    st.divider()
    st.subheader("👤 TU PERFIL")
    
    user_name = st.text_input(
        "Tu nombre:",
        value=st.session_state.user_name,
        placeholder="Ej: Alex, María..."
    )
    
    if user_name != st.session_state.user_name:
        st.session_state.user_name = user_name
        if hasattr(ai_client, 'set_user_name'):
            ai_client.set_user_name(user_name)

def render_statistics() -> None:
    """Renderiza estadísticas"""
    st.divider()
    st.subheader("📊 ESTADÍSTICAS")
    
    # Calcular tiempo de sesión
    session_time = time.time() - st.session_state.session_start_time
    hours = int(session_time // 3600)
    minutes = int((session_time % 3600) // 60)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Mensajes", len(st.session_state.messages))
        st.metric("Solicitudes", st.session_state.total_requests)
    
    with col2:
        st.metric("Tokens", f"{st.session_state.total_tokens:,}")
        st.metric("Sesión", f"{hours}h {minutes}m")

def render_quick_actions() -> None:
    """Renderiza acciones rápidas"""
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 **Limpiar Chat**", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history_size = 0
            st.success("Chat limpiado")
            time.sleep(0.3)
            st.rerun()
    
    with col2:
        if st.button("🔄 **Reiniciar**", use_container_width=True):
            # Guardar configuraciones importantes
            keep_keys = ['current_temperature', 'selected_model', 'user_name']
            backup = {k: st.session_state[k] for k in keep_keys if k in st.session_state}
            
            # Limpiar todo
            for key in list(st.session_state.keys()):
                if key not in keep_keys:
                    del st.session_state[key]
            
            # Restaurar
            for k, v in backup.items():
                st.session_state[k] = v
            
            st.session_state.session_start_time = time.time()
            st.success("App reiniciada")
            time.sleep(0.3)
            st.rerun()

def render_system_info() -> None:
    """Renderiza información del sistema"""
    st.divider()
    st.caption(f"💻 ThinkPad T480s")
    st.caption(f"🐍 Python {sys.version.split()[0]}")
    st.caption(f"🕒 {datetime.now().strftime('%H:%M:%S')}")

def render_welcome_card() -> None:
    """Renderiza tarjeta de bienvenida"""
    if st.session_state.first_visit:
        st.session_state.first_visit = False
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {settings.DARK_CARD}, #2D2D5C);
                    padding: 2rem;
                    border-radius: 15px;
                    margin: 1rem 0;
                    text-align: center;
                    border: 1px solid rgba(255,255,255,0.1);'>
            <h2 style='color: {settings.PRIMARY_COLOR}; margin-top: 0;'>
                🚀 ¡Bienvenido a BEST-IA!
            </h2>
            <p style='color: #B0B0D0;'>
                Tu asistente personal con inteligencia artificial.
                Puedes escribir o usar comandos de voz.
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_chat_header() -> None:
    """Renderiza encabezado del chat"""
    personality_names = {
        "helpful": "🤗 Útil",
        "friendly": "👋 Amigable",
        "technical": "⚙️ Técnico",
        "funny": "😄 Divertido",
        "creative": "🎨 Creativo",
        "brief": "⚡ Conciso"
    }
    
    current_personality = personality_names.get(
        st.session_state.selected_personality,
        "🤗 Útil"
    )
    
    st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; margin: 1.5rem 0;'>
        <h2 style='color: {settings.PRIMARY_COLOR}; margin: 0;'>💬 CHAT</h2>
        <span style='background: {settings.SECONDARY_COLOR}20; 
                     color: {settings.SECONDARY_COLOR}; 
                     padding: 0.5rem 1rem; 
                     border-radius: 20px;
                     font-weight: 600;'>
            {current_personality}
        </span>
    </div>
    """, unsafe_allow_html=True)

def render_chat_history() -> None:
    """Renderiza el historial del chat"""
    if st.session_state.messages:
        for msg in st.session_state.messages:
            with st.chat_message(msg.get("role", "assistant")):
                # Mostrar contenido
                content = msg.get("content", "")
                if msg.get("voice_input"):
                    st.markdown(f"🎤 {content}")
                else:
                    st.markdown(content)
                
                # Mostrar hora
                if msg.get("timestamp"):
                    timestamp = datetime.fromtimestamp(msg["timestamp"]).strftime("%H:%M")
                    st.caption(timestamp)
    else:
        st.info("💬 No hay mensajes aún. ¡Escribe algo o activa la voz!")

def process_text_input() -> None:
    """Procesa entrada de texto"""
    prompt = st.chat_input(f"Escribe tu mensaje, {st.session_state.user_name}...")
    
    if prompt:
        # Mostrar mensaje
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Guardar
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": time.time(),
            "user_name": st.session_state.user_name
        })
        
        # Obtener respuesta
        with st.chat_message("assistant"):
            with st.spinner("🤖 Pensando..."):
                respuesta = ai_client.chat(prompt, st.session_state.current_temperature)
                
                if respuesta.get("success"):
                    st.markdown(respuesta["answer"])
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": respuesta["answer"],
                        "timestamp": time.time(),
                        "metadata": {
                            "personality": st.session_state.selected_personality,
                            "model": respuesta.get("model", st.session_state.selected_model),
                            "tokens": respuesta.get("tokens", 0)
                        }
                    })
                    
                    st.session_state.total_requests += 1
                    st.session_state.total_tokens += respuesta.get("tokens", 0)
                else:
                    st.error(f"Error: {respuesta.get('answer', 'Error')}")

def render_action_buttons() -> None:
    """Renderiza botones de acción"""
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🧹 **Nuevo**", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("📊 **Stats**", use_container_width=True):
            st.info(f"""
            **Estadísticas:**
            - Mensajes: {len(st.session_state.messages)}
            - Solicitudes: {st.session_state.total_requests}
            - Tokens: {st.session_state.total_tokens:,}
            - Personalidad: {st.session_state.selected_personality}
            """)
    
    with col3:
        if st.button("💾 **Guardar**", use_container_width=True):
            if st.session_state.messages:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_{timestamp}.txt"
                
                chat_text = f"Chat BEST-IA - {datetime.now()}\n"
                chat_text += "=" * 50 + "\n\n"
                
                for msg in st.session_state.messages:
                    role = "TÚ" if msg.get("role") == "user" else "BEST-IA"
                    chat_text += f"{role}:\n{msg.get('content', '')}\n\n"
                
                st.download_button(
                    "📥 Descargar",
                    chat_text,
                    filename,
                    "text/plain"
                )
    
    with col4:
        if st.button("⚙️ **Sistema**", use_container_width=True):
            st.info(f"""
            **Sistema:**
            - API: {'✅ Conectada' if ai_client.client else '❌ Demo'}
            - Voz: {'✅ Activa' if st.session_state.voice_enabled else '❌ Inactiva'}
            - Modelo: {st.session_state.selected_model}
            - Usuario: {st.session_state.user_name}
            """)

def render_footer() -> None:
    """Renderiza el pie de página"""
    st.divider()
    
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem;'>
        <p style='color: #666;'>
            🚀 {settings.APP_NAME} v{settings.APP_VERSION} | 
            🎯 {st.session_state.selected_personality} | 
            { '🎤 Voz Activa' if st.session_state.voice_enabled else '🔇 Sin Voz' }
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal de BEST-IA"""
    
    # 1. INICIALIZACIÓN
    initialize_session_state()
    
    # 2. CONFIGURACIÓN DE PÁGINA
    st.set_page_config(
        page_title=f"{settings.APP_NAME} 🤖",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 3. APLICAR TEMA
    st.markdown(theme_manager.get_css(), unsafe_allow_html=True)
    
    # 4. HEADER
    render_header()
    
    # 5. SIDEBAR - TODAS LAS CONFIGURACIONES
    with st.sidebar:
        st.markdown("### ⚙️ CONFIGURACIÓN")
        render_voice_section()      # Primero la voz
        render_api_status()          # Estado de API
        render_ai_configuration()    # Configuración IA
        render_personality_section() # Personalidades
        render_user_profile()        # Perfil usuario
        render_statistics()          # Estadísticas
        render_quick_actions()       # Acciones rápidas
        render_system_info()         # Info sistema
    
    # 6. PROCESAR VOZ - CRÍTICO
    voice_processed = process_voice_input()
    if voice_processed:
        st.rerun()
    
    # 7. MANEJADOR DE EMERGENCIA
    emergency_voice_handler()
    
    # 8. ÁREA PRINCIPAL DE CHAT
    render_welcome_card()
    render_chat_header()
    render_chat_history()
    
    # 9. ENTRADA DE TEXTO
    process_text_input()
    
    # 10. ACCIONES Y FOOTER
    render_action_buttons()
    render_footer()

# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    main()