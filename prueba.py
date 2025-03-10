import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import io
import base64

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("Dashboard Centro Médico", className="text-center"),

    dcc.Upload(
        id='upload-data',
        children=html.Button('Subir CSV o Excel', className="btn btn-primary"),
        multiple=False
    ),
    
    html.Div(id='output-data-upload'),
    
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Pacientes Atendidos", className="card-title"),
                html.H2(id='pacientes-atendidos', className="card-text")
            ])
        ]), width=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Doctores Disponibles", className="card-title"),
                html.H2(id='doctores-disponibles', className="card-text")
            ])
        ]), width=4),
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico_pacientes')),
        dbc.Col(dcc.Graph(id='grafico_doctores'))
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico_especialidad')),
        dbc.Col(dcc.Graph(id='grafico_edades'))
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico_consultas'))
    ])
])

# Función para leer archivos cargados
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = io.BytesIO(base64.b64decode(content_string))
    
    if filename.endswith('.csv'):
        df = pd.read_csv(decoded)
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(decoded)
    else:
        return None
    
    return df

@app.callback(
    [
        Output('pacientes-atendidos', 'children'),
        Output('doctores-disponibles', 'children'),
        Output('grafico_pacientes', 'figure'),
        Output('grafico_doctores', 'figure'),
        Output('grafico_especialidad', 'figure'),
        Output('grafico_edades', 'figure'),
        Output('grafico_consultas', 'figure')
    ],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def actualizar_dashboard(contents, filename):
    if contents is None:
        return "N/A", "N/A", px.scatter(), px.scatter(), px.scatter(), px.scatter(), px.scatter()
    
    df = parse_contents(contents, filename)
    if df is None:
        return "Error", "Error", px.scatter(), px.scatter(), px.scatter(), px.scatter(), px.scatter()
    
    fig_pacientes = px.bar(df, x='Especialidad', title='Pacientes por Especialidad')
    fig_doctores = px.histogram(df, x='Doctor', title='Consultas por Doctor')
    fig_especialidad = px.pie(df, names='Especialidad', title='Distribución de Especialidades')
    fig_edades = px.box(df, x='Edad', title='Distribución de Edades')
    fig_consultas = px.line(df, x='Fecha', y='Consultas', title='Consultas a lo Largo del Tiempo')
    
    return df['Paciente ID'].nunique(), df['Doctor'].nunique(), fig_pacientes, fig_doctores, fig_especialidad, fig_edades, fig_consultas

if __name__ == '__main__':
    app.run_server(debug=True)
