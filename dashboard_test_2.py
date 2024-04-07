import pandas as pd
from dash import Dash, dcc, html, Input, Output

# importing our functions python script
import functions as fns

# may want to import null if needed
# import null


# this will allow us to create a stacked area plot

# Loading in some sample data, forecasts for solar in this case
df = pd.read_csv("master_output/master_wind_data.csv")
## df = pd.read_csv('output/popular_visuals/world_net_demand_march_2024.csv')

# converting our 'period' column to datetime
df["period"] = pd.to_datetime(df["period"])

# incase you wanna see the info of the data that we are grabbing
# print(df.info())

# creating dashapp
app = Dash(__name__)

# App layout with dropdowns and date filter
app.layout = html.Div(
    [
        # allows users to select how they want to use the dashboard
        # either they want to compare historical forecasts or not
        dcc.Dropdown(
            id="select-purpose",
            options=[
                {"label": "Comparison", "value": "comparison"},
                {"label": "Current Forecast", "value": "no comparison"},
            ],
            value="comparison",
        ),
        # allows user to select hue of data visualization
        dcc.Dropdown(
            id="select-hue",
            options=[
                {"label": col, "value": col}
                for col in df.columns
                if col != "period_forecast"
            ],
            value="forecast_period",
        ),
        # allows user to select color based on another columns
        dcc.Dropdown(
            id="select-color",
            options=[
                {"label": col, "value": col}
                for col in df.columns
                if col != "forecast_period"
            ],
        ),
        # allows users to select the y axis (x axis is always default period)
        dcc.Dropdown(
            id="select-column",
            options=[
                {"label": col, "value": col} for col in df.columns if col != "period"
            ],
            value="value",  # this means it will by default set to 'value' column from our df
        ),
        # allows users to now select what kind of plot they would like to use
        dcc.Dropdown(
            id="select-plot",
            options=[
                {"label": "Scatter", "value": "scatter"},
                {"label": "Line", "value": "line"},
                {"label": "Area Plot", "value": "area"},
                {"label": "Bar Plot", "value": "bar"},
                {"label": "Stacked Area Plot", "value": "stackedarea"},
            ],
            value="line",
        ),
        # automatically labels the series description (y axis label)
        dcc.Dropdown(
            id="select-seriesId",
            options=[{"label": i, "value": i} for i in df["seriesId"].unique()],
            value=df["seriesId"].unique()[0],
            multi=True,
        ),
        # allows user to select and filter by date range
        dcc.DatePickerRange(
            id="date-range",
            min_date_allowed=df["period"].min(),
            max_date_allowed=df["period"].max(),
            start_date=df["period"].min(),
            end_date=df["period"].max(),
        ),
        # shows the graph
        dcc.Graph(id="graph"),
    ]
)


# Update graph based on user selections
@app.callback(
    Output("graph", "figure"),
    Input("select-purpose", "value"),  # allows user to select to compare or not compare
    Input("select-hue", "value"),
    Input("select-color", "value"),  # serves as a second color/hue
    Input("select-column", "value"),
    Input("select-plot", "value"),
    Input("select-seriesId", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_graph(
    purpose,
    hue_column,
    color_col,
    column,
    plot_type,
    seriesDescription,
    start_date,
    end_date,
):
    # true if statement to see if pupose is working correctly
    if purpose == "no comparison":
        """
        is user does not want a comparison, then just allow them to see most recent 
        forecast
        """
        # we are returning any data that has the most recent period
        recent_df = fns.recent_forecast(df=df)

        # filtered recent forecast by date
        filtered_df = recent_df[
            (recent_df["period"] >= start_date) & (recent_df["period"] <= end_date)
        ]

        # importing function that returns a graph
        fig = fns.gimme_plot(
            dataframe=filtered_df,
            y_ax=column,
            plot_type=plot_type,
            color_by=color_col,
            hue_by=hue_column,
            topic_choice=seriesDescription,
        )

        # updated the dashboard that we have created
        fig.update_layout(
            title="",
            xaxis_title="",
            yaxis_title="",
            plot_bgcolor="white",
            font_family="arial",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
        )

        # returns the figure to the website
        return fig

    else:
        """
        run this code if the user descides they want to compare forecasts to track changes
        """
        # filtered recent forecast by date
        filtered_df = df[(df["period"] >= start_date) & (df["period"] <= end_date)]

        # importing function that returns a graph
        fig = fns.gimme_plot(
            dataframe=filtered_df,
            y_ax=column,
            plot_type=plot_type,
            color_by=color_col,
            hue_by=hue_column,
            topic_choice=seriesDescription,
        )

        # updated the dashboard that we have created
        fig.update_layout(
            title="",
            xaxis_title="",
            yaxis_title="",
            plot_bgcolor="white",
            font_family="arial",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
        )

        # returns the figure to the website
        return fig


# run the app
if __name__ == "__main__":
    app.run_server(debug=True)
