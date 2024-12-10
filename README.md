# AI JSON Collector

## ¿Qué es AI JSON Collector?

**AI JSON Collector** es una herramienta diseñada para procesar texto y generar archivos JSON utilizando modelos de razonamiento. Su propósito principal es simplificar la creación de datos estructurados a partir de entradas textuales, aumentando la productividad y reduciendo el tiempo necesario para tareas repetitivas.

Esta herramienta permite procesar texto directamente o ejecutar scripts Python personalizados para realizar consultas avanzadas.

---

## Características principales

1. **Procesamiento de texto o código Python personalizado:**
   - Puedes ingresar texto directamente para ser procesado por el modelo.
   - También puedes escribir y ejecutar código Python en tiempo real mediante el método `send_query(query)`.

2. **Sistema de log avanzado:**
   - Mantiene un registro claro del estado de cada subproceso con actualizaciones en tiempo real.
   - Los estados de los subprocesos se presentan en un árbol de procesos y se distinguen por colores:
     - **Azul:** En progreso.
     - **Verde:** Completado.
     - **Rojo:** Error.

3. **Procesamiento paralelo:**
   - Permite ejecutar múltiples consultas de manera simultánea sin interrumpir la experiencia del usuario.

4. **Gestión automática de archivos:**
   - Los archivos JSON generados se guardan automáticamente en la carpeta `docs` con nombres derivados del contenido.

---

## ¿Cómo puedo ejecutar este proyecto por mi cuenta?

### Requisitos previos

Asegúrate de tener instalado **Python** (preferiblemente la última versión) y las siguientes bibliotecas:

- `datetime`
- `dateutil`
- `PyQt5`
- `gradio_client`

Puedes instalar estas bibliotecas ejecutando el siguiente comando en tu terminal:

```sh
pip install datetime python-dateutil PyQt5 gradio_client
```

---

## Configuración inicial
### Preparar el archivo de prompt (preprompt.txt):

1. **Antes de ejecutar el programa, configura el archivo preprompt.txt con las instrucciones que el modelo seguirá para procesar las consultas. Este archivo puede contener una estructura básica de JSON o cualquier texto que proporcione contexto al modelo.**

Ejemplo de contenido de preprompt.txt:
```json
{
    "fecha": "YYYYMMDD", // Formato de fecha: AñoMesDía, Ejemplo: 20240812
    "nombre": "string", // Nombre del usuario, Ejemplo: "Juan Pérez"
    "edad": , // Edad del usuario, Ejemplo: 22
}
No incluyas comentarios en la respuesta final.

```

2. **Estructura del proyecto:**

Asegúrate de mantener la siguiente estructura de carpetas y archivos en tu proyecto:
```bash
AI-JSON-Collector/
├── docs/               # Carpeta donde se guardan los archivos JSON generados
├── preprompt.txt       # Archivo de configuración del prompt
├── main.py             # Archivo principal del programa
└── README.md           # Este archivo
```

---

## Ejecución del proyecto
### Sigue estos pasos para usar la herramienta:

1. **Inicia el programa:** Ejecuta el archivo principal del proyecto en tu terminal:

```sh
python main.py
```
2. **Interacción con la interfaz gráfica:** La aplicación tiene un único botón para enviar consultas. Dependiendo de si estás en el Modo Texto o el Modo Código, el botón tendrá el siguiente comportamiento:

 - **Modo Texto:** Procesa el texto ingresado en el cuadro principal mediante el modelo y genera un archivo JSON automáticamente.
 - **Modo Código:** Ejecuta el código Python escrito en el cuadro de entrada. Este código puede incluir llamadas al método send_query(query) para enviar consultas personalizadas al modelo.

3. **Visualiza los procesos en tiempo real:** Consulta el árbol de procesos en la interfaz para ver el estado de cada tarea. Los colores indican el progreso:

	- **Azul:** El proceso está en curso.
	- **Verde:** El proceso ha sido completado con éxito.
	- **Rojo:** Ocurrió un error.

---

## Ejemplo de uso del modo código

En el modo código, puedes escribir un script como el siguiente para realizar consultas personalizadas:

```python
import random
"""
Envía una consulta personalizada al modelo, y llamamos al metodo send_query() con el texto inicial, que se completa con
el texto en el archivo preprompt.txt y se crea un subproceso donde se envia la solicitud al modelo de lenguaje natural 
para procesar.
"""
for i in range(0,int(random.random())*100) 
	send_query(query=f"Inventate los datos de la persona para rellenar el json, y de nombre del archivo usa \"nombre\"")
```

Esto ejecutará la consulta y mostrará el progreso en el sistema de log en tiempo real.

---

## Contribuciones
¡Las contribuciones son bienvenidas! Si encuentras algún error o tienes ideas para nuevas funcionalidades, no dudes en:

1. Abrir un issue en el repositorio del proyecto.
2. Crear un pull request con tu mejora o corrección.
3. Compartir tu experiencia o sugerencias para ayudar a mejorar esta herramienta.

---

## Créditos
**AI JSON Collector** fue desarrollado como una herramienta para facilitar y acelerar el manejo de archivos JSON, con especial énfasis en la simplicidad y la eficiencia.

¡Gracias por usar AI JSON Collector! 🎉