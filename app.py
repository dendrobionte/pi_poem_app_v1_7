import streamlit as st
import re
from collections import OrderedDict

st.set_page_config(page_title="Poética visual de π – Versión 1_6", layout="wide")

# --- ESTILO VISUAL PERSONALIZADO ---
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: 'Georgia', serif;
        background-color: #f4f1ec;
        color: #2f2f2f;
    }
    .tanka-block {
        padding: 1.2em;
        margin-bottom: 1.5em;
        border-top: 2px dotted #bfae9c;
        border-bottom: 2px dotted #bfae9c;
        text-align: center;
        font-size: 1.1em;
        line-height: 1.6em;
    }
    .symbol {
        font-size: 1.3em;
        color: #a07d52;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌀 Poética visual de π – Versión 1_6")
st.markdown("Explora cómo el número π transforma un texto en Tankas numerados con estilo, y visualiza su flujo generativo en tiempo real.")

# --- FUNCIONES ---
def limpiar_texto(texto):
    palabras = re.findall(r"\b[a-záéíóúüñ]+\b", texto.lower())
    return list(OrderedDict.fromkeys(palabras))

@st.cache_data
def cargar_decimales_pi():
    with open("pi_decimals.txt", "r") as f:
        return f.read().strip().replace("\n", "")

def to_roman(n):
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman = ''
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman += syms[i]
            n -= val[i]
        i += 1
    return roman

def generar_versos(palabras, longitud=7):
    return [palabras[i:i+longitud] for i in range(0, len(palabras), longitud) if len(palabras[i:i+longitud]) == longitud]

def transformar_en_tanka(verso, i):
    if len(verso) != 7:
        return None
    numero = to_roman(i)
    return f"<div class='tanka-block'><div class='symbol'>{numero}</div>{verso[0]}<br>{verso[1]} {verso[2]}<br>{verso[3]}<br>{verso[4]} {verso[5]}<br>{verso[6]}</div>"

# --- INTERFAZ PRINCIPAL ---
archivo = st.file_uploader("📄 Sube un archivo .txt", type="txt")

if archivo:
    texto = archivo.read().decode("utf-8")
    palabras = limpiar_texto(texto)
    total = len(palabras)
    st.success(f"✔️ Texto cargado con {total} palabras únicas.")

    pi = cargar_decimales_pi()

    st.sidebar.header("🔧 Parámetros de generación")
    modo = st.sidebar.selectbox("Modo de lectura de π", ["Directo", "Inverso", "Espaciado", "Modular"])
    tam_bloque = st.sidebar.selectbox("Tamaño del bloque (cifras)", [3, 4, 5], index=1)
    inicio = st.sidebar.slider("Punto de inicio", 0, 10000, 0)
    salto = st.sidebar.slider("Salto entre bloques (solo para 'Espaciado')", 1, 20, 1)

    if modo == "Inverso":
        pi_transformado = pi[::-1]
    elif modo == "Espaciado":
        pi_transformado = ''.join(pi[i] for i in range(inicio, len(pi), salto))
    else:
        pi_transformado = pi

    usados = set()
    resultado = []
    registros = []
    i = inicio if modo != "Espaciado" else 0

    while len(usados) < total and i + tam_bloque <= len(pi_transformado):
        bloque = int(pi_transformado[i:i+tam_bloque])
        if modo == "Modular":
            idx = bloque % total
        else:
            idx = bloque - 1

        if 0 <= idx < total and idx not in usados:
            palabra = palabras[idx]
            resultado.append(palabra)
            usados.add(idx)
            registros.append((i, pi_transformado[i:i+tam_bloque], idx + 1, palabra))
        i += tam_bloque

    # --- RESUMEN DE FLUJO DE π EN SIDEBAR ---
    st.sidebar.markdown("### 📊 Flujo de lectura de π")
    if registros:
        vista = registros[:5]
        resumen = "\n".join([f"{b} → {p}" for (_, b, _, p) in vista])
        st.sidebar.text(resumen)

    # --- POEMA Y TANKAS ---
    poema = " ".join(resultado)
    st.markdown("### ✨ Poema generado")
    st.text_area("Texto:", poema, height=200)
    st.download_button("💾 Descargar poema", poema, file_name="poema_pi.txt", mime="text/plain")

    versos = generar_versos(resultado)
    tankas = [transformar_en_tanka(v, idx+1) for idx, v in enumerate(versos) if transformar_en_tanka(v, idx+1)]

    if tankas:
        st.markdown("### 🌸 Tankas visuales")
        for t in tankas:
            st.markdown(t, unsafe_allow_html=True)
        texto_tankas = "\n\n".join([re.sub('<[^<]+?>', '', t) for t in tankas])
        st.download_button("💾 Descargar tankas", texto_tankas, file_name="tankas_pi.txt", mime="text/plain")

    # --- TABLA COMPLETA DE FLUJO ---
    if registros:
        st.markdown("### 🔍 Tabla de flujo de π")
        st.dataframe({
            "Posición en π": [r[0] for r in registros],
            "Bloque": [r[1] for r in registros],
            "Índice resultado": [r[2] for r in registros],
            "Palabra seleccionada": [r[3] for r in registros]
        }, use_container_width=True)
else:
    st.info("📥 Sube un archivo para comenzar.")