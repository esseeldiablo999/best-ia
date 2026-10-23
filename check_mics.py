import speech_recognition as sr

print("🎤 LISTANDO MICRÓFONOS DISPONIBLES:")
mics = sr.Microphone.list_microphone_names()
for i, mic in enumerate(mics):
    print(f"  [{i}] {mic}")

print(f"\n📊 Total: {len(mics)} micrófonos")

# Probar cada micrófono
print("\n🔍 PROBANDO MICRÓFONOS:")
for i in range(min(3, len(mics))):  # Probar solo los primeros 3
    try:
        with sr.Microphone(device_index=i) as source:
            print(f"  Mic {i}: ✅ Funciona")
    except Exception as e:
        print(f"  Mic {i}: ❌ Error - {str(e)[:50]}")