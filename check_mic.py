"""
check_mic.py - Diagnóstico de micrófonos
"""

import speech_recognition as sr

print("=" * 60)
print("🎤 DIAGNÓSTICO DE MICRÓFONOS")
print("=" * 60)

# Listar todos los micrófonos
print("\n1. 📋 MICRÓFONOS DISPONIBLES:")
mics = sr.Microphone.list_microphone_names()

for i, mic in enumerate(mics):
    print(f"   [{i}] {mic}")

print(f"\n📊 Total: {len(mics)} micrófonos")

# Probar cada micrófono
print("\n2. 🔍 PROBANDO MICRÓFONOS...")

working_mics = []

for i in range(len(mics)):
    try:
        print(f"\n   Probando micrófono [{i}]...")
        mic = sr.Microphone(device_index=i)
        recognizer = sr.Recognizer()
        
        with mic as source:
            print("      Ajustando ruido ambiente...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"      ✅ Micrófono [{i}] RESPONDE")
            working_mics.append(i)
            
    except Exception as e:
        print(f"      ❌ Error: {str(e)[:50]}")

print("\n" + "=" * 60)
print("📊 RESULTADOS:")
print(f"   ✅ Micrófonos que funcionan: {working_mics}")
print(f"   ❌ Total probados: {len(mics)}")
print("=" * 60)

if working_mics:
    print(f"\n🎯 RECOMENDACIÓN: Usa micrófono índice {working_mics[0]}")
    print(f"   En voice_module.py, cambia: self.mic_device_index = {working_mics[0]}")
else:
    print("\n❌ NINGÚN MICRÓFONO FUNCIONA")
    print("   Verifica:")
    print("   1. ¿El micrófono está conectado?")
    print("   2. ¿Windows lo reconoce? (Configuración → Sistema → Sonido)")
    print("   3. ¿Tiene permisos? (Configuración → Privacidad → Micrófono)")