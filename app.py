# app.py
import streamlit as st
import pandas as pd
from utils import cargar_json, guardar_json

# Cargar las preguntas desde el JSON
preguntas = cargar_json()

# Inicializar variables de sesión para el índice y el modo edición
if "indice" not in st.session_state:
    st.session_state.indice = 0
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# ============
# Barra lateral: Navegación y listado de índices
# ============
st.sidebar.subheader("Navegación de Preguntas")
lista_indices = list(range(1, len(preguntas) + 1))
selected_index = st.sidebar.selectbox("Selecciona la pregunta:", lista_indices, index=st.session_state.indice)
st.session_state.indice = selected_index - 1

if st.sidebar.checkbox("Mostrar índice general", value=True):
    resumen = []
    for i, pregunta in enumerate(preguntas):
        num = i + 1
        enunciado = pregunta.get("enunciado", "").strip() or "<Vacío>"
        resumen.append({"Número": num, "Enunciado": enunciado})
    df_resumen = pd.DataFrame(resumen)
    st.sidebar.write(df_resumen)

# ============
# Página Principal
# ============
st.title("Revisión y Edición de Preguntas")
st.write(f"**Pregunta {st.session_state.indice + 1} de {len(preguntas)}**")
current_question = preguntas[st.session_state.indice]

# Botones de navegación y acciones
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Previo"):
        st.session_state.indice = max(0, st.session_state.indice - 1)
with col2:
    if st.button("Editar"):
        st.session_state.edit_mode = True
with col3:
    if st.button("OK") and st.session_state.edit_mode:
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
# Área de Visualización / Edición de la Pregunta
# ============
if st.session_state.edit_mode:
    st.subheader("Modo Edición")
    enunciado = st.text_input("Enunciado:", value=current_question["enunciado"])
    opciones_text = st.text_area("Opciones (una por línea):", value="\n".join(current_question["opciones"]))
    concepto = st.text_input("Concepto a Estudiar:", value=current_question.get("concept_to_study", ""))
    explicacion = st.text_area("Explicación OpenAI:", value=current_question.get("explicacion_openai", ""))
    
    if st.button("Aplicar Cambios"):
        if enunciado.strip() == "":
            st.error("El enunciado no puede estar vacío.")
        else:
            current_question["enunciado"] = enunciado.strip()
            opciones = [op.strip() for op in opciones_text.split("\n") if op.strip() != ""]
            if opciones:
                current_question["opciones"] = opciones
            else:
                st.error("Las opciones no pueden estar vacías.")
            current_question["concept_to_study"] = concepto.strip()
            current_question["explicacion_openai"] = explicacion.strip()
            preguntas[st.session_state.indice] = current_question
            st.success("Cambios aplicados. Presiona OK para guardar en el JSON.")
else:
    st.subheader("Vista de la Pregunta")
    enunciado_display = current_question["enunciado"].strip() or "<Vacío>"
    st.write(f"**Enunciado:** {enunciado_display}")
    
    st.write("**Opciones:**")
    if current_question["opciones"]:
        letras = "abcdefghijklmnopqrstuvwxyz"
        # Vamos a obtener la lista de respuestas correctas (se asume que es una lista de strings)
        correct_answers = [resp.strip() for resp in current_question.get("respuesta_correcta", [])]
        for idx, opcion in enumerate(current_question["opciones"]):
            letra = letras[idx] if idx < len(letras) else f"{idx+1}"
            # Se compara la opción actual con las respuestas correctas de forma sensible a espacios
            marker = " ✅" if opcion.strip() in correct_answers else ""
            st.write(f"{letra}) {opcion}{marker}")
    else:
        st.write("- <Vacío>")
    
    # Mostrar campos adicionales
    concepto_display = current_question.get("concept_to_study", "").strip() or "<Vacío>"
    explicacion_display = current_question.get("explicacion_openai", "").strip() or "<Vacío>"
    st.write("**Concepto a Estudiar:**")
    st.write(concepto_display)
    st.write("**Explicación OpenAI:**")
    st.write(explicacion_display)

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
