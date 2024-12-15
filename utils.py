import os
import json

def load_json_files(directory_path="web_files/_users_query/"):
    """
    Carga todos los archivos JSON de la carpeta especificada y devuelve una lista con su contenido.

    :param directory_path: Ruta de la carpeta donde están los archivos JSON.
    :return: Lista con el contenido de todos los archivos JSON.
    """
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
                        # Cargar el contenido del archivo JSON
                        data = json.load(json_file)
                        json_data_list.append(data)
                    except json.JSONDecodeError as e:
                        print(f"Error al decodificar el archivo {file_name}: {e}")
        
        return json_data_list

    except Exception as e:
        print(f"Error al cargar los archivos JSON: {e}")
        return []
