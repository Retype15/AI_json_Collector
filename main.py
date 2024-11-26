import sys
import json
import re
from datetime import datetime, timedelta
from dateutil import parser

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from gradio_client import Client

def clean_filename(filename): 
    pattern = r'[<>:"/\\|?*]' 
    clean_filename = re.sub(pattern, '', filename) 
    return clean_filename

class QueryThread(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, client, query):
        super().__init__()
        self.client = client
        self.query = query

    def run(self):
        json_file = ""
        
        try:
            with open("preprompt.txt", 'r', encoding='utf-8') as archivo:
                json_file = archivo.read()  
        except FileNotFoundError: 
            print("El archivo no se encontró.")
        except IOError: 
            print("Hubo un error al leer el archivo.")
        response_text = ""
        try:
            result = self.client.predict(
                query=self.query + json_file,
                history=[],
                system="You are Jessy, and Jessy only can response the user query in .json format file",
                radio="72B",
                api_name="/model_chat"
            )
            response_text = result[1][0][1]['text']
        except error:
            response_text = "An Error ocurred... Please try again"
        self.result_ready.emit(response_text)
        
class QuickSaveThread(QThread):
    finished = pyqtSignal(str)  
        
    def __init__(self, client, query): 
        super().__init__() 
        self.client = client 
        self.query = query 
    def run(self): 
        json_file = "" 
        try: 
            with open("preprompt.txt", 'r', encoding='utf-8') as archivo: 
                json_file = archivo.read() 
        except FileNotFoundError: 
            print("El archivo no se encontró.") 
        except IOError: 
            print("Hubo un error al leer el archivo.") 
        response_text = "" 
        try: 
            result = self.client.predict(
                query=self.query + json_file, 
                history=[], 
                system="You are Jessy, and Jessy only can response the user query in .json format file and in the first line must write what is defined between the <>", 
                radio="72B", api_name="/model_chat" 
            ) 
            response_text = result[1][0][1]['text'] 
        except error: 
            response_text = "An Error ocurred... Please try again" 
            
        # Guardar la respuesta 
        first_line, remaining_text = response_text.split('\n', 1)
        first_line = clean_filename(first_line)
        if len(first_line) <= 2:
            first_line = "error_in_name"
        with open(f"docs/{first_line}.json", "w", encoding="utf-8") as file: 
            file.write(remaining_text)
        self.finished.emit(f"Guardado rápido completado de {first_line}")
        


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Chatbot Query Program")

        # Layout principal
        self.layout = QVBoxLayout()

        # Ingreso de texto del usuario
        self.label = QLabel("Ingrese el texto:")
        self.layout.addWidget(self.label)
        
        self.text_input = QTextEdit()
        self.layout.addWidget(self.text_input)
        
        # Botón para enviar la consulta
        self.button = QPushButton("Enviar")
        self.button.clicked.connect(self.send_query)
        self.layout.addWidget(self.button)
        
        # Botón para guardar la respuesta rapidamente
        self.quick_save_button = QPushButton("Procesar y guardar")
        self.quick_save_button.clicked.connect(self.quick_save)
        self.layout.addWidget(self.quick_save_button)

        
        # Mostrar la respuesta
        self.result_label = QLabel("Respuesta:")
        self.layout.addWidget(self.result_label)
        
        self.result_output = QTextEdit()
        #self.result_output.setReadOnly(True)
        self.layout.addWidget(self.result_output)

        # Indicador de procesamiento
        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        # Botón para guardar la respuesta
        self.save_button = QPushButton("Guardar Respuesta")
        self.save_button.clicked.connect(self.save_response)
        self.layout.addWidget(self.save_button)

        # Definir la configuración visual
        self.setFont(QFont("Arial", 12))
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
            QLineEdit, QTextEdit {
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
        """)

        self.client = Client("Qwen/Qwen2.5")
        self.setLayout(self.layout)

    def send_query(self):
        # Mostrar mensaje de procesamiento
        self.status_label.setText("Procesando...")

        # Obtener el texto ingresado por el usuario
        user_text = self.text_input.toPlainText()
        self.result_output.setPlainText("")

        # Iniciar el subproceso para la consulta
        self.query_thread = QueryThread(self.client, user_text)
        self.query_thread.result_ready.connect(self.display_result)
        self.query_thread.start()

    def display_result(self, response_text):
        # Mostrar la respuesta en la interfaz
        self.result_output.setPlainText(response_text)
        # Actualizar mensaje de estado
        self.status_label.setText("Proceso completado")
        
    def save_response(self):
        # Guardar la respuesta en un archivo con el nombre definido en la primera linea
        response_text = self.result_output.toPlainText()
        first_line, remaining_text = response_text.split('\n', 1)
        first_line = clean_filename(first_line)
        if len(first_line) <= 2:
            first_line = "error_in_name"
        with open(f"docs/{clean_filename(first_line)}.json", "w", encoding="utf-8") as file:
            file.write(remaining_text)
        self.status_label.setText("Guardado completado")

    def quick_save(self):
        # Obtener el texto ingresado por el usuario
        user_text = self.text_input.toPlainText() 
        # Iniciar el subproceso para la consulta y guardado rápido 
        self.quick_save_thread = QuickSaveThread(self.client, user_text)
        self.quick_save_thread.finished.connect(self.display_save_status)
        self.quick_save_thread.start()
    
    
    def display_save_status(self, message):
        self.status_label.setText(message)

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
