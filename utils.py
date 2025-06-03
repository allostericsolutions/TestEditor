import json

# Ruta del archivo JSON donde se almacenan las preguntas.
FILE_PATH = "data/preguntas.json"

def cargar_json():
    """
    Carga el archivo JSON y retorna la lista de preguntas.
    Si el archivo no existe o hay un error, se debería manejar la excepción en producción.
    """
    with open(FILE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

def guardar_json(data):
    """
    Guarda la lista de preguntas en el archivo JSON.
    
    Args:
        data (list): Lista de diccionarios con la información de las preguntas.
    """
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
