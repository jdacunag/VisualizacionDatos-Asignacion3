"""
Dashboard de exposición · Proyecto Integrador · Equipo 8
Recomendador de contratos públicos SECOP II

Recorrido de 6 secciones (≈ 6 min) en el orden de la exposición: de qué trata, por qué
importa, objetivo, resultados, arquitectura y metodología, hallazgos y conclusiones. Se navega desde el
sidebar o con Anterior / Siguiente. El sidebar permite personalizar la experiencia:
nivel de detalle (general o técnico) y texto grande para proyector.

Datos: tablas de la capa oro (Athena, base secop_gold) exportadas a datos/*.csv con las
consultas de consultas_gold.sql. Las cifras sueltas (CIFRAS) vienen del resumen del
proyecto del 17 de noviembre de 2026.
Colores: azules institucionales del KIT UI de GOV.CO (#3366CC y #004884).
"""
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).parent
DATOS = RAIZ / "datos"

# ---------------------------------------------------------------- paleta GOV.CO
AZUL = "#3366CC"          # azul GOV.CO: lo que queremos que se mire
AZUL_OSC = "#004884"      # azul oscuro GOV.CO: sidebar y énfasis
AZUL_SUAVE = "#E8EFFA"    # fondo de notas
AMARILLO = "#FFCD00"      # amarillo del Gobierno de Colombia: solo acentos pequeños
AMARILLO_SUAVE = "#FFF8D9"  # fondo de los datos clave
NEUTRO = "#a8a69f"        # contexto / referencia
TINTA = "#0b0b0b"
TINTA_2 = "#4b4a47"
TINTA_3 = "#85847e"
REJILLA = "#e6e4df"
FONDO = "#fcfcfb"
FUENTE_SECOP = ("Fuente: SECOP II, Colombia Compra Eficiente, datos.gov.co "
                "(CC BY-SA 4.0). Procesamiento: Equipo 8, capa oro en AWS.")
MESES = ["ene.", "feb.", "mar.", "abr.", "may.", "jun.", "jul.", "ago.", "sep.",
         "oct.", "nov.", "dic."]

CIFRAS = {
    "procesos": 625_625, "filas_fuente_millones": 10.6, "participaciones": 1_979_268,
    "contratos": 5_709_481, "empresas_dia": 38_500, "procesos_abiertos_dia": 2_000,
    "minutos_corrida": 59, "usd_noche": 1.6, "usd_mes_bd": 14, "api_ms": 100,
    "candidatos": 150, "variables": 106, "parejas_millones": 97,
    "lista2_modelo": 67.7, "lista2_ref": 62.3, "ece": 0.0053,
    "atipicos": 766, "umbral_atipico": 1e11, "mayor_atipico": 7.7e15,
    "ingesta_antes": 3, "ingesta_despues": 100,
}

SECCIONES = [
    ("De qué trata", "0:50"),
    ("Por qué importa", "1:00"),
    ("Objetivo", "0:30"),
    ("Resultados", "1:00"),
    ("Arquitectura y metodología", "1:20"),
    ("Conclusiones", "0:50"),
]

EQUIPO = [
    ("Juan Diego Acuña", "Ingeniería de datos"),
    ("David Lopera", "Aprendizaje automático"),
    ("Jacobo Restrepo", "MLOps"),
    ("Nicolás Hurtado", "Web y visualización"),
    ("José Alejandro Duque", "Web y visualización"),
]


# ---------------------------------------------------------------- utilidades
def miles(x: float, dec: int = 0) -> str:
    """Formato colombiano: 1.234.567,8"""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def nbsp(t: str) -> str:
    return t.replace(" %", " %")


def base_fig(alto: int) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        height=alto, margin=dict(l=10, r=20, t=10, b=10),
        paper_bgcolor=FONDO, plot_bgcolor=FONDO, showlegend=False,
        font=dict(family="Source Sans Pro, Segoe UI, Helvetica, Arial, sans-serif",
                  size=15, color=TINTA_2),
        hoverlabel=dict(bgcolor="white", font_size=14, font_color=TINTA),
        bargap=0.35, separators=",.",
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False,
                     tickfont=dict(color=TINTA_3))
    fig.update_yaxes(showgrid=False, zeroline=False, showline=False,
                     tickfont=dict(color=TINTA_2))
    return fig


def mostrar(fig: go.Figure):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def html(texto: str, col=None):
    (col or st).markdown(texto, unsafe_allow_html=True)


def titulo_grafica(mensaje: str, detalle: str = ""):
    html(f"<div class='g-tit'>{nbsp(mensaje)}</div>"
         f"{f'<div class=g-det>{detalle}</div>' if detalle else ''}")


def fuente(texto: str = FUENTE_SECOP, separada: bool = False):
    estilo = " style='margin-top:.5rem'" if separada else ""
    html(f"<div class='fuente'{estilo}>{texto}</div>")


def nota(texto: str, col=None):
    html(f"<div class='nota'>{texto}</div>", col)


def dato_clave(texto: str, col=None):
    """Nota con acento amarillo, reservada para un solo dato por pantalla."""
    html(f"<div class='nota dato'>{texto}</div>", col)


def tarjeta(col, titulo: str, cuerpo: str, pie: str = "", kicker: str = "",
            activa: bool = False):
    html(f"<div class='card{' card-on' if activa else ''}'>"
         f"{f'<div class=card-k>{kicker}</div>' if kicker else ''}"
         f"<div class='card-t'>{titulo}</div><div class='card-c'>{cuerpo}</div>"
         f"{f'<div class=card-p>{pie}</div>' if pie else ''}</div>", col)


def encabezado(i: int, mensaje: str, bajada: str = ""):
    html(f"<div class='kicker'>{i + 1} · {SECCIONES[i][0]}</div>"
         f"<h1 class='msg'>{nbsp(mensaje)}</h1>"
         f"{f'<div class=bajada>{bajada}</div>' if bajada else ''}")


def tecnico() -> bool:
    return st.session_state.get("nivel") == "Técnico"


def etiquetas_finales(fig, finales, x, fmt, sep):
    """Etiquetas al final de cada línea, separadas lo mínimo para no encimarse."""
    finales = sorted(finales, key=lambda f: f[1])
    ys = [f[1] for f in finales]
    for _ in range(200):
        for k in range(len(ys) - 1):
            falta = sep - (ys[k + 1] - ys[k])
            if falta > 0:
                ys[k] -= falta / 2
                ys[k + 1] += falta / 2
        ys[0] = max(ys[0], sep * 0.5)
    for (m, v, dest), y in zip(finales, ys):
        etq = f"{m} {fmt(v)}"
        fig.add_annotation(x=x, y=y, text=f"<b>{etq}</b>" if dest else etq,
                           xanchor="left", xshift=12, showarrow=False,
                           font=dict(color=TINTA if dest else TINTA_2, size=13))


ESCALA_AZUL = [[0, "#F2F6FC"], [0.35, "#A9C1EA"], [0.7, AZUL], [1, AZUL_OSC]]
ORDEN_MODALIDADES = ["Mínima cuantía", "Selección abreviada", "Régimen especial",
                     "Licitación pública", "Concurso de méritos"]


def matriz(z: pd.DataFrame, fmt, hover: str, alto: int, zmax=None) -> go.Figure:
    """Mapa de calor modalidad × año con el valor escrito en cada celda."""
    fig = base_fig(alto)
    fig.add_heatmap(z=z.values, x=[str(c) for c in z.columns], y=list(z.index),
                    colorscale=ESCALA_AZUL, zmin=0, zmax=zmax or float(z.values.max()),
                    text=[[fmt(v) for v in fila] for fila in z.values],
                    texttemplate="%{text}", textfont=dict(size=13),
                    xgap=3, ygap=3, showscale=False, hovertemplate=hover)
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=13, color=TINTA_2))
    fig.update_xaxes(side="top", type="category", tickfont=dict(size=13, color=TINTA_2))
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    return fig


@st.cache_data
def cargar():
    merc = pd.read_csv(DATOS / "mercado_anual.csv")
    des = pd.read_csv(DATOS / "desempeno.csv", parse_dates=["fecha_corte"])
    cal = pd.read_csv(DATOS / "calidad_fuente.csv", parse_dates=["semana_inicio"])
    met = pd.read_csv(DATOS / "metricas_modelo.csv")
    return merc, des, cal, met


@st.cache_data
def consultas() -> dict:
    """Bloques '-- @archivo.csv · descripción' de consultas_gold.sql."""
    texto = (RAIZ / "consultas_gold.sql").read_text(encoding="utf-8")
    salida = {}
    for b in re.split(r"^-- @", texto, flags=re.M)[1:]:
        cabeza, _, sql = b.partition("\n")
        archivo, _, desc = cabeza.partition(" · ")
        salida[archivo.strip()] = (desc.strip(), sql.strip())
    return salida


# ---------------------------------------------------------------- página y estilo
st.set_page_config(page_title="Recomendador SECOP II · Equipo 8", layout="wide",
                   initial_sidebar_state="expanded")

if "sec" not in st.session_state:
    st.session_state.sec = 0
if "nivel" not in st.session_state:
    st.session_state.nivel = "General"


def ir_a(i: int):
    st.session_state.sec = i


def ir(delta: int):
    st.session_state.sec = min(max(st.session_state.sec + delta, 0), len(SECCIONES) - 1)


with st.sidebar:
    html("<div class='marca'>Recomendador<br>SECOP II</div>"
         "<div class='lado'>Contratos públicos abiertos, recomendados cada mañana a "
         "cada empresa con su probabilidad de ganar.</div>")
    st.write("")
    html("<div class='lado-t'>Secciones</div>")
    i_sec = st.session_state.sec
    with st.container(key="menu"):
        for i, (nombre, _) in enumerate(SECCIONES):
            st.button(f"{i + 1} · {nombre}", key=f"menu_{i}", on_click=ir_a, args=(i,),
                      type="primary" if i == i_sec else "secondary", width="stretch")
    st.progress((i_sec + 1) / len(SECCIONES))
    st.divider()
    html("<div class='lado-t'>Personaliza la vista</div>")
    with st.container(key="nivel_box"):
        st.segmented_control("Nivel de detalle", ["General", "Técnico"], key="nivel",
                             help="Técnico muestra modelos, servicios de AWS, definiciones "
                                  "de métricas y las consultas SQL a la capa oro.")
    proyector = st.toggle("Texto grande (proyector)", value=False)
    st.divider()
    html("<div class='lado'><b>Equipo 8</b><br>" +
         "<br>".join(f"{n} · <span class='tenue'>{r}</span>" for n, r in EQUIPO) +
         "</div>")
    st.write("")
    html("<div class='lado'>Proyecto Integrador · Machine Learning, Big Data y "
         "Visualización de datos · Universidad EAFIT · 2026</div>")
    st.write("")
    html("<div class='lado'><b>Datos:</b> SECOP II, Colombia Compra Eficiente "
         "(datos.gov.co, CC BY-SA 4.0). Gráficas construidas con consultas a las tablas "
         "de la capa oro en Athena.</div>")

escala = 1.12 if proyector else 1.0
html(f"""
<style>
  html {{font-size: {16 * escala:.1f}px;}}
  .block-container {{max-width: 1260px; padding-top: 2rem; padding-bottom: 3rem;}}
  .kicker {{text-transform: uppercase; letter-spacing: .1em; font-size: .9rem;
            color: {AZUL}; font-weight: 700; display: flex; align-items: center; gap: .5rem;}}
  .kicker::before {{content: ""; display: inline-block; width: 22px; height: 4px;
                    border-radius: 2px; background: {AMARILLO};}}
  .nota.dato {{background: {AMARILLO_SUAVE}; border-left-color: {AMARILLO};}}
  .st-key-que_es_proceso [data-testid="stExpander"] details, .st-key-que_es_oferente [data-testid="stExpander"] details, .st-key-como_medimos [data-testid="stExpander"] details {{background: {AMARILLO_SUAVE};
      border: 1px solid {AMARILLO}; border-left: 4px solid {AMARILLO}; border-radius: 8px;}}
  .st-key-que_es_proceso [data-testid="stExpander"] summary p, .st-key-que_es_oferente [data-testid="stExpander"] summary p, .st-key-como_medimos [data-testid="stExpander"] summary p {{font-weight: 700;
      color: {AZUL_OSC}; font-size: 1.02rem;}}
  .st-key-que_es_proceso [data-testid="stExpander"] summary:hover p {{color: {AZUL};}}
  .st-key-que_es_proceso [data-testid="stExpander"] summary, .st-key-que_es_oferente [data-testid="stExpander"] summary, .st-key-como_medimos [data-testid="stExpander"] summary {{background: transparent;}}
  .st-key-que_es_proceso [data-testid="stExpanderDetails"] p, .st-key-que_es_oferente [data-testid="stExpanderDetails"] p, .st-key-como_medimos [data-testid="stExpanderDetails"] p, .st-key-como_medimos [data-testid="stExpanderDetails"] li {{font-size: 1.03rem;
      line-height: 1.5;}}
  h1.msg {{font-size: 2.25rem; line-height: 1.18; color: {AZUL_OSC}; font-weight: 750;
           margin: .3rem 0 .6rem 0; padding: 0; max-width: 1080px;}}
  .bajada {{font-size: 1.1rem; color: {TINTA_2}; line-height: 1.5; max-width: 1080px;
            margin-bottom: 1.1rem;}}
  .g-tit {{font-size: 1.1rem; font-weight: 650; color: {TINTA}; line-height: 1.3;}}
  .g-det {{font-size: .92rem; color: {TINTA_2}; margin: .15rem 0 .2rem 0;}}
  .fuente {{font-size: .8rem; color: {TINTA_3}; margin-top: -.3rem;}}
  .nota {{background: {AZUL_SUAVE}; border-left: 4px solid {AZUL}; border-radius: 8px;
          padding: .9rem 1.1rem; color: {TINTA}; font-size: 1.03rem; line-height: 1.5;}}
  .nota b {{color: {AZUL_OSC};}}
  .card {{background: white; border: 1px solid {REJILLA}; border-radius: 10px;
          padding: .9rem 1rem; height: 100%;}}
  .card-on {{border: 2px solid {AZUL}; background: {AZUL_SUAVE};}}
  .card-k {{color: {AZUL}; font-size: .76rem; font-weight: 700; letter-spacing: .08em;
            text-transform: uppercase; margin-bottom: .15rem;}}
  .card-t {{font-weight: 650; color: {TINTA}; font-size: 1.02rem; margin-bottom: .3rem;}}
  .card-c {{color: {TINTA_2}; font-size: .95rem; line-height: 1.42;}}
  .card-p {{color: {TINTA_3}; font-size: .82rem; margin-top: .45rem;}}
  .sub {{font-size: 1.3rem; font-weight: 700; color: {AZUL_OSC}; margin: 1.4rem 0 .7rem 0;}}
  .grande {{font-size: 2.3rem; font-weight: 750; color: {AZUL_OSC}; line-height: 1.1;}}
  [data-testid="stMetricValue"] {{font-size: 1.95rem; font-weight: 700; color: {AZUL_OSC};}}
  [data-testid="stMetricLabel"] p {{font-size: .95rem; color: {TINTA_2};}}
  /* sidebar en azul oscuro GOV.CO */
  [data-testid="stSidebar"] {{background: {AZUL_OSC}; border-top: 5px solid {AMARILLO};}}
  [data-testid="stSidebar"] [data-testid="stProgressBarTrack"] > div {{background: {AMARILLO};}}
  [data-testid="stSidebar"] .marca::after {{content: ""; display: block; width: 36px; height: 3px;
                                            background: {AMARILLO}; margin-top: .45rem; border-radius: 2px;}}
  [data-testid="stSidebar"] * {{color: #ffffff;}}
  [data-testid="stSidebar"] .lado {{font-size: .9rem; color: #dce6f5; line-height: 1.55;}}
  [data-testid="stSidebar"] .lado b {{color: #ffffff;}}
  [data-testid="stSidebar"] .tenue {{color: #a9bfe0;}}
  [data-testid="stSidebar"] .lado-t {{font-weight: 700; font-size: .95rem; margin-bottom: .3rem;}}
  [data-testid="stSidebar"] .marca {{font-size: 1.45rem; font-weight: 800; line-height: 1.15;
                                     margin-bottom: .4rem;}}
  [data-testid="stSidebar"] hr {{border-color: rgba(255,255,255,.25);}}
  /* menú de secciones: filas en vez de circulitos */
  .st-key-menu {{gap: .15rem;}}
  .st-key-menu button {{justify-content: flex-start; background: transparent;
      border: none; border-left: 4px solid transparent; border-radius: 6px;
      padding: .45rem .75rem; min-height: 0;}}
  .st-key-menu button > div, .st-key-menu button [data-testid="stMarkdownContainer"] {{
      justify-content: flex-start; text-align: left; width: 100%;}}
  .st-key-menu button p {{font-size: .95rem; text-align: left;}}
  .st-key-menu button:hover {{background: rgba(255,255,255,.10); border-left-color: rgba(255,205,0,.5);}}
  .st-key-menu button[kind="primary"] {{background: rgba(255,255,255,.16);
      border-left-color: {AMARILLO};}}
  .st-key-menu button[kind="primary"] p {{font-weight: 700;}}
  .st-key-menu button:focus:not(:active) {{color: #fff; border-color: transparent;}}
  .st-key-menu button[kind="primary"]:focus:not(:active) {{border-left-color: {AMARILLO};}}
  /* selector General / Técnico sobre fondo oscuro */
  .st-key-nivel_box button {{background: transparent; border-color: rgba(255,255,255,.35);}}
  .st-key-nivel_box button[kind="segmented_controlActive"] {{background: rgba(255,255,255,.18);
      border-color: {AMARILLO};}}
  .st-key-nivel_box button[kind="segmented_controlActive"] p {{font-weight: 700;}}
  [data-testid="stSidebar"] [data-testid="stProgressBarTrack"] {{background: rgba(255,255,255,.22);}}
</style>
""")

merc, des, cal, met = cargar()


def pie_navegacion():
    st.write("")
    c = st.columns([2, 6, 2])
    c[0].button("← Anterior", on_click=ir, args=(-1,), width="stretch",
                disabled=st.session_state.sec == 0)
    c[2].button("Siguiente →", on_click=ir, args=(1,), width="stretch",
                type="primary", disabled=st.session_state.sec == len(SECCIONES) - 1)


# ================================================================ 1 · DE QUÉ TRATA
def seccion_1():
    encabezado(0, "Un “Netflix de contratos públicos” para las empresas que le venden "
                  "al Estado",
               "El Estado compra de todo: medicamentos, obras, computadores, aseo. Casi "
               "todas esas compras se publican en <b>SECOP II</b>, un tablero de anuncios "
               "donde cada proceso de contratación recibe ofertas de empresas.")
    c = st.columns(4)
    c[0].metric("Procesos abiertos al día", f"≈ {miles(CIFRAS['procesos_abiertos_dia'])}",
                help="Procesos de SECOP II abiertos que el sistema revisa en la corrida diaria.")
    c[1].metric("Empresas recomendadas al día", f"≈ {miles(CIFRAS['empresas_dia'])}",
                help="Empresas con historial de participación en SECOP II.")
    c[2].metric("Histórico de procesos", miles(CIFRAS["procesos"]),
                help=f"De {miles(CIFRAS['filas_fuente_millones'], 1)} millones de filas "
                     "leídas, sin versiones repetidas ni duplicados.")
    c[3].metric("Participaciones para aprender", miles(CIFRAS["participaciones"]),
                help="Qué empresa ofertó en qué proceso: la base del modelo.")

    # ---- fila 1: el mercado y el problema práctico, lado a lado
    c = st.columns([6, 5], gap="large")
    with c[0]:
        html("<div class='sub'>Un mercado grande y creciente</div>")
        vista = st.segmented_control("Ver", ["Por año", "Matriz por modalidad"],
                                     default="Por año", key="vol_vista",
                                     label_visibility="collapsed") or "Por año"
        anual = merc.groupby("anio").procesos.sum()
        a0, a1 = int(anual.index.min()), int(anual.index.max())
        anio_lleno = a1 - 1
        mc_share = 100 * merc[(merc.anio == anio_lleno) &
                              (merc.modalidad_grupo == "Mínima cuantía")].procesos.sum() \
            / anual[anio_lleno]
        if vista == "Por año":
            titulo_grafica(f"Los procesos publicados se duplicaron: de "
                           f"{miles(anual[a0] / 1000)} mil en {a0} a "
                           f"{miles(anual[anio_lleno] / 1000)} mil en {anio_lleno}",
                           "Procesos publicados por año, cinco modalidades principales")
            fig = base_fig(300)
            colores = [AZUL if a < a1 else "#A9C1EA" for a in anual.index]
            fig.add_bar(x=[f"{a}*" if a == a1 else str(a) for a in anual.index],
                        y=anual.values, marker=dict(color=colores, cornerradius=4),
                        text=[f"{miles(v / 1000)} mil" for v in anual.values],
                        textposition="outside", textfont=dict(size=13, color=TINTA),
                        cliponaxis=False,
                        hovertemplate="%{x}: %{y:,.0f} procesos<extra></extra>")
            fig.update_yaxes(showticklabels=False, range=[0, anual.max() * 1.18])
            fig.update_xaxes(type="category")
            mostrar(fig)
            fuente(f"Tabla oro <code>mercado_mensual</code>. *{a1}: enero a noviembre "
                   f"(barra clara).")
        else:
            titulo_grafica(f"{mc_share:.0f} de cada 100 procesos son de mínima cuantía, "
                           f"las compras pequeñas",
                           "Procesos publicados por modalidad y año (miles)")
            z = (merc.pivot(index="modalidad_grupo", columns="anio", values="procesos")
                 .reindex(ORDEN_MODALIDADES))
            z.columns = [f"{a}*" if a == a1 else str(a) for a in z.columns]
            mostrar(matriz(z / 1000, lambda v: miles(v, 1),
                           "%{y} · %{x}: %{z:,.1f} mil procesos<extra></extra>", 300))
            fuente(f"Tabla oro <code>mercado_mensual</code>. *{a1}: enero a noviembre.")
    with c[1]:
        html("<div class='sub'>El problema: revisarlos a mano no es posible</div>")
        minutos = st.slider("¿Cuántos minutos tarda una persona en leer un proceso?",
                            1, 15, 3, key="min_proceso",
                            help="Mueve el control: el cálculo usa los ≈ 2.000 procesos "
                                 "abiertos que hay cada día.")
        horas = CIFRAS["procesos_abiertos_dia"] * minutos / 60
        jornadas = horas / 8
        html(f"<div class='grande'>{miles(horas)} horas al día</div>"
             f"<div class='g-det'>para revisar los procesos abiertos: "
             f"<b>{miles(jornadas, 0)} personas</b> trabajando 8 horas, solo leyendo. "
             f"Una mipyme no tiene ese equipo.</div>")
        fig = base_fig(170)
        fig.add_bar(y=["Una jornada laboral", "Leer todos los procesos"], x=[8, horas],
                    orientation="h", marker=dict(color=[NEUTRO, AZUL], cornerradius=4),
                    text=["8 h", f"{miles(horas)} h"], textposition="outside",
                    textfont=dict(size=14, color=TINTA), cliponaxis=False, hoverinfo="skip")
        fig.update_xaxes(showticklabels=False, range=[0, max(horas, 8) * 1.2])
        fig.update_yaxes(tickfont=dict(size=13, color=TINTA_2))
        fig.update_layout(bargap=0.35)
        mostrar(fig)

    # ---- resumen y qué es un proceso
    html("<div class='sub'>En resumen</div>"
         "<div class='bajada' style='font-size:1.15rem; color:#0b0b0b'>SECOP II tiene cerca "
         "de 2.000 procesos abiertos cada día, y el número de procesos publicados se duplicó "
         "en cinco años. Ninguna empresa pequeña alcanza a revisarlos todos: muchas "
         "oportunidades se pierden y cada vez menos empresas compiten por cada contrato.</div>")
    st.write("")
    with st.container(key="que_es_proceso"):
        with st.expander("¿Qué es un proceso?"):
            st.markdown("Un **proceso de contratación** es el anuncio con el que una entidad "
                        "del Estado avisa que quiere comprar algo. La entidad puede ser una "
                        "alcaldía, un hospital, un ministerio, el Ejército, entre otras. Es como "
                        "publicar una oferta de trabajo, pero para comprar un bien o un "
                        "servicio.")


# ================================================================ 2 · POR QUÉ IMPORTA
def serie_competencia(medida: str) -> pd.DataFrame:
    tot = (merc.groupby("anio")[["procesos_con_oferentes", "procesos_unico_oferente",
                                  "suma_oferentes"]].sum().reset_index())
    tot["modalidad_grupo"] = "Todas"
    d = pd.concat([merc, tot], ignore_index=True)
    if medida == "unico":
        d["valor"] = 100 * d.procesos_unico_oferente / d.procesos_con_oferentes
    else:
        d["valor"] = d.suma_oferentes / d.procesos_con_oferentes
    return d


def grafica_competencia(medida: str, destacada: str, a0: int, a1: int) -> go.Figure:
    d = serie_competencia(medida)
    d = d[(d.anio >= a0) & (d.anio <= a1)]
    anio_max = int(merc.anio.max())
    es_pct = medida == "unico"
    fig = base_fig(360)
    finales = []
    for m, g in d.sort_values("anio").groupby("modalidad_grupo"):
        if m == "Todas" and destacada != "Todas":
            continue
        dest = m == destacada
        col = AZUL if dest else NEUTRO
        fig.add_scatter(
            x=g.anio, y=g.valor, mode="lines+markers",
            line=dict(color=col, width=3.5 if dest else 1.5),
            marker=dict(size=10 if dest else 6, color=col),
            customdata=g.procesos_con_oferentes,
            hovertemplate=(f"<b>{m}</b> · %{{x}}<br>"
                           + ("%{y:.1f} % con un solo oferente" if es_pct
                              else "%{y:.1f} oferentes por proceso")
                           + "<br>%{customdata:,} procesos con oferentes<extra></extra>"))
        finales.append((m, g.valor.iloc[-1], dest))
    rango = d.valor.max() * 1.15
    etiquetas_finales(fig, finales, a1,
                      (lambda v: f"{v:.0f} %") if es_pct else (lambda v: miles(v, 1)),
                      rango * 0.065)
    anios = sorted(d.anio.unique())
    fig.update_xaxes(tickvals=anios,
                     ticktext=[f"{a}*" if a == anio_max else str(a) for a in anios],
                     range=[anios[0] - 0.2, anios[-1] + 0.4 + 0.38 * len(anios)])
    fig.update_yaxes(range=[0, 80 if es_pct else rango], showgrid=True, gridcolor=REJILLA,
                     ticksuffix=" %" if es_pct else "", dtick=20 if es_pct else None)
    return fig


def seccion_2():
    tot = merc.groupby("anio")[["procesos_unico_oferente", "procesos_con_oferentes"]].sum()
    a_min, a_max = int(tot.index.min()), int(tot.index.max())
    p_fin = 100 * tot.iloc[-1, 0] / tot.iloc[-1, 1]
    encabezado(1, f"Cada vez compiten menos empresas: en {a_max}, casi la mitad de los "
                  f"procesos tuvo un solo oferente",
               "Con un solo oferente, el Estado no tiene con qué comparar precios.")
    with st.container(key="que_es_oferente"):
        with st.expander("¿Qué significa «un solo oferente»?"):
            st.markdown("Un **oferente** es una empresa que envía una oferta a un proceso. Un "
                        "proceso tiene **un solo oferente** cuando solo una empresa se "
                        "presentó: la entidad no tiene otras ofertas con las que comparar el "
                        "precio o la calidad, y termina contratando con la única que llegó. "
                        "Entre más procesos así, menos competencia hay en las compras del "
                        "Estado.")
    st.write("")
    # se resalta la modalidad más usada y se muestra todo el periodo disponible
    destacada = "Mínima cuantía"
    a0, a1 = a_min, a_max

    c = st.columns([7, 4], gap="large")
    with c[0]:
        t1, t2 = st.tabs(["Procesos con un solo oferente", "Ofertas por proceso"])
        with t1:
            titulo_grafica("Sube en las cinco modalidades",
                           "% de procesos con oferentes en los que se presentó una sola "
                           "empresa, por año")
            mostrar(grafica_competencia("unico", destacada, a0, a1))
        with t2:
            titulo_grafica("Y cada proceso recibe menos ofertas",
                           "Ofertas promedio por proceso con oferentes, por año")
            mostrar(grafica_competencia("oferentes", destacada, a0, a1))
        fuente(f"{FUENTE_SECOP} Tabla oro <code>mercado_mensual</code>. "
               f"*{a_max}: enero a noviembre.")
    with c[1]:
        d_u = serie_competencia("unico")
        d_o = serie_competencia("oferentes")
        sel = lambda d, a: float(d[(d.modalidad_grupo == destacada) & (d.anio == a)].valor.iloc[0])
        u0, u1, o0, o1 = sel(d_u, a0), sel(d_u, a1), sel(d_o, a0), sel(d_o, a1)
        nombre = "todas las modalidades" if destacada == "Todas" else destacada.lower()
        st.write("")
        c2 = st.columns(2)
        c2[0].metric(f"Un solo oferente {a1}", f"{u1:.0f} %", f"{u1 - u0:+.0f} pp vs. {a0}",
                     delta_color="inverse")
        c2[1].metric(f"Ofertas por proceso {a1}", miles(o1, 1),
                     f"{miles(o1 - o0, 1)} vs. {a0}", delta_color="normal")
        nota(f"En <b>{nombre}</b>, entre {a0} y {a1} los procesos con un solo oferente "
             f"pasaron del <b>{u0:.0f} %</b> al <b>{u1:.0f} %</b>, y cada proceso pasó de "
             f"{miles(o0, 1)} a {miles(o1, 1)} ofertas.")
        st.write("")
        tarjeta(st, "Para las mipymes", "Encuentran oportunidades que hoy se les pasan, "
                "sin revisar miles de procesos a mano.")
        st.write("")
        tarjeta(st, "Para el Estado", f"Hoy el {p_fin:.0f} % de los procesos no tiene con qué "
                "comparar precios. Más empresas compitiendo: mejores precios y más "
                "transparencia.")

    # ---- matriz modalidad × año y dónde se concentra el problema
    html("<div class='sub'>Dónde está el problema</div>")
    c = st.columns([6, 5], gap="large")
    with c[0]:
        medida_m = st.segmented_control("Matriz de", ["Un solo oferente", "Ofertas por proceso"],
                                        default="Un solo oferente", key="matriz_medida",
                                        label_visibility="collapsed") or "Un solo oferente"
        es_pct = medida_m == "Un solo oferente"
        d = serie_competencia("unico" if es_pct else "oferentes")
        d = d[(d.modalidad_grupo != "Todas") & (d.anio >= a0) & (d.anio <= a1)]
        z = d.pivot(index="modalidad_grupo", columns="anio", values="valor") \
            .reindex(ORDEN_MODALIDADES)
        z.columns = [f"{a}*" if a == a_max else str(a) for a in z.columns]
        if es_pct:
            titulo_grafica("La matriz se oscurece hacia la derecha en todas las modalidades",
                           "% de procesos con un solo oferente · más oscuro = menos competencia")
            fig = matriz(z, lambda v: f"{v:.0f} %",
                         "%{y} · %{x}: %{z:.1f} % con un solo oferente<extra></extra>",
                         290, zmax=75)
        else:
            titulo_grafica("Licitaciones y concursos reciben más ofertas, pero también caen",
                           "Ofertas promedio por proceso · más oscuro = más competencia")
            fig = matriz(z, lambda v: miles(v, 1),
                         "%{y} · %{x}: %{z:.1f} ofertas por proceso<extra></extra>", 290)
        mostrar(fig)
        fuente(f"Tabla oro <code>mercado_mensual</code>. *{a_max}: enero a noviembre.")
    with c[1]:
        b = merc[merc.anio == a1].set_index("modalidad_grupo").reindex(ORDEN_MODALIDADES)
        tot_u = b.procesos_unico_oferente.sum()
        tot_c = b.procesos_con_oferentes.sum()
        titulo_grafica(f"En {a1}, {miles(tot_u)} de {miles(tot_c)} procesos con ofertas "
                       f"tuvieron un solo oferente ({100 * tot_u / tot_c:.0f} %)",
                       "Procesos con ofertas por modalidad (gris) y, de ellos, los que "
                       "tuvieron un solo oferente (azul)")
        b = b.iloc[::-1]
        pct = 100 * b.procesos_unico_oferente / b.procesos_con_oferentes
        fig = base_fig(330)
        fig.add_bar(y=b.index, x=b.procesos_con_oferentes, orientation="h",
                    name="Procesos con ofertas", marker=dict(color="#dcdad3", cornerradius=4),
                    text=[f"{miles(u)} de {miles(c)} · <b>{p:.0f} %</b>" for u, c, p in
                          zip(b.procesos_unico_oferente, b.procesos_con_oferentes, pct)],
                    textposition="outside", textfont=dict(size=13, color=TINTA),
                    cliponaxis=False,
                    hovertemplate="<b>%{y}</b><br>%{x:,.0f} procesos con ofertas<extra></extra>")
        fig.add_bar(y=b.index, x=b.procesos_unico_oferente, orientation="h",
                    name="Con un solo oferente",
                    marker=dict(color=AZUL, cornerradius=4), width=0.5,
                    customdata=pct,
                    hovertemplate=("<b>%{y}</b><br>%{x:,.0f} con un solo oferente "
                                   "(%{customdata:.0f} %)<extra></extra>"))
        fig.update_layout(barmode="overlay", bargap=0.3)
        fig.update_xaxes(showticklabels=False,
                         range=[0, b.procesos_con_oferentes.max() * 2.0])
        fig.update_yaxes(tickfont=dict(size=13, color=TINTA_2))
        mostrar(fig)
        fuente(f"Tabla oro <code>mercado_mensual</code>. "
               f"{'*' if a1 == a_max else ''}{a1}{': enero a noviembre' if a1 == a_max else ''}.")


# ================================================================ 3 · OBJETIVO
OBJETIVOS = [
    ("Datos", "Juan Diego Acuña",
     "Montar un pipeline en AWS que traiga a diario los datos de SECOP II, los limpie y "
     "los deje listos para el modelo y el análisis, con controles de calidad y trazabilidad.",
     ["Ingesta diaria verificada 100 % completa contra la fuente en las 4 tablas",
      "10,6 M filas leídas → 625.625 procesos únicos: cada proceso llega repetido una vez por versión y queda una sola fila",
      "Capas bronce, plata y oro sobre Apache Iceberg, con versiones"]),
    ("Modelos", "David Lopera",
     "Entrenar y evaluar modelos que recuperen candidatos, estimen la probabilidad de "
     "ganar y ordenen las recomendaciones, sin usar información del futuro.",
     ["NDCG@10 de 0,462 (+28 % sobre la referencia)",
      "P(gana) calibrada: error de 0,0053",
      "Evaluado una sola vez en un año que el modelo no vio"]),
    ("Producción", "Jacobo Restrepo",
     "Poner los modelos en producción: ejecución diaria automática, publicación segura, "
     "monitoreo y alertas.",
     ["Corrida completa en ≈ 59 minutos, cada día a las 7:30",
      "Publicación todo o nada; si falla, la API sigue con la versión anterior",
      "≈ USD 1,6 por noche"]),
    ("Consulta", "Nicolás Hurtado y José Alejandro Duque",
     "Ofrecer una página web y un dashboard para consultar las recomendaciones y analizar "
     "el mercado de contratación pública.",
     ["API pública con respuesta de ≈ 100 ms",
      "Página web de consulta por empresa",
      "Este dashboard, construido con consultas a la capa oro"]),
]


def seccion_objetivo():
    encabezado(2, "Recomendar a cada empresa, todos los días y sin intervención manual, "
                  "los procesos donde tiene interés y opción de ganar",
               "Con su probabilidad de ganar, y disponible por una API y una página web. "
               "Lo dividimos en cuatro objetivos, uno por área del equipo. Elige uno para "
               "ver qué entregó:")
    nombres = [o[0] for o in OBJETIVOS]
    elegido = st.segmented_control("Objetivo específico", nombres, default=nombres[0],
                                   key="objetivo", label_visibility="collapsed") \
        or nombres[0]
    c = st.columns(4)
    for i, (col, (t, quien, _, _)) in enumerate(zip(c, OBJETIVOS)):
        tarjeta(col, t, quien, kicker=f"Objetivo {i + 1}", activa=t == elegido)
    st.write("")
    t, quien, texto, evidencia = OBJETIVOS[nombres.index(elegido)]
    c = st.columns([5, 5], gap="large")
    with c[0]:
        html(f"<div class='sub'>{t}</div><div class='bajada'>{texto}</div>"
             f"<div class='g-det'>Responsable: <b>{quien}</b></div>")
    with c[1]:
        html("<div class='sub'>Qué entregó</div>")
        nota("<br>".join(f"✓ {e}" for e in evidencia))
    st.write("")
    fuente("Las tres materias en un solo producto: Big Data, aprendizaje automático y "
           "visualización.")


# ================================================================ 5 · ARQUITECTURA Y METODOLOGÍA
# Nodo: (título, subtítulo, x, y, etapa a la que lleva un clic)
NODOS = {
    "fuente":   ("datos.gov.co", "API Socrata · 4 tablas", 0.9, 3.9, "Ingesta"),
    "sfn":      ("Step Functions", "dispara la corrida 7:30", 3.0, 5.25, "Ingesta"),
    "ingesta":  ("ECS Fargate", "ingesta diaria", 3.0, 3.9, "Ingesta"),
    "bronce":   ("S3 · Bronce", "datos tal como llegan", 5.0, 3.9, "Plata"),
    "plata":    ("Glue Spark · Plata", "limpios, sin duplicados", 7.0, 3.9, "Plata"),
    "oro":      ("Glue · Oro", "estrella + agregados", 9.0, 3.9, "Oro"),
    "athena":   ("Athena", "consultas SQL", 11.0, 3.9, "Este dashboard"),
    "dash":     ("Este dashboard", "Streamlit", 13.1, 3.9, "Este dashboard"),
    "cw":       ("CloudWatch · SNS", "métricas y alertas", 5.0, 5.25, "Monitoreo"),
    "evid":     ("Evidently", "deriva de datos", 11.0, 5.25, "Monitoreo"),
    "modelo":   ("Fargate · LightGBM", "candidatos y P(gana)", 9.0, 1.75, "Modelo"),
    "mlflow":   ("MLflow", "versiones del modelo", 11.0, 1.75, "Modelo"),
    "rds":      ("RDS PostgreSQL", "listas publicadas", 6.0, 1.75, "Publicación"),
    "api":      ("Lambda · FastAPI", "API pública", 3.0, 1.75, "Publicación"),
    "web":      ("Página web", "Vue · por empresa", 0.9, 1.75, "Publicación"),
    "empresas": ("Empresas", "≈ 38.500 al día", 0.9, 0.45, "Publicación"),
}
ARISTAS = [  # (origen, destino, texto, de control o monitoreo)
    ("fuente", "ingesta", "", False), ("ingesta", "bronce", "", False),
    ("bronce", "plata", "", False), ("plata", "oro", "", False),
    ("oro", "athena", "", False), ("athena", "dash", "", False),
    ("oro", "modelo", "", False), ("modelo", "rds", "", False),
    ("rds", "api", "", False), ("api", "web", "", False), ("web", "empresas", "", False),
    ("modelo", "mlflow", "", True), ("sfn", "ingesta", "", True),
    ("sfn", "cw", "", True), ("oro", "evid", "", True),
]
ETAPAS = {
    "Todo": (list(NODOS), "La cadena completa corre sola cada mañana y termina en ≈ 59 "
             "minutos. Los datos entran arriba a la izquierda y las recomendaciones salen "
             "abajo a la izquierda, hacia las empresas.",
             "Si un paso crítico falla, no se publica nada y la API sigue sirviendo la "
             "versión anterior."),
    "Ingesta": (["fuente", "sfn", "ingesta", "bronce"],
                "A las 7:30, Step Functions dispara la ingesta: se descargan de "
                "datos.gov.co los últimos 45 días de las 4 tablas, por fecha de negocio.",
                "La ingesta original traía solo el 3 % de lo nuevo; rediseñada, hoy se "
                "verifica 100 % completa."),
    "Plata": (["bronce", "plata"],
              "Glue (Spark) limpia, tipa y quita duplicados. Unifica la identidad de cada "
              "proveedor; las pocas filas con errores se apartan con su motivo.",
              "10,6 M filas leídas → 625.625 procesos únicos."),
    "Oro": (["plata", "oro", "athena"],
            "Modelo estrella (6 dimensiones, 3 hechos) y tablas agregadas sobre Apache "
            "Iceberg: cada tabla guarda versiones y se consulta con Athena.",
            "Cada entrenamiento se puede reproducir con los datos tal como estaban."),
    "Modelo": (["oro", "modelo", "mlflow"],
               "Recupera 150 candidatos por empresa, calcula 106 variables, estima P(gana) "
               "y arma las dos listas. MLflow guarda cada versión del modelo.",
               "97 millones de parejas posibles → 150 candidatos por empresa."),
    "Publicación": (["modelo", "rds", "api", "web", "empresas"],
                    "Las listas se publican de forma atómica (todo o nada) en PostgreSQL y "
                    "se sirven por una API pública que consume la página web.",
                    "Respuesta de la API ≈ 100 ms."),
    "Este dashboard": (["oro", "athena", "dash"],
                       "Las gráficas de este dashboard salen de tablas de la capa oro "
                       "consultadas con Athena y exportadas a CSV.",
                       "Las consultas están abajo, en «Consultas a la capa oro»."),
    "Monitoreo": (["sfn", "cw", "oro", "evid"],
                  "CloudWatch y SNS mandan alertas por correo; Evidently vigila la deriva "
                  "de los datos. No hay credenciales guardadas en el código.",
                  "Cada recomendación se rastrea hasta su versión de datos y de modelo."),
}
ORDEN_NODOS = list(NODOS)
BW, BH = 1.72, 0.82          # tamaño de cada caja en unidades del diagrama


def caja(x, y, w, h, r=0.12):
    """Ruta SVG de un rectángulo redondeado centrado en (x, y)."""
    x0, x1, y0, y1 = x - w / 2, x + w / 2, y - h / 2, y + h / 2
    return (f"M{x0 + r},{y0} L{x1 - r},{y0} Q{x1},{y0} {x1},{y0 + r} "
            f"L{x1},{y1 - r} Q{x1},{y1} {x1 - r},{y1} L{x0 + r},{y1} "
            f"Q{x0},{y1} {x0},{y1 - r} L{x0},{y0 + r} Q{x0},{y0} {x0 + r},{y0} Z")


def borde(xa, ya, xb, yb):
    """Punto donde la recta de A a B sale de la caja centrada en A."""
    dx, dy = xb - xa, yb - ya
    t = min((BW / 2 + 0.06) / abs(dx) if dx else 9e9, (BH / 2 + 0.06) / abs(dy) if dy else 9e9)
    return xa + dx * t, ya + dy * t


def diagrama(etapa: str) -> go.Figure:
    activos = set(ETAPAS[etapa][0])
    fig = go.Figure()
    # contenedores: nube de AWS y lago de datos
    fig.add_shape(type="path", path=caja(7.05, 3.3, 10.1, 5.25, 0.25),
                  line=dict(color=AZUL_OSC, width=1.5, dash="dash"), fillcolor="rgba(0,0,0,0)",
                  layer="below")
    fig.add_annotation(x=2.15, y=5.82, text="<b>AWS Cloud · us-east-1</b>", showarrow=False,
                       xanchor="left", font=dict(color=AZUL_OSC, size=13))
    fig.add_shape(type="path", path=caja(7.0, 3.82, 6.2, 1.5, 0.18),
                  line=dict(color="#c9d6ec", width=1), fillcolor="#f2f6fc", layer="below")
    fig.add_annotation(x=4.0, y=4.47, text="Lago de datos en S3 · Apache Iceberg",
                       showarrow=False, xanchor="left", font=dict(color=TINTA_2, size=11))
    # flechas
    for a, b, etq, disc in ARISTAS:
        xa, ya, xb, yb = NODOS[a][2], NODOS[a][3], NODOS[b][2], NODOS[b][3]
        on = a in activos and b in activos
        sx, sy = borde(xa, ya, xb, yb)
        ex, ey = borde(xb, yb, xa, ya)
        fig.add_annotation(x=ex, y=ey, ax=sx, ay=sy, xref="x", yref="y", axref="x",
                           ayref="y", showarrow=True, arrowhead=2, arrowsize=1.1,
                           arrowwidth=2.4 if on else 1.2,
                           arrowcolor=AZUL_OSC if on else "#c6c4bd", text="")
        if etq:
            fig.add_annotation(x=(sx + ex) / 2, y=(sy + ey) / 2 - 0.22, text=etq,
                               showarrow=False, font=dict(size=11, color=TINTA_2))
    # cajas
    for n in ORDEN_NODOS:
        t, sub, x, y, _ = NODOS[n]
        on = n in activos
        fig.add_shape(type="path", path=caja(x, y, BW, BH),
                      fillcolor=AZUL if on else "#f1f0ed",
                      line=dict(color=AZUL_OSC if on else "#d3d1ca", width=1.2))
        fig.add_annotation(x=x, y=y, showarrow=False,
                           text=f"<b>{t}</b><br><span style='font-size:11px'>{sub}</span>",
                           font=dict(size=13, color="white" if on else "#7d7c76"))
    # capa invisible para el hover y el clic
    fig.add_scatter(x=[NODOS[n][2] for n in ORDEN_NODOS], y=[NODOS[n][3] for n in ORDEN_NODOS],
                    mode="markers", marker=dict(size=46, symbol="square",
                                                color="rgba(0,0,0,0)"),
                    unselected=dict(marker=dict(opacity=1)),
                    hovertext=[f"<b>{NODOS[n][0]}</b><br>{NODOS[n][1]}<br>"
                               f"<i>clic: ver etapa {NODOS[n][4]}</i>" for n in ORDEN_NODOS],
                    hoverinfo="text")
    fig.update_layout(height=440, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor=FONDO,
                      plot_bgcolor=FONDO, showlegend=False, dragmode=False,
                      hoverlabel=dict(bgcolor="white", font_size=13, font_color=TINTA))
    fig.update_xaxes(range=[-0.1, 14.1], visible=False, fixedrange=True)
    fig.update_yaxes(range=[-0.05, 6.05], visible=False, fixedrange=True)
    return fig


def seccion_arquitectura():
    encabezado(4, f"Una cadena automática en AWS que cada mañana va de los datos abiertos "
                  f"a las recomendaciones en ≈ {CIFRAS['minutos_corrida']} minutos",
               "Recorre la arquitectura por etapa: el diagrama resalta los servicios que "
               "intervienen y explica qué pasa en cada una.")
    # un clic en un servicio del diagrama cambia la etapa (se procesa antes del selector)
    sel = st.session_state.get("arq")
    puntos = sel.selection.points if sel and sel.selection else []
    firma = tuple(p["point_index"] for p in puntos)
    if puntos and firma != st.session_state.get("arq_ultima"):
        st.session_state.etapa = NODOS[ORDEN_NODOS[puntos[0]["point_index"]]][4]
    st.session_state.arq_ultima = firma

    etapa = st.segmented_control("Etapa", list(ETAPAS), default="Todo", key="etapa",
                                 label_visibility="collapsed") or "Todo"
    st.plotly_chart(diagrama(etapa), width="stretch", key="arq", on_select="rerun",
                    selection_mode="points", config={"displayModeBar": False})
    _, texto, dato = ETAPAS[etapa]
    c = st.columns([6, 4], gap="large")
    html(f"<div class='g-tit'>{etapa}</div><div class='card-c' style='font-size:1rem'>"
         f"{texto}</div>", c[0])
    dato_clave(dato, c[1])
    st.write("")

    c = st.columns(4)
    c[0].metric("Filas leídas → procesos",
                f"{miles(CIFRAS['filas_fuente_millones'], 1)} M → "
                f"{miles(CIFRAS['procesos'] / 1000)} mil",
                help="La fuente repite versiones de cada proceso; plata deja una fila por "
                     "proceso; las filas con errores se apartan con su motivo.")
    c[1].metric("Parejas posibles → candidatos",
                f"{CIFRAS['parejas_millones']} M → {CIFRAS['candidatos']}",
                help="Puntuar todas las parejas empresa-proceso serían 97 millones al día. "
                     "Primero se recuperan 150 candidatos por empresa y luego se ordenan, "
                     "como en YouTube o Netflix.")
    c[2].metric("Corrida diaria", f"≈ {CIFRAS['minutos_corrida']} min",
                help="De la ingesta a la publicación, de 7:30 a 8:30 a. m.")
    c[3].metric("Costo por noche", f"≈ USD {miles(CIFRAS['usd_noche'], 1)}",
                help=f"Más ≈ USD {CIFRAS['usd_mes_bd']} al mes de base de datos. Los "
                     "servicios solo cobran mientras se usan.")

    st.write("")
    with st.expander("Consultas a la capa oro: así se construyó este dashboard",
                     expanded=tecnico()):
        st.markdown(
            "Las gráficas salen de **tablas de la capa oro** (base `secop_gold`), "
            "consultadas con **Athena**. Cada consulta se exporta a un CSV en `datos/`, y "
            "los porcentajes se calculan en el dashboard a partir de conteos, para que se "
            "puedan volver a agregar sin error.")
        q = consultas()
        tabs = st.tabs(list(q.keys()))
        for tab, (archivo, (desc, sql)) in zip(tabs, q.items()):
            with tab:
                df = pd.read_csv(DATOS / archivo)
                st.caption(f"{desc} · {len(df)} filas → datos/{archivo}")
                st.code(sql, language="sql")
                if tecnico():
                    st.dataframe(df.head(8), hide_index=True, width="stretch")


# ================================================================ 4 · RESULTADOS
def evidencia(col, objetivo: str, cifra: str, explicacion: str, detalle: str):
    """Tarjeta: una parte del objetivo y el dato que demuestra que se cumple."""
    html(f"<div class='card' style='min-height:205px'><div class='card-k'>{objetivo}</div>"
         f"<div class='grande' style='font-size:2rem'>{nbsp(cifra)}</div>"
         f"<div class='card-t' style='margin-top:.2rem'>{nbsp(explicacion)}</div>"
         f"<div class='card-p'>{nbsp(detalle)}</div></div>", col)


def seccion_resultados():
    h = des[des.lista == "historial"].sort_values("fecha_corte").copy()
    h["acum"] = 100 * h.se_presento.cumsum() / h.participaciones_reales.cumsum()
    ult = h.iloc[-1]
    f0, f1 = h.fecha_corte.min(), h.fecha_corte.max()
    dias = h.fecha_corte.nunique()
    dias_cal = (f1 - f0).days + 1
    pct_sem = h.acum.iloc[-1]
    recall = met.set_index("metrica")
    r_mod = float(recall.loc["Recall@10", "modelo"]) * 100
    r_ref = float(recall.loc["Recall@10", "referencia"]) * 100

    encabezado(3, f"De cada 10 ofertas que hicieron las empresas, {pct_sem / 10:.0f} eran "
                  f"procesos que ya les habíamos recomendado",
               "Revisamos cada parte del objetivo con datos reales: lo que el sistema "
               "recomendó cada día y lo que las empresas hicieron después en SECOP II.")

    # ---- el objetivo, parte por parte
    c = st.columns(4)
    evidencia(c[0], "A cada empresa", f"{miles(ult.empresas)}",
              "empresas recibieron sus listas",
              f"el {f1.day} de noviembre, con ≈ {ult.recomendaciones / ult.empresas:.0f} "
              f"procesos cada una")
    evidencia(c[1], "Todos los días, sin intervención", f"{dias} de {dias_cal} días",
              "con listas publicadas",
              f"del {f0.day} al {f1.day} de noviembre; cada corrida tarda ≈ "
              f"{CIFRAS['minutos_corrida']} min")
    evidencia(c[2], "Donde tiene interés", f"{pct_sem / 10:.0f} de cada 10",
              "ofertas reales estaban en su lista",
              f"{miles(h.se_presento.sum())} de {miles(h.participaciones_reales.sum())} "
              f"ofertas en la semana")
    evidencia(c[3], "Y opción de ganar", f"≈ {miles(CIFRAS['ece'] * 100, 1)} puntos",
              "de error promedio en la probabilidad de ganar",
              "si el modelo dice 20 %, la empresa gana ≈ 2 de cada 10 veces")

    st.write("")
    with st.container(key="como_medimos"):
        with st.expander("¿Cómo lo medimos?"):
            st.markdown(
                "- **En la vida real (producción):** cada día cruzamos lo que el sistema le "
                "recomendó a cada empresa con las ofertas que esa empresa hizo de verdad en "
                "SECOP II. Si una empresa se presentó a un proceso que estaba en su lista, "
                "es un acierto.\n"
                "- **En una prueba con datos que el modelo nunca vio:** lo entrenamos con "
                "datos hasta junio de 2025 y lo probamos una sola vez con el año siguiente, "
                "como si estuviéramos en el pasado recomendando a ciegas.\n"
                "- **Sin el modelo vs. con el modelo:** comparamos contra un filtro simple "
                "que solo escoge candidatos parecidos, sin ordenarlos con el modelo.")
            if tecnico():
                st.markdown("**Métricas técnicas de la prueba (lista 1)**")
                st.dataframe(pd.DataFrame({
                    "Métrica": ["Precision@10", "Recall@10", "NDCG@10",
                                "Oportunidades plausibles (lista 2)", "ECE de P(gana)"],
                    "Modelo": ["0,110", "0,566", "0,462", "67,7 %", "0,0053"],
                    "Referencia": ["0,086", "0,455", "0,362", "62,3 % (azar)", "—"],
                }), hide_index=True, width="stretch")

    # ---- dos gráficas que lo respaldan
    st.write("")
    c = st.columns(2, gap="large")
    with c[0]:
        titulo_grafica(f"En la vida real acierta igual que en la prueba: "
                       f"{miles(pct_sem, 1)} % frente a {miles(r_mod, 1)} %",
                       "% de las ofertas reales que ya estaban en la lista de esa empresa")
        if not tecnico():
            fig = base_fig(320)
            fig.add_bar(x=["En la prueba<br>(un año que el modelo no vio)",
                           f"En la vida real<br>({f0.day} al {f1.day} de noviembre)"],
                        y=[r_mod, pct_sem], marker=dict(color=[NEUTRO, AZUL], cornerradius=4),
                        text=[f"{miles(r_mod, 1)} %", f"<b>{miles(pct_sem, 1)} %</b>"],
                        textposition="outside", textfont=dict(size=18, color=TINTA),
                        cliponaxis=False, hoverinfo="skip")
            fig.update_yaxes(range=[0, 100], showticklabels=False)
            fig.update_xaxes(tickfont=dict(size=13, color=TINTA_2))
            fig.update_layout(bargap=0.45)
            mostrar(fig)
        else:
            fig = base_fig(320)
            fig.add_hline(y=r_mod, line=dict(color=TINTA_3, width=1.5, dash="dot"))
            fig.add_annotation(x=f1, y=r_mod, text=f"Prueba<br>{miles(r_mod, 1)} %",
                               xshift=14, xanchor="left", showarrow=False, align="left",
                               font=dict(color=TINTA_2, size=13))
            tam = 7 + 12 * (h.participaciones_reales / h.participaciones_reales.max()) ** 0.5
            fig.add_scatter(x=h.fecha_corte, y=100 * h.cobertura, mode="markers",
                            marker=dict(size=tam, color="#A9C1EA"),
                            customdata=h[["participaciones_reales", "se_presento"]],
                            hovertemplate=("%{x|%d nov.} (solo ese día): %{y:.1f} %<br>"
                                           "%{customdata[1]} de %{customdata[0]} ofertas"
                                           "<extra></extra>"))
            fig.add_scatter(x=h.fecha_corte, y=h.acum, mode="lines+markers",
                            line=dict(color=AZUL, width=3), marker=dict(size=8, color=AZUL),
                            hovertemplate="Acumulado al %{x|%d nov.}: %{y:.1f} %<extra></extra>")
            fig.update_yaxes(ticksuffix=" %", range=[0, 100], dtick=25, showgrid=True,
                             gridcolor=REJILLA)
            fig.update_xaxes(tickvals=h.fecha_corte,
                             ticktext=[f"{d.day} nov." for d in h.fecha_corte],
                             range=[f0 - pd.Timedelta(hours=12), f1 + pd.Timedelta(days=1.3)])
            mostrar(fig)
            st.caption("Línea: acumulado de la semana · puntos: cada día (tamaño = ofertas).")
        fuente("Tabla oro <code>desempeno_recomendaciones</code>: recomendaciones de cada "
               "día cruzadas con las ofertas reales en SECOP II.")
    with c[1]:
        titulo_grafica(f"Con el modelo encontramos {r_mod - r_ref:.0f} procesos más de "
                       f"cada 100 que con un filtro simple",
                       "De cada 100 procesos a los que una empresa se presentó, cuántos "
                       "estaban entre sus 10 primeras recomendaciones")
        fig = base_fig(320)
        fig.add_bar(y=["Con el modelo", "Solo un filtro simple"], x=[r_mod, r_ref],
                    orientation="h", marker=dict(color=[AZUL, NEUTRO], cornerradius=4),
                    text=[f"<b>{r_mod:.0f}</b> de 100", f"{r_ref:.0f} de 100"],
                    textposition="outside", textfont=dict(size=16, color=TINTA),
                    cliponaxis=False, hoverinfo="skip")
        fig.update_xaxes(range=[0, 100], showticklabels=False)
        fig.update_yaxes(tickfont=dict(size=14, color=TINTA_2), autorange="reversed")
        fig.update_layout(bargap=0.55)
        mostrar(fig)
        fuente(f"Prueba con datos de jul. 2025 a jul. 2026 que el modelo nunca vio. Mejora "
               f"de {100 * (r_mod / r_ref - 1):.0f} % sobre el filtro simple.")

    # ---- tiempo con y sin el recomendador (estimación)
    u = des[des.fecha_corte == des.fecha_corte.max()].set_index("lista")
    por_empresa = sum(u.loc[l, "recomendaciones"] / u.loc[l, "empresas"]
                      for l in ["historial", "oportunidad"] if l in u.index)
    html("<div class='sub'>¿Cuánto tiempo le ahorra a una empresa?</div>")
    c = st.columns([4, 7], gap="large")
    with c[0]:
        minutos = st.slider("Minutos que tarda en leer un proceso", 1, 15, 3, key="min_res",
                            help="El mismo supuesto de la calculadora de la sección 1.")
        sin_h = CIFRAS["procesos_abiertos_dia"] * minutos / 60
        con_min = por_empresa * minutos
        ahorro = 100 * (1 - con_min / 60 / sin_h)
        html(f"<div class='grande'>{miles(sin_h)} h → {miles(con_min)} min</div>"
             f"<div class='g-det'>al día. En vez de leer los ≈ "
             f"{miles(CIFRAS['procesos_abiertos_dia'])} procesos abiertos, la empresa lee sus "
             f"≈ {por_empresa:.0f} recomendados: <b>{miles(ahorro, 0)} % menos tiempo</b>, y "
             f"ahí ya están 6 de cada 10 procesos a los que termina presentándose.</div>")
    with c[1]:
        titulo_grafica(f"Sin el recomendador, {miles(sin_h)} horas al día; con él, "
                       f"{miles(con_min)} minutos",
                       "Tiempo diario de lectura estimado para una empresa")
        fig = base_fig(210)
        fig.add_bar(y=[f"Sin el recomendador · ≈ {miles(CIFRAS['procesos_abiertos_dia'])} "
                       f"procesos", f"Con el recomendador · ≈ {por_empresa:.0f} procesos"],
                    x=[sin_h, con_min / 60], orientation="h",
                    marker=dict(color=[NEUTRO, AZUL], cornerradius=4),
                    text=[f"{miles(sin_h)} h", f"{miles(con_min)} min"],
                    textposition="outside", textfont=dict(size=15, color=TINTA),
                    cliponaxis=False, hoverinfo="skip")
        fig.update_xaxes(range=[0, sin_h * 1.2], showticklabels=False)
        fig.update_yaxes(tickfont=dict(size=13, color=TINTA_2), autorange="reversed")
        fig.update_layout(bargap=0.4)
        mostrar(fig)
        fuente(f"Estimación, no medición de uso: supone el mismo tiempo por proceso. "
               f"Recomendados por empresa ({por_empresa:.0f}) según la tabla oro "
               f"<code>desempeno_recomendaciones</code> (listas 1 y 2 del "
               f"{des.fecha_corte.max().day} de noviembre).")


# ================================================================ 6 · HALLAZGOS Y CONCLUSIONES
def grafica_unspsc(medida: str) -> go.Figure:
    d = cal.copy()
    d["pct"] = 100 * d.procesos_sin_categoria / d.procesos_publicados
    fig = base_fig(280)
    if medida == "%":
        antes = d[d.pct < 50]
        fig.add_scatter(x=d.semana_inicio, y=d.pct, mode="lines+markers",
                        line=dict(color=AZUL, width=2.5), marker=dict(size=7, color=AZUL),
                        customdata=d[["procesos_sin_categoria", "procesos_publicados"]],
                        hovertemplate=("Semana del %{x|%d/%m}: %{y:.1f} %<br>"
                                       "%{customdata[0]:,} de %{customdata[1]:,} procesos"
                                       "<extra></extra>"))
        fig.add_annotation(x=antes.semana_inicio.iloc[len(antes) // 2], y=antes.pct.mean(),
                           yshift=22, showarrow=False, font=dict(color=TINTA_2, size=14),
                           text=f"≈ {antes.pct.mean():.0f} % sin categoría")
        fig.add_annotation(x=d.semana_inicio.iloc[-1], y=d.pct.iloc[-1], yshift=-24,
                           xanchor="right", showarrow=False, font=dict(color=TINTA, size=14),
                           text=f"<b>{miles(d.pct.iloc[-1], 1)} %</b>")
        fig.update_yaxes(ticksuffix=" %", range=[0, 105], dtick=25, showgrid=True,
                         gridcolor=REJILLA)
    else:
        con = d.procesos_publicados - d.procesos_sin_categoria
        fig.add_bar(x=d.semana_inicio, y=con, name="Con categoría",
                    marker=dict(color=NEUTRO), hovertemplate="Con categoría: %{y:,}<extra></extra>")
        fig.add_bar(x=d.semana_inicio, y=d.procesos_sin_categoria, name="Sin categoría",
                    marker=dict(color=AZUL),
                    hovertemplate="Sin categoría: %{y:,}<extra></extra>")
        fig.update_layout(barmode="stack", bargap=0.15, showlegend=True,
                          legend=dict(orientation="h", y=1.12, x=0, font=dict(size=13)))
        fig.update_yaxes(showgrid=True, gridcolor=REJILLA, title=None)
    meses = d.semana_inicio.dt.to_period("M").drop_duplicates().dt.to_timestamp()
    fig.update_xaxes(tickvals=meses, ticktext=[MESES[m.month - 1] for m in meses])
    return fig


def seccion_6():
    # --- datos
    tot = merc.groupby("anio")[["procesos_unico_oferente", "procesos_con_oferentes"]].sum()
    tot["pct"] = 100 * tot.procesos_unico_oferente / tot.procesos_con_oferentes
    a0, a1 = int(tot.index.min()), int(tot.index.max())
    h = des[des.lista == "historial"]
    aciertos, ofertas = int(h.se_presento.sum()), int(h.participaciones_reales.sum())
    pct_ok = 100 * aciertos / ofertas
    u = des[des.fecha_corte == des.fecha_corte.max()].set_index("lista")
    por_empresa = sum(u.loc[l, "recomendaciones"] / u.loc[l, "empresas"]
                      for l in ["historial", "oportunidad"] if l in u.index)
    empresas = int(u.loc["historial", "empresas"])
    abiertos = CIFRAS["procesos_abiertos_dia"]

    encabezado(5, "Cada mañana, más de 38 mil empresas reciben las oportunidades que antes "
                  "se les pasaban",
               "Partimos de un problema real, construimos una solución que ya funciona y "
               "medimos que cumple lo que prometimos.")

    def bloque_cierre(col, paso, cifra, texto):
        html(f"<div class='card-k'>{paso}</div>"
             f"<div class='grande' style='font-size:2.2rem'>{nbsp(cifra)}</div>"
             f"<div class='card-t' style='min-height:4.8rem'>{nbsp(texto)}</div>", col)

    c = st.columns(3, gap="large")
    # 1. Problema
    with c[0]:
        bloque_cierre(st, "1 · El problema", f"{tot.pct.iloc[0]:.0f} % → {tot.pct.iloc[-1]:.0f} %",
                      f"procesos con un solo oferente entre {a0} y {a1}: cada vez "
                      f"compiten menos empresas")
        fig = base_fig(190)
        fig.add_scatter(x=[str(a) for a in tot.index], y=tot.pct, mode="lines+markers",
                        line=dict(color=AZUL, width=3), marker=dict(size=7, color=AZUL),
                        fill="tozeroy", fillcolor="rgba(51,102,204,.10)",
                        hovertemplate="%{x}: %{y:.1f} % con un solo oferente<extra></extra>")
        fig.update_yaxes(range=[0, 60], ticksuffix=" %", dtick=20, showgrid=True,
                         gridcolor=REJILLA)
        fig.update_xaxes(type="category", tickvals=[str(a0), str(a1)])
        mostrar(fig)
    # 2. Solución
    with c[1]:
        bloque_cierre(st, "2 · La solución", f"{miles(abiertos)} → {por_empresa:.0f}",
                      "procesos para revisar cada día: el sistema escoge por cada empresa")
        fig = base_fig(190)
        fig.add_bar(y=["Sin el sistema", "Con el sistema"], x=[abiertos, por_empresa],
                    orientation="h", marker=dict(color=[NEUTRO, AZUL], cornerradius=4),
                    text=[f"{miles(abiertos)}", f"{por_empresa:.0f}"],
                    textposition="outside", textfont=dict(size=13, color=TINTA),
                    cliponaxis=False, hoverinfo="skip")
        fig.update_xaxes(range=[0, abiertos * 1.25], showticklabels=False)
        fig.update_yaxes(autorange="reversed", tickfont=dict(size=13, color=TINTA_2))
        fig.update_layout(bargap=0.4)
        mostrar(fig)
    # 3. Resultado
    with c[2]:
        bloque_cierre(st, "3 · El resultado", f"{pct_ok / 10:.0f} de cada 10",
                      "ofertas reales eran procesos que ya le habíamos recomendado a esa "
                      "empresa")
        fig = base_fig(190)
        fig.add_pie(values=[aciertos, ofertas - aciertos], hole=0.68, sort=False,
                    marker=dict(colors=[AZUL, "#e3e1da"], line=dict(color=FONDO, width=2)),
                    labels=["Estaban en su lista", "No estaban"], textinfo="none",
                    hovertemplate="%{label}: %{value:,} ofertas<extra></extra>")
        fig.add_annotation(text=f"<b>{miles(pct_ok, 0)} %</b><br>"
                                f"<span style='font-size:11px'>{miles(aciertos)} de "
                                f"{miles(ofertas)}</span>",
                           showarrow=False, font=dict(size=20, color=AZUL_OSC))
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        mostrar(fig)

    st.write("")
    html(f"<div class='nota dato' style='font-size:1.25rem; line-height:1.55'>"
         f"Antes, una mipyme tenía que buscar entre <b>{miles(abiertos)} procesos</b> al día. "
         f"Hoy recibe cada mañana <b>{por_empresa:.0f}</b>, con su probabilidad de ganar, y "
         f"en ellos ya están <b>{pct_ok / 10:.0f} de cada 10</b> procesos a los que termina "
         f"presentándose.</div>")

    html("<div class='sub'>Lo que logramos</div>")
    c = st.columns(3)
    tarjeta(c[0], "Un sistema que ya funciona",
            f"No es un prototipo: corre solo cada mañana y hoy atiende a "
            f"{miles(empresas)} empresas, sin que nadie lo opere.", kicker="✓ Construido")
    tarjeta(c[1], "Hecho solo con datos abiertos",
            "Todo sale de SECOP II en datos.gov.co: cualquier persona puede consultar lo que "
            "usamos y verificar los resultados.", kicker="✓ Verificable")
    tarjeta(c[2], "Más empresas, más competencia",
            "Si más empresas encuentran los procesos que les sirven, menos contratos quedan "
            "con un solo oferente y el Estado compra mejor.", kicker="✓ Con impacto")

    st.write("")
    with st.expander("Retos de los datos que superamos"):
        d = cal.copy()
        d["pct"] = 100 * d.procesos_sin_categoria / d.procesos_publicados
        quiebre = d[d.pct >= 50].iloc[0]
        st.markdown(
            f"- **La categoría desapareció:** desde la semana del {quiebre.semana_inicio.day} "
            f"de septiembre, SECOP dejó de publicar la categoría de los procesos (del ≈ 13 % "
            f"al {d.pct.iloc[-1]:.0f} % sin categoría). La inferimos desde la descripción.\n"
            "- **La ingesta estaba incompleta:** solo traía el 3 % de lo nuevo; la rediseñamos "
            "y hoy se verifica 100 % completa.\n"
            "- **Valores imposibles:** 766 contratos superan los 100 mil millones de pesos (el "
            "mayor dice 7,7 mil billones); se marcan como atípicos.")
        if tecnico():
            mostrar(grafica_unspsc("%"))
    with st.expander("Limitaciones y trabajo futuro", expanded=tecnico()):
        st.markdown(
            "- SECOP no publica el precio que ofertó cada empresa, la variable que más pesa "
            "para ganar.\n"
            "- Reentrenar el modelo con datos nuevos y sin depender de la categoría UNSPSC.\n"
            "- Recarga completa semanal, para actualizar procesos de más de 45 días.\n"
            "- Recomendaciones para empresas que nunca han participado en SECOP.")


# ================================================================ render
[seccion_1, seccion_2, seccion_objetivo, seccion_resultados, seccion_arquitectura,
 seccion_6][st.session_state.sec]()
pie_navegacion()
