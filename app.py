# app.py
# Versión optimizada con una sola llamada a la API y timeout
import streamlit as st
import random
import google.generativeai as genai
import json
import time

# --- SECCIÓN DE LÓGICA (EL "CEREBRO" CON IA) ---

# Configuración de la API de Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_CONFIGURADO = True
except (KeyError, FileNotFoundError):
    GEMINI_CONFIGURADO = False

# Modelo de IA generativa
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Nueva función que genera todo en una sola llamada ---
def generar_publicacion_con_ia(tipo_prenda, marca, color, talla, estado, caracteristicas):
    """Crea título y descripción en una sola llamada a la API, esperando una respuesta JSON."""
    
    # Prompt detallado que solicita una respuesta en formato JSON
    prompt = f"""
    Actúa como una experta en marketing de moda para la plataforma GoTrendier. Tu reputación es 5 estrellas.
    Tu tarea es generar un título y una descripción para una publicación de ropa.

    DATOS DE LA PRENDA:
    - Tipo de prenda: {tipo_prenda}
    - Marca: {marca}
    - Talla: {talla}
    - Color: {color}
    - Estado: {estado}
    - Características extra: {caracteristicas if caracteristicas else "ninguna"}

    INSTRUCCIONES DE FORMATO DE SALIDA:
    Responde estrictamente con un objeto JSON que contenga dos claves: "titulo" y "descripcion".
    - El valor de "titulo" debe ser un string atractivo de 6 a 8 palabras.
    - El valor de "descripcion" debe ser un string con una descripción chic, juvenil y persuasiva que integre naturalmente las características de la prenda, comience con un saludo llamativo y termine con una llamada a la acción.

    Ejemplo de formato de respuesta:
    {{
      "titulo": "Increíble Vestido Zara Talla M Floral",
      "descripcion": "¡Alerta Trend! Este vestido Zara es la pieza que necesitas..."
    }}

    Genera únicamente el objeto JSON, sin texto adicional, explicaciones o comillas de bloque de código.
    """
    
    # Configuración de la petición con un timeout de 60 segundos
    request_options = {"timeout": 60}
    
    response = model.generate_content(prompt, request_options=request_options)
    
    # Limpiar y parsear la respuesta JSON
    # A veces la IA envuelve la respuesta en ```json ... ```, lo eliminamos.
    cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
    
    data = json.loads(cleaned_response)
    
    return data["titulo"], data["descripcion"]

# La función de precio se mantiene igual
def generar_precio_sugerido(tipo_prenda, marca, estado):
    tipo_prenda_norm = tipo_prenda.lower().strip()
    marca_norm = marca.lower().strip()
    precios_base = {
        ("vestido", "zara"): 850, ("vestido", "h&m"): 700, ("vestido", "shein"): 450,
        ("vestido", "michael kors"): 2800, ("blusa", "michael kors"): 1200,
        ("pantalón", "zara"): 750, ("pantalón", "levis"): 1200,
        ("blusa", "zara"): 600, ("blusa", "h&m"): 500,
    }
    multiplicadores_estado = {"Nuevo con etiqueta": 1.0, "Nuevo sin etiqueta": 0.90, "Usado una vez": 0.80, "Usado en buen estado": 0.70}
    precio_mercado = precios_base.get((tipo_prenda_norm, marca_norm), 600)
    precio_ajustado_estado = precio_mercado * multiplicadores_estado.get(estado, 0.7)
    multiplicador_confianza = random.uniform(1.05, 1.10)
    precio_con_premium = precio_ajustado_estado * multiplicador_confianza
    precio_final = int(precio_con_premium / 10) * 10 - 1
    return f"${precio_final:,.2f} MXN"

# --- SECCIÓN 1: LA INTERFAZ DE USUARIO ---

st.set_page_config(page_title="Asistente de publicación IA", layout="centered")
st.markdown("""<style> .stApp{background-color:#FFFFFF;} </style>""", unsafe_allow_html=True)
st.title("✨ Asistente de Publicación con IA")
st.markdown("Rellena los datos y deja que la IA de Gemini cree los textos por ti.")
st.markdown("---")

if not GEMINI_CONFIGURADO:
    st.error("🚨 ¡Falta la API Key de Gemini! Crea el archivo .streamlit/secrets.toml y añade tu clave para continuar.")
else:
    with st.container():
        tipo_prenda = st.text_input("Tipo de prenda", placeholder="Ej: Vestido, Pantalón, Blusa")
        marca = st.text_input("Marca", placeholder="Ej: Zara, H&M, Levi's")
        estado_prenda = st.selectbox("Estado de la prenda", ("Nuevo con etiqueta", "Nuevo sin etiqueta", "Usado una vez", "Usado en buen estado"))
        talla = st.text_input("Talla", placeholder="Ej: CH, M, G, 28")
        color = st.text_input("Color", placeholder="Ej: Azul cielo, Negro, Estampado floral")
        caracteristicas_especiales = st.text_area("Características especiales", placeholder="Ej: Tiro alto, Tela de lino, Bordado a mano")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 ¡Generar con IA!"):
        if not all([tipo_prenda, marca, talla, color]):
            st.error("¡Oops! Asegúrate de rellenar todos los campos para obtener el mejor resultado.")
        else:
            with st.spinner("✨ La IA de Gemini está creando tu publicación... (esto puede tardar unos segundos)"):
                try:
                    # Llamada a la nueva función única
                    titulo_generado, descripcion_generada = generar_publicacion_con_ia(tipo_prenda, marca, color, talla, estado_prenda, caracteristicas_especiales)
                    
                    st.session_state.titulo = titulo_generado
                    st.session_state.descripcion = descripcion_generada
                    st.session_state.precio = generar_precio_sugerido(tipo_prenda, marca, estado_prenda)

                except Exception as e:
                    st.error(f"Ocurrió un error al contactar a la IA: {e}")
                    st.info("Inténtalo de nuevo. Si el error persiste, puede ser un problema con el servicio de Gemini o tu conexión.")
    
    if 'precio' in st.session_state:
        st.markdown("---")
        st.subheader(f"Precio Sugerido: {st.session_state.precio}")
        st.markdown("---")
        
        st.caption("TÍTULO GENERADO POR IA")
        st.markdown(st.session_state.titulo)
        if 'titulo' in st.session_state:
            st.copy_button("Copiar Título", st.session_state.titulo, key="copy_titulo")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.caption("DESCRIPCIÓN GENERADA POR IA")
        st.markdown(st.session_state.descripcion)
        if 'descripcion' in st.session_state:
            st.copy_button("Copiar Descripción", st.session_state.descripcion, key="copy_desc")