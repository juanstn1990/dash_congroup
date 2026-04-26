"""Natural language chat → SQL → DuckDB using OpenAI."""
import json
import os
from typing import Any

import duckdb
from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from pydantic import BaseModel

from app.auth import get_current_user
from app.services.queries import DB_PATH

router = APIRouter()

SYSTEM_PROMPT = """Eres un asistente de análisis para Congroup, un concesionario Mazda.
Respondes preguntas sobre datos de ventas consultando la base de datos con SQL para DuckDB.

SCHEMA:
Tabla pedidosmazdas (pedidos/ventas activos: statecode=0 AND cgib_nodepedido IS NOT NULL):
- Vendedor: "_cgib_vendedormg_value@OData.Community.Display.V1.FormattedValue"
- Fecha aviso/entrega (FechaSimulada): TRY_CAST(FechaSimulada AS DATE)
- Fecha pedido: TRY_CAST(cgib_fechainicialdelpedido AS DATE)
- Matrícula: cgib_matricula (NULL = sin placa)
- Expediente: cgib_nroexpediente (NULL = pendiente, NOT NULL = subido)
- BB1 (beneficio bruto 1): cgib_bb1_
- BB2: cgib_bb2
- BB3: cgib_bb3
- Descuento concesión: cgib_descconcesion
- Importe financiación: cgib_importedefinanciacion (>0 = financiado)
- Tipo de venta: cgib_tipoventa
- ID pedido: cgib_pedidosmazdaid

Tabla stockvehiculosmazdas:
- VIN: cgib_vin
- Fecha matriculación: cgib_fechamatriculacion

REGLAS CRÍTICAS DE SQL:
- SIEMPRE pon entre comillas dobles las columnas con caracteres especiales (@, espacios, puntos).
  CORRECTO:   "_cgib_vendedormg_value@OData.Community.Display.V1.FormattedValue"
  INCORRECTO: _cgib_vendedormg_value@OData.Community.Display.V1.FormattedValue
- Usa YEAR() y MONTH() para filtrar fechas.
- Usa TRY_CAST para conversiones de fecha.
- Máximo 50 filas en el resultado (añade LIMIT 50 si no hay límite).
- Solo SELECT (sin INSERT/UPDATE/DELETE).
- Responde siempre en español.
- Cuando presentes números monetarios, usa el formato contable estándar.
"""


def _get_schema_summary() -> str:
    """Fetches table names and column count as a quick sanity string."""
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
        con.close()
        return f"Tablas disponibles: {', '.join(tables)}"
    except Exception:
        return ""


def _run_sql(sql: str) -> tuple[list[dict], list[str]]:
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        raise ValueError("Solo se permiten consultas SELECT.")
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        df = con.execute(sql).fetchdf().head(50)
        con.close()
        return df.to_dict(orient="records"), list(df.columns)
    except Exception as e:
        con.close()
        raise ValueError(str(e))


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[Message] = []


@router.post("")
async def chat(req: ChatRequest, current_user: str = Depends(get_current_user)):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(500, "OPENAI_API_KEY no configurada en el servidor.")

    client = OpenAI(api_key=api_key)

    tools: list[dict[str, Any]] = [
        {
            "type": "function",
            "function": {
                "name": "execute_sql",
                "description": "Ejecuta una consulta SQL en la base de datos DuckDB y devuelve los resultados.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "Consulta SQL para DuckDB (solo SELECT).",
                        }
                    },
                    "required": ["sql"],
                },
            },
        }
    ]

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *[{"role": m.role, "content": m.content} for m in req.history],
        {"role": "user", "content": req.question},
    ]

    # First call: let the model decide if it needs SQL
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0,
    )

    msg = response.choices[0].message
    sql_used: str | None = None
    data: list[dict] | None = None
    columns: list[str] | None = None
    sql_error: str | None = None

    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        sql_used = args.get("sql", "")

        try:
            data, columns = _run_sql(sql_used)
            tool_result = json.dumps(data[:10], ensure_ascii=False, default=str)
        except ValueError as e:
            sql_error = str(e)
            tool_result = json.dumps({"error": sql_error}, ensure_ascii=False)

        # Second call: model explains the results in natural language
        messages.append(msg.model_dump(exclude_none=False))
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            }
        )

        final = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
        )
        answer = final.choices[0].message.content or ""
    else:
        answer = msg.content or ""

    return {
        "answer": answer,
        "sql": sql_used,
        "columns": columns,
        "data": data,
        "error": sql_error,
    }
