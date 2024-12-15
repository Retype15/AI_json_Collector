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
        print(f"En proceso...{self.process_id}, in filename: {self.file_name}")
        try:
            if self.schema:
                self.model.set_ai_config(self.schema)
            response = self.model.call_ai(self.query)
            response_text = response.text
            print(response_text)
            print(f"Proceso de la solicitud {self.process_id} completado satisfactoriamente.")
        except Exception as e:
            print(f"Error {e}")
            self.finished.emit(self.process_id, f"Error: Fallo al procesar la consulta. {str(e)}", "error", "")
            return
        
        if self.file_name:
            try:
                ruta = os.path.dirname(os.path.abspath(__file__))
                print(f"Intentando guardar el archivo en {ruta}/{self.file_name}...")
                if self.file_name:
                    os.makedirs(os.path.dirname(ruta + '/' + self.file_name), exist_ok=True)
                
                with open(f"{ruta}/{self.file_name}", "w", encoding="utf-8") as file:
                    file.write(response_text)
                self.finished.emit(self.process_id, f"Guardado como \'{self.file_name}.json\' completado.", "completed", response_text)
            except Exception as e:
                print(e)
                self.finished.emit(self.process_id, f"Error al guardar el archivo: {str(e)}", "error", "")
        else:
            self.finished.emit(self.process_id, f"Proceso completado!", "completed", response_text)
            print(response_text)

        if self.post_process_callback:
            self.post_process_callback(response_text, self.file_name)
            
            
def clean_filename(filename):
    pattern = r'[<>:"/\\|?*]'
    return re.sub(pattern, '', filename)