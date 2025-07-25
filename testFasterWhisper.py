from faster_whisper import WhisperModel

rutaAudio = "/home/leonel-perez/Escritorio/canciones mario/Algo de Abrazos(2).mp3"

#configuración LLM
model_size = "small"
model = WhisperModel(model_size, device="cpu", compute_type="int8")
segments, info = model.transcribe(rutaAudio, beam_size=5)

# Guardar en archivo e imprimir en consola
with open("transcripcion.txt", "w", encoding="utf-8") as f:
    print("Lenguaje: '%s' con (probabilidad de %d%%)\n" % (info.language, int(info.language_probability * 100)))
    f.write(f"Idioma Detectado: {info.language} (probabilidad {info.language_probability * 100:.2f}%)\n\n")
    for segment in segments:
        print("[%.1fs -> %.1fs] %s" % (segment.start, segment.end, segment.text))
        f.write(f"{segment.text}\n")