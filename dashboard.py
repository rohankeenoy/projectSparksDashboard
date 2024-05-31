from dash import Dash, dcc, html, Input, Output, State
import base64
import io
import plotly.graph_objs as go
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

def load_svg(filename):
    with open(filename, 'rb') as f:
        return f.read()

# Load cloud SVG
cloud_svg = load_svg('cloud.svg')

header = html.Div(
    [
        html.Div([
            html.Img(
                src='data:image/svg+xml;base64,{}'.format(base64.b64encode(cloud_svg).decode()),
                style={'height': '80px', 'paddingLeft': '10px', 'paddingRight': '10px'}
            ),
            html.H1('Project Sparks Dashboard', style={'margin': '0', 'padding': '10px'}),
        ], style={'display': 'flex'}),
        html.Div([
            html.Div([
                html.A(html.Button('Per-Pixel Landclass', id='btn-landclass'), href='/landclass'),
                html.A(html.Button('Feature Evaluations', id='btn-features'), href='/features'),
                html.A(html.Button('Model Evaluation', id='btn-model'), href='/modeleval')
            ], style={'display': 'flex', 'justifyContent': 'flex-end' })
        ], style={})
    ],
    style={
        'justifyContent': 'space-between',
        'position': 'fixed',
        'top': '0',
        'left': '0',
        'width': '100%',
        'backgroundColor': '#f8f9fa',
        'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
        'zIndex': '1000',
        'display': 'flex',
        'alignItems': 'center'
    }
)




# Define the sidebar
sidebar = html.Div(
    [
        html.H2('Options'),
        html.Hr(),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=True
        ),
        dcc.Dropdown(
            id='row-selector',
            options=[],
            placeholder='Select a row'
        )
    ],
    id='sidebar',
    style={'flex': '30%', 'padding': '20px', 'marginTop': '60px', 'transition': 'margin-left 0.5s'}
)

# Define the main content layout
content = html.Div(
    [
        html.H2('Per-Pixel Land Classification'),
        html.Div(id='output-data', className='six columns'),  # Map and histogram column
    ],
    id='content',
    style={'flex': '70%', 'padding': '20px', 'marginTop': '60px'}
)

# Combine the header, sidebar, and main content into one layout
app.layout = html.Div(
    [
        header,
        html.Button('☰', id='toggle-button', n_clicks=0, style={'position': 'absolute', 'top': '70px', 'left': '10px', 'zIndex': '999'}),
        sidebar,
        content
    ],
    id='container',
    style={'display': 'flex'}
)

@app.callback(
    Output('sidebar', 'style'),
    [Input('toggle-button', 'n_clicks')]
)
def toggle_sidebar(nClicks):
    if nClicks % 2 == 0:
        return {'flex': '30%', 'padding': '20px', 'marginTop': '60px', 'transition': 'margin-left 0.5s'}
    else:
        return {'flex': '0%', 'padding': '20px', 'marginTop': '60px', 'transition': 'margin-left 0.5s', 'display': 'none'}

@app.callback(
    Output('content', 'style'),
    [Input('toggle-button', 'n_clicks')]
)
def adjust_content_width(nClicks):
    if nClicks % 2 == 0:
        return {'flex': '70%', 'padding': '20px', 'marginTop': '60px'}
    else:
        return {'flex': '100%', 'padding': '20px', 'marginTop': '60px'}

def whichData(df):
    hasCoords = any('coords' in col.lower() for col in df.columns)
    if hasCoords:
        return "polygon"
    else:
        return "histogram"
    
def getNumberOfRows(df):
    return df.shape[0]

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            return df
            
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
            return df
    except Exception as e:
        print(e)
        return None

@app.callback(
    Output('row-selector', 'options'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_row_options(list_of_contents, list_of_names):
    if list_of_contents is not None:
        # Use the first file to set the row options, assuming both files have the same number of rows
        df = parse_contents(list_of_contents[0], list_of_names[0], None)
        if df is not None:
            return [{'label': f'Row {i}', 'value': i} for i in range(1, df.shape[0] + 1)]
    return []

@app.callback(
    Output('output-data', 'children'),
    [Input('row-selector', 'value')],
    [State('upload-data', 'contents'),
     State('upload-data', 'filename')]
)
def update_output(selected_row, list_of_contents, list_of_names):
    if selected_row is not None and list_of_contents is not None:
        dfs = [parse_contents(c, n, None) for c, n in zip(list_of_contents, list_of_names)]
        output = []
        for df in dfs:
            if df is not None:
                data_type = whichData(df)
                if data_type == "polygon":
                    output.append(createMap(df, selected_row))
                elif data_type == "histogram":
                    output.append(create_histogram(df, selected_row))
        return output
    return []

def create_histogram(df, selected_row):
    data = []
    for col in df.columns:
        trace = go.Bar(
            x=[col],
            y=[df.loc[selected_row - 1, col]],
            name=col
        )
        data.append(trace)

    layout = go.Layout(
        title=f"Number of Pixels For Land Classification in Row {selected_row}",
        xaxis=dict(title='Land Classification'),
        yaxis=dict(title='Number of pixels in Land Classification'),
        barmode='group',
        margin=dict(l=40, r=40, t=40, b=40)
    )

    fig = go.Figure(data=data, layout=layout)
    return dcc.Graph(figure=fig)

def createMap(df, selected_row):
    row = df.iloc[selected_row - 1]
    polygonPointsStr = row['coords']
    polygonPoints = eval(polygonPointsStr)

    xCoords = [point[0] for point in polygonPoints[0]]
    yCoords = [point[1] for point in polygonPoints[0]]

    fig = go.Figure(go.Scattermapbox(
        mode='lines+markers',
        lon=xCoords + [xCoords[0]],
        lat=yCoords + [yCoords[0]],
        marker=dict(size=10),
        line=dict(width=2, color='blue'),
        fill='toself',
        fillcolor='rgba(0,0,255,0.2)',
    ))

    fig.update_layout(
        title='Polygon on Map',
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            style='carto-positron',
            bearing=0,
            center=dict(
                lat=sum(yCoords) / len(yCoords),
                lon=sum(xCoords) / len(xCoords)
            ),
            pitch=0,
            zoom=9
        ),
    )

    return dcc.Graph(figure=fig)

if __name__ == '__main__':
    app.run_server(debug=True)
