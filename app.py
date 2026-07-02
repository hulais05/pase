"""
PASE — el pase de tu flota a la mina.
Demo de gestión de flota para contratistas mineros del NOA.
Mantené tu flota habilitada para entrar al yacimiento.

Ejecutar:  streamlit run app.py
Datos 100% ficticios (ver data.py).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data import (
    EMPRESA, HOY, DOCS_CRITICOS, DOCS_TODOS, DIAS_ALERTA,
    cargar_flota, cargar_siniestros, estado_doc,
)

# ----------------------------------------------------------------------------
st.set_page_config(page_title="PASE · Gestión de flota", page_icon="🛡️", layout="wide")

VERDE, AMARILLO, ROJO, GRIS = "#2e7d32", "#f9a825", "#c62828", "#607d8b"

COLOR_ESTADO = {
    "HABILITADO": VERDE, "POR VENCER": AMARILLO, "NO HABILITADO": ROJO,
    "Vigente": VERDE, "Por vencer": AMARILLO, "Vencido": ROJO,
}
EMOJI_ESTADO = {
    "HABILITADO": "🟢", "POR VENCER": "🟡", "NO HABILITADO": "🔴",
    "Vigente": "🟢", "Por vencer": "🟡", "Vencido": "🔴",
}

st.markdown("""
<style>
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, header {visibility: hidden;}
/* el botón para re-desplegar el sidebar vive dentro del header: mantenerlo visible */
[data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"],
[data-testid="stExpandSidebarButton"] {visibility: visible;}
.block-container {padding-top: 2rem;}
.kpi-card {background:#ffffff;border:1px solid #e6e6e6;border-radius:14px;
           padding:18px 20px;box-shadow:0 1px 4px rgba(0,0,0,.06);}
.kpi-num {font-size:2.1rem;font-weight:700;line-height:1.1;}
.kpi-lbl {font-size:.8rem;color:#666;text-transform:uppercase;letter-spacing:.04em;}
.badge {padding:3px 12px;border-radius:20px;color:#fff;font-weight:600;font-size:.85rem;}
.doc-row {padding:8px 0;border-bottom:1px solid #eee;}
</style>
""", unsafe_allow_html=True)


def moneda(x):
    return f"${x:,.0f}".replace(",", ".")


def kpi(col, num, lbl, color="#222"):
    col.markdown(
        f'<div class="kpi-card"><div class="kpi-num" style="color:{color}">{num}</div>'
        f'<div class="kpi-lbl">{lbl}</div></div>',
        unsafe_allow_html=True,
    )


def badge(texto, color):
    return f'<span class="badge" style="background:{color}">{texto}</span>'


# ----------------------------------------------------------------------------
@st.cache_data
def _flota():
    return cargar_flota()


@st.cache_data
def _siniestros():
    return cargar_siniestros()


flota = _flota()
siniestros = _siniestros()

# ----------------------------------------------------------------------------
# Personalización por URL: ?c=<clave> muestra el demo a nombre de un prospecto.
# El nombre real solo aparece con su link; el demo público queda genérico.
_CLIENTES = {"maga": "Grupo Maga"}
_c = st.query_params.get("c", "")
if _c in _CLIENTES:
    EMPRESA = _CLIENTES[_c]

# ----------------------------------------------------------------------------
# Sidebar
st.sidebar.markdown("## 🛡️ **PASE**")
st.sidebar.caption("El pase de tu flota a la mina")
st.sidebar.markdown(f"**Cliente:** {EMPRESA}")
st.sidebar.markdown(f"**Fecha:** {HOY.strftime('%d/%m/%Y')}")
st.sidebar.divider()
_VISTAS = ["🚦 Semáforo de Flota", "🛻 Ficha de Vehículo", "💥 Siniestros", "📊 Reporte Ejecutivo"]
# permite abrir una vista directo por URL: ?v=0..3 (links directos a cada pantalla)
try:
    _idx = int(st.query_params.get("v", 0))
    _idx = _idx if 0 <= _idx < len(_VISTAS) else 0
except (ValueError, TypeError):
    _idx = 0
vista = st.sidebar.radio("Navegación", _VISTAS, index=_idx)
st.sidebar.divider()
if _c in _CLIENTES:
    st.sidebar.caption(f"Demo preparado para {EMPRESA} · datos ficticios · ESG Consulting NOA")
else:
    st.sidebar.caption("Demo con datos ficticios · ESG Consulting NOA")


# ============================================================================
# VISTA 1 — SEMÁFORO DE FLOTA
# ============================================================================
if vista.startswith("🚦"):
    st.title("🚦 Semáforo de Flota")
    st.caption("¿Qué unidades pueden ingresar hoy al yacimiento?")

    total = len(flota)
    habil = (flota["Estado"] == "HABILITADO").sum()
    por_vencer = (flota["Estado"] == "POR VENCER").sum()
    no_habil = (flota["Estado"] == "NO HABILITADO").sum()
    pct_habil = round(100 * habil / total)

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, total, "Unidades en flota")
    kpi(c2, f"{habil}", "🟢 Habilitadas", VERDE)
    kpi(c3, f"{por_vencer}", "🟡 Por vencer (≤30 días)", AMARILLO)
    kpi(c4, f"{no_habil}", "🔴 NO habilitadas", ROJO)

    st.markdown("")
    if no_habil > 0:
        st.error(
            f"⚠️ **{no_habil} unidad(es) no pueden ingresar al yacimiento hoy** "
            f"por documentación vencida. Cada día detenida es facturación perdida."
        )

    # Filtros
    f1, f2 = st.columns(2)
    areas = ["Todas"] + sorted(flota["Área"].unique().tolist())
    area_sel = f1.selectbox("Filtrar por área", areas)
    estados = ["Todos", "NO HABILITADO", "POR VENCER", "HABILITADO"]
    estado_sel = f2.selectbox("Filtrar por estado", estados)

    df = flota.copy()
    if area_sel != "Todas":
        df = df[df["Área"] == area_sel]
    if estado_sel != "Todos":
        df = df[df["Estado"] == estado_sel]

    # ordenar por urgencia (días al venc crítico ascendente)
    df = df.sort_values("Días al venc. crítico")

    st.subheader(f"Unidades ({len(df)})")
    for _, r in df.iterrows():
        col = st.columns([0.7, 2.2, 1.3, 1.6, 1.4])
        col[0].markdown(f"### {EMOJI_ESTADO[r['Estado']]}")
        col[1].markdown(f"**{r['Interno']}** · {r['Marca']} {r['Modelo']}  \n"
                        f"<small>{r['Patente']} · {r['Área']}</small>", unsafe_allow_html=True)
        col[2].markdown(badge(r["Estado"], COLOR_ESTADO[r["Estado"]]), unsafe_allow_html=True)
        dias = r["Días al venc. crítico"]
        if dias < 0:
            txt = f"**{r['Doc. crítico próximo']}** venció hace {abs(dias)} días"
        else:
            txt = f"**{r['Doc. crítico próximo']}** vence en {dias} días"
        col[3].markdown(f"<small>{txt}</small>", unsafe_allow_html=True)
        col[4].markdown(f"<small>Conductor:<br>{r['Conductor']}</small>", unsafe_allow_html=True)


# ============================================================================
# VISTA 2 — FICHA DE VEHÍCULO
# ============================================================================
elif vista.startswith("🛻"):
    st.title("🛻 Ficha de Vehículo (legajo digital)")

    opciones = [f"{r['Interno']} — {r['Marca']} {r['Modelo']} ({r['Patente']})"
                for _, r in flota.iterrows()]
    sel = st.selectbox("Seleccioná una unidad", opciones)
    interno = sel.split(" — ")[0]
    r = flota[flota["Interno"] == interno].iloc[0]

    st.markdown(f"### {EMOJI_ESTADO[r['Estado']]} {r['Interno']} — "
                f"{r['Marca']} {r['Modelo']}  "
                f"{badge(r['Estado'], COLOR_ESTADO[r['Estado']])}", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Patente", r["Patente"])
    c2.metric("Año", int(r["Año"]))
    c3.metric("Área", r["Área"])
    c4.metric("Conductor", r["Conductor"])

    st.divider()
    cizq, cder = st.columns([1.3, 1])

    with cizq:
        st.subheader("📄 Documentación y vencimientos")
        for d in DOCS_TODOS:
            dias = r[f"dias_{d}"]
            fecha = r[f"venc_{d}"]
            est = estado_doc(dias)
            critico = " 🔒" if d in DOCS_CRITICOS else ""
            if dias < 0:
                detalle = f"venció hace {abs(dias)} días"
            else:
                detalle = f"faltan {dias} días"
            st.markdown(
                f'<div class="doc-row">{EMOJI_ESTADO[est]} <b>{d}</b>{critico} '
                f'&nbsp;·&nbsp; vence {fecha.strftime("%d/%m/%Y")} '
                f'&nbsp;<small style="color:#888">({detalle})</small></div>',
                unsafe_allow_html=True,
            )
        st.caption("🔒 = documento exigido por la mina para ingresar al yacimiento")

    with cder:
        st.subheader("🔧 Mantenimiento")
        st.metric("Km actual", f"{r['Km actual']:,.0f}".replace(",", "."))
        km_falta = r["Km al service"]
        st.metric("Próximo service", f"{r['Km próx. service']:,.0f} km".replace(",", "."),
                  delta=f"faltan {km_falta:,.0f} km".replace(",", "."),
                  delta_color="inverse" if km_falta < 2000 else "normal")
        if km_falta < 2000:
            st.warning("⚠️ Service próximo a vencer por kilometraje.")
        st.metric("Costo mantenimiento (12 meses)", moneda(r["Costo mant. anual"]))
        st.metric("Aseguradora", r["Aseguradora"])

    # Siniestros de esta unidad
    sin_u = siniestros[siniestros["Interno"] == interno]
    if len(sin_u):
        st.divider()
        st.subheader("💥 Siniestros de esta unidad")
        st.dataframe(
            sin_u[["Fecha", "Tipo de siniestro", "Estado", "Días abierto", "Costo estimado"]]
            .assign(**{"Costo estimado": sin_u["Costo estimado"].map(moneda)}),
            hide_index=True, width="stretch",
        )


# ============================================================================
# VISTA 3 — SINIESTROS
# ============================================================================
elif vista.startswith("💥"):
    st.title("💥 Gestión de Siniestros")
    st.caption("Seguimiento de denuncias ante aseguradoras hasta el cierre")

    abiertos = siniestros[siniestros["Estado"] != "Cerrado"]
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, len(siniestros), "Siniestros (12 meses)")
    kpi(c2, len(abiertos), "Abiertos", ROJO if len(abiertos) else VERDE)
    prom = round(abiertos["Días abierto"].mean()) if len(abiertos) else 0
    kpi(c3, f"{prom} días", "Promedio abierto", AMARILLO)
    kpi(c4, moneda(siniestros["Costo estimado"].sum()), "Costo total estimado")

    st.markdown("")
    df = siniestros.merge(flota[["Interno", "Marca", "Modelo", "Patente"]], on="Interno")
    df["Vehículo"] = df["Marca"] + " " + df["Modelo"] + " (" + df["Patente"] + ")"
    df = df.sort_values("Días abierto", ascending=False)

    def color_estado(v):
        return f"color:{COLOR_ESTADO.get(v, GRIS)};font-weight:600"

    vis = df[["Interno", "Vehículo", "Fecha", "Tipo de siniestro",
              "Aseguradora", "Estado", "Días abierto", "Costo estimado"]].copy()
    vis["Costo estimado"] = vis["Costo estimado"].map(moneda)
    st.dataframe(
        vis.style.map(color_estado, subset=["Estado"]),
        hide_index=True, width="stretch",
    )

    st.subheader("Siniestros por tipo")
    fig = px.bar(df.groupby("Tipo de siniestro")["Costo estimado"].sum().reset_index(),
                 x="Costo estimado", y="Tipo de siniestro", orientation="h",
                 color_discrete_sequence=[ROJO])
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="")
    st.plotly_chart(fig, width="stretch")


# ============================================================================
# VISTA 4 — REPORTE EJECUTIVO
# ============================================================================
else:
    st.title("📊 Reporte Ejecutivo")
    st.caption(f"{EMPRESA} · al {HOY.strftime('%d/%m/%Y')}")

    total = len(flota)
    habil = (flota["Estado"] == "HABILITADO").sum()
    pct = round(100 * habil / total)
    costo_mant = flota["Costo mant. anual"].sum()
    venc_30 = sum(0 <= flota[f"dias_{d}"].iloc[i] <= DIAS_ALERTA
                  for i in range(total) for d in DOCS_CRITICOS)
    costo_sin = siniestros["Costo estimado"].sum()

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, f"{pct}%", "Flota habilitada", VERDE if pct >= 80 else AMARILLO)
    kpi(c2, venc_30, "Vencimientos próx. 30 días", AMARILLO)
    kpi(c3, moneda(costo_mant), "Costo mant. anual")
    kpi(c4, moneda(costo_sin), "Costo siniestros (12m)")

    st.divider()
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("Estado de habilitación")
        cont = flota["Estado"].value_counts().reindex(
            ["HABILITADO", "POR VENCER", "NO HABILITADO"]).fillna(0)
        fig = go.Figure(go.Pie(
            labels=cont.index, values=cont.values, hole=.55,
            marker_colors=[VERDE, AMARILLO, ROJO]))
        fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, width="stretch")

    with g2:
        st.subheader("Costo de mantenimiento por tipo")
        por_tipo = flota.groupby("Tipo")["Costo mant. anual"].sum().reset_index()
        fig = px.bar(por_tipo, x="Tipo", y="Costo mant. anual",
                     color_discrete_sequence=["#1565c0"])
        fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), xaxis_title="")
        st.plotly_chart(fig, width="stretch")

    st.subheader("Próximos vencimientos críticos (ordenados por urgencia)")
    filas = []
    for _, r in flota.iterrows():
        for d in DOCS_CRITICOS:
            filas.append({"Interno": r["Interno"],
                          "Vehículo": f"{r['Marca']} {r['Modelo']}",
                          "Documento": d, "Vence": r[f"venc_{d}"],
                          "Días": r[f"dias_{d}"]})
    prox = pd.DataFrame(filas).sort_values("Días").head(12)
    prox["Estado"] = prox["Días"].map(lambda x: EMOJI_ESTADO[estado_doc(x)])
    prox["Vence"] = prox["Vence"].map(lambda f: f.strftime("%d/%m/%Y"))
    st.dataframe(prox[["Estado", "Interno", "Vehículo", "Documento", "Vence", "Días"]],
                 hide_index=True, width="stretch")

    st.info("💡 Este reporte se genera solo. Reemplaza la planilla de Excel que hoy "
            "se actualiza a mano y que nadie mira hasta que un vehículo queda parado en el portón.")
