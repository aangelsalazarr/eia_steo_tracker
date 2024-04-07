import pandas as pd
from collections import OrderedDict
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

import dash_bootstrap_components as dbc

# Loading in some sample data, forecasts for solar in this case
df = pd.read_csv('master_output/master_battery_data.csv')

# converting our 'period' column to datetime
df['period'] = pd.to_datetime(df['period'])

# incase you wanna see the info of the data that we are grabbing
# print(df.info())

# creating dashapp
app = Dash(__name__)

# App layout with dropdowns and date filter
app.layout = html.Div([
    dcc.Dropdown(
        id='select-column',
        options=[
            {'label': col, 'value': col} for col in df.columns if col != 'period'
            ],
        value='value'  # this means it will by default set to 'value' column from our df
        ),
    
    dcc.Dropdown(
        id='select-filter',
        options = [
            {'label': 'Filter by Specific Series Topic', 'value': True},
            {'label': 'Do Not Filter by Specific Series Topic', 'value': False}
        ]
    ),

    dcc.Dropdown(
        id='select-plot',
        options=[
            {'label': 'Scatter', 'value': 'scatter'}, 
            {'label': 'Line', 'value': 'line'}, 
            {'label': 'Area Plot', 'value': 'area'},
            {'label': 'Bar Plot', 'value': 'bar'}
            ],
        value='line'
        ),

    dcc.Dropdown(
        id='select-hue', 
        options=[
            {'label': col, 
             'value': col} for col in df.columns if col not in ['period', 
                                                                'select-column']],
            value='forecast_month'
        ), 

    dcc.Dropdown(
        id='select-seriesDescription',
        options = [
            {'label': i, 'value': i} for i in df['seriesDescription'].unique()
        ],
        value=df['seriesDescription'].unique()[0]
        ),

    dcc.DatePickerRange(
        id='date-range',
        min_date_allowed=df['period'].min(),
        max_date_allowed=df['period'].max(),
        start_date=df['period'].min(),
        end_date=df['period'].max()
        ),
    dcc.Graph(id='graph')
    ])

# Update graph based on user selections
@app.callback(
    Output('graph', 'figure'),
    Input('select-column', 'value'),
    Input('select-filter', 'value'),
    Input('select-plot', 'value'),
    Input('select-hue', 'value'),
    Input('select-seriesDescription', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
)

def update_graph(column, select_filter, plot_type, hue_column, seriesDescription, 
                 start_date, end_date):

    if select_filter == True: 

        # this allows the user to filter the data being presented by date
        filtered_df = df[(df['period'] >= start_date) & (df['period'] <= end_date)]

        # filtering by seriesDescription
        temp_df = filtered_df[filtered_df['seriesDescription'] == str(seriesDescription)]

        # here we are creating the plot!
        if plot_type == 'scatter':
            fig = px.scatter(temp_df[temp_df['seriesDescription'] == seriesDescription], 
                            x='period', y=column, color=hue_column)

        elif plot_type == 'line':
            fig = px.line(temp_df[temp_df['seriesDescription'] == seriesDescription], 
                        x='period', y=column, color=hue_column)
            
        elif plot_type == 'area':
            fig = px.area(temp_df[temp_df['seriesDescription']==seriesDescription],
                        x='period', y=column, color=hue_column)
            
        elif plot_type == 'bar':
            # setting up the colors for or graphs
            bar_colors = ['red', 'blue']

            fig = px.bar(temp_df[temp_df['seriesDescription']==seriesDescription], 
                         x='period', y=column, color=hue_column, barmode='group')
            
    else: 
        
        # this allows the user to filter the data being presented by date
        filtered_df = df[(df['period'] >= start_date) & (df['period'] <= end_date)]

        # here we are creating the plot!
        if plot_type == 'scatter':
            fig = px.scatter(filtered_df, 
                            x='period', y=column, color=hue_column)

        elif plot_type == 'line':
            fig = px.line(filtered_df, 
                        x='period', y=column, color=hue_column)
            
        elif plot_type == 'area':
            fig = px.area(filtered_df,
                        x='period', y=column, color=hue_column)
            
        elif plot_type == 'bar':
            fig = px.bar(filtered_df,
                         x='period', y=column, color=hue_column)
    

    # updated the dashboard that we have created
    fig.update_layout(title=f"", 
                        xaxis_title = f'', 
                        yaxis_title = f'{filtered_df['unit'][0]}', 
                        plot_bgcolor='white', 
                        font_family='arial',
                        xaxis=dict(showgrid=False), 
                        yaxis=dict(showgrid=False),
                        ) # background color

    # returns the figure to the website
    return fig

# run the app
if __name__ == '__main__':
    app.run_server(debug=True)
