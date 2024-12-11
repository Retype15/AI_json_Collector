import sys
import re
import time  # Agregar esta importación para rastrear tiempos en segundos
import uuid  # Para generar identificadores únicos
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QTreeWidget, QTreeWidgetItem
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from gradio_client import Client

# Utilidad para limpiar nombres de archivos
def clean_filename(filename):
    pattern = r'[<>:"/\\|?*]'
    return re.sub(pattern, '', filename)

# Subproceso para manejar consultas al modelo
class QuickSaveThread(QThread):
    status_update = pyqtSignal(str, str, str)  # Señal para actualizar el estado (process_id, mensaje, estado)
    finished = pyqtSignal(str, str, str, str)  # Señal al completar el proceso (process_id, mensaje final, estado, texto de respuesta)

    def __init__(self, client, query, process_id, save_to_file=True, post_process_callback=None):
        super().__init__()
        self.client = client
        self.query = query
        self.process_id = process_id  # Identificador único del proceso
        self.save_to_file = save_to_file  # Determina si guardar el archivo
        self.post_process_callback = post_process_callback

    def run(self):
        json_file = ""
        self.status_update.emit(self.process_id, "Leyendo archivo preprompt.txt...", "in_progress")
        
        try:
            with open("preprompt.txt", 'r', encoding='utf-8') as archivo:
                json_file = archivo.read()
        except FileNotFoundError:
            self.status_update.emit(self.process_id, "Error: El archivo preprompt.txt no se encontró.", "error")
            return
        except IOError:
            self.status_update.emit(self.process_id, "Error al leer el archivo preprompt.txt.", "error")
            return

        self.status_update.emit(self.process_id, "Enviando la consulta al modelo...", "in_progress")
        response_text = ""
        try:
            result = self.client.predict(
                query=self.query + json_file,
                history=[],
                system="You are Jessy, and Jessy only can respond to the user query in JSON format, and write just first line the json the filename or the name chosen by the user and json in the second.",
                radio="72B",
                api_name="/model_chat"
            )
            response_text = result[1][0][1]['text']
        except Exception as e:
            self.status_update.emit(self.process_id, f"Error: Fallo al procesar la consulta. {str(e)}", "error")
            return

        #self.status_update.emit(self.process_id, "Procesando la respuesta del modelo...", "in_progress")
        if response_text.startswith('{'):
            first_line, remaining_text = f"no_name_{self.process_id}", response_text
        else:
            first_line, remaining_text = response_text.split('\n', 1)
        if self.save_to_file:
            try:
                first_line = clean_filename(first_line)
                if len(first_line) <= 2:
                    first_line = f"error_in_name_{self.process_id}"
                if self.save_to_file:
                    with open(f"docs/{first_line}.json", "w", encoding="utf-8") as file:
                        file.write(remaining_text)
                self.finished.emit(self.process_id, f"Guardado rápido completado: {first_line}.json", "completed", remaining_text)
            except Exception as e:
                self.finished.emit(self.process_id, f"Error al guardar el archivo: {str(e)}", "error", "")
        else:
            self.finished.emit(self.process_id, f"Proceso completado!", "completed", remaining_text)

        if self.post_process_callback:
            self.post_process_callback(remaining_text)

# Ventana principal de la aplicación
class MainWindow(QWidget):
    CONFIG_FILE = "config.json"
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Chatbot Query Program")
        self.resize(600, 500)
        self.setFont(QFont("Arial", 12))
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
            QTextEdit {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #5cb85c;
                color: #fff;
                border: none;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
            QPushButton:checked {
                background-color: #337ab7;
                color: #fff;
            }
        """)

        # Layout principal
        self.layout = QVBoxLayout()

        self.program_mode_label = QLabel("En este modo, puedes escribir tu propio código Python para ejecutar un proceso.")
        self.program_mode_label.setVisible(False)
        self.layout.addWidget(self.program_mode_label)


        # Botón estilizado para cambiar entre modos
        self.mode_toggle = QPushButton("Modo: Texto", self)
        self.mode_toggle.setCheckable(True)
        self.mode_toggle.setChecked(False)
        self.mode_toggle.clicked.connect(self.toggle_mode)
        self.layout.addWidget(self.mode_toggle)

        # Entrada de texto
        self.label = QLabel("Ingrese el texto:")
        self.layout.addWidget(self.label)

        # Campo de texto adicional para el modo "programa"
        self.code_input = QTextEdit(self)
        self.code_input.setPlaceholderText("Escribe tu código Python aquí...\n usa el metodo send_query(optional query=\"texto extra\")\n metodo active_processes() devuelve la lista de procesos activos")
        self.code_input.setVisible(False)  # Oculto por defecto
        self.layout.addWidget(self.code_input)

        self.text_input = QTextEdit()
        self.layout.addWidget(self.text_input)
        
        # Botón para guardar rápidamente
        self.quick_save_button = QPushButton("Procesar y Guardar")
        self.quick_save_button.clicked.connect(self.quick_save)
        self.layout.addWidget(self.quick_save_button)

        # Estado de procesos
        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        # Árbol de procesos
        self.process_tree = QTreeWidget()
        self.process_tree.setHeaderLabels(["Proceso", "Estado"])
        # Configurar anchos de columnas
        self.process_tree.setColumnWidth(0, 200)  # Columna "Proceso"
        self.process_tree.setColumnWidth(1, 300)  # Columna "Estado"

        self.layout.addWidget(self.process_tree)
        self.process_items = {}  # Diccionario para rastrear procesos

        # Cliente de la API
        self.client = Client("Qwen/Qwen2.5")
        self.setLayout(self.layout)
        self.threads = []  # Lista para rastrear subprocesos activos

        self.process_times = {}  # Diccionario para rastrear tiempos de inicio de cada proceso
        self.timer = QTimer(self)  # Temporizador global para actualizar el estado
        self.timer.timeout.connect(self.update_progress_times)
        self.timer.start(1000)  # Actualización cada segundo
        
        self.load_configuration()


    def toggle_mode(self):
        if self.mode_toggle.isChecked():
            self.mode_toggle.setText("Modo: Programa")
            self.text_input.setVisible(False)
            self.code_input.setVisible(True)
        else:
            self.mode_toggle.setText("Modo: Texto")
            self.text_input.setVisible(True)
            self.code_input.setVisible(False)


    def quick_save(self):
        process_id = str(uuid.uuid4())

        if self.mode_toggle.isChecked():  # Modo programa
            user_code = self.code_input.toPlainText()

            # Crear un entorno seguro para ejecutar el código del usuario
            local_scope = {
                "send_query": self.send_query,  # Permitir que el usuario llame a send_query
                "active_processes": self.get_active_processes,
                #"self": self,
            }

            try:
                exec(user_code, {}, local_scope)  # Ejecutar el código del usuario
            except Exception as e:
                self.status_label.setText(f"Error en el código: {str(e)}")
                return  # Evitar continuar si hay errores
        else:  # Modo texto (predeterminado)
            user_text = self.text_input.toPlainText()

            self.send_query(query=user_text)

    def update_process_state(self, process_id, message, status):
        if process_id not in self.process_items:
            # Si no existe un proceso para este ID, crea uno
            process_item = QTreeWidgetItem([f"Proceso {process_id[:8]}", message])
            process_item.setForeground(1, Qt.blue)  # Color azul para estado inicial
            self.process_tree.addTopLevelItem(process_item)
            self.process_items[process_id] = process_item
            self.process_times[process_id] = time.time()
        else:
            process_item = self.process_items[process_id]

        # Actualizar el mensaje del proceso
        process_item.setText(1, message)

        # Actualizar el color del estado
        if status == "completed":
            process_item.setForeground(1, Qt.green)
        elif status == "error":
            # Mantener el color rojo solo si es un error
            process_item.setForeground(1, Qt.red)
        else:
            # Azul para estados en progreso
            process_item.setForeground(1, Qt.blue)
        # Eliminar el proceso del rastreador de tiempos si ya no está en progreso
        if status in ["completed", "error"]:
            if process_id in self.process_times:
                del self.process_times[process_id]

    def send_query(self, query="", save_to_file=True, post_process=None, wait_for_previous=False):
        """
        Enviar una consulta al modelo con opciones de post-procesamiento y sincronización.
        """
        if wait_for_previous:
            # Esperar a que todos los procesos previos se completen
            for thread in self.threads:
                thread.wait()

        process_id = str(uuid.uuid4())

        # Crear el subproceso de QuickSaveThread con el callback de post-procesamiento
        quick_save_thread = QuickSaveThread(self.client, query, process_id, save_to_file, post_process)
        quick_save_thread.status_update.connect(lambda: self.update_process_state(process_id, "En progreso...", "in_progress"))
        quick_save_thread.finished.connect(
            lambda process_id, message, status, response_text: self.handle_query_completion(process_id, message, status, response_text)
        )
        quick_save_thread.finished.connect(lambda: self.cleanup_thread(quick_save_thread))  # Limpieza
        quick_save_thread.start()

        # Añadir el subproceso a la lista de subprocesos activos
        self.threads.append(quick_save_thread)

        # Añadir un estado inicial a la lista
        self.update_process_state(process_id, "Iniciando proceso...", "in_progress")

    def handle_query_completion(self, process_id, message, status, response_text):
        """
        Maneja la finalización de un proceso, actualizando el estado en la interfaz
        y mostrando el resultado si corresponde.
        """
        self.update_process_state(process_id, message, status)

        if status == "completed":
            self.status_label.setText(f"Proceso {process_id[:8]} completado: {message}")
        elif status == "error":
            self.status_label.setText(f"Error en el proceso {process_id[:8]}: {message}")
        else:
            self.status_label.setText(f"Proceso {process_id[:8]} en estado desconocido.")


    def cleanup_thread(self, thread):
        if thread in self.threads:
            self.threads.remove(thread)

    def update_progress_times(self):
        """
        Actualiza los tiempos de los procesos en progreso cada segundo.
        """
        current_time = time.time()  # Tiempo actual en segundos

        for process_id, start_time in list(self.process_times.items()):
            elapsed_time = int(current_time - start_time)  # Tiempo transcurrido en segundos

            if elapsed_time > 120:  # Límite de 2 minutos
                self.stop_process(process_id, reason="El proceso excedió el límite de tiempo (2 minutos).")
            else:
                # Actualizar el estado del proceso con el tiempo transcurrido
                if process_id in self.process_items:
                    process_item = self.process_items[process_id]
                    process_item.setText(1, f"En progreso... {elapsed_time} seg")


    def stop_process(self, process_id, reason="El proceso excedió el límite de tiempo."):
        """
        Detiene un subproceso por su ID y actualiza su estado en la interfaz.
        """
        if process_id in self.process_items:
            process_item = self.process_items[process_id]
            process_item.setText(1, f"Error: {reason}")
            process_item.setForeground(1, Qt.red)  # Actualizar el color a rojo

        # Finalizar el subproceso asociado si está activo
        for thread in self.threads:
            if thread.process_id == process_id and thread.isRunning():
                thread.terminate()  # Forzar la terminación del subproceso
                thread.wait()  # Esperar que se detenga completamente
                self.threads.remove(thread)  # Limpiar la lista de subprocesos

        # Eliminar el proceso del rastreador de tiempos
        if process_id in self.process_times:
            del self.process_times[process_id]


    def get_active_processes(self):
        active_processes = []
        for thread in self.threads:
            if thread.isRunning():  # Verifica si el subproceso aún está en ejecución
                active_processes.append(thread.process_id)

        return active_processes

    def load_configuration(self):
        """
        Carga el archivo de configuración y restaura el estado del programa.
        """
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
                # Restaurar texto y código guardados
                self.text_input.setPlainText(config.get("text_input", ""))
                self.code_input.setPlainText(config.get("code_input", ""))
        except FileNotFoundError:
            # Si no existe el archivo, continuar con valores por defecto
            pass
        except json.JSONDecodeError as e:
            print(f"Error al cargar la configuración: {str(e)}")

    def save_configuration(self):
        """
        Guarda el estado actual del programa en un archivo de configuración.
        """
        config = {
            "text_input": self.text_input.toPlainText(),
            "code_input": self.code_input.toPlainText(),
        }
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as config_file:
                json.dump(config, config_file, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error al guardar la configuración: {str(e)}")

    def closeEvent(self, event):
        """
        Se asegura de detener cualquier subproceso en ejecución antes de cerrar la ventana.
        """
        for thread in self.threads:
            if thread.isRunning():
                thread.terminate()
                thread.wait()
                self.threads.remove(thread)
        
        self.save_configuration()
        super().closeEvent(event)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
