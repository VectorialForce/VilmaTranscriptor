import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from faster_whisper import WhisperModel

def escribir_log(mensaje):
    log_text.config(state='normal')
    log_text.insert(tk.END, mensaje + '\n')
    log_text.see(tk.END)
    log_text.config(state='disabled')

def transcribir_audio():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.mp3 *.wav *.m4a *.mp4")])
    if not archivo:
        escribir_log("No se seleccionó ningún archivo.")
        return

    texto_transcripcion.delete(1.0, tk.END)
    escribir_log(f"Archivo seleccionado: {archivo}")
    escribir_log("Cargando modelo...")

    try:
        model = WhisperModel("base", device="cpu") # Puedes usar "small", "medium", etc.
        escribir_log("Modelo cargado. Iniciando transcripción...")
        segments, info = model.transcribe(archivo, beam_size=5)

        texto_completo = ""
        for segment in segments:
            texto_completo += segment.text + " "
        texto_transcripcion.delete(1.0, tk.END)
        texto_transcripcion.insert(tk.END, texto_completo)
        escribir_log("Transcripción finalizada correctamente.")
    except Exception as e:
        escribir_log(f"Error: {e}")
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Transcriptor de Audios para Mamá")
root.geometry("600x500")

boton = tk.Button(root, text="Seleccionar audio y transcribir", command=transcribir_audio)
boton.pack(pady=10)

texto_transcripcion = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=18)
texto_transcripcion.pack(expand=True, fill="both", padx=10, pady=(0,5))

log_label = tk.Label(root, text="Log:")
log_label.pack(anchor="w", padx=10)

log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=5, state='disabled', bg="#eee")
log_text.pack(fill="x", padx=10, pady=(0,10))

root.mainloop()