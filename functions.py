"""
The purpose of this file is to store functions that we will be referring to in our data gathering process
"""

# importing plotly express
import plotly.express as px

# we will need packages that allow us to make a GET request
import requests

# importing packages that will allow us to transform our data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# we will need to access files from our system
import os
import datetime

# importing packages that will allow us to set visual params for our plots


# GRABBING API KEY FROM TEXT FILE
def get_api_key(txt_file, key_loc):
    """
    Purpose is to go into a txt file and grab the EIA API Key needed to make data requests
    """
    with open(txt_file, "r") as f:
        lines = f.readlines()
        api_key = lines[key_loc]
        print("successfully grabbed you API Key")

        return api_key


# TRANSLATING A PARAMS JSON OBJECT BEFORE MAKING A DATA REQUEST
def create_params_obj(series_id, start_period):
    """
    Purpose is to create our own params object that we can pass in our
    data request.
    Given some constraints and vars, create a params json object
    """
    # setting up a variable for todays date
    today = datetime.date.today()
    year_month = today.strftime("%Y-%m")

    # creating the json object that will make the request
    params_object = {
        "frequency": "monthly",  # usually we want monthly data from STEO dataset
        "data": ["value"],
        "facets": {"seriesId": [str(series_id)]},
        "start": str(start_period),
        "end": str(year_month),
        "sort": [{"column": "period", "direction": "desc"}],
        "offset": 0,
        "length": 5000,
    }

    return params_object


# GRABBING DATA FROM EIA OPEN DATA
def grab_steo_data(params_object, api_key):
    """
    Purpose is to make a request to EIA Open Data API for STEO specific data
    """
    # this is the base url for STEO
    url = "https://api.eia.gov/v2/steo/data/"

    # frequency of data, either monthly, quarterly, or annually
    freq = "&frequency=" + str(params_object["frequency"])

    # data type
    d_type = "&data[0]=" + str(params_object["data"][0])

    # this ensures that we sort data by period
    sort = "&sort[0][column]=period"

    # placing our sort order in a descending format
    direction = "&sort[0][direction]=desc"

    # offset, not entirely sure what this is
    offset = "&offset=0"

    # length of the data that we are requesting, the max that we can request is 5_000
    length = "&length=5000"

    # essentially, if the facets params section of the object has something process it
    if len(params_object["facets"]) > 0:
        facet = f'&facets[seriesId][]={params_object['facets']['seriesId'][0]}'
        start = f'&start={params_object['start']}'

        # concatenating all url segments
        full_url = f"{url}?api_key={api_key}{freq}{d_type}{facet}{start}{sort}{direction}{offset}{length}"

    else:
        start = f'&start={params_object['start']}'

        # concatenating all url segments to create a full url
        full_url = f"{url}?api_key={api_key}{freq}{d_type}{start}{sort}{direction}{offset}{length}"

        # letting the user know that the facets length was 0 aka that no features were selected
        print(f'facets object length is {len(params_object['facets'])}!')

    # let's check our full url
    # print(full_url)

    # we know begin the request process
    request = requests.get(full_url)
    data = request.json()

    # grabbing just the data, stripping the data object from unnecessary stuff
    entries = data["response"]["data"]

    # converting the data we just grabbed into a df
    dataframe = pd.DataFrame(data=entries)

    # changing the period column into a data type
    dataframe["period"] = pd.to_datetime(dataframe["period"])

    # returning the dataframe
    return dataframe


# GIVEN A LIST OF SERIES IDS, CREATE A PARAM OBJECT, GRAB DATA, AND ADD IT TO A DF
def series_to_dataframe(series_list, start_date, save_path, key):
    """
    Purpose is to process a list of series IDs and make a data request
    """

    # creating an empty dataframe
    main_df = pd.DataFrame()

    # iterating through each series id in the list to request data
    for series in series_list:
        # first, we want to create a json params object to process request
        params = create_params_obj(series_id=series, start_period=start_date)

        # now we want to request the data
        temp_df = grab_steo_data(params_object=params, api_key=key)

        # now we are adding this specific temp df into our main df
        main_df = pd.concat([main_df, temp_df])

    # resetting index of our dataframe
    main_df = main_df.reset_index(drop=True)

    # making the value column into a float
    main_df["value"] = main_df["value"].astype(float)

    # before saving out data file let's make sure we create col documenting forecast month
    main_df["forecast_period"] = save_path[-11:-4]

    # need to convert the forecast period column to a datetype
    main_df["forecast_period"] = pd.to_datetime(
        main_df["forecast_period"], format="%Y_%m"
    )

    # now we are going to save our data into a file system
    main_df.to_csv(save_path, index=False)

    return main_df


# GIVEN SOME PARAMS, PLOT THE DATA!
def gimme_lineplot(dataframe, title, width=16, height=8):
    fig = plt.figure()
    fig.set_figwidth(width)
    fig.set_figheight(height)

    sns.lineplot(
        data=dataframe, x="period", y="value", hue="seriesDescription", errorbar=None
    )
    plt.legend().set_title(None)
    plt.title(str(title))
    plt.xlabel("")
    plt.ylabel(dataframe["unit"][0])
    plt.xticks(rotation=90)

    plt.show()


# MEANDER THROUGH SPECIFIC FOLDERS AND CONCAT DATA INTO ONE DATAFRAME
def concat_dfs(folderpath, df_name):
    """
    Purpose of this function is to grab all files from a specific area, concatenate them and then outpout them
    as a master df

    need to import os and pandas
    """
    # creating any empty list where all datafiles will be stored
    dfs = []

    # grabbing all datafiles from the provided path
    for filename in os.listdir(folderpath):
        if filename.endswith("csv"):
            file_path = os.path.join(folderpath, filename)

            try:
                # reading the csv file to make sure that it is good to go
                df = pd.read_csv(file_path)

                # adding to our master df
                dfs.append(df)

            except Exception as e:
                print(f"error reading {filename}: {e}")
                continue  # we must move forward king

    # concetanating all of our dfs
    master_df = pd.concat(dfs, axis=0)

    # resetting our index
    master_df = master_df.reset_index()

    # dropping the dumb 'index' column
    master_df = master_df.drop(columns="index", axis=1)

    # setting our period column to a date type
    master_df["period"] = pd.to_datetime(master_df["period"])

    # saving our file under 'master output'
    master_df.to_csv(f"master_output/{df_name}.csv", index=False)

    # letting the homies know everythig is good to go
    print("Master data has been successfully processed")

    print(master_df.info())


# GRAB A LIST OF PERIOD FORECASTS FROM THE 'FORECAST PERIOD' COLUMN
def recent_forecast(df):
    """
    given a dataframe, only grab the most recent forecast data
    """

    # grabbing the forecast date column and returning as a list
    forecast_periods = df["forecast_period"].tolist()

    # variable storing the most recent list
    recent_period = max(forecast_periods)

    # filter dataframe to only include data with most recent forecast
    df_filtered = df[df["forecast_period"] == recent_period]

    return df_filtered


# GIVEN WHAT USER SELECTS, RETURN THE TYPE OF GRAPH WITH NECESSARY PARAMETERS
def gimme_plot(
    dataframe, y_ax, hue_by, topic_choice, color_by, x_ax="period", plot_type="lineplot"
):
    """
    purpose is to return a graph depending on what kind of graph is called
    """

    if plot_type == "line":
        fig = px.line(
            dataframe[dataframe["seriesId"].isin(topic_choice)],
            x=x_ax,
            y=y_ax,
            hue_by=hue_by,
            color=color_by,
        )

    elif plot_type == "scatter":
        fig = px.scatter(
            dataframe[dataframe["seriesId"].isin(topic_choice)],
            x=x_ax,
            y=y_ax,
            hue_by=hue_by,
            color=color_by,
        )

    elif plot_type == "area":
        fig = px.area(
            dataframe[dataframe["seriesId"].isin(topic_choice)],
            x=x_ax,
            y=y_ax,
            hue_by=hue_by,
            color=color_by,
        )

    elif plot_type == "bar":
        fig = px.bar(
            dataframe[dataframe["seriesId"].isin(topic_choice)],
            x=x_ax,
            y=y_ax,
            hue_by=hue_by,
            color=color_by,
            barmode="group",
        )

    elif plot_type == "stackedarea":
        fig = px.area(
            dataframe[dataframe["seriesId"].isin(topic_choice)],
            x=x_ax,
            y=y_ax,
            hue_by=hue_by,
            color=color_by,
            line_group=hue_by,
        )

    return fig


# POPULAR VISUAL FUNCTIONS THAT TAKES IN A SERIES LIST
def pop_visual(series_list, start_date, api_key, figure_name):
    """
    purpose of this function is to grab the necessary data, create the necessary
    save paths and process it all together irrespective of what list is provided
    """
    # creating a save date by grabbing todays date
    save_date = datetime.date.today().strftime("%Y_%m")

    # creating a save path using the the save date variable
    save_path = f"output/popular_visuals/{figure_name}_{save_date}.csv"

    # temporary dataframe that will be used to process and store requested data
    pop_df = series_to_dataframe(
        series_list=series_list, start_date=start_date, save_path=save_path, key=api_key
    )

    # printing information on the processed data so that it can be checked for any errors
    # print(pop_df.info())

    # returning the df so that it can be further processed and used
    return pop_df
