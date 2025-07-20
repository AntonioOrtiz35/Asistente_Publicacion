# app.py
# CÓDIGO FINAL - Versión de máxima compatibilidad
import streamlit as st
import random

# --- SECCIÓN DE LÓGICA (EL "CEREBRO") ---

def generar_precio_sugerido(tipo_prenda, marca, estado):
    tipo_prenda_norm = tipo_prenda.lower().strip()
    marca_norm = marca.lower().strip()
    precios_base = {
        ("vestido", "zara"): 850, ("vestido", "h&m"): 700, ("vestido", "shein"): 450,
        ("vestido", "michael kors"): 2800,
        ("pantalón", "zara"): 750, ("pantalón", "levis"): 1200, ("pantalón", "bershka"): 650,
        ("blusa", "zara"): 600, ("blusa", "h&m"): 500, ("blusa", "stradivarius"): 550,
        ("blusa", "michael kors"): 1200,
        ("chamarra", "zara"): 1500, ("chamarra", "h&m"): 1200,
        ("falda", "zara"): 700, ("falda", "forever 21"): 400,
        ("cárdigan", "st. john's bay"): 450
    }
    multiplicadores_estado = {"Nuevo con etiqueta": 1.0, "Nuevo sin etiqueta": 0.90, "Usado una vez": 0.80, "Usado en buen estado": 0.70}
    precio_mercado = precios_base.get((tipo_prenda_norm, marca_norm), 600)
    precio_ajustado_estado = precio_mercado * multiplicadores_estado.get(estado, 0.7)
    multiplicador_confianza = random.uniform(1.05, 1.10)
    precio_con_premium = precio_ajustado_estado * multiplicador_confianza
    precio_final = int(precio_con_premium / 10) * 10 - 1
    return f"${precio_final:,.2f} MXN"

def generar_titulo(tipo_prenda, marca, color, talla):
    adjetivos = ["Increíble", "Perfecto", "Moderno", "Estilizado", "Único", "Ideal"]
    random.shuffle(adjetivos)
    
    plantillas = [
        f"{tipo_prenda.capitalize()} {marca.capitalize()} Talla {talla} Color {color.capitalize()}",
        f"{adjetivos[0]} {tipo_prenda} de {marca.capitalize()} - Talla {talla}",
        f"{tipo_prenda.capitalize()} Color {color.capitalize()} de {marca.capitalize()} ({adjetivos[0]})"
    ]
    return random.choice(plantillas)

def generar_descripcion_chic(tipo_prenda, talla, color, estado, caracteristicas):
    estado_positivo = {"Nuevo con etiqueta": "nuevo, con su etiqueta intacta", "Nuevo sin etiqueta": "nuevo, nunca usado", "Usado una vez": "usado solo una vez, como nuevo", "Usado en buen estado": "en excelente estado, súper cuidado"}[estado]
    frase_narrativa = ""
    if caracteristicas:
        lista_caracteristicas = [c.strip() for c in caracteristicas.split(',')]
        if len(lista_caracteristicas) == 1:
            frase_narrativa = f"Destaca especialmente por su **{lista_caracteristicas[0]}**. "
        elif len(lista_caracteristicas) == 2:
            frase_narrativa = f"Te encantarán sus detalles, como el **{lista_caracteristicas[0]}** y su **{lista_caracteristicas[1]}**. "
        else:
            resto = ", ".join(lista_caracteristicas[:-1])
            ultimo = lista_caracteristicas[-1]
            frase_narrativa = f"Entre sus toques únicos están su **{resto}** y **{ultimo}**. "

    plantillas = [
        f"¡Una joyita para tu clóset! ✨ Este {tipo_prenda} {marca} color {color} es todo lo que buscas. Es talla {talla} y está {estado_positivo}. {frase_narrativa}Es ideal para robar miradas. ¡Que no te lo ganen!",
        f"ALERTA TREND 🚨: {tipo_prenda.capitalize()} {marca.capitalize()} talla {talla} súper chic. {frase_narrativa}El color {color} es un must y está {estado_positivo}. ¡Añádelo a tu bolsa ya!",
        f"La pieza perfecta existe: {tipo_prenda} {marca} talla {talla} en un increíble color {color}. Está {estado_positivo}. {frase_narrativa}Es una compra 100% segura conmigo. No lo dejes ir. 😉"
    ]
    
    return random.choice(plantillas)


# --- SECCIÓN 1: LA INTERFAZ DE USUARIO ---

st.set_page_config(page_title="Asistente de publicación", layout="centered")
st.markdown("""<style> .stApp{background-color:#FFFFFF;} </style>""", unsafe_allow_html=True)
st.title("Asistente de publicación")
st.markdown("Rellena los datos de tu prenda para generar textos y precios optimizados.")
st.markdown("---")

with st.container():
    tipo_prenda = st.text_input("Tipo de prenda", placeholder="Ej: Vestido, Pantalón, Blusa")
    marca = st.text_input("Marca", placeholder="Ej: Zara, H&M, Levi's")
    estado_prenda = st.selectbox("Estado de la prenda", ("Nuevo con etiqueta", "Nuevo sin etiqueta", "Usado una vez", "Usado en buen estado"))
    talla = st.text_input("Talla", placeholder="Ej: CH, M, G, 28")
    color = st.text_input("Color", placeholder="Ej: Azul cielo, Negro, Estampado floral")
    caracteristicas_especiales = st.text_area("Características especiales (separa por comas)", placeholder="Ej: Tiro alto, Tela de lino, Bordado a mano")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("✨ ¡Generar Publicación!"):
    if not all([tipo_prenda, marca, talla, color]):
        st.error("¡Oops! Asegúrate de rellenar todos los campos para obtener el mejor resultado.")
    else:
        # La IA no se usa en esta versión, usamos la lógica de plantillas
        st.session_state.precio = generar_precio_sugerido(tipo_prenda, marca, estado_prenda)
        st.session_state.titulo = generar_titulo(tipo_prenda, marca, color, talla)
        st.session_state.descripcion = generar_descripcion_chic(tipo_prenda, talla, color, estado_prenda, caracteristicas_especiales)

if 'precio' in st.session_state:
    st.markdown("---")
    st.subheader(f"Precio Sugerido: {st.session_state.precio}")
    st.markdown("---")
    
    st.caption("TÍTULO SUGERIDO")
    st.code(st.session_state.titulo, language=None)
    
    st.caption("DESCRIPCIÓN SUGERIDA")
    st.code(st.session_state.descripcion, language=None)
