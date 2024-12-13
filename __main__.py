from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTextEdit, QLabel, QFileDialog, QListWidget, QTreeWidget, QTreeWidgetItem, QStackedWidget, QScrollArea, QGridLayout
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
#from PyQt5.QtCore import Qt, QThread, pyqtSignal

import sys
import os
import uuid
from PIL import Image
import time

# Importar modelo Gemini_20 de la biblioteca local AI
from AI import Gemini_20
from quick_save_thread import QuickSaveThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz Profesional")
        self.setGeometry(100, 100, 800, 600)

        # Contenedor principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Botones de modos
        self.mode_buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.mode_buttons_layout)

        self.text_mode_button = QPushButton("Modo Texto")
        self.program_mode_button = QPushButton("Modo Programa")
        self.image_mode_button = QPushButton("Modo Imagen")

        self.mode_buttons_layout.addWidget(self.text_mode_button)
        self.mode_buttons_layout.addWidget(self.program_mode_button)
        self.mode_buttons_layout.addWidget(self.image_mode_button)

        # Stacked widget para los modos
        self.modes_stack = QStackedWidget()
        self.layout.addWidget(self.modes_stack)

        # Modo Texto
        self.text_widget = QTextEdit()
        self.modes_stack.addWidget(self.text_widget)

        # Modo Programa
        self.program_widget = QTextEdit()
        self.program_widget.setPlaceholderText("Escribe tu código Python aquí...")
        self.modes_stack.addWidget(self.program_widget)

        # Modo Imagen
        self.image_widget = QWidget()
        self.image_layout = QVBoxLayout(self.image_widget)

        # Scroll Area para lista de imágenes
        self.image_scroll_area = QScrollArea()
        self.image_scroll_area.setWidgetResizable(True)
        self.image_list_container = QWidget()
        self.image_grid_layout = QGridLayout(self.image_list_container)
        self.image_list_container.setLayout(self.image_grid_layout)
        self.image_scroll_area.setWidget(self.image_list_container)
        self.image_layout.addWidget(self.image_scroll_area)

        self.add_image_button = QPushButton("Añadir Imagen")
        self.image_layout.addWidget(self.add_image_button)

        self.remove_image_button = QPushButton("Eliminar Imagen")
        self.image_layout.addWidget(self.remove_image_button)

        self.modes_stack.addWidget(self.image_widget)

        # Cambiar modos
        self.text_mode_button.clicked.connect(lambda: self.modes_stack.setCurrentWidget(self.text_widget))
        self.program_mode_button.clicked.connect(lambda: self.modes_stack.setCurrentWidget(self.program_widget))
        self.image_mode_button.clicked.connect(lambda: self.modes_stack.setCurrentWidget(self.image_widget))

        # Botón de función
        self.action_button = QPushButton("Procesar")
        self.layout.addWidget(self.action_button)
        self.action_button.clicked.connect(self.quick_save)
        
        # Estado de procesos
        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)
        
        # QTreeWidget
        self.process_tree = QTreeWidget()
        self.process_tree.setHeaderLabels(["Proceso", "Estado"])
        self.process_tree.setColumnWidth(0, 200)
        self.process_tree.setColumnWidth(1, 300)
        self.layout.addWidget(self.process_tree)
        self.process_items = {}  # Diccionario para rastrear procesos

        # Conectar botones de modo Imagen
        self.add_image_button.clicked.connect(self.add_images)
        self.remove_image_button.clicked.connect(self.remove_selected_images)

        self.image_widgets = []  # Lista para almacenar widgets de imágenes

        # Instanciar modelo Gemini_20
        self.model = Gemini_20()
        self.threads = []  # Lista para rastrear subprocesos activos

        self.process_times = {}  # Diccionario para rastrear tiempos de inicio de cada proceso
        self.timer = QTimer(self)  # Temporizador global para actualizar el estado
        self.timer.timeout.connect(self.update_progress_times)
        self.timer.start(1000)  # Actualización cada segundo

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

    def add_images(self):
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Seleccionar imágenes", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)
        if file_paths:
            for path in file_paths:
                self.add_image_widget(path)

    def add_image_widget(self, image_path):
        if not os.path.exists(image_path):
            return

        row = len(self.image_widgets) // 4  # Máximo 4 imágenes por fila
        col = len(self.image_widgets) % 4

        # Crear un botón con el ícono de la imagen
        pixmap = QPixmap(image_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_button = QPushButton()
        image_button.setIcon(QIcon(pixmap))
        image_button.setIconSize(pixmap.size())
        image_button.setCheckable(True)
        image_button.setToolTip(image_path)

        self.image_grid_layout.addWidget(image_button, row, col)
        self.image_widgets.append(image_button)

    def remove_selected_images(self):
        for button in self.image_widgets[:]:  # Copia para evitar modificar mientras iteramos
            if button.isChecked():
                self.image_grid_layout.removeWidget(button)
                button.deleteLater()
                self.image_widgets.remove(button)

    def quick_save(self):
        process_id = str(uuid.uuid4())

        if self.modes_stack.currentWidget() == self.program_widget:  # Modo programa
            user_code = self.program_widget.toPlainText()

            # Crear un entorno seguro para ejecutar el código del usuario
            local_scope = {
                "send_query": self.send_query,  # Permitir que el usuario llame a send_query
                #"active_processes": self.get_active_processes,
            }

            try:
                exec(user_code, {}, local_scope)  # Ejecutar el código del usuario
            except Exception as e:
                self.status_label.setText(f"Error en el código: {str(e)}")
                return  # Evitar continuar si hay errores
                
        elif self.modes_stack.currentWidget() == self.image_widget:  # Modo imágenes
            for button in self.image_widgets:
                image_path = button.toolTip()
                image_name = os.path.splitext(os.path.basename(image_path))[0]  # Nombre sin extensión
                img = Image.open(image_path)
                self.send_query([img, "Extract from the Image"],image_name)
        else:  # Modo texto (predeterminado)
            user_text = self.text_widget.toPlainText()
            #img = Image.open('test_2.jpg')
            self.send_query([user_text], file_name="OLAOLA")
    
    def send_query(self, query, file_name="", post_process=None):
        #print(query, '\n', file_name)
        
        process_id = str(uuid.uuid4())
        
        quick_save_thread = QuickSaveThread(self.model, query, process_id, file_name, post_process)
        quick_save_thread.status_update.connect(lambda: self.update_process_state(process_id, "En progreso...", "in_progress"))
        quick_save_thread.finished.connect(
            lambda process_id, message, status, response_text: self.handle_query_completion(process_id, message, status, response_text)
        )
        quick_save_thread.finished.connect(lambda: self.cleanup_thread(quick_save_thread))  # Limpieza
        quick_save_thread.start()
        
        self.threads.append(quick_save_thread)
        
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

    def cleanup_thread(self, thread):
        if thread in self.threads:
            self.threads.remove(thread)
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
