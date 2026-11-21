# Dashboard de exposición · Recomendador SECOP II · Equipo 8

Streamlit con un recorrido de 6 secciones en el orden de la exposición: de qué trata, por qué importa, objetivo, resultados, arquitectura y metodología, y conclusiones. Se navega desde el sidebar o con los botones Anterior / Siguiente.

**Personalización (sidebar):** nivel de detalle *General* o *Técnico* (muestra servicios, definiciones, consultas SQL y muestras de datos) y *Texto grande* para proyector.

**Interacción por sección:**
1. Procesos por año (barras o matriz modalidad × año) junto a la calculadora de horas para revisarlos a mano; resumen del problema y desplegable «¿Qué es un proceso?».
2. Desplegable «¿Qué significa un solo oferente?»; pestañas un solo oferente / ofertas por proceso (mínima cuantía resaltada); matriz modalidad × año y barras de procesos con ofertas frente a los que tuvieron un solo oferente, por modalidad.
3. Selector de objetivo con lo que entregó cada área.
4. Cuatro tarjetas que muestran cada parte del objetivo con datos; desplegable «¿Cómo lo medimos?» (con métricas técnicas en modo Técnico); acierto en producción frente a la prueba (dos barras; detalle diario en modo Técnico); modelo frente a un filtro simple; estimación del tiempo de lectura con y sin el recomendador.
5. Diagrama de arquitectura en AWS por etapas, con clic sobre cada servicio.
6. Cierre problema → solución → resultado con una gráfica cada uno; «Lo que logramos»; desplegables de retos de datos y limitaciones.

**Colores:** azules institucionales del KIT UI de GOV.CO (`#3366CC` y `#004884`) como color principal, con acentos pequeños en el amarillo del Gobierno (`#FFCD00`): franja del sidebar, barra de progreso, marca de sección y un dato clave por pantalla.

## Correrlo

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicarlo (Streamlit Community Cloud, gratis)

1. Suban esta carpeta a un repositorio de GitHub.
2. Entren a https://share.streamlit.io, elijan **Create app**, el repositorio y `app.py`.
3. Queda en una URL `https://<nombre>.streamlit.app`. Ábranla antes de exponer porque tarda en "despertar".

## Estructura

```
app.py                 dashboard
consultas_gold.sql     consultas a la capa oro (la sección 5 las muestra)
datos/                 resultados de esas consultas, en CSV
.streamlit/config.toml tema de colores
GUION.md               guion de 6 minutos
```

## De dónde salen los datos

Las gráficas se construyen con **consultas a las tablas de la capa oro** (Athena, base `secop_gold`). Todas están en `consultas_gold.sql`:

| Archivo en `datos/` | Tabla oro | Gráfica |
|---|---|---|
| `mercado_anual.csv` | `mercado_mensual` | Un solo oferente y oferentes promedio, por año y modalidad (sección 2) |
| `desempeno.csv` | `desempeno_recomendaciones` | Aciertos diarios de la lista 1 en producción (sección 4) |
| `calidad_fuente.csv` | `calidad_fuente` | Procesos sin categoría UNSPSC por semana (sección 6) |
| `metricas_modelo.csv` | Evaluación de ML (MLflow) | Modelo vs. referencia (sección 4) |

Para actualizar una gráfica, vuelvan a correr su consulta en Athena, descarguen el resultado y reemplacen el CSV. Los porcentajes se calculan en la app a partir de conteos.

Las cifras sueltas (KPI) están en el diccionario `CIFRAS` de `app.py` y salen del resumen del proyecto del 17 de noviembre de 2026.
