# app.py
import streamlit as st
import pandas as pd
import unicodedata
import json
from utils import cargar_json, generar_txt, limpiar_texto
import time
import os

# ============
# Autenticación
# ============
USUARIOS = {
    "marievapaula@gmail.com": "vascular33",
    "ciclosporina2@hotmail.com": "vascular33",
}

def check_password():
    def password_entered():
        if (
            st.session_state["username"] in USUARIOS
            and st.session_state["password"]
            == USUARIOS[st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.image("assets/logo empresa.PNG", width=200)
        with st.form("login"):
            st.text_input("Correo", key="username")
            st.text_input("Contraseña", type="password", key="password")
            st.form_submit_button("Ingresar", on_click=password_entered)
        if st.session_state["password_correct"]:
            st.experimental_rerun()
        return False
    else:
        return True

# ============
# Interfaz Streamlit
# ============
if not check_password():
    st.stop()

# Sidebar
st.sidebar.image("assets/logo empresa.PNG", width=200)
st.sidebar.markdown("<p style='font-size: 12px;'>Revisión y Edición de Preguntas proyecto RVT</p>", unsafe_allow_html=True)

# Recuperación del borrador
def cargar_borrador(filepath="data/borrador_preguntas.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            # Leer el contenido del archivo
            contenido = f.read()

            # Dividir el contenido en preguntas
            preguntas = contenido.split("==== Pregunta ")[1:]

            # Procesar cada pregunta
            nuevas_preguntas = []
            for pregunta in preguntas:
                # Dividir la pregunta en líneas
                lineas = pregunta.split("\n")

                # Extraer el Enunciado
                enunciado = lineas[2].split(": ")[1]

                # Extraer las Opciones
                opciones = []
                respuesta_correcta = []
                for linea in lineas[4:8]:
                    if linea.startswith(("a) ", "b) ", "c) ", "d) ")):
                        opcion = linea[3:].split(" ✅")[0]
                        opciones.append(opcion)
                        if "✅" in linea:
                            respuesta_correcta.append(opcion)

                # Extraer Concepto, Explicación OpenAI e Imagen
                concepto = lineas[9].split(": ")[1]
                explicacion_openai = lineas[10].split(": ")[1]
                image_explanation = lineas[11].split(": ")[1]

                # Crear el diccionario de la pregunta
                nueva_pregunta = {
                    "clasificacion": "",
                    "enunciado": enunciado,
                    "opciones": opciones,
                    "respuesta_correcta": respuesta_correcta,
                    "concept_to_study": concepto,
                    "explicacion_openai": explicacion_openai,
                    "image_explanation": image_explanation,
                }
                nuevas_preguntas.append(nueva_pregunta)
            return nuevas_preguntas
    except FileNotFoundError:
        st.warning("No se encontró el archivo borrador.")
        return []
    except Exception as e:
        st.error(f"Error al cargar el borrador: {e}")
        return []

if st.sidebar.button("Cargar Borrador"):
    st.session_state.nuevas_preguntas = cargar_borrador()
    st.experimental_rerun()

# Cargar las preguntas desde el JSON (SOLO UNA VEZ al inicio)
if "preguntas" not in st.session_state:
    st.session_state.preguntas = cargar_json()

preguntas = st.session_state.preguntas

# Inicializar variables de sesión
if "indice" not in st.session_state:
    st.session_state.indice = 0
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "preguntas_editadas" not in st.session_state:
    st.session_state.preguntas_editadas = set()
if "nuevas_preguntas" not in st.session_state:
    st.session_state.nuevas_preguntas = []

st.sidebar.subheader("Navegación de Preguntas")

# Lista de Clasificación
lista_clasificaciones = [
    "1 Normal Anatomy, Perfusion, and Function",
    "2 Pathology, Perfusion, and Function",
    "3 Surgically Altered Anatomy and Pathology",
    "4 Physiologic Exams",
    "5 Ultrasound-guided Procedures/Intraoperative Assessment",
    "6 Quality Assurance, Safety, and Physical Principles",
    "7 Preparation, Documentation, and Communication"
]

# Crear la lista de opciones para el selectbox con un indicador para las preguntas editadas
lista_indices = []
for i, pregunta in enumerate(preguntas):
    num = i + 1
    enunciado = pregunta.get("enunciado", "").strip() or "<Vacío>"
    if i in st.session_state.preguntas_editadas:
        lista_indices.append(f"{num}: {enunciado} (Editada)")
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
# Pestañas Principales
# ============
tab1, tab2, tab3 = st.tabs(["Revisión y Edición de Preguntas", "Creación de Preguntas", "ARDMS Content Outline"])

with tab1:
    st.title("Revisión y Edición de Preguntas")
    st.write(f"**Pregunta {st.session_state.indice + 1} de {len(preguntas)}**")
    current_question = preguntas[st.session_state.indice]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Previo"):
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
                st.session_state.preguntas[st.session_state.indice] = current_question
                st.success("Cambios preparados. Descarga el TXT para guardar la pregunta.")
            st.session_state.edit_mode = False
    with col4:
        if st.button("Siguiente"):
            st.session_state.preguntas[st.session_state.indice] = current_question
            st.session_state.indice = min(len(preguntas) - 1, st.session_state.indice + 1)

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
                explicacion = explicacion.strip()
                preguntas[st.session_state.indice] = current_question

                st.success("Cambios aplicados (solo en memoria).")
                st.session_state.edit_mode = False
                st.session_state.preguntas[st.session_state.indice] = current_question
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

    txt_bytes = generar_txt(preguntas)
    st.download_button(
        label="Descarga documento de la Preguntas editadas",
        data=txt_bytes,
        file_name=f"preguntas.txt",
        mime="text/plain"
    )

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

with tab2:
    # Formulario de Creación de Preguntas
    with st.form("nueva_pregunta_form", clear_on_submit=False):
        clasificacion = st.selectbox("Clasificación", lista_clasificaciones)
        enunciado = st.text_input("Enunciado")

        opcion1_col, correct1_col = st.columns([3, 1])
        with opcion1_col:
            opcion1 = st.text_input("Opción 1")
        with correct1_col:
            respuesta_correcta1 = st.checkbox("Correcta", key="rc1")

        opcion2_col, correct2_col = st.columns([3, 1])
        with opcion2_col:
            opcion2 = st.text_input("Opción 2")
        with correct2_col:
            respuesta_correcta2 = st.checkbox("Correcta", key="rc2")

        opcion3_col, correct3_col = st.columns([3, 1])
        with opcion3_col:
            opcion3 = st.text_input("Opción 3")
        with correct3_col:
            respuesta_correcta3 = st.checkbox("Correcta", key="rc3")

        opcion4_col, correct4_col = st.columns([3, 1])
        with opcion4_col:
            opcion4 = st.text_input("Opción 4")
        with correct4_col:
            respuesta_correcta4 = st.checkbox("Correcta", key="rc4")

        concepto = st.text_input("Concepto a Estudiar")
        explicacion_openai = st.text_area("Explicación OpenAI")
        image_explanation = st.text_input("Explicación de la Imagen (URL)")

        submitted = st.form_submit_button("Guardar Pregunta")

        if submitted:
            nueva_pregunta = {
                "clasificacion": clasificacion,
                "enunciado": enunciado,
                "opciones": [opcion1, opcion2, opcion3, opcion4],
                "respuesta_correcta": [
                    opcion1 if respuesta_correcta1 else None,
                    opcion2 if respuesta_correcta2 else None,
                    opcion3 if respuesta_correcta3 else None,
                    opcion4 if respuesta_correcta4 else None,
                ],
                "concept_to_study": concepto,
                "explicacion_openai": explicacion_openai,
                "image_explanation": image_explanation,
            }
            nueva_pregunta["respuesta_correcta"] = [opc for opc in nueva_pregunta["respuesta_correcta"] if opc is not None]
            st.session_state.nuevas_preguntas.append(nueva_pregunta)
            st.success("Pregunta guardada!")

    # Vista previa de las preguntas creadas
    st.subheader("Preguntas Creadas")
    for i, pregunta in enumerate(st.session_state.nuevas_preguntas):
        with st.expander(f"Pregunta {i+1}: {pregunta['enunciado'][:50] + '...' if len(pregunta['enunciado']) > 50 else pregunta['enunciado']}"):

            col1, col2 = st.columns([1,10])
            with col1:
                if st.button("Editar", key=f"editar_{i}"):
                    pass
            with col2:
                if st.button("Eliminar", key=f"eliminar_{i}"):
                    del st.session_state.nuevas_preguntas[i]
                    st.experimental_rerun()

            # Vista previa de la pregunta
            st.write(f"**Clasificación:** {pregunta['clasificacion'].split(' ', 1)[1] if ' ' in pregunta['clasificacion'] else pregunta['clasificacion']}")
            st.write(f"**Enunciado:** {pregunta['enunciado']}")
            st.write("**Opciones:**")
            for i, opcion in enumerate(pregunta['opciones']):
                marker = "✅ " if opcion in pregunta['respuesta_correcta'] else ""
                st.write(f"  {i+1}) {opcion} {marker}")
            st.write(f"**Concepto a Estudiar:** {pregunta['concept_to_study']}")
            st.write(f"**Explicación OpenAI:** {pregunta['explicacion_openai']}")
            st.write(f"**Explicación de la Imagen:** {pregunta['image_explanation']}")

    def generar_txt_nuevas_preguntas(preguntas):
        texto = ""
        for i, pregunta in enumerate(preguntas):
            texto += f"==== Pregunta {i+1} ====\n"
            titulo = "Pregunta Nueva\n"
            texto += titulo
            clasificacion = pregunta.get("clasificacion", "")
            texto += f"Clasificación: {clasificacion.split(' ', 1)[1] if ' ' in clasificacion else clasificacion}\n"
            enunciado = pregunta.get("enunciado", "").strip() or "<Vacío>"
            texto += f"Enunciado: {enunciado}\n"
            texto += "Opciones:\n"
            letras = "abcdefghijklmnopqrstuvwxyz"
            correct_answers = [op.strip() for op in pregunta.get("respuesta_correcta", [])]
            if pregunta.get("opciones"):
                for idx, opc in enumerate(pregunta["opciones"]):
                    opcion = opc
                    letra = letras[idx] if idx < len(letras) else f"{idx+1}"
                    marker = " ✅" if opcion in correct_answers else ""
                    texto += f"{letra}) {opcion}{marker}\n"
            else:
                texto += "- <Vacío>\n"
            concepto = pregunta.get("concept_to_study", "").strip() or "<Vacío>"
            texto += f"Concepto a Estudiar: {concepto}\n"
            explicacion = pregunta.get("explicacion_openai", "").strip() or "<Vacío>"
            texto += f"Explicación OpenAI: {explicacion}\n"
            explicacion_imagen = pregunta.get("image_explanation", "").strip() or "<Vacío>"
            texto += f"Explicación de la Imagen: {explicacion_imagen}\n"
            texto += "\n"
        return texto.encode('utf-8')

    if st.session_state.nuevas_preguntas:
        txt_bytes = generar_txt_nuevas_preguntas(st.session_state.nuevas_preguntas)
        st.download_button(
            label="Descargar TXT de Preguntas Creadas",
            data=txt_bytes,
            file_name="nuevas_preguntas.txt",
            mime="text/plain",
        )

    def guardar_borrador(preguntas, filepath="data/borrador_preguntas.txt"):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for i, pregunta in enumerate(preguntas):
                    f.write(f"==== Pregunta {i+1} ====\n")
                    titulo = "Pregunta Nueva\n"
                    f.write(titulo)
                    clasificacion = pregunta.get("clasificacion", "")
                    f.write(f"Clasificación: {clasificacion}\n")
                    enunciado = pregunta.get("enunciado", "").strip() or "<Vacío>"
                    f.write(f"Enunciado: {enunciado}\n")
                    texto += "Opciones:\n"
                    letras = "abcdefghijklmnopqrstuvwxyz"
                    correct_answers = [op.strip() for op in pregunta.get("respuesta_correcta", [])]
                    if pregunta.get("opciones"):
                        for idx, opc in enumerate(pregunta["opciones"]):
                            opcion = opc
                            letra = letras[idx] if idx < len(letras) else f"{idx+1}"
                            marker = " ✅" if opcion in correct_answers else ""
                            f.write(f"{letra}) {opcion}{marker}\n")
                    else:
                        f.write("- <Vacío>\n")
                    concepto = pregunta.get("concept_to_study", "").strip() or "<Vacío>"
                    f.write(f"Concepto a Estudiar: {concepto}\n")
                    explicacion = pregunta.get("explicacion_openai", "").strip() or "<Vacío>"
                    explicacion_imagen = pregunta.get("image_explanation", "").strip() or "<Vacío>"
                    f.write(f"Explicación de la Imagen: {explicacion_imagen}\n")
                    f.write("\n")
        except Exception as e:
            st.error(f"Error al guardar el borrador: {e}")

    # Inicializar la variable de sesión para el último guardado
    if "ultimo_guardado" not in st.session_state:
        st.session_state.ultimo_guardado = time.time()

    # Guardar el borrador automáticamente cada 120 segundos (2 minutos)
    if time.time() - st.session_state.ultimo_guardado > 120:
        guardar_borrador(st.session_state.nuevas_preguntas)
        st.session_state.ultimo_guardado = time.time()
    st.info("Borrador guardado automaticamente.")

with tab3:
    st.header("ARDMS Content Outline")
    st.markdown("[Vascular Technology Content Outline](https://ardms.org/wp-content/uploads/pdf/Vascular-Technology-Content-Outline.pdf)")
