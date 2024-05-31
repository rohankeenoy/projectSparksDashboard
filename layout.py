import dash_html_components as html
import dash_core_components as dcc

# Define layout for page 1
page_1_layout = html.Div([
    html.H1('Per Pixel Land Classifications for data in collection'),
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
        multiple=False
    ),
    html.Div(id='output-data-upload-histogram'),  # Add a placeholder for the histogram data
    html.Div(id='output-data-upload-map'),  # Add a placeholder for the map data
    dcc.Dropdown([]),
    dcc.Link('Go to Page 2', href='/page-2')
])

# Define layout for page 2
page_2_layout = html.Div([
    html.H1('Page For Viewing the Tabular Data in Server'),
    html.P('This is the content of page 2.'),
    dcc.Link('Go to Page 1', href='/page-1')
])

# Define main layout for the app
layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
