"""

Queries SQL para análisis de pedidos Mazda
Relaciona: pedidos, vendedores, stock y dimensión tiempo

IMPORTANTE: Usa FechaSimulada (calculada desde cgib_mesavisoname) para los joins con dim_tiempo
"""

import duckdb


def get_connection(db_path="mazda.duckdb"):
    """Retorna conexión a DuckDB"""
    return duckdb.connect(db_path)


# =====================================================
# 📊 PEDIDOS CON VENDEDORES
# =====================================================

def pedidos_con_vendedores(con):
    """
    Pedidos con información del vendedor
    JOIN: pedidos._cgib_vendedormg_value = vendedors.cgib_vendedorid
    """
    query = """
        SELECT
            p.cgib_pedidosmazdaid,
            p.cgib_nodepedido,
            p.cgib_vin,
            p.cgib_version,
            p.cgib_fechainicialdelpedido,
            p.cgib_estadodelpedido,
            p.cgib_concesionario,
            v.cgib_vendedorid,
            v.cgib_nombres as vendedor_nombre,
            v.cgib_correoelectronico as vendedor_email,
            v.cgib_telefonotrabajo as vendedor_telefono,
            v.statecode as vendedor_estado
        FROM pedidosmazdas p
        LEFT JOIN vendedors v
            ON p._cgib_vendedormg_value = v.cgib_vendedorid
    """
    return con.execute(query).df()


def pedidos_por_vendedor(con):
    """
    Resumen de pedidos por vendedor
    """
    query = """
        SELECT
            v.cgib_vendedorid,
            v.cgib_nombres as vendedor,
            v.cgib_correoelectronico as email,
            COUNT(p.cgib_pedidosmazdaid) as total_pedidos,
            COUNT(DISTINCT p.cgib_vin) as pedidos_con_vin,
            COUNT(DISTINCT YEAR(CAST(p.cgib_fechainicialdelpedido AS DATE))) as años_activo,
            MIN(CAST(p.cgib_fechainicialdelpedido AS DATE)) as primera_venta,
            MAX(CAST(p.cgib_fechainicialdelpedido AS DATE)) as ultima_venta
        FROM vendedors v
        LEFT JOIN pedidosmazdas p
            ON p._cgib_vendedormg_value = v.cgib_vendedorid
        WHERE v.statecode = 0  -- Solo vendedores activos
        GROUP BY v.cgib_vendedorid, v.cgib_nombres, v.cgib_correoelectronico
        HAVING COUNT(p.cgib_pedidosmazdaid) > 0
        ORDER BY total_pedidos DESC
    """
    return con.execute(query).df()


def top_vendedores_por_periodo(con, año=2025, mes=None):
    """
    Top vendedores en un período específico usando FechaSimulada
    """
    filtro_mes = f"AND MONTH(CAST(p.FechaSimulada AS DATE)) = {mes}" if mes else ""

    query = f"""
        SELECT
            v.cgib_nombres as vendedor,
            COUNT(p.cgib_pedidosmazdaid) as total_pedidos,
            COUNT(CASE WHEN p.cgib_vin IS NOT NULL THEN 1 END) as con_vin,
            ROUND(COUNT(CASE WHEN p.cgib_vin IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as pct_con_vin
        FROM pedidosmazdas p
        LEFT JOIN vendedors v
            ON p._cgib_vendedormg_value = v.cgib_vendedorid
        WHERE YEAR(CAST(p.FechaSimulada AS DATE)) = {año}
            {filtro_mes}
        GROUP BY v.cgib_nombres
        ORDER BY total_pedidos DESC
        LIMIT 10
    """
    return con.execute(query).df()


# =====================================================
# 🚗 PEDIDOS CON STOCK (JOIN POR VIN)
# =====================================================

def pedidos_con_stock(con):
    """
    Pedidos relacionados con stock por VIN
    JOIN: pedidos.cgib_vin = stock.cgib_vin
    """
    query = """
        SELECT
            p.cgib_pedidosmazdaid,
            p.cgib_nodepedido,
            p.cgib_vin,
            p.cgib_version,
            p.cgib_fechainicialdelpedido as fecha_pedido,
            p.cgib_estadodelpedido,
            s.cgib_stockvehiculosmazdaid,
            s.cgib_tipodestock,
            s.cgib_fechamatriculacion as fecha_matricula_stock,
            s.cgib_estado as estado_stock,
            CASE
                WHEN s.cgib_vin IS NOT NULL THEN 'Con Stock'
                ELSE 'Sin Stock'
            END as tiene_stock
        FROM pedidosmazdas p
        LEFT JOIN stockvehiculosmazdas s
            ON p.cgib_vin = s.cgib_vin
        WHERE p.cgib_vin IS NOT NULL
    """
    return con.execute(query).df()


def pedidos_sin_stock(con):
    """
    Pedidos que tienen VIN pero no están en stock
    """
    query = """
        SELECT
            p.cgib_nodepedido,
            p.cgib_vin,
            p.cgib_version,
            p.cgib_fechainicialdelpedido,
            p.cgib_estadodelpedido,
            p.cgib_concesionario
        FROM pedidosmazdas p
        LEFT JOIN stockvehiculosmazdas s
            ON p.cgib_vin = s.cgib_vin
        WHERE p.cgib_vin IS NOT NULL
            AND s.cgib_vin IS NULL
        ORDER BY p.cgib_fechainicialdelpedido DESC
    """
    return con.execute(query).df()


def analisis_stock_por_pedido(con):
    """
    Análisis de relación pedidos-stock
    """
    query = """
        SELECT
            COUNT(DISTINCT p.cgib_pedidosmazdaid) as total_pedidos,
            COUNT(DISTINCT p.cgib_vin) as pedidos_con_vin,
            COUNT(DISTINCT s.cgib_vin) as vins_en_stock,
            COUNT(DISTINCT CASE WHEN s.cgib_vin IS NOT NULL THEN p.cgib_pedidosmazdaid END) as pedidos_con_stock,
            ROUND(COUNT(DISTINCT CASE WHEN s.cgib_vin IS NOT NULL THEN p.cgib_pedidosmazdaid END) * 100.0 /
                  COUNT(DISTINCT CASE WHEN p.cgib_vin IS NOT NULL THEN p.cgib_pedidosmazdaid END), 2) as pct_pedidos_en_stock
        FROM pedidosmazdas p
        LEFT JOIN stockvehiculosmazdas s ON p.cgib_vin = s.cgib_vin
    """
    return con.execute(query).df()


# =====================================================
# 📅 PEDIDOS CON DIMENSIÓN TIEMPO
# =====================================================

def pedidos_con_dimension_tiempo(con, fecha_desde=None, fecha_hasta=None):
    """
    Pedidos con información completa de dimensión tiempo
    JOIN: CAST(pedidos.FechaSimulada AS DATE) = dim_tiempo.fecha
    """
    filtro_fecha = ""
    if fecha_desde and fecha_hasta:
        filtro_fecha = f"WHERE t.fecha BETWEEN DATE '{fecha_desde}' AND DATE '{fecha_hasta}'"
    elif fecha_desde:
        filtro_fecha = f"WHERE t.fecha >= DATE '{fecha_desde}'"
    elif fecha_hasta:
        filtro_fecha = f"WHERE t.fecha <= DATE '{fecha_hasta}'"

    query = f"""
        SELECT
            p.cgib_pedidosmazdaid,
            p.cgib_nodepedido,
            p.cgib_vin,
            p.cgib_version,
            p.cgib_mesavisoname,
            p.FechaSimulada,
            t.fecha,
            t.año,
            t.mes,
            t.nombre_mes,
            t.trimestre,
            t.año_trimestre,
            t.dia_semana,
            t.nombre_dia,
            t.semana_año,
            t.es_fin_semana,
            p.cgib_estadodelpedido,
            p.cgib_concesionario
        FROM pedidosmazdas p
        INNER JOIN dim_tiempo t
            ON CAST(p.FechaSimulada AS DATE) = t.fecha
        {filtro_fecha}
        ORDER BY t.fecha DESC
    """
    return con.execute(query).df()


def pedidos_por_mes(con, año=None):
    """
    Resumen de pedidos por mes usando FechaSimulada
    """
    filtro_año = f"WHERE t.año = {año}" if año else ""

    query = f"""
        SELECT
            t.año,
            t.mes,
            t.nombre_mes,
            t.año_mes,
            COUNT(p.cgib_pedidosmazdaid) as total_pedidos,
            COUNT(CASE WHEN p.cgib_vin IS NOT NULL THEN 1 END) as pedidos_con_vin,
            COUNT(DISTINCT p.cgib_concesionario) as concesionarios_activos
        FROM dim_tiempo t
        LEFT JOIN pedidosmazdas p
            ON CAST(p.FechaSimulada AS DATE) = t.fecha
        {filtro_año}
        GROUP BY t.año, t.mes, t.nombre_mes, t.año_mes
        HAVING COUNT(p.cgib_pedidosmazdaid) > 0
        ORDER BY t.año DESC, t.mes DESC
    """
    return con.execute(query).df()


def pedidos_por_trimestre(con):
    """
    Resumen de pedidos por trimestre usando FechaSimulada
    """
    query = """
        SELECT
            t.año,
            t.trimestre,
            t.año_trimestre,
            COUNT(p.cgib_pedidosmazdaid) as total_pedidos,
            COUNT(DISTINCT p.cgib_vin) as vins_unicos,
            COUNT(DISTINCT p.cgib_concesionario) as concesionarios,
            ROUND(AVG(CASE WHEN p.cgib_vin IS NOT NULL THEN 1.0 ELSE 0.0 END) * 100, 2) as pct_con_vin
        FROM dim_tiempo t
        LEFT JOIN pedidosmazdas p
            ON CAST(p.FechaSimulada AS DATE) = t.fecha
        WHERE t.año >= 2024
        GROUP BY t.año, t.trimestre, t.año_trimestre
        HAVING COUNT(p.cgib_pedidosmazdaid) > 0
        ORDER BY t.año DESC, t.trimestre DESC
    """
    return con.execute(query).df()


def pedidos_por_dia_semana(con, año=2025):
    """
    Análisis de pedidos por día de la semana usando FechaSimulada
    """
    query = f"""
        SELECT
            t.dia_semana,
            t.nombre_dia,
            COUNT(p.cgib_pedidosmazdaid) as total_pedidos,
            ROUND(COUNT(p.cgib_pedidosmazdaid) * 100.0 / SUM(COUNT(p.cgib_pedidosmazdaid)) OVER(), 2) as porcentaje
        FROM dim_tiempo t
        INNER JOIN pedidosmazdas p
            ON CAST(p.FechaSimulada AS DATE) = t.fecha
        WHERE t.año = {año}
        GROUP BY t.dia_semana, t.nombre_dia
        ORDER BY t.dia_semana
    """
    return con.execute(query).df()


# =====================================================
# 🔗 CONSULTA COMPLETA: TODOS LOS JOINS
# =====================================================

def pedidos_completo(con, fecha_desde=None, fecha_hasta=None):
    """
    Vista completa: pedidos + vendedores + stock + dimensión tiempo
    Usa FechaSimulada para el join temporal
    """
    filtro_fecha = ""
    if fecha_desde and fecha_hasta:
        filtro_fecha = f"AND t.fecha BETWEEN DATE '{fecha_desde}' AND DATE '{fecha_hasta}'"
    elif fecha_desde:
        filtro_fecha = f"AND t.fecha >= DATE '{fecha_desde}'"
    elif fecha_hasta:
        filtro_fecha = f"AND t.fecha <= DATE '{fecha_hasta}'"

    query = f"""
        SELECT
            -- Pedido
            p.cgib_pedidosmazdaid,
            p.cgib_nodepedido,
            p.cgib_vin,
            p.cgib_version,
            p.cgib_estadodelpedido,
            p.cgib_concesionario,
            p.cgib_mesavisoname,
            p.FechaSimulada,

            -- Tiempo
            t.fecha,
            t.año,
            t.mes,
            t.nombre_mes,
            t.trimestre,
            t.año_trimestre,
            t.nombre_dia,
            t.es_fin_semana,

            -- Vendedor
            v.cgib_vendedorid,
            v.cgib_nombres as vendedor_nombre,
            v.cgib_correoelectronico as vendedor_email,

            -- Stock
            s.cgib_stockvehiculosmazdaid,
            s.cgib_tipodestock,
            s.cgib_fechamatriculacion as fecha_matricula_stock,
            CASE
                WHEN s.cgib_vin IS NOT NULL THEN TRUE
                ELSE FALSE
            END as tiene_stock

        FROM pedidosmazdas p
        LEFT JOIN dim_tiempo t
            ON CAST(p.FechaSimulada AS DATE) = t.fecha
        LEFT JOIN vendedors v
            ON p._cgib_vendedormg_value = v.cgib_vendedorid
        LEFT JOIN stockvehiculosmazdas s
            ON p.cgib_vin = s.cgib_vin
        WHERE p.FechaSimulada IS NOT NULL
            {filtro_fecha}
        ORDER BY t.fecha DESC
    """
    return con.execute(query).df()


def kpis_generales(con):
    """
    KPIs generales del negocio usando FechaSimulada
    """
    query = """
        SELECT
            COUNT(DISTINCT p.cgib_pedidosmazdaid) as total_pedidos,
            COUNT(DISTINCT p.cgib_vin) as total_vins,
            COUNT(DISTINCT v.cgib_vendedorid) as total_vendedores,
            COUNT(DISTINCT s.cgib_stockvehiculosmazdaid) as total_stock,
            COUNT(DISTINCT p.cgib_concesionario) as total_concesionarios,
            COUNT(DISTINCT t.año) as años_con_datos,
            MIN(t.fecha) as primera_fecha,
            MAX(t.fecha) as ultima_fecha,
            ROUND(COUNT(DISTINCT p.cgib_vin) * 100.0 / COUNT(DISTINCT p.cgib_pedidosmazdaid), 2) as pct_pedidos_con_vin,
            ROUND(COUNT(DISTINCT CASE WHEN s.cgib_vin IS NOT NULL THEN p.cgib_pedidosmazdaid END) * 100.0 /
                  COUNT(DISTINCT CASE WHEN p.cgib_vin IS NOT NULL THEN p.cgib_pedidosmazdaid END), 2) as pct_pedidos_en_stock
        FROM pedidosmazdas p
        LEFT JOIN dim_tiempo t ON CAST(p.FechaSimulada AS DATE) = t.fecha
        LEFT JOIN vendedors v ON p._cgib_vendedormg_value = v.cgib_vendedorid
        LEFT JOIN stockvehiculosmazdas s ON p.cgib_vin = s.cgib_vin
    """
    return con.execute(query).df()


# =====================================================
# 🚗 MATRÍCULAS POR MODELO
# =====================================================

def matriculas_por_modelo(con, años=[2025, 2026]):
    """
    Matrículas agrupadas por modelo y mes
    Similar al formato de la tabla de Grupo Cars
    """
    años_str = ','.join(map(str, años))

    query = f"""
        SELECT
            COALESCE(p.cgib_version, 'Sin Modelo') as modelo,
            t.año,
            t.mes,
            t.nombre_mes,
            COUNT(p.cgib_pedidosmazdaid) as total_matriculas
        FROM pedidosmazdas p
        INNER JOIN dim_tiempo t
            ON CAST(p.FechaSimulada AS DATE) = t.fecha
        WHERE t.año IN ({años_str})
            AND p.cgib_vin IS NOT NULL
        GROUP BY p.cgib_version, t.año, t.mes, t.nombre_mes
        ORDER BY p.cgib_version, t.año, t.mes
    """
    return con.execute(query).df()


def resumen_matriculas_por_modelo(con, años=[2025, 2026]):
    """
    Resumen total de matrículas por modelo
    """
    años_str = ','.join(map(str, años))

    query = f"""
        SELECT
            COALESCE(p.cgib_version, 'Sin Modelo') as modelo,
            COUNT(p.cgib_pedidosmazdaid) as total_matriculas,
            COUNT(DISTINCT t.año) as años_activo,
            MIN(t.fecha) as primera_matricula,
            MAX(t.fecha) as ultima_matricula
        FROM pedidosmazdas p
        INNER JOIN dim_tiempo t
            ON CAST(p.FechaSimulada AS DATE) = t.fecha
        WHERE t.año IN ({años_str})
            AND p.cgib_vin IS NOT NULL
        GROUP BY p.cgib_version
        ORDER BY total_matriculas DESC
    """
    return con.execute(query).df()


# =====================================================
# 👥 RESUMEN POR VENDEDOR
# =====================================================

def resumen_vendedores(con):
    """
    Tabla resumen completa por vendedor con todas las métricas de negocio
    Incluye: conteos, BBs, descuentos, financiación, expedientes
    """
    query = """
        SELECT
            -- Vendedor
            COALESCE(v.cgib_nombres, 'Sin asignar')                             AS vendedor,

            -- Conteos básicos
            COUNT(DISTINCT CASE WHEN p.cgib_matricula IS NOT NULL
                THEN p.cgib_pedidosmazdaid END)                                 AS con_placa,

            COUNT(DISTINCT CASE WHEN p._cgib_vinstock_value IS NOT NULL
                THEN p.cgib_pedidosmazdaid END)                                 AS subidos,

            COUNT(DISTINCT CASE WHEN p.cgib_fechamatriculacion IS NULL
                THEN p.cgib_pedidosmazdaid END)                                 AS pendientes,

            COUNT(DISTINCT p.cgib_pedidosmazdaid)                               AS pedidos,

            COUNT(DISTINCT CASE WHEN p.cgib_fechamatriculacion IS NOT NULL
                THEN p.cgib_pedidosmazdaid END)                                 AS ventas,

            -- BB1: Suma y Media
            ROUND(SUM(COALESCE(p.cgib_bb1_, 0)), 2)                            AS suma_bb1,
            ROUND(AVG(COALESCE(p.cgib_bb1_, 0)), 2)                            AS media_bb1,

            -- BB2: Suma y Media
            ROUND(SUM(COALESCE(p.cgib_bb2, 0)), 2)                             AS suma_bb2,
            ROUND(AVG(COALESCE(p.cgib_bb2, 0)), 2)                             AS media_bb2,

            -- BB3: Suma y Media
            ROUND(SUM(COALESCE(p.cgib_bb3, 0)), 2)                             AS suma_bb3,
            ROUND(AVG(COALESCE(p.cgib_bb3, 0)), 2)                             AS media_bb3,

            -- Descuento promedio (en porcentaje)
            ROUND(AVG(COALESCE(p.cgib_descconcesion, 0)) * 100, 2)             AS media_descuento_pct,

            -- Operaciones financiadas
            COUNT(DISTINCT CASE WHEN p.cgib_productofinanciero IS NOT NULL
                AND p.cgib_productofinanciero != ''
                THEN p.cgib_pedidosmazdaid END)                                 AS operaciones_financiadas,

            -- Tienen fecha de matriculación
            COUNT(DISTINCT CASE WHEN p.cgib_fechamatriculacion IS NOT NULL
                THEN p.cgib_pedidosmazdaid END)                                 AS tienen_fecha_matriculacion,

            -- Tienen expediente
            COUNT(DISTINCT CASE WHEN p.cgib_nroexpediente IS NOT NULL
                THEN p.cgib_pedidosmazdaid END)                                 AS tienen_expediente,

            -- NO tienen expediente
            COUNT(DISTINCT CASE WHEN p.cgib_nroexpediente IS NULL
                THEN p.cgib_pedidosmazdaid END)                                 AS no_tienen_expediente,

            -- Conteo por fecha de pedido
            COUNT(DISTINCT CASE WHEN p.cgib_fechainicialdelpedido IS NOT NULL
                THEN p.cgib_pedidosmazdaid END)                                 AS conteo_con_fecha_pedido,

            -- Conteo total de registros
            COUNT(*)                                                            AS conteo_total_registros

        FROM pedidosmazdas p
        LEFT JOIN vendedors v ON p._cgib_vendedormg_value = v.cgib_vendedorid

        GROUP BY v.cgib_nombres
        ORDER BY pedidos DESC
    """
    return con.execute(query).df()


def resumen_vendedores_filtrado(con, anio=None, mes=None):
    """
    Tabla resumen por vendedor basada en consulta_base.sql
    - pedidos: usa cgib_fechainicialdelpedido
    - resto: usa FechaSimulada/fecha aviso

    Parámetros:
        anio: año para filtrar (None = todos)
        mes: mes para filtrar (None = todos)
    """
    query = """
        WITH consulta_base AS (
            SELECT
                -- Dimensiones
                ped."_cgib_vendedormg_value@OData.Community.Display.V1.FormattedValue" AS vendedor,
                ped."_cgib_vinstock_value@OData.Community.Display.V1.FormattedValue"   AS vin,
                ped."cgib_nroexpediente@OData.Community.Display.V1.FormattedValue"     AS expediente,
                ped.cgib_matricula AS matricula,

                -- Fechas
                TRY_CAST(ped.cgib_fechainicialdelpedido AS DATE) AS fecha_pedido,
                TRY_CAST(ped.FechaSimulada AS DATE) AS mes_aviso,

                -- Importes
                COALESCE(ped.cgib_bb1_, 0) AS bb1,
                COALESCE(ped.cgib_bb2, 0)  AS bb2,
                COALESCE(ped.cgib_bb3, 0)  AS bb3,
                COALESCE(ped.cgib_descconcesion, 0) AS descuento,
                ped.cgib_importedefinanciacion AS importe_financiacion,
                ped.cgib_productofinanciero AS producto_financiero,

                -- IDs para contar
                ped.cgib_pedidosmazdaid AS id_pedido,
                ped._cgib_vinstock_value AS id_vin_stock,
                ped.cgib_nroexpediente AS nro_expediente,

                -- Stock
                stk.cgib_fechamatriculacion AS fecha_matriculacion_stock

            FROM pedidosmazdas ped
            LEFT JOIN (
                SELECT
                    cgib_vin,
                    cgib_fechamatriculacion,
                    ROW_NUMBER() OVER (PARTITION BY cgib_vin ORDER BY cgib_fechamatriculacion DESC) as rn
                FROM stockvehiculosmazdas
            ) stk ON ped.cgib_vin = stk.cgib_vin AND stk.rn = 1

            WHERE
                ped.statecode = 0
                AND ped.cgib_nodepedido IS NOT NULL
        )

        SELECT
            COALESCE(cb.vendedor, 'Sin asignar') AS vendedor,

            -- CON PLACA: los que tienen fecha de matriculación, filtrado por mes_aviso
            COUNT(DISTINCT CASE
                WHEN (cb.fecha_matriculacion_stock IS NOT NULL)
                    AND (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.id_pedido
            END) AS con_placa,

            -- SUBIDOS: los que tienen expediente, filtrado por mes_aviso
            COUNT(DISTINCT CASE
                WHEN (cb.nro_expediente IS NOT NULL)
                    AND (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.id_pedido
            END) AS subidos,

            -- PENDIENTES: los que NO tienen expediente, filtrado por mes_aviso
            COUNT(DISTINCT CASE
                WHEN (cb.nro_expediente IS NULL)
                    AND (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.id_pedido
            END) AS pendientes,

            -- PEDIDOS: filtrado por fecha_pedido
            COUNT(DISTINCT CASE
                WHEN (cb.fecha_pedido IS NOT NULL)
                    AND (? IS NULL OR YEAR(cb.fecha_pedido) = ?)
                    AND (? IS NULL OR MONTH(cb.fecha_pedido) = ?)
                THEN cb.id_pedido
            END) AS pedidos,

            -- VENTAS: conteo de TODOS los registros filtrado por mes_aviso
            COUNT(DISTINCT CASE
                WHEN (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.id_pedido
            END) AS ventas,

            -- BB1: filtrado por mes_aviso
            ROUND(SUM(CASE
                WHEN (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.bb1 ELSE 0
            END), 2) AS suma_bb1,
            ROUND(AVG(CASE
                WHEN (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.bb1
            END), 2) AS media_bb1,

            -- BB2: filtrado por mes_aviso
            ROUND(SUM(CASE
                WHEN (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.bb2 ELSE 0
            END), 2) AS suma_bb2,
            ROUND(AVG(CASE
                WHEN (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.bb2
            END), 2) AS media_bb2,

            -- BB3: filtrado por mes_aviso
            ROUND(SUM(CASE
                WHEN (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.bb3 ELSE 0
            END), 2) AS suma_bb3,
            ROUND(AVG(CASE
                WHEN (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.bb3
            END), 2) AS media_bb3,

            -- DESCUENTO: filtrado por mes_aviso
            ROUND(AVG(CASE
                WHEN (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.descuento * 100
            END), 2) AS media_descuento_pct,

            -- OPERACIONES FINANCIADAS: importe_financiacion > 0, filtrado por mes_aviso
            COUNT(DISTINCT CASE
                WHEN (cb.importe_financiacion > 0)
                    AND (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.id_pedido
            END) AS operaciones_financiadas

        FROM consulta_base cb

        GROUP BY cb.vendedor
        HAVING pedidos > 0 OR ventas > 0
        ORDER BY pedidos DESC
    """

    # Preparar parámetros
    params = [
        anio, anio, mes, mes,          # con_placa
        anio, anio, mes, mes,          # subidos
        anio, anio, mes, mes,          # pendientes
        anio, anio, mes, mes,          # pedidos
        anio, anio, mes, mes,          # ventas
        anio, anio, mes, mes,          # bb1 suma
        anio, anio, mes, mes,          # bb1 media
        anio, anio, mes, mes,          # bb2 suma
        anio, anio, mes, mes,          # bb2 media
        anio, anio, mes, mes,          # bb3 suma
        anio, anio, mes, mes,          # bb3 media
        anio, anio, mes, mes,          # descuento
        anio, anio, mes, mes           # operaciones_financiadas
    ]

    return con.execute(query, params).df()


def ventas_por_vendedor_tipo(con, anio=None, mes=None):
    """
    Ventas por vendedor y tipo de venta
    Filtrado por mes_aviso (FechaSimulada)

    Parámetros:
        anio: año para filtrar (None = todos)
        mes: mes para filtrar (None = todos)
    """
    query = """
        SELECT
            COALESCE(ped."_cgib_vendedormg_value@OData.Community.Display.V1.FormattedValue", 'Sin asignar') AS vendedor,
            COALESCE(ped.cgib_tipoventa, 'Sin tipo') AS tipo_venta,
            COUNT(DISTINCT ped.cgib_pedidosmazdaid) AS cantidad,
            ROUND(COUNT(DISTINCT ped.cgib_pedidosmazdaid) * 100.0 /
                  SUM(COUNT(DISTINCT ped.cgib_pedidosmazdaid)) OVER (PARTITION BY ped."_cgib_vendedormg_value@OData.Community.Display.V1.FormattedValue"), 1) AS porcentaje
        FROM pedidosmazdas ped
        WHERE
            ped.statecode = 0
            AND ped.cgib_nodepedido IS NOT NULL
            AND (? IS NULL OR YEAR(TRY_CAST(ped.FechaSimulada AS DATE)) = ?)
            AND (? IS NULL OR MONTH(TRY_CAST(ped.FechaSimulada AS DATE)) = ?)
        GROUP BY
            ped."_cgib_vendedormg_value@OData.Community.Display.V1.FormattedValue",
            ped.cgib_tipoventa
        HAVING cantidad > 0
        ORDER BY vendedor, cantidad DESC
    """

    params = [anio, anio, mes, mes]
    return con.execute(query, params).df()


# =====================================================
# 📊 EJEMPLO DE USO
# =====================================================

if __name__ == "__main__":
    con = get_connection()

    print("="*80)
    print("📊 QUERIES - ANÁLISIS DE PEDIDOS MAZDA")
    print("="*80 + "\n")

    # KPIs Generales
    print("📈 KPIs GENERALES:")
    print(kpis_generales(con))

    # Pedidos por mes
    print("\n📅 PEDIDOS POR MES (2025):")
    print(pedidos_por_mes(con, año=2025))

    # Top vendedores
    print("\n👥 TOP 10 VENDEDORES (2025):")
    print(top_vendedores_por_periodo(con, año=2025))

    # Análisis stock
    print("\n🚗 ANÁLISIS STOCK:")
    print(analisis_stock_por_pedido(con))

    # Pedidos por trimestre
    print("\n📊 PEDIDOS POR TRIMESTRE:")
    print(pedidos_por_trimestre(con))

    # Pedidos por día de la semana
    print("\n📆 PEDIDOS POR DÍA DE LA SEMANA (2025):")
    print(pedidos_por_dia_semana(con, año=2025))

    # Resumen por vendedor
    print("\n👥 RESUMEN POR VENDEDOR:")
    print(resumen_vendedores(con).head(10))

    con.close()

    print("\n✅ Queries ejecutadas correctamente!")
    print("💡 Importa este módulo para usar las funciones en tu app Streamlit")
