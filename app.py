import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import pandas_datareader as pdr
import pandas as pd
import os
from datetime import datetime

tiingo_key = os.environ['TIINGO_KEY']

app = dash.Dash()

available_tickers = pd.read_csv('data/NASDAQcompanylist.csv').set_index('Symbol')['Name']

today = datetime.now().strftime('%Y-%m-%d')

app.layout = html.Div([html.H1('Stock Ticker Dashboard'),
                        html.Div([
                            html.Div([html.H2('Select stock symbols:'),
                                        dcc.Dropdown(id='stock-picker',
                                            options=[{'label': f"{t} {available_tickers.loc[t]}", 'value': t} for t in available_tickers.index],
                                            multi=True)],
                                style={'verticalAlign': 'top', 'width': '30%', 'display': 'inline-block'}),
                            html.Div([html.H2('Select start and end dates:'),
                                        dcc.DatePickerRange(id='date-picker',
                                            initial_visible_month=today,
                                            display_format='DD-MM-YYYY',
                                            end_date=today)],
                                style={'paddingLeft': '20', 'display': 'inline-block'}),
                            html.Div([html.Button(id='submit-button',
                                        n_clicks=0,             # tracks number of clicks
                                        children='Submit',
                                        style={'fontSize': 24})],
                                style={'paddingLeft': '20', 'display': 'inline-block'})
                                    ]),
                        html.Div([dcc.Graph(id='prices-plot',
                                            figure={'data': [],
                                                    'layout': go.Layout(title='Prices')})])])

@app.callback(Output('prices-plot', 'figure'),
                [Input('submit-button', 'n_clicks')],
                [State('stock-picker', 'value'),
                State('date-picker', 'start_date'),
                State('date-picker', 'end_date')])
def get_prices(n_clicks, ticker_list, start, end):
    if ticker_list is None:
        return {'data': [],
                'layout': go.Layout(title='Prices')}

    df = pdr.tiingo.TiingoDailyReader(ticker_list,
                                        start=start,
                                        end=end,
                                        api_key=tiingo_key).read()
    df = df.reset_index(level=['date', 'symbol']) # reset multi-index to new single-index

    data = [go.Scatter(x=df['date'],
                            y=df[df['symbol'] == t]['adjClose'],
                            name=t,
                            mode='lines') for t in ticker_list]
    figure = {'data': data,
                'layout': go.Layout(title=f"{', '.join(ticker_list)} Prices",
                                    hovermode='closest')}
    return figure

if __name__ == '__main__':
    app.run_server()
