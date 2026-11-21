-- =====================================================================================
-- Consultas a la capa oro (Athena, base secop_gold) que alimentan este dashboard.
-- Cada resultado se descarga como CSV en la carpeta datos/.
-- El dashboard muestra estas mismas consultas en la sección 4 (las lee de este archivo).
-- =====================================================================================

-- @mercado_anual.csv · Competencia por año y grupo de modalidad
SELECT anio, modalidad_grupo,
       sum(procesos_publicados)      AS procesos,
       sum(procesos_con_oferentes)   AS procesos_con_oferentes,
       sum(procesos_unico_oferente)  AS procesos_unico_oferente,
       sum(suma_oferentes)           AS suma_oferentes
FROM secop_gold.mercado_mensual
WHERE anio BETWEEN 2020 AND 2026
GROUP BY 1, 2
ORDER BY 1, 2;

-- @desempeno.csv · Desempeño diario de las recomendaciones en producción
SELECT fecha_corte, lista, empresas, recomendaciones,
       participaciones_reales, se_presento, cobertura,
       recomendaciones_adjudicadas, se_presento_adjudicadas, gano,
       ganes_esperados
FROM secop_gold.desempeno_recomendaciones
ORDER BY fecha_corte, lista;

-- @calidad_fuente.csv · Procesos sin categoría UNSPSC por semana
SELECT semana_inicio, procesos_publicados, procesos_sin_categoria
FROM secop_gold.calidad_fuente
WHERE semana_inicio >= date '2026-06-01'
ORDER BY semana_inicio;
