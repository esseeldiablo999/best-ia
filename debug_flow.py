"""
Debug del flujo de voz
"""

import streamlit as st

print("=" * 60)
print("🔍 DEBUG DEL FLUJO DE VOZ")
print("=" * 60)

# Simular session_state
test_state = {
    'new_voice_input': True,
    'last_voice_input': 'cuál es la capital de méxico',
    'messages': [],
    'user_name': 'Usuario'
}

print(f"1. 📊 ESTADO INICIAL:")
print(f"   new_voice_input: {test_state['new_voice_input']}")
print(f"   last_voice_input: '{test_state['last_voice_input']}'")
print(f"   messages: {len(test_state['messages'])} mensajes")

print(f"\n2. 🎯 CONDICIONES:")
print(f"   new_voice_input AND last_voice_input: {test_state['new_voice_input'] and test_state['last_voice_input']}")

print(f"\n3. 📝 PROCESAMIENTO:")
print(f"   Texto a procesar: '{test_state['last_voice_input']}'")

print(f"\n4. 🔄 FLUJO ESPERADO:")
print("""
   1. ✅ Voz detecta "bestia cuál es la capital de méxico"
   2. ✅ Callback establece last_voice_input y new_voice_input = True
   3. ✅ process_voice_input() detecta condiciones
   4. ✅ Muestra mensaje en chat
   5. ✅ Llama a IA
   6. ✅ Muestra respuesta
   7. ✅ st.rerun() actualiza UI
""")

print(f"\n5. 🚨 POSIBLES PROBLEMAS:")
print("""
   A. ❌ st.rerun() no se ejecuta correctamente
   B. ❌ Mensajes no se guardan en session_state
   C. ❌ Streamlit no detecta cambios en session_state
   D. ❌ Thread de voz no puede modificar UI directamente
""")

print(f"\n6. 🛠️ SOLUCIONES:")
print("""
   SOLUCIÓN 1: Usar st.experimental_rerun() en lugar de st.rerun()
   SOLUCIÓN 2: Forzar actualización con st.session_state.update()
   SOLUCIÓN 3: Usar callback que llame a una función con @st.cache_data
   SOLUCIÓN 4: Implementar websockets para actualización en tiempo real
""")

print("\n" + "=" * 60)
print("🎯 PRUEBA INMEDIATA:")
print("=" * 60)
print("""
1. En app.py, CAMBIA st.rerun() por:
   st.experimental_rerun()

2. O usa:
   st.session_state.update()
   st.experimental_rerun()
""")