# app.py
import streamlit as st
from utils import cargar_json, guardar_json

# Cargar las preguntas desde el JSON
preguntas = cargar_json()

# Inicializar variables en la sesión para el índice actual y el modo edición
if "indice" not in st.session_state:
    st.session_state.indice = 0
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# Título de la aplicación
st.title("Revisión y Edición de Preguntas")

# Validar que existan preguntas en el archivo
if not preguntas:
    st.write("No se encontraron preguntas. Usa el botón 'Agregar Nueva Pregunta' para comenzar.")
    st.stop()

# Seleccionar la pregunta actual
current_question = preguntas[st.session_state.indice]

st.write(f"**Pregunta {st.session_state.indice + 1} de {len(preguntas)}**")

# Sección de botones de navegación y acciones
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Previo"):
        st.session_state.indice = max(0, st.session_state.indice - 1)
with col2:
    if st.button("Editar"):
        st.session_state.edit_mode = True
with col3:
    if st.button("OK") and st.session_state.edit_mode:
        # Validamos que el enunciado no esté vacío antes de guardar
        if current_question["enunciado"].strip() == "":
            st.error("El enunciado no puede estar vacío.")
        else:
            guardar_json(preguntas)
            st.success("¡Cambios guardados!")
            st.session_state.edit_mode = False
with col4:
    if st.button("Siguiente"):
        st.session_state.indice = min(len(preguntas) - 1, st.session_state.indice + 1)

# Muestra el formulario de edición o la visualización de la pregunta según el modo actual
if st.session_state.edit_mode:
    st.subheader("Modo Edición")
    # Entrada para editar el enunciado
    enunciado = st.text_input("Enunciado:", value=current_question["enunciado"])
    # Entrada para editar las opciones, separadas por saltos de línea
    opciones_text = st.text_area("Opciones (cada opción en una línea):", value="\n".join(current_question["opciones"]))
    
    # Botón para aplicar los cambios en memoria
    if st.button("Aplicar Cambios"):
        if enunciado.strip() == "":
            st.error("El enunciado no puede estar vacío.")
        else:
            current_question["enunciado"] = enunciado.strip()
            # Procesar las opciones, eliminando líneas en blanco
            opciones = [op.strip() for op in opciones_text.split("\n") if op.strip() != ""]
            if opciones:
                current_question["opciones"] = opciones
                # Actualizamos la pregunta en la lista
                preguntas[st.session_state.indice] = current_question
                st.success("Cambios aplicados. Presiona OK para guardar en el JSON.")
            else:
                st.error("Las opciones no pueden estar vacías.")
else:
    st.subheader("Vista de la Pregunta")
    st.write(f"**Enunciado:** {current_question['enunciado']}")
    st.write("**Opciones:**")
    for opcion in current_question["opciones"]:
        st.write(f"- {opcion}")

# Botón para agregar una nueva pregunta
if st.button("Agregar Nueva Pregunta"):
    nueva_pregunta = {
        "clasificacion": "",
        "grupo": 0,
        "tipo_pregunta": "multiple_choice",
        "enunciado": "",
        "image": "",
        "opciones": [],
        "respuesta_correcta": [],
        "concept_to_study": "",
        "explicacion_openai": "",
        "image_explanation": ""
    }
    preguntas.append(nueva_pregunta)
    st.session_state.indice = len(preguntas) - 1
    st.session_state.edit_mode = True  # Al agregar, activar de inmediato el modo edición
    guardar_json(preguntas)
    st.info("Nueva pregunta añadida. Edítala a continuación.")
