# utils.py
import json
import streamlit as st
import os
import unicodedata

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

def limpiar_texto(text):
    """
    Normaliza el texto y elimina los caracteres que no se puedan codificar en Latin-1.
    """
    if not text:
        return ""
    # Normaliza el texto (NFKD) y elimina los caracteres que no sean codificables en Latin-1.
    return unicodedata.normalize("NFKD", text).encode("latin1", errors="ignore").decode("latin1")

def generar_txt(preguntas):  # Recibe la lista de preguntas completa
    """
    Genera un archivo de texto con la información de todas las preguntas.
    """
    texto = ""
    for i, pregunta in enumerate(preguntas):
        texto += f"==== Pregunta {i+1} ====\n"

        # Título
        titulo = "Pregunta Editada\n"
        texto += titulo

        # Enunciado
        enunciado = limpiar_texto(pregunta.get("enunciado", "").strip() or "<Vacío>")
        texto += f"Enunciado: {enunciado}\n"

        # Opciones
        texto += "Opciones:\n"
        letras = "abcdefghijklmnopqrstuvwxyz"
        # Se limpian las respuestas correctas para compararlas de forma segura
        correct_answers = [limpiar_texto(r.strip()) for r in pregunta.get("respuesta_correcta", [])]
        if pregunta.get("opciones"):
            for idx, opc in enumerate(pregunta["opciones"]):
                opcion = limpiar_texto(opc)
                letra = letras[idx] if idx < len(letras) else f"{idx+1}"
                marker = " ✅" if opcion in correct_answers else ""
                texto += f"{letra}) {opcion}{marker}\n"
        else:
            texto += "- <Vacío>\n"

        # Concepto a Estudiar
        concepto = limpiar_texto(pregunta.get("concept_to_study", "").strip() or "<Vacío>")
        texto += f"Concepto a Estudiar: {concepto}\n"

        # Explicación OpenAI
        explicacion = limpiar_texto(pregunta.get("explicacion_openai", "").strip() or "<Vacío>")
        texto += f"Explicación OpenAI: {explicacion}\n"
        texto += "\n"  # Separador entre preguntas

    return texto.encode('utf-8')  # Codificar a UTF-8 para manejar Unicode
