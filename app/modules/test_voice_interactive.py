"""
test_voice_interactive.py - Prueba interactiva del módulo de voz
"""

from app.modules.voice_module import voice_module
import time

def on_command_detected(command):
    """Callback cuando se detecta un comando"""
    print(f"\n🎯 COMANDO RECIBIDO: '{command}'")
    print("🤖 Procesando...")
    
    # Responder por voz
    voice_module.speak(f"Recibí el comando: {command}")

print("=" * 60)
print("🎤 PRUEBA INTERACTIVA DEL MÓDULO DE VOZ")
print("=" * 60)

# 1. Mostrar información
print("\n1. 📊 INFORMACIÓN DEL MÓDULO:")
print(f"   Micrófono: índice {voice_module.mic_device_index}")
print(f"   Idioma: {voice_module.language}")
print(f"   Velocidad: {voice_module.voice_rate}")
print(f"   Volumen: {voice_module.voice_volume}")

# 2. Probar micrófono
print("\n2. 🎤 PROBANDO MICRÓFONO...")
input("   Presiona ENTER y habla algo...")

if voice_module.test_microphone():
    print("   ✅ Micrófono funciona")
else:
    print("   ❌ Problema con micrófono")
    exit()

# 3. Probar altavoces
print("\n3. 🔊 PROBANDO ALTAVOCES...")
voice_module.test_speakers()

# 4. Iniciar escucha
print("\n4. 🎤 INICIANDO MODO ESCUCHA...")
print("   Di: 'BEST IA' seguido de tu comando")
print("   Ejemplo: 'BEST IA, ¿qué hora es?'")
print("\n   Presiona Ctrl+C para salir")

voice_module.start_listening(on_command_detected)

# 5. Mantener el programa corriendo
try:
    while True:
        time.sleep(1)
        # Mostrar estado cada 10 segundos
        if int(time.time()) % 10 == 0:
            status = voice_module.get_status()
            print(f"\n📊 Estado: {status['listening'] and '🎤 Escuchando' or '🔇 Detenido'}")
            print(f"   Comandos recibidos: {status['stats']['total_commands']}")
except KeyboardInterrupt:
    print("\n\n🛑 Deteniendo...")
    voice_module.stop_listening()
    print("✅ Prueba finalizada")