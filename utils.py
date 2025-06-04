import json
import streamlit as st
import os  # Importa la librería os

# Ruta del archivo JSON donde se almacenan las preguntas.
FILE_PATH = "data/preguntas.json"

def cargar_json():
    """
    Carga el archivo JSON y retorna la lista de preguntas.
    Si el archivo no existe o hay un error, se maneja la excepción y se muestra un mensaje en Streamlit.
    """
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        st.warning(f"Archivo '{FILE_PATH}' no encontrado. Se creará uno nuevo al guardar.")
        return []  # Retorna una lista vacía si el archivo no existe
    except json.JSONDecodeError:
        st.error(f"Error: El archivo JSON '{FILE_PATH}' está corrupto o no es válido.")
        return []
    except Exception as e:
        st.error(f"Error inesperado al cargar el archivo JSON: {e}")
        return []

def guardar_json(data):
    """
    Guarda la lista de preguntas en el archivo JSON.
    Crea el directorio si no existe.

    Args:
        data (list): Lista de diccionarios con la información de las preguntas.
    """
    try:
        # Crea el directorio si no existe
        os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
        with open(FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        st.success(f"Preguntas guardadas en '{FILE_PATH}'")  # Feedback visual
    except Exception as e:
        st.error(f"Error al guardar el archivo JSON: {e}")
