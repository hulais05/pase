"""
Generador de datos ficticios para el demo PASE.
Simula la flota de un contratista minero del NOA.
Todos los datos son inventados. Las fechas se calculan relativas a HOY
para que el semáforo siempre tenga casos verde / amarillo / rojo.
"""

from datetime import date, timedelta
import pandas as pd

# --- Configuración del cliente ficticio ---
EMPRESA = "Transportes del Norte S.R.L."
MINA_CLIENTE = "Operación minera (cliente)"
HOY = date.today()

# Documentos que la mina EXIGE para que un vehículo pueda ingresar al yacimiento.
# Si alguno está vencido -> el vehículo NO puede entrar (no factura).
DOCS_CRITICOS = ["RTO", "Seguro", "Habilitación mina", "Matafuegos"]
DOCS_TODOS = DOCS_CRITICOS + ["Cédula"]

# Umbral de alerta: faltan <= 30 días para vencer -> amarillo
DIAS_ALERTA = 30


def _f(dias):
    """Devuelve una fecha a 'dias' de HOY (negativo = ya venció)."""
    return HOY + timedelta(days=dias)


# Cada vehículo trae el offset en días de cada documento respecto de hoy.
# Mezcla pensada para que el demo muestre casos claros.
_FLOTA = [
    # interno, tipo, marca, modelo, anio, patente, area, conductor, aseguradora,
    # km_actual, km_prox_service, costo_mant_anual,
    # vencimientos {doc: dias}
    ("INT-01", "Camioneta", "Toyota", "Hilux SRV 4x4", 2023, "AF 482 KP", "Mina", "Carlos Quispe", "La Segunda", 78500, 80000, 1850000,
        {"RTO": 210, "Seguro": 45, "Habilitación mina": 120, "Matafuegos": 90, "Cédula": 900}),
    ("INT-02", "Camioneta", "VW", "Amarok V6", 2022, "AD 715 LM", "Mina", "Rubén Cardozo", "Federación Patronal", 112300, 115000, 2100000,
        {"RTO": 18, "Seguro": 60, "Habilitación mina": 14, "Matafuegos": 25, "Cédula": 1200}),
    ("INT-03", "Camioneta", "Ford", "Ranger XLT", 2021, "AC 990 TR", "Logística", "Marta Liendro", "Sancor Seguros", 145800, 150000, 1620000,
        {"RTO": -22, "Seguro": 150, "Habilitación mina": 40, "Matafuegos": 200, "Cédula": 600}),
    ("INT-04", "Camión", "Mercedes-Benz", "Actros 2546 (cisterna)", 2020, "AB 334 QW", "Mina", "Jorge Vilte", "La Segunda", 268400, 270000, 4850000,
        {"RTO": 95, "Seguro": 25, "Habilitación mina": 75, "Matafuegos": 12, "Cédula": 1500}),
    ("INT-05", "Camión", "Iveco", "Tector 170E22 (volcador)", 2019, "AA 128 PD", "Mina", "Néstor Cruz", "Federación Patronal", 312700, 320000, 5320000,
        {"RTO": 300, "Seguro": -10, "Habilitación mina": 180, "Matafuegos": 60, "Cédula": 2000}),
    ("INT-06", "Camioneta", "Toyota", "Hilux SR 4x2", 2024, "AG 051 NB", "Administración", "Lucía Farfán", "Sancor Seguros", 31200, 40000, 720000,
        {"RTO": 540, "Seguro": 220, "Habilitación mina": 260, "Matafuegos": 300, "Cédula": 1100}),
    ("INT-07", "Camión", "Scania", "P360 (tractor)", 2018, "AA 776 ZX", "Logística", "Héctor Mamaní", "Allianz", 421000, 425000, 6100000,
        {"RTO": 7, "Seguro": 110, "Habilitación mina": -3, "Matafuegos": 130, "Cédula": 800}),
    ("INT-08", "Camioneta", "VW", "Amarok Comfortline", 2022, "AD 233 HK", "Planta", "Sergio Ríos", "La Segunda", 98700, 100000, 1430000,
        {"RTO": 160, "Seguro": 28, "Habilitación mina": 95, "Matafuegos": 22, "Cédula": 1000}),
    ("INT-09", "Camioneta", "Ford", "Ranger Limited", 2023, "AF 619 CT", "Mina", "Diego Ovando", "Federación Patronal", 64500, 70000, 980000,
        {"RTO": 365, "Seguro": 75, "Habilitación mina": 50, "Matafuegos": 110, "Cédula": 1300}),
    ("INT-10", "Camión", "Mercedes-Benz", "Atego 1726 (carga)", 2021, "AC 444 BV", "Logística", "Pablo Sosa", "Sancor Seguros", 187300, 190000, 3750000,
        {"RTO": 33, "Seguro": 20, "Habilitación mina": 210, "Matafuegos": 5, "Cédula": 700}),
    ("INT-11", "Camioneta", "Toyota", "Hilux SRX 4x4", 2024, "AG 880 MR", "Mina", "Andrea Guzmán", "Allianz", 22100, 30000, 540000,
        {"RTO": 600, "Seguro": 300, "Habilitación mina": 320, "Matafuegos": 280, "Cédula": 1400}),
    ("INT-12", "Camión", "Iveco", "Daily (utilitario)", 2020, "AB 902 LF", "Planta", "Raúl Tolaba", "La Segunda", 156800, 160000, 2240000,
        {"RTO": 80, "Seguro": 19, "Habilitación mina": 8, "Matafuegos": 170, "Cédula": 950}),
    ("INT-13", "Camioneta", "VW", "Amarok Highline", 2021, "AC 117 GD", "Administración", "Verónica Paz", "Federación Patronal", 134500, 140000, 1680000,
        {"RTO": 250, "Seguro": 130, "Habilitación mina": 190, "Matafuegos": 240, "Cédula": 1150}),
    ("INT-14", "Camión", "Scania", "G410 (cisterna agua)", 2019, "AA 503 WT", "Mina", "Miguel Aban", "Allianz", 298600, 300000, 5780000,
        {"RTO": 27, "Seguro": 200, "Habilitación mina": 21, "Matafuegos": -8, "Cédula": 1800}),
    ("INT-15", "Camioneta", "Ford", "Ranger XL 4x4", 2022, "AD 661 PJ", "Logística", "Fernando Yapura", "Sancor Seguros", 119900, 120000, 1290000,
        {"RTO": 140, "Seguro": 90, "Habilitación mina": 65, "Matafuegos": 48, "Cédula": 1050}),
]

# Siniestros ficticios (denuncias ante aseguradoras y su seguimiento)
_SINIESTROS = [
    # interno, fecha (dias desde hoy, negativo=pasado), tipo, aseguradora, estado, dias_abierto, costo_estimado
    ("INT-02", -12, "Choque lateral", "Federación Patronal", "En reparación", 12, 980000),
    ("INT-05", -48, "Granizo", "Federación Patronal", "En reparación", 48, 1450000),
    ("INT-07", -5, "Rotura de parabrisas", "Allianz", "Denunciado", 5, 220000),
    ("INT-10", -95, "Vuelco (sin lesionados)", "Sancor Seguros", "Cerrado", 0, 3200000),
    ("INT-03", -150, "Robo de rueda de auxilio", "Sancor Seguros", "Cerrado", 0, 145000),
    ("INT-14", -3, "Daño en cisterna por carga", "Allianz", "Denunciado", 3, 670000),
]


def _estado_doc(dias):
    if dias < 0:
        return "Vencido"
    if dias <= DIAS_ALERTA:
        return "Por vencer"
    return "Vigente"


def _estado_vehiculo(vencimientos):
    """Determina si el vehículo puede ingresar a la mina."""
    estados_criticos = [_estado_doc(vencimientos[d]) for d in DOCS_CRITICOS]
    if "Vencido" in estados_criticos:
        return "NO HABILITADO"
    if "Por vencer" in estados_criticos:
        return "POR VENCER"
    return "HABILITADO"


def cargar_flota() -> pd.DataFrame:
    filas = []
    for (interno, tipo, marca, modelo, anio, patente, area, conductor, aseguradora,
         km_actual, km_prox, costo_mant, venc) in _FLOTA:
        estado = _estado_vehiculo(venc)
        # documento crítico más próximo a vencer (o ya vencido)
        prox_doc = min(DOCS_CRITICOS, key=lambda d: venc[d])
        filas.append({
            "Interno": interno,
            "Tipo": tipo,
            "Marca": marca,
            "Modelo": modelo,
            "Año": anio,
            "Patente": patente,
            "Área": area,
            "Conductor": conductor,
            "Aseguradora": aseguradora,
            "Km actual": km_actual,
            "Km próx. service": km_prox,
            "Km al service": km_prox - km_actual,
            "Costo mant. anual": costo_mant,
            "Estado": estado,
            "Doc. crítico próximo": prox_doc,
            "Días al venc. crítico": venc[prox_doc],
            **{f"venc_{d}": _f(venc[d]) for d in DOCS_TODOS},
            **{f"dias_{d}": venc[d] for d in DOCS_TODOS},
        })
    return pd.DataFrame(filas)


def cargar_siniestros() -> pd.DataFrame:
    filas = []
    for interno, dias, tipo, aseg, estado, dias_ab, costo in _SINIESTROS:
        filas.append({
            "Interno": interno,
            "Fecha": _f(dias),
            "Tipo de siniestro": tipo,
            "Aseguradora": aseg,
            "Estado": estado,
            "Días abierto": dias_ab,
            "Costo estimado": costo,
        })
    return pd.DataFrame(filas)


def estado_doc(dias):
    return _estado_doc(dias)
