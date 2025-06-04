# app.py
import streamlit as st
import pandas as pd
from utils import cargar_json, guardar_json

# Cargar las preguntas desde el JSON
preguntas = cargar_json()

# Inicializar variables en sesión para llevar el control del índice y el modo edición
if "indice" not in st.session_state:
    st.session_state.indice = 0
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# ============
# Bar lateral: Navegación y listado de índices
# ============
st.sidebar.subheader("Navegación de Preguntas")
# Muestra un selectbox con todos los índices numerados (1,2,3,...)
lista_indices = list(range(1, len(preguntas) + 1))
selected_index = st.sidebar.selectbox("Selecciona la pregunta:", lista_indices, index=st.session_state.indice)
# Actualizar el índice en la sesión según la selección
st.session_state.indice = selected_index - 1

# Mostrar un resumen de todas las preguntas, incluso si el enunciado está vacío
if st.sidebar.checkbox("Mostrar índice general", value=True):
    resumen = []
    for i, pregunta in enumerate(preguntas):
        num = i + 1
        # Si el enunciado está vacío (o es solo espacios), mostramos "<Vacío>"
        enunciado = pregunta.get("enunciado", "").strip() or "<Vacío>"
        resumen.append({"Número": num, "Enunciado": enunciado})
    df_resumen = pd.DataFrame(resumen)
    st.sidebar.write(df_resumen)

# ============
# Página Principal
# ============
st.title("Revisión y Edición de Preguntas")
st.write(f"**Pregunta {st.session_state.indice + 1} de {len(preguntas)}**")

# Obtener la pregunta actual según el índice
current_question = preguntas[st.session_state.indice]

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
        # Validar que el enunciado (campo obligatorio) no esté vacío
        if current_question["enunciado"].strip() == "":
            st.error("El enunciado no puede estar vacío.")
        else:
            guardar_json(preguntas)
            st.success("¡Cambios guardados!")
            st.session_state.edit_mode = False
with col4:
    if st.button("Siguiente"):
        st.session_state.indice = min(len(preguntas) - 1, st.session_state.indice + 1)

# ============
# Área de Visualización / Edición
# ============
if st.session_state.edit_mode:
    st.subheader("Modo Edición")
    # Formulario de edición para el enunciado y las opciones
    enunciado = st.text_input("Enunciado:", value=current_question["enunciado"])
    opciones_text = st.text_area("Opciones (una por línea):", value="\n".join(current_question["opciones"]))
    
    if st.button("Aplicar Cambios"):
        if enunciado.strip() == "":
            st.error("El enunciado no puede estar vacío.")
        else:
            current_question["enunciado"] = enunciado.strip()
            # Procesar la lista de opciones eliminando líneas vacías
            opciones = [op.strip() for op in opciones_text.split("\n") if op.strip() != ""]
            if opciones:
                current_question["opciones"] = opciones
                preguntas[st.session_state.indice] = current_question
                st.success("Cambios aplicados. Presiona OK para guardar en el JSON.")
            else:
                st.error("Las opciones no pueden estar vacías.")
else:
    st.subheader("Vista de la Pregunta")
    # Mostrar el enunciado; si está vacío se indica "<Vacío>"
    enunciado = current_question["enunciado"].strip() or "<Vacío>"
    st.write(f"**Enunciado:** {enunciado}")
    
    st.write("**Opciones:**")
    if current_question["opciones"]:
        for opcion in current_question["opciones"]:
            st.write(f"- {opcion}")
    else:
        st.write("- <Vacío>")

# ============
# Botón para agregar una nueva pregunta
# ============
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
    st.session_state.edit_mode = True  # Activar la edición de inmediato
    guardar_json(preguntas)
    st.info("Nueva pregunta añadida. Edítala a continuación.")
