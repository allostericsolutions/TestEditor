# app.py
import streamlit as st
import pandas as pd
import unicodedata
import json
from utils import cargar_json, generar_txt

# ============
# Autenticación
# ============
# ... (código de autenticación) ...

# ============
# Interfaz Streamlit
# ============

if not check_password():
    st.stop()  # No ejecutar el resto de la app si la contraseña es incorrecta

# Mostrar el logo de la empresa en la barra lateral
st.sidebar.image("assets/logo empresa.PNG", width=200)

# Cargar las preguntas desde el JSON (SOLO UNA VEZ al inicio)
if "preguntas" not in st.session_state:
    st.session_state.preguntas = cargar_json()

preguntas = st.session_state.preguntas  # Usar la lista del estado de sesión

# Inicializar variables de sesión para el índice, el modo edición y el conjunto de preguntas editadas
if "indice" not in st.session_state:
    st.session_state.indice = 0
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "preguntas_editadas" not in st.session_state:
    st.session_state.preguntas_editadas = set()  # Conjunto para rastrear las preguntas editadas

# ============
# Barra lateral: Navegación e índice
# ============
st.sidebar.subheader("Navegación de Preguntas")

# Crear la lista de opciones para el selectbox con un indicador para las preguntas editadas
lista_indices = []
for i, pregunta in enumerate(preguntas):
    num = i + 1
    enunciado = pregunta.get("enunciado", "").strip() or "<Vacío>"
    if i in st.session_state.preguntas_editadas:
        lista_indices.append(f"{num}: {enunciado} (Editada)")  # Indicador visual
    else:
        lista_indices.append(f"{num}: {enunciado}")

selected_index_str = st.sidebar.selectbox("Selecciona la pregunta:", lista_indices, index=st.session_state.indice)
st.session_state.indice = int(selected_index_str.split(":")[0]) - 1

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
        # Guardar la pregunta actual en el estado de la sesión ANTES de cambiar el índice
        st.session_state.preguntas[st.session_state.indice] = current_question
        st.session_state.indice = max(0, st.session_state.indice - 1)
with col2:
    if st.button("Editar"):
        st.session_state.edit_mode = True
with col3:
    if st.button("OK") and st.session_state.edit_mode:
        if current_question["enunciado"].strip() == "":
            st.error("El enunciado no puede estar vacío.")
        else:
            # Guardar la pregunta actual en el estado de la sesión ANTES de salir del modo edición
            st.session_state.preguntas[st.session_state.indice] = current_question
            st.success("Cambios preparados. Descarga el TXT para guardar la pregunta.")
        st.session_state.edit_mode = False
with col4:
    if st.button("Siguiente"):
        # Guardar la pregunta actual en el estado de la sesión ANTES de cambiar el índice
        st.session_state.preguntas[st.session_state.indice] = current_question
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

            st.success("Cambios aplicados (solo en memoria).")
            st.session_state.edit_mode = False
            # Guardar la pregunta actual en el estado de la sesión DESPUÉS de aplicar los cambios
            st.session_state.preguntas[st.session_state.indice] = current_question
            # Agregar el índice de la pregunta al conjunto de preguntas editadas
            st.session_state.preguntas_editadas.add(st.session_state.indice)

else:
    st.subheader("Vista de la Pregunta")
    enunciado_display = current_question["enunciado"].strip() or "<Vacío>"
    st.write(f"**Enunciado:** {enunciado_display}")

    st.write("**Opciones:**")
    if current_question["opciones"]:
        letras = "abcdefghijklmnopqrstuvwxyz"
        correct_answers = [op.strip() for op in current_question.get("respuesta_correcta", [])]
        for idx, opcion in enumerate(current_question["opciones"]):
            letra = letras[idx] if idx < len(letras) else f"{idx+1}"
            marker = " ✅" if opcion.strip() in correct_answers else ""
            st.write(f"{letra}) {opcion}{marker}")
    else:
        st.write("- <Vacío>")

    concepto_display = current_question.get("concept_to_study", "").strip() or "<Vacío>"
    explicacion_display = current_question.get("explicacion_openai", "").strip() or "<Vacío>"
    st.write("**Concepto a Estudiar:**")
    st.write(concepto_display)
    st.write("**Explicación OpenAI:**")
    st.write(explicacion_display)

# ============
# Botón para generar y descargar el TXT
# ============
txt_bytes = generar_txt(preguntas)
st.download_button(
    label="Descarga documento de la Preguntas editadas",
    data=txt_bytes,
    file_name=f"preguntas.txt",
    mime="text/plain"
)

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
    st.session_state.edit_mode = True
    st.info("Nueva pregunta añadida. Edítala a continuación.")
