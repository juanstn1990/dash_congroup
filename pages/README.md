# Páginas

Esta carpeta está lista para que agregues nuevas páginas a tu aplicación Dash.

## Cómo agregar una nueva página

1. **Crea un archivo** en esta carpeta (ej: `ventas.py`)
2. **Define una función** que retorne el layout de la página
3. **Importa en `app.py`** y agrégala al sistema de navegación

### Ejemplo: `pages/ventas.py`

```python
from dash import html
import dash_bootstrap_components as dbc

def ventas_layout():
    return html.Div([
        html.H1("Dashboard de Ventas"),
        dbc.Alert("Contenido aquí", color="info")
    ])
```

### Luego en `app.py`:

```python
# Importar al inicio
from pages.ventas import ventas_layout

# Agregar en sidebar()
nav_link('/ventas', '📊', 'Ventas'),

# Agregar en display_page()
if pathname == '/ventas':
    return ventas_layout()
```

## Estructura recomendada

Cada página debe retornar:
- Sidebar (opcional, si quieres mantener navegación)
- Contenido principal con `marginLeft: '270px'` si usas sidebar

```python
def mi_pagina():
    return html.Div([
        sidebar(current_user.id, '/mi-ruta'),
        html.Div([
            # Tu contenido aquí
        ], style={'marginLeft': '270px', 'padding': '2rem'})
    ])
```
