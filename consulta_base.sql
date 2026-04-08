WITH pedidos AS (
    SELECT 
        -- Dimensiones
        ped."_cgib_vendedormg_value@OData.Community.Display.V1.FormattedValue" AS vendedor,
        ped."_cgib_vinstock_value@OData.Community.Display.V1.FormattedValue"   AS vin,
        ped."cgib_nroexpediente@OData.Community.Display.V1.FormattedValue"     AS expediente,

        -- Fechas
        DATE(ped.cgib_fechainicialdelpedido) AS fecha_pedido,

        TRY_STRPTIME(
            REPLACE(REPLACE(REPLACE(REPLACE(
            REPLACE(REPLACE(REPLACE(REPLACE(
            REPLACE(REPLACE(REPLACE(REPLACE(
                "_cgib_mesaviso_value@OData.Community.Display.V1.FormattedValue",
                'Enero','January'),'Febrero','February'),'Marzo','March'),'Abril','April'),
                'Mayo','May'),'Junio','June'),'Julio','July'),'Agosto','August'),
                'Septiembre','September'),'Octubre','October'),'Noviembre','November'),'Diciembre','December'
            ),
        '%B %Y')::DATE AS mes_aviso,

        -- Importes
        CAST(REPLACE(REPLACE(ped."cgib_bb1_@OData.Community.Display.V1.FormattedValue", '.', ''), ',', '.') AS DOUBLE) AS bb1,
        CAST(REPLACE(REPLACE(ped."cgib_bb2@OData.Community.Display.V1.FormattedValue", '.', ''), ',', '.') AS DOUBLE)  AS bb2,
        CAST(REPLACE(REPLACE(ped."cgib_bb3@OData.Community.Display.V1.FormattedValue", '.', ''), ',', '.') AS DOUBLE)  AS bb3,

        ped.cgib_descconcesion           AS descuento,
        ped.cgib_importedefinanciacion   AS importe_financiacion,
        ped.cgib_tipoventa               AS 
        

    FROM mazda.main.pedidosmazdas ped

    WHERE 
        ped.statecode = 0
        AND (
            ped."_cgib_mesaviso_value@OData.Community.Display.V1.FormattedValue"
            NOT IN ('ANULADO', 'MODIFICADO')
            OR ped."_cgib_mesaviso_value@OData.Community.Display.V1.FormattedValue" IS NULL
        )
),

stock AS (
    SELECT
        stk.cgib_vin                AS vin_stock,
        stk.cgib_fechamatriculacion AS fecha_matriculacion
    FROM mazda.main.stockvehiculosmazdas stk
    QUALIFY ROW_NUMBER() OVER (PARTITION BY stk.cgib_vin) = 1
)

SELECT 
    *
FROM pedidos ped
LEFT JOIN stock stk
    ON ped.vin = stk.vin_stock;