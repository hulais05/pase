# PASE 🛡️

**El pase de tu flota a la mina.**
Demo de gestión de flota para **contratistas mineros del NOA**.

El cliente no es la minera (que ya tiene SAP), sino los contratistas y proveedores
que le prestan servicio y deben tener su flota con la documentación al día para
poder ingresar al yacimiento. Si un papel está vencido, el vehículo queda parado en
el portón y no se factura.

## Vistas del demo
1. **🚦 Semáforo de Flota** — qué unidades pueden ingresar hoy (verde / amarillo / rojo).
2. **🛻 Ficha de Vehículo** — legajo digital: documentación, vencimientos, mantenimiento, costos, siniestros.
3. **💥 Siniestros** — seguimiento de denuncias ante aseguradoras hasta el cierre.
4. **📊 Reporte Ejecutivo** — KPIs y gráficos que hoy se arman a mano en Excel.

> Datos 100% ficticios (ver `data.py`). Flota de ejemplo: *Transportes del Norte S.R.L.*

## Cómo correrlo localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Abre en http://localhost:8501

## Demo en vivo
Desplegado en Streamlit Community Cloud (entrada: `app.py`).

## Origen
El aviso de búsqueda "Analista de Gestión de Flota" (Ganfeng Lithium) define el
listado de funciones que el producto resuelve: vencimientos VTV/RTO, pólizas,
historial y costos de mantenimiento, siniestros, documentación de contratistas y
reportes de gestión.

---
*ESG Consulting NOA*
