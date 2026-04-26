"""
Queries SQL para análisis de pedidos Mazda
Adaptado para FastAPI backend
"""
import os
import duckdb
import pandas as pd

DB_PATH = os.environ.get("DUCKDB_PATH", "/home/juanstn/git/streamlit_congroup/mazda.duckdb")


def get_connection(db_path: str = DB_PATH):
    """Retorna conexión a DuckDB"""
    return duckdb.connect(db_path, read_only=True)


def obtener_años_disponibles(db_path: str = DB_PATH):
    con = get_connection(db_path)
    años = con.execute("""
        SELECT DISTINCT YEAR(TRY_CAST(FechaSimulada AS DATE)) as año
        FROM pedidosmazdas
        WHERE FechaSimulada IS NOT NULL
        ORDER BY año DESC
    """).df()['año'].tolist()
    con.close()
    return [int(a) for a in años if a is not None]


def resumen_vendedores_filtrado(con, anio=None, mes=None):
    """
    Tabla resumen por vendedor basada en consulta_base.sql
    - pedidos: usa cgib_fechainicialdelpedido
    - resto: usa FechaSimulada/fecha aviso
    """
    query = """
        WITH consulta_base AS (
            SELECT
                ped."_cgib_vendedormg_value@OData.Community.Display.V1.FormattedValue" AS vendedor,
                ped."_cgib_vinstock_value@OData.Community.Display.V1.FormattedValue"   AS vin,
                ped."cgib_nroexpediente@OData.Community.Display.V1.FormattedValue"     AS expediente,
                ped.cgib_matricula AS matricula,
                TRY_CAST(ped.cgib_fechainicialdelpedido AS DATE) AS fecha_pedido,
                TRY_CAST(ped.FechaSimulada AS DATE) AS mes_aviso,
                COALESCE(ped.cgib_bb1_, 0) AS bb1,
                COALESCE(ped.cgib_bb2, 0)  AS bb2,
                COALESCE(ped.cgib_bb3, 0)  AS bb3,
                COALESCE(ped.cgib_descconcesion, 0) AS descuento,
                ped.cgib_importedefinanciacion AS importe_financiacion,
                ped.cgib_productofinanciero AS producto_financiero,
                ped.cgib_pedidosmazdaid AS id_pedido,
                ped._cgib_vinstock_value AS id_vin_stock,
                ped.cgib_nroexpediente AS nro_expediente,
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
            COUNT(DISTINCT CASE
                WHEN (cb.fecha_matriculacion_stock IS NOT NULL)
                    AND (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.id_pedido
            END) AS con_placa,
            COUNT(DISTINCT CASE
                WHEN (cb.nro_expediente IS NOT NULL)
                    AND (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.id_pedido
            END) AS subidos,
            COUNT(DISTINCT CASE
                WHEN (cb.nro_expediente IS NULL)
                    AND (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.id_pedido
            END) AS pendientes,
            COUNT(DISTINCT CASE
                WHEN (cb.fecha_pedido IS NOT NULL)
                    AND (? IS NULL OR YEAR(cb.fecha_pedido) = ?)
                    AND (? IS NULL OR MONTH(cb.fecha_pedido) = ?)
                THEN cb.id_pedido
            END) AS pedidos,
            COUNT(DISTINCT CASE
                WHEN (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.id_pedido
            END) AS ventas,
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
            ROUND(AVG(CASE
                WHEN (? IS NULL OR YEAR(cb.mes_aviso) = ?)
                    AND (? IS NULL OR MONTH(cb.mes_aviso) = ?)
                THEN cb.descuento * 100
            END), 2) AS media_descuento_pct,
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
    params = [
        anio, anio, mes, mes,
        anio, anio, mes, mes,
        anio, anio, mes, mes,
        anio, anio, mes, mes,
        anio, anio, mes, mes,
        anio, anio, mes, mes,
        anio, anio, mes, mes,
        anio, anio, mes, mes,
        anio, anio, mes, mes,
        anio, anio, mes, mes,
        anio, anio, mes, mes,
        anio, anio, mes, mes,
        anio, anio, mes, mes,
    ]
    return con.execute(query, params).df()


def ventas_por_vendedor_tipo(con, anio=None, mes=None):
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
