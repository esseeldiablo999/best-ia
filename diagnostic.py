"""
diagnostic.py - Diagnóstico del sistema de voz
"""

import sys
import traceback

def check_voice_system():
    print("=" * 50)
    print("🔍 DIAGNÓSTICO SISTEMA DE VOZ")
    print("=" * 50)
    
    # 1. Verificar imports
    print("\n1. 📦 VERIFICANDO IMPORTS:")
    try:
        import speech_recognition as sr
        print("   ✅ SpeechRecognition")
        print(f"     Versión: {sr.__version__}")
    except Exception as e:
        print(f"   ❌ SpeechRecognition: {e}")
    
    try:
        import pyttsx3
        print("   ✅ pyttsx3")
    except Exception as e:
        print(f"   ❌ pyttsx3: {e}")
    
    try:
        import pyaudio
        print("   ✅ pyaudio")
    except Exception as e:
        print(f"   ❌ pyaudio: {e}")
    
    # 2. Verificar micrófonos
    print("\n2. 🎤 VERIFICANDO MICRÓFONOS:")
    try:
        import speech_recognition as sr
        mics = sr.Microphone.list_microphone_names()
        print(f"   ✅ {len(mics)} micrófonos detectados")
        for i, mic in enumerate(mics[:3]):  # Mostrar solo primeros 3
            print(f"     {i}: {mic}")
        if len(mics) > 3:
            print(f"     ... y {len(mics)-3} más")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Verificar módulo personalizado
    print("\n3. 🤖 VERIFICANDO MÓDULO PERSONALIZADO:")
    try:
        from app.modules.voice_module import voice_module
        print("   ✅ Módulo importado correctamente")
        
        # Verificar métodos
        methods = ['start_listening', 'stop_listening', 'speak', 'test_microphone']
        for method in methods:
            if hasattr(voice_module, method):
                print(f"     ✅ {method}() disponible")
            else:
                print(f"     ❌ {method}() NO disponible")
                
    except Exception as e:
        print(f"   ❌ Error importando módulo: {e}")
        print(f"     Traceback: {traceback.format_exc()}")
    
    # 4. Verificar session_state
    print("\n4. 💾 VERIFICANDO SESSION_STATE:")
    try:
        import streamlit as st
        print("   ✅ Streamlist importado")
        print(f"     Versión: {st.__version__}")
        
        # Variables críticas
        critical_vars = ['new_voice_input', 'last_voice_input', 'voice_enabled']
        for var in critical_vars:
            if var in st.session_state:
                print(f"     ✅ {var}: {st.session_state[var]}")
            else:
                print(f"     ⚠️  {var}: NO INICIALIZADA")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RECOMENDACIONES:")
    print("=" * 50)
    
    if 'app.modules.voice_module' in sys.modules:
        print("1. ✅ El módulo de voz está cargado")
        print("2. 🔧 Ejecuta la app y activa el modo voz")
        print("3. 🎤 Di: 'BEST IA, hola'")
        print("4. 📝 Verifica que aparezca en el chat")
    else:
        print("1. ❌ El módulo no se carga correctamente")
        print("2. 📁 Verifica la ruta: app/modules/voice_module.py")
        print("3. 🔧 Revisa los imports en app.py")
    
    print("\n🚀 Comando de prueba:")
    print("   streamlit run app.py")

if __name__ == "__main__":
    check_voice_system()