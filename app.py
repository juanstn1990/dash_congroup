"""
Dash App con Flask-Login - Resumen de Vendedores Grupo Cars Mazda
Sesión manejada completamente en el servidor
"""

import dash
from dash import html, dcc, callback, Input, Output, State, no_update, dash_table
import dash_bootstrap_components as dbc
from flask import Flask, session, redirect, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import secrets
from datetime import datetime

# Importar queries
from queries import resumen_vendedores_filtrado, ventas_por_vendedor_tipo, get_connection

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
AZUL = "#1B3A6B"
AZUL_MED = "#2E6BE6"
AZUL_CLAR = "#EBF2FF"
VERDE = "#0D7C66"
VERDE_CL = "#D6F5EE"
ROJO = "#C0392B"
ROJO_CL = "#FDECEA"
NARANJA = "#E07B39"
GRIS = "#F4F6FA"
GRIS_MED = "#E2E8F0"
TEXTO = "#1C2B3A"
GRIS_TEXT = "#64748B"

VALID_USERS = {'admin': 'admin'}

# ── USUARIO SIMPLE ────────────────────────────────────────────────────────────
class User(UserMixin):
    def __init__(self, username):
        self.id = username

# ── CREAR SERVIDOR FLASK ──────────────────────────────────────────────────────
server = Flask(__name__)
server.secret_key = secrets.token_hex(32)

# ── CONFIGURAR FLASK-LOGIN ────────────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

@login_manager.user_loader
def load_user(username):
    if username in VALID_USERS:
        return User(username)
    return None

# ── CREAR APP DASH ────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap'
    ],
    suppress_callback_exceptions=True,
    url_base_pathname='/'
)

# ── COMPONENTES UI ────────────────────────────────────────────────────────────
def sidebar(username, current_path):
    def nav_link(href, icon, text):
        active_style = {'background': 'rgba(255,255,255,0.15)'} if href == current_path else {}
        return dcc.Link(
            f'{icon} {text}',
            href=href,
            style={
                'color': '#E2EAF4',
                'textDecoration': 'none',
                'padding': '10px 15px',
                'display': 'block',
                'borderRadius': '8px',
                'marginBottom': '5px',
                **active_style
            }
        )

    return html.Div([
        html.Img(src='/assets/Logo_congroup-web2.png', style={'width': '180px', 'margin': '0 auto 1rem', 'display': 'block'}),
        html.Hr(style={'borderColor': '#2E4A7A'}),
        html.P("Navegación", style={'color': '#E2EAF4', 'fontWeight': '600', 'marginBottom': '1rem'}),
        nav_link('/', '📊', 'Resumen de Vendedores'),
        html.Hr(style={'borderColor': '#2E4A7A', 'margin': '1rem 0'}),
        html.Small(f'👤 {username}', style={'color': '#94B8E0', 'display': 'block', 'marginBottom': '1rem', 'padding': '0 10px'}),
        html.A('🚪 Cerrar sesión', href='/logout', style={
            'color': 'white',
            'background': '#C0392B',
            'padding': '10px',
            'textAlign': 'center',
            'display': 'block',
            'borderRadius': '8px',
            'textDecoration': 'none',
            'fontWeight': '600'
        })
    ], style={
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'bottom': 0,
        'width': '250px',
        'background': AZUL,
        'padding': '1rem',
        'overflowY': 'auto'
    })

def login_form(error=False):
    return html.Div([
        html.Div([
            # Card de login
            html.Div([
                # Logo
                html.Div([
                    html.Img(src='/assets/Logo_congroup-web2.png',
                            style={'width': '220px', 'display': 'block', 'margin': '0 auto 20px'})
                ], style={'textAlign': 'center'}),

                # Título
                html.Div([
                    html.H1("Congroup Analytics",
                           style={
                               'textAlign': 'center',
                               'color': 'white',
                               'fontSize': '32px',
                               'fontWeight': '700',
                               'marginBottom': '40px',
                               'letterSpacing': '-0.5px'
                           })
                ]),

                # Formulario
                html.Div([
                    # Input Usuario
                    html.Div([
                        html.Label("Usuario", style={
                            'color': 'white',
                            'fontSize': '14px',
                            'fontWeight': '600',
                            'marginBottom': '8px',
                            'display': 'block'
                        }),
                        dbc.Input(
                            id='username',
                            placeholder='Ingresa tu usuario',
                            type='text',
                            style={
                                'background': 'rgba(255,255,255,0.15)',
                                'border': '1px solid rgba(255,255,255,0.3)',
                                'color': 'white',
                                'padding': '12px 16px',
                                'borderRadius': '8px',
                                'fontSize': '15px'
                            },
                            className='mb-3'
                        )
                    ]),

                    # Input Contraseña
                    html.Div([
                        html.Label("Contraseña", style={
                            'color': 'white',
                            'fontSize': '14px',
                            'fontWeight': '600',
                            'marginBottom': '8px',
                            'display': 'block'
                        }),
                        dbc.Input(
                            id='password',
                            placeholder='Ingresa tu contraseña',
                            type='password',
                            style={
                                'background': 'rgba(255,255,255,0.15)',
                                'border': '1px solid rgba(255,255,255,0.3)',
                                'color': 'white',
                                'padding': '12px 16px',
                                'borderRadius': '8px',
                                'fontSize': '15px'
                            },
                            className='mb-4'
                        )
                    ]),

                    # Botón Login
                    html.Button(
                        '→  Iniciar Sesión',
                        id='btn-login',
                        style={
                            'width': '100%',
                            'background': 'white',
                            'color': AZUL,
                            'border': 'none',
                            'padding': '14px',
                            'borderRadius': '8px',
                            'fontSize': '16px',
                            'fontWeight': '700',
                            'cursor': 'pointer',
                            'transition': 'all 0.3s ease',
                            'boxShadow': '0 4px 12px rgba(0,0,0,0.15)'
                        },
                        className='mb-3'
                    ),

                    # Error
                    dbc.Alert(
                        '❌ Usuario o contraseña incorrectos',
                        color='danger',
                        style={
                            'background': 'rgba(220,53,69,0.15)',
                            'border': '1px solid rgba(220,53,69,0.3)',
                            'color': '#ffebee',
                            'borderRadius': '8px',
                            'padding': '12px',
                            'fontSize': '14px'
                        },
                        className='mt-3'
                    ) if error else html.Div(),

                    html.Div(id='login-msg')
                ])

            ], style={
                'maxWidth': '440px',
                'margin': '0 auto',
                'padding': '50px 40px',
                'background': f'linear-gradient(135deg, {AZUL} 0%, {AZUL_MED} 100%)',
                'borderRadius': '20px',
                'boxShadow': '0 20px 60px rgba(27,58,107,0.4)',
                'border': '1px solid rgba(255,255,255,0.1)'
            })
        ], style={
            'minHeight': '100vh',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'padding': '20px'
        })
    ], style={
        'background': f'linear-gradient(to bottom right, {AZUL} 0%, #0f2744 50%, {AZUL} 100%)',
        'minHeight': '100vh'
    })

def obtener_años_disponibles():
    """Obtiene años disponibles en las fechas"""
    con = get_connection()
    años = con.execute("""
        SELECT DISTINCT YEAR(TRY_CAST(FechaSimulada AS DATE)) as año
        FROM pedidosmazdas
        WHERE FechaSimulada IS NOT NULL
        ORDER BY año DESC
    """).df()['año'].tolist()
    con.close()
    return años

def resumen_vendedores_page():
    """Dashboard de Resumen de Vendedores"""
    # Obtener fecha actual
    fecha_actual = datetime.now()
    año_actual = fecha_actual.year
    mes_actual = fecha_actual.month

    años_disponibles = obtener_años_disponibles()
    meses = [
        {'label': 'Todos', 'value': 'todos'},
        {'label': 'Enero', 'value': 1},
        {'label': 'Febrero', 'value': 2},
        {'label': 'Marzo', 'value': 3},
        {'label': 'Abril', 'value': 4},
        {'label': 'Mayo', 'value': 5},
        {'label': 'Junio', 'value': 6},
        {'label': 'Julio', 'value': 7},
        {'label': 'Agosto', 'value': 8},
        {'label': 'Septiembre', 'value': 9},
        {'label': 'Octubre', 'value': 10},
        {'label': 'Noviembre', 'value': 11},
        {'label': 'Diciembre', 'value': 12}
    ]

    return html.Div([
        sidebar(current_user.id, '/'),
        html.Div([
            # Header
            html.Div([
                html.H1("📊 Resumen de Vendedores - Grupo Cars Mazda",
                       style={'color': 'white', 'margin': '0', 'padding': '20px'})
            ], style={'background': AZUL, 'marginBottom': '20px', 'borderRadius': '8px'}),

            # Filtro de Fecha
            html.Div([
                html.H4("📅 Filtro de Fecha", style={'marginBottom': '15px', 'color': AZUL}),
                html.P("Pedidos usa fecha de pedido | Resto usa fecha aviso (FechaSimulada)",
                      style={'fontSize': '12px', 'color': '#666', 'marginBottom': '15px'}),

                html.Div([
                    html.Div([
                        html.Label("Año:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                        dcc.Dropdown(
                            id='anio',
                            options=[{'label': 'Todos', 'value': 'todos'}] +
                                    [{'label': str(a), 'value': a} for a in años_disponibles],
                            value=año_actual if año_actual in años_disponibles else 'todos',
                            clearable=False
                        )
                    ], style={'width': '30%', 'display': 'inline-block', 'paddingRight': '20px'}),

                    html.Div([
                        html.Label("Mes:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                        dcc.Dropdown(
                            id='mes',
                            options=meses,
                            value=mes_actual,
                            clearable=False
                        )
                    ], style={'width': '30%', 'display': 'inline-block'})
                ])
            ], style={'background': 'white', 'padding': '20px', 'borderRadius': '8px',
                     'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),

            # KPIs
            html.Div(id='kpis-container', style={'marginBottom': '20px'}),

            # Gráficos
            html.Div([
                dbc.Row([
                    dbc.Col([dcc.Graph(id='grafico-top-vendedores')], width=6),
                    dbc.Col([dcc.Graph(id='grafico-distribucion')], width=6)
                ], className='mb-3'),

                dbc.Row([
                    dbc.Col([dcc.Graph(id='grafico-bb')], width=6),
                    dbc.Col([dcc.Graph(id='grafico-expedientes')], width=6)
                ], className='mb-3')
            ]),

            # Tabla
            html.Div([
                html.H3("📋 Tabla Detallada", style={'marginBottom': '15px'}),
                html.Div(id='tabla-vendedores')
            ], style={'background': 'white', 'padding': '20px', 'borderRadius': '8px',
                     'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),

            # Ventas por Tipo
            html.Div([
                html.H3("📊 Ventas por Vendedor y Tipo de Venta", style={'marginBottom': '15px'}),
                html.Div(id='tabla-ventas-tipo')
            ], style={'background': 'white', 'padding': '20px', 'borderRadius': '8px',
                     'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),

            # Gráfico Distribución por Tipo
            html.Div([
                html.H3("📈 Distribución por Tipo de Venta (Top Vendedores)", style={'marginBottom': '15px'}),
                dcc.Graph(id='grafico-tipo-venta')
            ], style={'background': 'white', 'padding': '20px', 'borderRadius': '8px',
                     'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'})

        ], style={'marginLeft': '270px', 'padding': '2rem', 'background': GRIS, 'minHeight': '100vh'})
    ])

# ── RUTAS FLASK ───────────────────────────────────────────────────────────────
@server.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# ── LAYOUT DASH ───────────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# ── CALLBACKS ─────────────────────────────────────────────────────────────────
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('btn-login', 'n_clicks'),
    [State('username', 'value'), State('password', 'value')],
    prevent_initial_call=True
)
def do_login(n, username, password):
    if username and password:
        if username in VALID_USERS and VALID_USERS[username] == password:
            user = User(username)
            login_user(user)
            return '/'
    return '/login?error=1'

@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    # Verificar autenticación
    if not current_user.is_authenticated:
        error = 'error=1' in request.url
        return login_form(error=error)

    # Dashboard de Resumen de Vendedores
    return resumen_vendedores_page()

@callback(
    [Output('kpis-container', 'children'),
     Output('grafico-top-vendedores', 'figure'),
     Output('grafico-distribucion', 'figure'),
     Output('grafico-bb', 'figure'),
     Output('grafico-expedientes', 'figure'),
     Output('tabla-vendedores', 'children'),
     Output('tabla-ventas-tipo', 'children'),
     Output('grafico-tipo-venta', 'figure')],
    [Input('anio', 'value'),
     Input('mes', 'value')]
)
def actualizar_dashboard(anio, mes):
    # Convertir 'todos' a None
    anio_filtro = None if anio == 'todos' else anio
    mes_filtro = None if mes == 'todos' else mes

    # Obtener datos
    con = get_connection()
    df = resumen_vendedores_filtrado(con, anio_filtro, mes_filtro)

    if df.empty:
        con.close()
        mensaje = html.Div("No hay datos para los filtros seleccionados",
                          style={'padding': '20px', 'textAlign': 'center', 'color': 'red',
                                'fontSize': '18px', 'fontWeight': 'bold'})
        return [mensaje] + [{}] * 5

    # ─── KPIs ───
    kpis = dbc.Row([
        dbc.Col([
            html.Div([
                html.H4(f"{df['con_placa'].sum():,}",
                       style={'margin': '0', 'fontSize': '32px', 'color': VERDE}),
                html.P("Con Placa", style={'margin': '0', 'color': '#666'})
            ], style={'background': 'white', 'padding': '20px', 'borderRadius': '8px',
                      'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'})
        ], width=2),

        dbc.Col([
            html.Div([
                html.H4(f"{df['subidos'].sum():,}",
                       style={'margin': '0', 'fontSize': '32px', 'color': AZUL_MED}),
                html.P("Subidos", style={'margin': '0', 'color': '#666'})
            ], style={'background': 'white', 'padding': '20px', 'borderRadius': '8px',
                      'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'})
        ], width=2),

        dbc.Col([
            html.Div([
                html.H4(f"{df['pendientes'].sum():,}",
                       style={'margin': '0', 'fontSize': '32px', 'color': NARANJA}),
                html.P("Pendientes", style={'margin': '0', 'color': '#666'})
            ], style={'background': 'white', 'padding': '20px', 'borderRadius': '8px',
                      'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'})
        ], width=2),

        dbc.Col([
            html.Div([
                html.H4(f"{df['pedidos'].sum():,}",
                       style={'margin': '0', 'fontSize': '32px', 'color': AZUL}),
                html.P("Pedidos", style={'margin': '0', 'color': '#666'})
            ], style={'background': 'white', 'padding': '20px', 'borderRadius': '8px',
                      'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'})
        ], width=2),

        dbc.Col([
            html.Div([
                html.H4(f"{df['ventas'].sum():,}",
                       style={'margin': '0', 'fontSize': '32px', 'color': ROJO}),
                html.P("Ventas", style={'margin': '0', 'color': '#666'})
            ], style={'background': 'white', 'padding': '20px', 'borderRadius': '8px',
                      'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'})
        ], width=2)
    ])

    # ─── Gráfico 1: Top Vendedores ───
    top10 = df.nlargest(10, 'pedidos')
    fig1 = px.bar(top10, x='pedidos', y='vendedor', orientation='h',
                  title='🏆 Top 10 Vendedores por Pedidos',
                  color='pedidos', color_continuous_scale='Blues', text='pedidos')
    fig1.update_traces(textposition='outside')
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, height=500)

    # ─── Gráfico 2: Ventas vs Pendientes ───
    top10_v = df.nlargest(10, 'ventas')
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name='Ventas', x=top10_v['vendedor'], y=top10_v['ventas'],
                          marker_color=VERDE))
    fig2.add_trace(go.Bar(name='Pendientes', x=top10_v['vendedor'], y=top10_v['pendientes'],
                          marker_color=NARANJA))
    fig2.update_layout(title='📊 Ventas vs Pendientes (Top 10)', barmode='group',
                      height=500, xaxis_tickangle=-45)

    # ─── Gráfico 3: BBs ───
    top10_bb = df.nlargest(10, 'media_bb3')
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=top10_bb['vendedor'], y=top10_bb['media_bb1'],
                             mode='lines+markers', name='Media BB1', line=dict(color='lightblue', width=2)))
    fig3.add_trace(go.Scatter(x=top10_bb['vendedor'], y=top10_bb['media_bb2'],
                             mode='lines+markers', name='Media BB2', line=dict(color='blue', width=2)))
    fig3.add_trace(go.Scatter(x=top10_bb['vendedor'], y=top10_bb['media_bb3'],
                             mode='lines+markers', name='Media BB3', line=dict(color='darkblue', width=2)))
    fig3.update_layout(title='💰 Media de BBs (Top 10)', height=500,
                      xaxis_tickangle=-45, hovermode='x unified')

    # ─── Gráfico 4: Expedientes ───
    top10_exp = df.nlargest(10, 'subidos')
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(name='Subidos (Con Expediente)', x=top10_exp['vendedor'],
                         y=top10_exp['subidos'], marker_color=VERDE))
    fig4.add_trace(go.Bar(name='Pendientes (Sin Expediente)', x=top10_exp['vendedor'],
                         y=top10_exp['pendientes'], marker_color=ROJO))
    fig4.update_layout(title='📋 Subidos vs Pendientes (Top 10)', barmode='stack',
                      height=500, xaxis_tickangle=-45)

    # ─── Tabla con fila de totales ───
    # Reordenar columnas
    columnas_ordenadas = [
        'vendedor', 'con_placa', 'subidos', 'pendientes', 'pedidos', 'ventas',
        'suma_bb1', 'media_bb1', 'suma_bb2', 'media_bb2', 'suma_bb3', 'media_bb3',
        'media_descuento_pct', 'operaciones_financiadas'
    ]
    df = df[columnas_ordenadas]

    # Crear fila de totales
    totales = {
        'vendedor': '🔢 TOTALES',
        'con_placa': df['con_placa'].sum(),
        'subidos': df['subidos'].sum(),
        'pendientes': df['pendientes'].sum(),
        'pedidos': df['pedidos'].sum(),
        'ventas': df['ventas'].sum(),
        'suma_bb1': round(df['suma_bb1'].sum(), 2),
        'media_bb1': round(df['media_bb1'].mean(), 2),
        'suma_bb2': round(df['suma_bb2'].sum(), 2),
        'media_bb2': round(df['media_bb2'].mean(), 2),
        'suma_bb3': round(df['suma_bb3'].sum(), 2),
        'media_bb3': round(df['media_bb3'].mean(), 2),
        'media_descuento_pct': round(df['media_descuento_pct'].mean(), 2),
        'operaciones_financiadas': df['operaciones_financiadas'].sum()
    }

    # Agregar totales al DataFrame
    df_con_totales = pd.concat([df, pd.DataFrame([totales])], ignore_index=True)

    tabla = dash_table.DataTable(
        data=df_con_totales.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in df.columns],
        style_table={
            'overflowX': 'auto',
            'overflowY': 'auto',
            'maxHeight': '600px'
        },
        style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': '14px'},
        style_header={
            'backgroundColor': AZUL,
            'color': 'white',
            'fontWeight': 'bold',
            'position': 'sticky',
            'top': 0,
            'zIndex': 1
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'},
            {
                'if': {'row_index': len(df)},
                'backgroundColor': '#e8f4f8',
                'fontWeight': 'bold',
                'borderTop': '2px solid #1f77b4'
            }
        ],
        sort_action='native',
        filter_action='native',
    )

    # ─── Ventas por Tipo ───
    df_tipo = ventas_por_vendedor_tipo(con, anio_filtro, mes_filtro)
    con.close()

    if df_tipo.empty:
        tabla_tipo = html.Div("No hay datos de ventas por tipo para este periodo",
                             style={'padding': '20px', 'textAlign': 'center', 'color': '#666'})
        fig_tipo = {}
    else:
        # Hacer pivot: vendedor en filas, tipo_venta en columnas
        df_pivot = df_tipo.pivot(index='vendedor', columns='tipo_venta', values='cantidad')

        # Llenar NaN con 0
        df_pivot = df_pivot.fillna(0).astype(int)

        # Agregar columna de Total
        df_pivot['TOTAL'] = df_pivot.sum(axis=1)

        # Ordenar por total descendente
        df_pivot = df_pivot.sort_values('TOTAL', ascending=False)

        # Agregar fila de TOTALES
        totales = df_pivot.sum(axis=0)
        totales.name = '🔢 TOTALES'
        df_pivot = pd.concat([df_pivot, totales.to_frame().T])

        # Resetear index para tener vendedor como columna
        df_pivot = df_pivot.reset_index()
        df_pivot.columns.name = None
        df_pivot = df_pivot.rename(columns={'index': 'Vendedor'})

        # Crear tabla con scroll
        tabla_tipo = dash_table.DataTable(
            data=df_pivot.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in df_pivot.columns],
            style_table={
                'overflowX': 'auto',
                'overflowY': 'auto',
                'maxHeight': '600px'
            },
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'fontSize': '14px',
                'minWidth': '100px'
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'Vendedor'},
                    'textAlign': 'left',
                    'fontWeight': '500',
                    'minWidth': '200px',
                    'position': 'sticky',
                    'left': 0,
                    'backgroundColor': 'white',
                    'zIndex': 2
                },
                {
                    'if': {'column_id': 'TOTAL'},
                    'fontWeight': 'bold',
                    'backgroundColor': '#e8f4f8'
                }
            ],
            style_header={
                'backgroundColor': AZUL,
                'color': 'white',
                'fontWeight': 'bold',
                'position': 'sticky',
                'top': 0,
                'zIndex': 3,
                'textAlign': 'center'
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'},
                {
                    'if': {'row_index': len(df_pivot) - 1},
                    'backgroundColor': '#e8f4f8',
                    'fontWeight': 'bold',
                    'borderTop': '2px solid #1f77b4'
                }
            ],
            sort_action='native',
            filter_action='native',
        )

        # Gráfico: Top 10 vendedores con distribución por tipo de venta
        # Obtener top 10 vendedores por cantidad total
        top_vendedores = df_tipo.groupby('vendedor')['cantidad'].sum().nlargest(10).index.tolist()
        df_top = df_tipo[df_tipo['vendedor'].isin(top_vendedores)]

        # Crear gráfico de barras apiladas
        fig_tipo = go.Figure()

        # Obtener tipos de venta únicos
        tipos_venta = df_top['tipo_venta'].unique()

        for tipo in tipos_venta:
            df_filtrado = df_top[df_top['tipo_venta'] == tipo]
            fig_tipo.add_trace(go.Bar(
                name=tipo,
                x=df_filtrado['vendedor'],
                y=df_filtrado['cantidad'],
                text=df_filtrado['cantidad'],
                textposition='auto',
                customdata=df_filtrado['vendedor'],
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Vendedor: %{customdata}<br>' +
                             'Cantidad: %{y}<br>' +
                             '<extra></extra>'
            ))

        fig_tipo.update_layout(
            title='Top 10 Vendedores - Distribución por Tipo de Venta',
            barmode='stack',
            height=500,
            xaxis_tickangle=-45,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )

    return kpis, fig1, fig2, fig3, fig4, tabla, tabla_tipo, fig_tipo

# ── EJECUTAR ──────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import os

    # Modo debug desde variable de entorno (por defecto False para producción)
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'

    print("\n" + "="*80)
    print("🚀 Dashboard Resumen de Vendedores - Grupo Cars Mazda")
    print("   ✅ Autenticación con Flask-Login")
    print("   ✅ Filtros dinámicos (Año y Mes)")
    print("   ✅ 5 KPIs principales + 4 gráficos + tabla detallada")
    print("="*80)
    print(f"\n🔧 Modo: {'DEBUG' if debug_mode else 'PRODUCCIÓN'}")
    print("📍 URL: http://localhost:8052")
    print("👤 Usuario: admin")
    print("🔑 Contraseña: admin")
    print("\n💡 Presiona CTRL+C para detener el servidor\n")
    app.run(debug=debug_mode, host='0.0.0.0', port=8052)
