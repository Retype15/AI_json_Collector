import os
import json
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

# Configure the API key (consider using environment variables for security)

schema_str = ''
ruta = os.path.dirname(os.path.abspath(__file__))

with open(ruta + "/Json.json", "r", encoding="utf-8") as file:
    schema_str = file.read()

# Crear el objeto Schema usando el diccionario
def create_schema(schema):
    if schema['type'] == 'object':
        properties = {k: create_schema(v) for k, v in schema.get('properties', {}).items()}
        return content.Schema(
            type=content.Type.OBJECT,
            properties=properties
        )
    elif schema['type'] == 'array':
        items = create_schema(schema['items'])
        return content.Schema(
            type=content.Type.ARRAY,
            items=items
        )
    elif schema['type'] == 'string':
        return content.Schema(
            type=content.Type.STRING
        )
    elif schema['type'] == 'integer':
        return content.Schema(
            type=content.Type.INTEGER
        )



class Gemini_20:
    schema_dict = ""
    def __init__(self, schema=""):
        if schema:
            self.schema_dict = schema
        else: 
            self.schema_dict = json.loads(schema_str)
            
        response_schema = create_schema(self.schema_dict)
        self.json_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_schema": response_schema,
            "response_mime_type": "application/json",
        }
            
        genai.configure(api_key="AIzaSyBOQwKlxo2UMSsk2-KaUt8SUc2XGzfr8MM") 
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=self.json_config,
        )
        print("Gemini API Cargado correctamente...")
        
    def call_ai(self, query):
        return self.model.generate_content(query)
        
    def set_ai_config(self, schema):
        if schema:
            self.json_config['response_schema'] = create_schema(schema)
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config=self.json_config,
            )

# Example usage:
if __name__ == "__main__":
    gemini_instance = Gemini_20()
    image_file = 'test_2.jpg'  # Replace with your image file path

    # Check if the image file exists
    if os.path.exists(image_file):
        extracted_data = gemini_instance.extract_menu_data(image_file)
        print(extracted_data)
    else:
        print(f"Error: The image file '{image_file}' does not exist.")