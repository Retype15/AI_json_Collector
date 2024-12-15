import os
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

class QuickSaveThread(QThread):
    status_update = pyqtSignal(str, str, str)  # Señal para actualizar el estado (process_id, mensaje, estado)
    finished = pyqtSignal(str, str, str, str)  # Señal al completar el proceso (process_id, mensaje final, estado, texto de respuesta)

    def __init__(self, model, query, process_id, file_name="", post_process_callback=None, schema=""):
        super().__init__()
        self.model = model
        self.query = query
        self.process_id = process_id  # Identificador único del proceso
        self.file_name = file_name  # Determina si guardar el archivo
        self.post_process_callback = post_process_callback
        self.schema = schema

    def run(self):
        self.status_update.emit(self.process_id, "Enviando la consulta al modelo...", "in_progress")
        response_text = ""
        print("En proceso...1")
        try:
            print("En proceso...gemini")
            if self.schema:
                self.model.set_ai_config(self.schema)
            response = self.model.call_ai(self.query)
            response_text = response.text
            print(response_text)
        except Exception as e:
            print(f"Error {e}")
            self.finished.emit(self.process_id, f"Error: Fallo al procesar la consulta. {str(e)}", "error", "")
            return
        print("This continue...")
        
        if self.file_name:
            try:
                ruta = os.path.dirname(os.path.abspath(__file__))
                print(ruta)
                if self.file_name:
                    os.makedirs(ruta + "/docs", exist_ok=True)
                print(response_text)
                
                with open(f"{ruta}/docs/{self.file_name}.json", "w", encoding="utf-8") as file:
                    file.write(response_text)
                self.finished.emit(self.process_id, f"Guardado como \'{self.file_name}.json\' completado.", "completed", response_text)
            except Exception as e:
                print(e)
                self.finished.emit(self.process_id, f"Error al guardar el archivo: {str(e)}", "error", "")
        else:
            self.finished.emit(self.process_id, f"Proceso completado!", "completed", response_text)
            print(response_text)

        if self.post_process_callback:
            self.post_process_callback(response_text)
            
            
def clean_filename(filename):
    pattern = r'[<>:"/\\|?*]'
    return re.sub(pattern, '', filename)