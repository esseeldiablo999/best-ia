"""
Prueba final del sistema de voz
"""

from app.modules.voice_module import voice_module
import time

print("=" * 60)
print("🚀 PRUEBA FINAL DEL SISTEMA DE VOZ")
print("=" * 60)

# 1. Testear micrófono
print("\n1. 🎤 PROBANDO MICRÓFONO...")
if voice_module.test_microphone():
    print("   ✅ Micrófono FUNCIONA correctamente")
else:
    print("   ❌ Micrófono tiene problemas")
    exit(1)

# 2. Testear TTS
print("\n2. 🔊 PROBANDO TTS...")
try:
    voice_module.speak("Prueba de voz uno dos tres", wait=True)
    print("   ✅ TTS FUNCIONA correctamente")
except Exception as e:
    print(f"   ❌ TTS error: {e}")

# 3. Simular escucha
print("\n3. 👂 SIMULANDO ESCUCHA...")
def test_callback(text):
    print(f"   ✅ Callback recibido: '{text}'")

if voice_module.start_listening(test_callback):
    print("   ✅ Escucha iniciada")
    print("   🎤 Di 'BEST IA, prueba de voz' en 5 segundos...")
    
    time.sleep(5)
    
    voice_module.stop_listening()
    print("   ✅ Escucha detenida")
else:
    print("   ❌ No se pudo iniciar escucha")

print("\n" + "=" * 60)
print("🎯 PRUEBA COMPLETADA")
print("=" * 60)
print("\n🚀 Ahora ejecuta: streamlit run app.py")