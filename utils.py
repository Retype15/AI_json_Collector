import os
import json
import requests

def load_json_files(directory_path="web_files"):
    json_data_list = []
    ruta = os.path.dirname(os.path.abspath(__file__)) + '/' + directory_path
    try:
        # Asegurarse de que la carpeta existe
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"La carpeta '{ruta}' no existe.")

        # Recorrer todos los archivos dentro de la carpeta
        for file_name in os.listdir(ruta):
            if file_name.endswith(".json"):  # Solo archivos JSON
                file_path = os.path.join(ruta, file_name)
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    try:
                        json_data_list.append(json_file)
                    except json.JSONDecodeError as e:
                        print(f"Error al decodificar el archivo {file_name}: {e}")
        
        return json_data_list

    except Exception as e:
        print(f"Error al cargar los archivos JSON: {e}")
        return []
import os
import json

def load_json_files(directory_path="web_files"):
    json_files_data = []
    ruta = os.path.dirname(os.path.abspath(__file__)) + '/' + directory_path
    
    try:
        # Asegurarse de que la carpeta existe
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"La carpeta '{ruta}' no existe.")

        # Recorrer todos los archivos dentro de la carpeta
        for file_name in os.listdir(ruta):
            if file_name.endswith(".json"):  # Solo archivos JSON
                file_path = os.path.join(ruta, file_name)
                file_name_w = os.path.splitext(file_name)[0]  # Nombre sin .json
                
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    try:
                        # Cargar el contenido del archivo JSON
                        data = json.load(json_file)
                        # Agregar (nombre del archivo, contenido) a la lista
                        json_files_data.append((file_name_w, data))
                    except json.JSONDecodeError as e:
                        print(f"Error al decodificar el archivo {file_name}: {e}")
        
        return json_files_data

    except Exception as e:
        print(f"Error al cargar los archivos JSON: {e}")
        return []


def load_json_as_string(file_path):
    try:
        # Abrir el archivo y leer su contenido como texto
        with open(file_path, 'r', encoding='utf-8') as json_file:
            json_string = json_file.read()
        return json_string
    except FileNotFoundError:
        print(f"El archivo '{file_path}' no se encontró.")
        return None
    except Exception as e:
        print(f"Error al cargar el archivo JSON: {e}")
        return None

def upload_to_blob(archive, file_name=""):
    url = "https://icd-restaurants-and-bars.vercel.app/api/save-json"
    
    file_name_parts = file_name.split('/')
    file_name_parts = file_name_parts[1:]
    nueva_ruta = '/'.join(file_name_parts)
    
    data = {
        "json_text": archive,
        "archive_name": nueva_ruta
    }
    response = requests.post(url, json=data)
    print("Estado:", response.status_code)
    print("Respuesta:", response.json())

if __name__ == "__main__":
    print(load_json_files("web_files/_users_query/"))
    