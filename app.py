# app.py
import streamlit as st
import pandas as pd
import unicodedata
from fpdf import FPDF
import json  # Importar json aquí
from utils import cargar_json, guardar_json  # Asegúrate de que utils.py exista

# ============
# Funciones Utilitarias
# ============

def limpiar_texto(text):
    """
    Normaliza el texto Unicode para mejorar la consistencia.
    Elimina caracteres de control y normaliza la forma de los caracteres.
    """
    if not text:
        return ""

    # Normalización NFKD para descomponer caracteres compuestos
    text = unicodedata.normalize("NFKD", text)

    # Eliminar caracteres de control
    text = ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C')

    return text.strip()

def generar_pdf(pregunta):
    """
    Genera un PDF con la información de la pregunta.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título
    titulo = "Pregunta Editada"
    pdf.cell(200, 10, txt=limpiar_texto(titulo), ln=True, align='C')
    pdf.ln(10)

    # Enunciado
    enunciado = limpiar_texto(pregunta.get("enunciado", "").strip() or "<Vacío>")
    pdf.multi_cell(0, 10, txt=f"Enunciado: {enunciado}")
    pdf.ln(5)

    # Opciones
    pdf.cell(0, 10, txt="Opciones:", ln=True)
    letras = "abcdefghijklmnopqrstuvwxyz"
    correct_answers = [limpiar_texto(r.strip()) for r in pregunta.get("respuesta_correcta", [])]
    if pregunta.get("opciones"):
        for idx, opc in enumerate(pregunta["opciones"]):
            opcion = limpiar_texto(opc)
            letra = letras[idx] if idx < len(letras) else f"{idx+1}"
            marker = " ✅" if opcion in correct_answers else ""
            pdf.multi_cell(0, 10, txt=f"{letra}) {opcion}{marker}")
    else:
        pdf.cell(0, 10, txt="- <Vacío>", ln=True)
    pdf.ln(5)

    # Concepto a Estudiar
    concepto = limpiar_texto(pregunta.get("concept_to_study", "").strip() or "<Vacío>")
    pdf.multi_cell(0, 10, txt=f"Concepto a Estudiar: {concepto}")
    pdf.ln(5)

    # Explicación OpenAI
    explicacion = limpiar_texto(pregunta.get("explicacion_openai", "").strip() or "<Vacío>")
    pdf.multi_cell(0, 10, txt=f"Explicación OpenAI: {explicacion}")

    # Generar los bytes del PDF (UTF-8)
    pdf_bytes = pdf.output(dest="S").encode("utf-8")
    return pdf_bytes

# ============
# Funciones de Carga/Guardado (en utils.py)
# ============

# utils.py (ejemplo)
# import json

# def cargar_json(filename="preguntas.json"):
#     try:
#         with open(filename, "r", encoding="utf-8") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return []  # Retorna una lista vacía si el archivo no existe
#     except json.JSONDecodeError:
#         st.error(f"Error: El archivo JSON '{filename}' está corrupto o no es válido.")
#         return []

# def guardar_json(data, filename="preguntas.json"):
#     try:
#         with open(filename, "w", encoding="utf-8") as f:
#             json.dump(data, f, ensure_ascii=False, indent=4)
#         st.success(f"Preguntas guardadas en '{filename}'") # feedback visual
#     except Exception as e:
#         st.error(f"Error al guardar el archivo JSON: {e}")

# ============
# Interfaz Streamlit
# ============

# Mostrar el logo de la empresa en la barra lateral
st.sidebar.image("assets/logo empresa.PNG", width=200)

# Cargar las preguntas desde el JSON
preguntas = cargar_json()

# Inicializar variables de sesión para el índice y el modo edición
if "indice" not in st.session_state:
    st.session_state.indice = 0
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# ============
# Barra lateral: Navegación e índice
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
            st.success("Cambios preparados. Descarga el PDF para guardar la pregunta.")
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
            st.success("Cambios aplicados. Presiona OK para preparar el PDF.")
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
# Botón para generar y descargar el PDF
# ============
pdf_bytes = generar_pdf(current_question)
st.download_button(
    label="Descargar PDF de la Pregunta",
    data=pdf_bytes,
    file_name=f"pregunta_{st.session_state.indice + 1}.pdf",
    mime="application/pdf"
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
    st.session_state.edit_mode = True  # Activar la edición de inmediato
    st.info("Nueva pregunta añadida. Edítala a continuación.")

# ============
# Botón para guardar todas las preguntas en el archivo JSON
# ============
if st.button("Guardar Todas las Preguntas"):
    guardar_json(preguntas)
