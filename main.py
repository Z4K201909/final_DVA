import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import os
import json

# Constants
DATA_DIR = 'data/processed/regional'
CLUSTER_FILES = {
    'K-Means': 'data/processed/clusters/kmeans_6.csv',
    'DTW': 'data/processed/clusters/DTW_6.csv'
}
ARIMA_DIR = 'data/processed/arima'

# Load city list
with open('city_list.json') as f:
    city_list = json.load(f)

# Feature display names
feature_name_map = {
    'median_list_price': 'Median list price',
    'median_sale_price': 'Median sale price'
}

# ARIMA labels
ARIMA_LABELS = {
    '(0, 0, 0)': 'White Noise',
    '(0, 0, 1)': '',
    '(0, 0, 2)': '',
    '(0, 0, 3)': '',
    '(0, 1, 0)': 'Random Walk',
    '(0, 1, 1)': 'Simple Exp. Smoothing',
    '(0, 1, 2)': '',
    '(0, 1, 3)': '',
    '(0, 2, 0)': '',
    '(0, 2, 1)': '',
    '(0, 2, 2)': '',
    '(0, 2, 3)': '',
    '(0, 3, 0)': '',
    '(0, 3, 1)': '',
    '(0, 3, 2)': '',
    '(0, 3, 3)': '',
    '(1, 0, 0)': '',
    '(1, 0, 1)': '',
    '(1, 0, 2)': '',
    '(1, 0, 3)': '',
    '(1, 1, 0)': '',
    '(1, 1, 1)': 'Common ARIMA',
    '(1, 1, 2)': '',
    '(1, 1, 3)': '',
    '(1, 2, 0)': '',
    '(1, 2, 1)': '',
    '(1, 2, 2)': '',
    '(1, 2, 3)': '',
    '(1, 3, 0)': '',
    '(1, 3, 1)': '',
    '(1, 3, 2)': '',
    '(1, 3, 3)': '',
    '(2, 0, 0)': '',
    '(2, 0, 1)': '',
    '(2, 0, 2)': '',
    '(2, 0, 3)': '',
    '(2, 1, 0)': '',
    '(2, 1, 1)': '',
    '(2, 1, 2)': '',
    '(2, 1, 3)': '',
    '(2, 2, 0)': '',
    '(2, 2, 1)': '',
    '(2, 2, 2)': '',
    '(2, 2, 3)': '',
    '(2, 3, 0)': '',
    '(2, 3, 1)': '',
    '(2, 3, 2)': '',
    '(2, 3, 3)': '',
    '(3, 0, 0)': '',
    '(3, 0, 1)': '',
    '(3, 0, 2)': '',
    '(3, 0, 3)': '',
    '(3, 1, 0)': '',
    '(3, 1, 1)': '',
    '(3, 1, 2)': '',
    '(3, 1, 3)': '',
    '(3, 2, 0)': '',
    '(3, 2, 1)': '',
    '(3, 2, 2)': '',
    '(3, 2, 3)': '',
    '(3, 3, 0)': '',
    '(3, 3, 1)': '',
    '(3, 3, 2)': '',
    '(3, 3, 3)': ''
}

RECOMMENDATIONS = {}

THEME_STYLES = {
    'bg': '#f9f9f9',
    'text': '#000000',
    'card': 'white',
    'shadow': '0 2px 10px rgba(0,0,0,0.05)',
    'plot_bg': 'white',
    'paper_bg': 'white',
    'border': '#ccc'
}

def get_arima_label(order):
    return f'{order} {ARIMA_LABELS.get(order, "")}'.strip()

def clean_city_label(code):
    code = code.replace('_metroarea', '').replace('metroarea', '')
    city, state = code.rsplit('_', 1)
    return f'{city}, {state}'

# Dash setup
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Real Estate Dashboard'


def get_arima_features():
    return sorted([f for f in os.listdir(ARIMA_DIR) if os.path.isdir(os.path.join(ARIMA_DIR, f))])

def get_arima_orders_for_feature(feature):
    path = os.path.join(ARIMA_DIR, feature)
    if not os.path.exists(path): return []
    orders = []
    for f in os.listdir(path):
        if f.endswith('.csv') and '_recommended' not in f:
            order = f.split('_')[-1].replace('.csv', '')
            orders.append(order)
        else:
            split = f.split('_')
            order = split[-2].replace('.csv', '')
            city = split[0]
            state = split[1]
            location = f'{city}_{state}'
            RECOMMENDATIONS[location] = order
    return sorted(set(orders))


def load_city_data(city):
    path = os.path.join(DATA_DIR, f'{city}.csv')
    if not os.path.exists(path): return None
    df = pd.read_csv(path)
    df = df[df['property_type'] == 'All Residential']
    df['period_begin'] = pd.to_datetime(df['period_begin'], errors='coerce')
    return df

def load_arima_prediction(city, feature, order):
    path = os.path.join(ARIMA_DIR, feature, f'{city}_{feature}_{order}.csv')
    if not os.path.exists(path): return None
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

# Layout
app.layout = html.Div(
    style={'fontFamily': 'Arial', 'backgroundColor': THEME_STYLES['bg'], 'color': THEME_STYLES['text'],
           'padding': '20px', 'maxWidth': '1200px', 'margin': '0 auto'},
    children=[
        html.H1('Real Estate Dashboard', style={'textAlign': 'center'}),
        html.Div([
            html.Label('Clustering Method:'),
            dcc.RadioItems(
                id='clustering-method',
                options=[{'label': name, 'value': name} for name in CLUSTER_FILES],
                value=list(CLUSTER_FILES.keys())[0],
                labelStyle={'display': 'inline-block', 'marginRight': '20px'}
            )
        ], style={'marginBottom': '20px'}),
        dcc.Graph(id='clustering-map', style={'marginBottom': '30px'}),
        html.Div(
            children=[
                html.Div([
                    html.Label('Feature of Interest:'),
                    dcc.RadioItems(
                        id='feature-dropdown',
                        labelStyle={'display': 'block'},
                        style={'marginTop': '5px'}
                    )
                ], style={'flex': '0.5', 'minWidth': '150px', 'display': 'flex', 'flexDirection': 'column'}),

                html.Div([
                    html.Label('Select Location:'),
                    dcc.Dropdown(
                        id='arima-location',
                        options=[{'label': clean_city_label(c), 'value': c} for c in sorted(city_list)],
                        value=sorted(city_list)[0],
                        style={'marginTop': '5px'}
                    )
                ], style={'flex': '0.65', 'minWidth': '75px', 'display': 'flex', 'flexDirection': 'column'}),

                html.Div([
                    html.Label('ARIMA Model:'),
                    dcc.Dropdown(
                        id='arima-order-dropdown',
                        style={'marginTop': '5px'}
                    )
                ], style={'flex': '1', 'minWidth': '200px', 'display': 'flex', 'flexDirection': 'column'}),

                html.Div([
                    html.Label('Compare With Another Location:'),
                    dcc.Dropdown(
                        id='arima-location-2',
                        options=[{'label': clean_city_label(c), 'value': c} for c in sorted(city_list)],
                        placeholder='(Optional)',
                        style={'marginTop': '5px'}
                    )
                ], style={'flex': '0.75', 'minWidth': '75px', 'display': 'flex', 'flexDirection': 'column'}),
            ],
            style={
                'display': 'flex',
                'gap': '10px',
                'justifyContent': 'space-between',
                'alignItems': 'flex-start',
                'marginBottom': '25px'
            }
        ),
        dcc.Graph(id='arima-graph')
    ]
)


@app.callback(Output('feature-dropdown', 'options'),
              Output('feature-dropdown', 'value'),
              Input('clustering-method', 'value'))
def load_features(_):
    allowed = ['median_list_price', 'median_sale_price']
    options = [{'label': feature_name_map.get(f, f), 'value': f} for f in get_arima_features() if f in allowed]
    default_value = options[0]['value']
    return options, default_value

@app.callback(Output('arima-order-dropdown', 'options'),
              Output('arima-order-dropdown', 'value'),
              Input('feature-dropdown', 'value'),
              Input('arima-location', 'value'))
def load_orders(feature, city):
    orders = get_arima_orders_for_feature(feature) if feature else []
    recommendation = RECOMMENDATIONS.get(city)

    options = []
    for o in sorted(orders):
        label = get_arima_label(o)
        if o == recommendation:
            label += ' (Recommended)'
        options.append({'label': label, 'value': o})

    return options, recommendation

@app.callback(Output('arima-graph', 'figure'),
              Input('arima-location', 'value'),
              Input('arima-location-2', 'value'),
              Input('feature-dropdown', 'value'),
              Input('arima-order-dropdown', 'value'))
def update_arima_graph(loc1, loc2, feature, order):
    colors = THEME_STYLES
    template = 'plotly_white'
    fig = go.Figure(layout=dict(template=template,
                                plot_bgcolor=colors['plot_bg'],
                                paper_bgcolor=colors['paper_bg'],
                                font=dict(color=colors['text']),
                                margin=dict(t=40, b=40, l=20, r=20),
                                legend=dict(x=0.01, y=0.99),
                                title='ARIMA Forecast'))

    if not all([loc1, feature, order]):
        return fig

    def plot_city(city, historical_color, prediction_color, confidence_interval_rgba):
        actual = load_city_data(city)
        forecast = load_arima_prediction(city, feature, order)
        if actual is None or forecast is None:
            return

        fig.add_trace(go.Scatter(x=actual['period_begin'], y=actual[feature], mode='lines',
                                 name=f'{clean_city_label(city)} Actual', line=dict(color=historical_color)))
        fig.add_trace(go.Scatter(x=forecast['date'], y=forecast['prediction'], mode='lines',
                                 name=f'{clean_city_label(city)} Forecast', line=dict(color=prediction_color)))
        if 'confidence_interval' in forecast.columns:
            try:
                intervals = forecast['confidence_interval'].str.strip('[]').str.split(',', expand=True).astype(float)
                fig.add_trace(
                    go.Scatter(x=forecast['date'], y=intervals[1], mode='lines', line=dict(width=0), showlegend=False))
                fig.add_trace(go.Scatter(x=forecast['date'], y=intervals[0], fill='tonexty', mode='lines',
                                         name=f'{clean_city_label(city)} Confidence Interval', line=dict(width=0),
                                         fillcolor=confidence_interval_rgba))
            except:
                pass

    plot_city(loc1, '#1f77b4', '#7aaed6', 'rgba(31, 119, 180, 0.2)')
    if loc2:
        plot_city(loc2, '#d62728', '#ff9896', 'rgba(214, 39, 40, 0.2)')

    return fig


@app.callback(Output('clustering-map', 'figure'),
              Input('clustering-method', 'value'))
def update_map(method):
    if not method or method not in CLUSTER_FILES:
        return go.Figure().update_layout(title='Select clustering method')
    df = pd.read_csv(CLUSTER_FILES[method])
    df = df[df['cluster'].notna()]
    df['cluster'] = df['cluster'].astype(int).astype(str)
    clusters = sorted(df['cluster'].unique())
    fig = px.scatter_geo(df, lat='latitude', lon='longitude', color='cluster', hover_name='city', scope='usa',
                         title=f'{method} Clusters',
                         color_discrete_sequence=['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00'],
                         category_orders={'cluster': clusters})
    fig.update_layout(
        geo=dict(scope='usa',projection_type='albers usa', bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict( title='Cluster', title_font=dict(size=16), font=dict(size=14), itemclick='toggleothers', itemsizing='constant')
    )
    return fig


if __name__ == '__main__':
    app.run(debug=True)

app = app.server