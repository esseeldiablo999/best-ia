"""
app.py - Aplicación principal de BEST-IA
Versión 5.2 - Código unificado, responsive y sin errores de sintaxis
"""

import streamlit as st
import time
import sys
import traceback
from datetime import datetime

# Importaciones locales
from app.core.database import init_db, save_message, get_all_messages, clear_history
from app.config.settings import settings
from app.core.ai_client import ai_client
from app.config.themes import theme_manager

# ==================== INICIALIZACIÓN DE SESSION STATE ====================

def initialize_session_state() -> None:
    """Inicializa todas las variables de session_state"""
    session_defaults = {
        'current_temperature': 0.7,
        'selected_model': 'deepseek-chat',
        'selected_personality': 'helpful',
        'user_name': 'Usuario',
        'first_visit': True,
        'messages': [],
        'chat_history_size': 0,
        'voice_enabled': False,
        'new_voice_input': False,
        'last_voice_input': '',
        'voice_history': [],
        'voice_module_available': False,
        'total_requests': 0,
        'total_tokens': 0,
        'session_start_time': time.time()
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # Inicializar Base de Datos y cargar historial
    init_db()
    if not st.session_state.get('messages'):
        st.session_state.messages = get_all_messages()

# ==================== FUNCIONES DE VOZ ====================

def load_voice_module():
    """Carga el módulo de voz de forma segura"""
    try:
        import os
        # Si estamos en Windows, cargamos la voz. Si es Linux (nube), la ignoramos.
        if os.name == 'nt':
            from app.modules.voice_module import voice_module
        else:
            voice_module = None

        if voice_module is None:
            st.session_state.voice_module_available = False
            return None
        
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
    """Procesa la entrada de voz de forma segura"""
    voice_text = st.session_state.get('last_voice_input', '')
    if not voice_text:
        return False
    
    try:
        st.session_state.last_voice_input = ""
        st.session_state.new_voice_input = False
        
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(f"🎤 **{voice_text}**")
        
        st.session_state.messages.append({
            "role": "user",
            "content": voice_text,
            "voice_input": True,
            "timestamp": time.time(),
            "user_name": st.session_state.user_name
        })
        
        current_temp = st.session_state.get("current_temperature", 0.7)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤖 Procesando voz..."):
                respuesta = ai_client.chat(voice_text, current_temp)
                
                if respuesta.get("success"):
                    st.markdown(respuesta["answer"])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": respuesta["answer"],
                        "timestamp": time.time()
                    })
                    st.session_state.total_requests += 1
                    st.session_state.total_tokens += respuesta.get("tokens", 0)
                    
                    if st.session_state.get('voice_enabled', False):
                        try:
                            from app.modules.voice_module import voice_module
                            voice_response = respuesta["answer"][:200] + "..." if len(respuesta["answer"]) > 200 else respuesta["answer"]
                            voice_module.speak(voice_response, wait=False)
                        except:
                            pass
                else:
                    st.error(f"Error: {respuesta.get('answer', 'Error desconocido')}")
        
        time.sleep(0.1)
        st.rerun()
        return True
    except Exception as e:
        print(f"❌ Error crítico en voz: {e}")
        return False

# ==================== FUNCIONES DE RENDERIZADO ====================

def render_header() -> None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style='text-align: center;'>
            <h1 style='color: {settings.PRIMARY_COLOR}; font-size: 3.5rem; margin-bottom: 0.5rem;'>
                🚀 {settings.APP_NAME}
            </h1>
            <p style='color: #888; font-size: 1.1rem;'>
                v{settings.APP_VERSION} | ThinkPad T480s | 16GB RAM
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_voice_section() -> None:
    st.divider()
    st.subheader("🎤 CONFIGURACIÓN DE VOZ")
    
    if 'voice_module' not in st.session_state:
        voice_module = load_voice_module()
        if voice_module:
            st.session_state.voice_module = voice_module
        else:
            st.error("❌ Módulo de voz no disponible (normal en la nube)")
            return
    
    voice_module = st.session_state.voice_module
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.voice_enabled:
            st.success("🎤 **ESCUCHANDO**")
        else:
            st.info("🔇 **EN PAUSA**")
            
    with col2:
        if st.button("🎤 **Probar Mic**", use_container_width=True):
            if voice_module.test_microphone():
                st.success("✅ Micrófono OK")
            else:
                st.error("❌ Error de micrófono")
    
    col3, col4 = st.columns(2)
    with col3:
        if st.session_state.voice_enabled:
            if st.button("🔴 **Desactivar Voz**", use_container_width=True):
                voice_module.stop_listening()
                st.session_state.voice_enabled = False
                st.rerun()
        else:
            if st.button("🟢 **Activar Voz**", use_container_width=True, type="primary"):
                def on_voice_detected(text):
                    if text and text.strip():
                        st.session_state.last_voice_input = text.strip()
                        st.session_state.new_voice_input = True
                
                if voice_module.start_listening(on_voice_detected):
                    st.session_state.voice_enabled = True
                    st.rerun()
                    
    with col4:
        if st.button("🔊 **Probar Voz**", use_container_width=True):
            voice_module.speak("Hola, soy BEST IA.")
            st.success("Voz probada")

def render_api_status() -> None:
    st.divider()
    st.subheader("🔑 ESTADO API")
    if hasattr(ai_client, 'client') and ai_client.client:
        st.success("✅ API Conectada")
    else:
        st.error("❌ API Key no configurada")

def render_ai_configuration() -> None:
    st.divider()
    st.subheader("⚙️ CONFIGURACIÓN IA")
    
    new_temp = st.slider("Temperatura", 0.0, 2.0, st.session_state.current_temperature, 0.1)
    st.session_state.current_temperature = new_temp
    
    model_options = ["deepseek-chat", "deepseek-coder"]
    selected_model = st.selectbox(
        "Modelo", 
        model_options,
        index=model_options.index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0
    )
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        if hasattr(ai_client, 'model'):
            ai_client.model = selected_model

def render_personality_section() -> None:
    st.divider()
    st.subheader("🎭 PERSONALIDAD")
    
    personalities = {
        "helpful": "🤗 Útil", "friendly": "👋 Amigable", "technical": "⚙️ Técnico",
        "funny": "😄 Divertido", "creative": "🎨 Creativo", "brief": "⚡ Conciso"
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

def render_user_profile() -> None:
    st.divider()
    st.subheader("👤 TU PERFIL")
    user_name = st.text_input("Tu nombre:", value=st.session_state.user_name)
    if user_name != st.session_state.user_name:
        st.session_state.user_name = user_name
        if hasattr(ai_client, 'set_user_name'):
            ai_client.set_user_name(user_name)

def render_statistics() -> None:
    st.divider()
    st.subheader("📊 ESTADÍSTICAS")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Mensajes", len(st.session_state.messages))
    with col2:
        st.metric("Tokens", f"{st.session_state.total_tokens:,}")

def render_quick_actions() -> None:
    st.divider()
    if st.button("🧹 **Limpiar Chat**", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

def render_system_info() -> None:
    st.divider()
    st.caption(f"💻 ThinkPad T480s | 🕒 {datetime.now().strftime('%H:%M:%S')}")

def render_file_analyzer() -> None:
    """Interfaz para subir y analizar documentos"""
    with st.expander("📁 Analizar un Documento (PDF, Word, TXT)"):
        uploaded_file = st.file_uploader("Sube tu archivo aquí", type=["pdf", "docx", "txt"])
        
        if uploaded_file is not None:
            if st.button("📄 Leer y Analizar", use_container_width=True, type="primary"):
                from app.modules.file_processor import FileProcessor
                
                with st.spinner("Extrayendo texto del documento..."):
                    doc_text = FileProcessor.extract_text(uploaded_file)
                
                if "⚠️" in doc_text or "❌" in doc_text:
                    st.error(doc_text)
                else:
                    st.success(f"✅ Documento leído ({len(doc_text)} caracteres).")
                    st.session_state['active_document'] = doc_text
                    st.info("🤖 BEST-IA está listo. Hazle una pregunta sobre el documento en el chat de abajo.")

def render_chat_history() -> None:
    if st.session_state.messages:
        for msg in st.session_state.messages:
            role = msg.get("role", "assistant")
            avatar = "🧑‍💻" if role == "user" else "🤖"
            
            with st.chat_message(role, avatar=avatar):
                content = msg.get("content", "")
                if msg.get("voice_input"):
                    st.markdown(f"🎤 {content}")
                else:
                    st.markdown(content)
    else:
        st.info("💬 No hay mensajes aún. ¡Escribe algo!")

def process_text_input() -> None:
    prompt = st.chat_input(f"Escribe tu mensaje, {st.session_state.user_name}...")
    if prompt:
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
        
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": time.time()
        })
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤖 Pensando..."):
                if 'active_document' in st.session_state and st.session_state['active_document']:
                    respuesta = ai_client.analyze_document(
                        st.session_state['active_document'], 
                        prompt, 
                        st.session_state.current_temperature
                    )
                else:
                    respuesta = ai_client.chat(prompt, st.session_state.current_temperature)
                
                if respuesta.get("success"):
                    st.markdown(respuesta["answer"])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": respuesta["answer"],
                        "timestamp": time.time()
                    })
                    st.session_state.total_requests += 1
                    st.session_state.total_tokens += respuesta.get("tokens", 0)
                else:
                    st.error(f"Error: {respuesta.get('answer', 'Error')}")

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    initialize_session_state()
    
    st.set_page_config(
        page_title=f"{settings.APP_NAME} 🤖",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Aplicar tema base
    st.markdown(theme_manager.get_css(), unsafe_allow_html=True)
    
    # CSS para corregir el diseño en celulares (letras gigantes)
    st.markdown("""
    <style>
        @media (max-width: 768px) {
            .stMarkdown p, .stMarkdown li { font-size: 16px !important; line-height: 1.5 !important; }
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { font-size: 20px !important; color: #6E44FF !important; margin-top: 15px !important; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    render_header()
    
    with st.sidebar:
        st.markdown("### ⚙️ CONFIGURACIÓN")
        render_voice_section()
        render_api_status()
        render_ai_configuration()
        render_personality_section()
        render_user_profile()
        render_statistics()
        render_quick_actions()
        render_system_info()
    
    if process_voice_input():
        st.rerun()
    
    st.markdown(f"### 💬 CHAT CON BEST-IA")
    render_file_analyzer()  # <-- AÑADE ESTA LÍNEA AQUÍ
    render_chat_history()
    process_text_input()

if __name__ == "__main__":
    main()