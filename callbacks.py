from dash.dependencies import Input, Output
import layout
import base64
import pandas as pd
import io

def register_callbacks(app):
    @app.callback(
        [Output('output-data-upload-histogram', 'children'),
         Output('output-data-upload-map', 'children')],
        [Input('upload-data', 'contents')]
    )
    def update_uploaded_data(contents):
        if contents is None:
            return html.Div(), html.Div()  # Return empty Divs if no content
        
        # Assuming only one file is uploaded
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # Check the columns of the DataFrame to determine which file type it is
        if 'latitude' in df.columns and 'longitude' in df.columns:
            # This is assumed to be map data
            return html.Div(), html.Div([
                html.H3('Uploaded Map Data'),
                dcc.Graph(
                    id='map-graph',
                    figure={}  # Your map figure here
                )
            ])
        else:
            # This is assumed to be histogram data
            return html.Div([
                html.H3('Uploaded Histogram Data'),
                dcc.Graph(
                    id='histogram-graph',
                    figure={}  # Your histogram figure here
                )
            ]), html.Div()
