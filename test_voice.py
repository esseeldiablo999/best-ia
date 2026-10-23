"""
test_voice.py - Prueba rápida del módulo de voz para BEST-IA
"""

from app.modules.voice_module import voice_module
import time

print("=" * 60)
print("🔍 PRUEBA DE VOZ - BEST IA")
print("=" * 60)

# 1. Verificar que el módulo existe
print("\n1. 📦 Verificando módulo...")
print(f"   ✅ Módulo cargado: {voice_module}")
print(f"   📊 Estado: listening={voice_module.is_listening}, speaking={voice_module.is_speaking}")

# 2. Probar micrófono
print("\n2. 🎤 Probando micrófono...")
print("   🔊 Habla algo en 3 segundos (di 'hola' o cualquier cosa)...")
time.sleep(1)
print("   ⏳ 3...")
time.sleep(1)
print("   ⏳ 2...")
time.sleep(1)
print("   ⏳ 1...")
time.sleep(1)

try:
    if voice_module.test_microphone():
        print("   ✅ ¡Micrófono FUNCIONA correctamente!")
    else:
        print("   ❌ Error con el micrófono")
        print("   📝 Verifica:")
        print("      - ¿El micrófono está conectado?")
        print("      - ¿Está activado en Windows? (Configuración > Privacidad > Micrófono)")
        print("      - ¿Otros programas pueden usarlo? (Grabadora de voz)")
except Exception as e:
    print(f"   ❌ Error probando micrófono: {e}")

# 3. Probar altavoz
print("\n3. 🔊 Probando altavoz...")
print("   ⏳ Escucharás una voz en 2 segundos...")
time.sleep(2)

try:
    voice_module.speak("Hola, soy BEST IA. Prueba de voz exitosa.", wait=True)
    print("   ✅ ¡Altavoz FUNCIONA correctamente!")
except Exception as e:
    print(f"   ❌ Error con altavoz: {e}")

# 4. Probar callback
print("\n4. 📞 Probando sistema de comandos...")
print("   ⏳ Escucharé por 10 segundos. Di: 'BEST IA, prueba de voz'")

def test_callback(text):
    print(f"   🎯 ¡Callback recibió: '{text}'!")

try:
    if voice_module.start_listening(test_callback):
        print("   ✅ Escucha iniciada")
        print("   👂 Escuchando... (10 segundos)")
        
        for i in range(10, 0, -1):
            print(f"      ⏱️ {i} segundos restantes...", end='\r')
            time.sleep(1)
        
        voice_module.stop_listening()
        print("\n   ✅ Escucha detenida")
    else:
        print("   ❌ No se pudo iniciar escucha")
except Exception as e:
    print(f"   ❌ Error en escucha: {e}")

print("\n" + "=" * 60)
print("✅ PRUEBA COMPLETADA")
print("=" * 60)
print("\n📝 RESUMEN:")
print("   Si TODO funcionó, ejecuta ahora:")
print("   streamlit run app.py")
print("\n   Si hubo errores, comparte qué viste arriba 👆")