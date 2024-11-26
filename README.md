# AI JSON Collector

## ¿Qué es AI JSON Collector?

AI JSON Collector es una herramienta diseñada para autocompletar archivos JSON utilizando modelos de razonamiento. Su objetivo es sintetizar los datos de entrada en formato de texto y convertirlos en formato JSON de manera rápida y sin esfuerzo. Esto aumenta la productividad en tareas sencillas y repetitivas relacionadas con el manejo de datos en formato JSON.

## ¿Cómo puedo ejecutar este proyecto por mi cuenta?

Seguir estos pasos es bastante sencillo. Asegúrate de tener Python instalado (preferiblemente la última versión), y verifica que tienes instaladas las siguientes bibliotecas:

- `datetime`
- `dateutil`
- `PyQt5`
- `gradio_client`

### Pasos para la ejecución:

1. **Instalar Bibliotecas:**
   Instala las bibliotecas necesarias utilizando pip:
   ```sh
   pip install datetime python-dateutil PyQt5 gradio_client
	```
	
2. **Configurar el Prompt:**
	Escribe en el archivo preprompt.txt el prompt que deseas pasar al modelo, incluyendo la estructura básica del JSON y explicaciones detalladas. Se recomienda hacer comentarios sobre la línea que indique cómo debería ser el dato que se guarde, el formato, ejemplos, etc.

Ejemplo de contenido en preprompt.txt:

```json
{
    "fecha": "YYYYMMDD", // Formato de fecha: AñoMesDía, Ejemplo: 20240812
    "nombre": "string", // Nombre del usuario, Ejemplo: "Juan Pérez"
	"edad": , // Edad del usuario, Ejemplo: 22
    ...
}
Datos solamente del usuario que mas hayan nombrado

En valores vacios usar Null.
No escribas los comentarios.

```

## Ejecución del Proyecto:
Una vez configurado el preprompt.txt, simplemente ejecuta el script principal de tu proyecto y espera a que el modelo de razonamiento se inicie, y luego el programa, donde usted le enviara el texto en el primer cuadro y presionara una de las opciones:
- Procesar: Envia el texto para ser procesado en la rama principal y lo mostrará en el recuadro de respuesta, donde se podra editar a conveniencia.
- Procesar y guardar: autocompletará el archivo JSON basado en los datos de entrada proporcionados y guardara el archivo en segundo plano y paralelo al proceso principal.
- Guardar respuesta: Guarda el texto de respuesta en un archivo json en docs, Importante: la primera linea define el nombre que tendra el archivo, por lo que es importante definirla para un nombramiento correcto.


## Contribuciones:
Las contribuciones son bienvenidas. Si encuentras algún error o tienes alguna sugerencia, por favor abre un issue o envía un pull request.

