import tkinter as tk
from tkinter import filedialog, scrolledtext
from tkinter.ttk import Progressbar
from faster_whisper import WhisperModel
import threading
import os
import time
from docx import Document

def seleccionar_archivos():
    archivos = filedialog.askopenfilenames(
        title="Selecciona uno o varios archivos de audio",
        filetypes=[("Archivos de audio", "*.mp3 *.wav *.m4a *.ogg *.flac"), ("Todos los archivos", "*.*")]
    )
    if archivos:
        threading.Thread(target=transcribir_archivos, args=(archivos, modelo_var.get())).start()

def transcribir_archivos(lista_audios, modelo_seleccionado):
    text_area.delete(1.0, tk.END)
    text_area.insert(
        tk.END,
        f"Configurando modelo '{modelo_seleccionado}'. Si no está descargado, esto puede tomar varios minutos...\n"
    )
    root.update()
    t0 = time.time()
    try:
        model = WhisperModel(modelo_seleccionado, device="cpu", compute_type="int8")
        t1 = time.time()
        if t1 - t0 > 5:
            text_area.insert(
                tk.END,
                f"Modelo '{modelo_seleccionado}' descargado y listo (tiempo: {int(t1 - t0)} segundos).\n\n"
            )
        else:
            text_area.insert(
                tk.END,
                f"Modelo '{modelo_seleccionado}' listo para usar.\n\n"
            )
        root.update()
    except Exception as e:
        text_area.insert(
            tk.END,
            f"Error al configurar/descargar el modelo '{modelo_seleccionado}': {str(e)}\n"
        )
        root.update()
        return

    for idx, rutaAudio in enumerate(lista_audios, 1):
        text_area.insert(tk.END, f"Procesando archivo {idx}/{len(lista_audios)}:\n{rutaAudio}\n\n")
        root.update()
        start_time = time.time()
        try:
            segments, info = model.transcribe(rutaAudio, beam_size=5)
        except Exception as e:
            text_area.insert(tk.END, f"Error transcribiendo '{rutaAudio}': {str(e)}\n{'-'*50}\n")
            root.update()
            continue

        encabezado = f"Lenguaje detectado: '{info.language}' (probabilidad {int(info.language_probability * 100)}%)"
        print(encabezado)
        text_area.insert(tk.END, encabezado + "\n\n")
        root.update()

        resultado = []

        duracion_total = info.duration if hasattr(info, 'duration') else max([s.end for s in segments])
        progress_bar["maximum"] = duracion_total
        progress_bar["value"] = 0

        for segment in segments:
            linea_con_timestamp = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text.strip()}"
            solo_texto = segment.text.strip()

            print(linea_con_timestamp)
            text_area.insert(tk.END, linea_con_timestamp + "\n")
            root.update()

            resultado.append(solo_texto)

            progreso_actual = min(segment.end, duracion_total)
            progress_bar["value"] = progreso_actual
            porcentaje = int((progreso_actual / duracion_total) * 100)
            elapsed = time.time() - start_time
            avg_time_per_sec = elapsed / progreso_actual if progreso_actual else 0
            secs_remaining = int((duracion_total - progreso_actual) * avg_time_per_sec) if avg_time_per_sec > 0 else 0
            porcentaje_label.config(
                text=f"Progreso: {porcentaje}% | Tiempo estimado restante: {secs_remaining}s"
            )
            root.update()

        # Guardar como .docx usando el nombre original del audio
        nombre_base = os.path.basename(rutaAudio)
        nombre_archivo = f"{nombre_base}_transcripcion.docx"
        document = Document()

        for linea in resultado:
            p = document.add_paragraph(linea)
            p.paragraph_format.space_after = 0  # elimina espacios extra

        document.save(nombre_archivo)

        progress_bar["value"] = duracion_total
        porcentaje_label.config(text="Progreso: 100% | ¡Transcripción completada!")
        root.update()
        text_area.insert(
            tk.END,
            f"\nTranscripción terminada. Archivo guardado como: {nombre_archivo}\n{'-'*50}\n"
        )
        root.update()

    text_area.insert(tk.END, "\nProceso de lote terminado. Todos los archivos han sido transcritos.\n")
    root.update()

root = tk.Tk()
root.title("Transcriptor batch de audio a DOCX con Whisper")
root.geometry("800x650")

label = tk.Label(root, text="Haz clic para seleccionar uno o varios archivos de audio", pady=10)
label.pack()

frame_modelo = tk.Frame(root)
frame_modelo.pack(pady=5)
tk.Label(frame_modelo, text="Elige el modelo Whisper: ").pack(side=tk.LEFT)

modelo_var = tk.StringVar(value="small")
modelos_whisper = [
    ("tiny", "tiny"),
    ("base", "base"),
    ("small", "small"),
    ("medium", "medium"),
    ("large-v2", "large-v2"),
]
for texto, valor in modelos_whisper:
    tk.Radiobutton(frame_modelo, text=texto, variable=modelo_var, value=valor).pack(side=tk.LEFT)

boton = tk.Button(root, text="Seleccionar Audios", command=seleccionar_archivos, width=20)
boton.pack()

porcentaje_label = tk.Label(root, text="Progreso: 0% | Tiempo estimado restante: --")
porcentaje_label.pack()

progress_bar = Progressbar(root, orient=tk.HORIZONTAL, length=350, mode='determinate')
progress_bar.pack(pady=10)

text_area = scrolledtext.ScrolledText(root, width=95, height=25, wrap=tk.WORD, font=("Arial", 10))
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()