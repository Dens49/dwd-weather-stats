import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import base64

from io import BytesIO

import ftp_file_loader
import geolocation
import data_wrangling

ftp_host = "opendata.dwd.de"
ftp_cwd = "/climate_environment/CDC/observations_germany/climate/daily/kl/historical/"
data_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep
ftp_loader = ftp_file_loader.FTPFileLoader(ftp_host, ftp_cwd, "anonymous", "", data_path)

# TODO: move html strings to template file
title_html = "<h3>{}</h3>"
base64_img_html = '<img src="data:image/png;base64, {}" />'

# the whole workflow is run from this function
def yearly_day_of_year_analysis(address, date):
    day_of_year_data = get_data(address, date)
    cleaned_data = clean_data(day_of_year_data)
    html = build_analysis_html(cleaned_data, address, date)    
    return html

def get_data(address, date):
    # get geolocation for address
    geolocation_result = geolocation.address_to_geolocation(address)
    if (geolocation_result == False):
        raise Exception(f"Geolocation for '{address}' could not be found")
    latitude = geolocation_result["latitude"]
    longitude = geolocation_result["longitude"]

    # get stations metadata
    stations = data_wrangling.get_and_prepare_stations(ftp_loader, data_path)

    # get closest station to geolocation of address
    closest_station = data_wrangling.get_closest_station_to_geolocation(stations, latitude, longitude)

    # get daily weather data for the station
    daily_weather = data_wrangling.get_and_prepare_daily_weather_data_for_station(ftp_loader, closest_station, data_path)

    # extract yearly weather data for day of year
    day_of_year_data = data_wrangling.extract_weather_data_for_day_of_year(daily_weather, date)

    return day_of_year_data

# TODO
def clean_data(day_of_year_data):
    return day_of_year_data

def build_analysis_html(day_of_year_data, address, date):
    # TODO: add format option to data_wrangling.format_datetime
    full_date = pd.Timestamp(date).strftime("%Y-%m-%d")
    md_date = pd.Timestamp(date).strftime("%m-%d")
    y_date = pd.Timestamp(date).strftime("%Y")
    y_date_from = pd.Timestamp(day_of_year_data.head(1)["date"].item(), unit = "ns").strftime("%Y")
    y_date_to = pd.Timestamp(day_of_year_data.tail(1)["date"].item(), unit = "ns").strftime("%Y")
    data_amount = day_of_year_data.shape[0]
    context_info = f"for {md_date} from {y_date_from} to {y_date_to} ({data_amount} Measurements)"

    html = []
    html.append(title_html.format("Data for " + address + " for " + full_date))
    
    x_axis_years = np.asarray(list(map(lambda x: pd.Timestamp(x, unit = "ns").strftime("%Y"), day_of_year_data["date"].values)))

    # TODO: might want to put max min and mean temperature in the same plot but with different colors

    # temperature mean TMK
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    day_of_year_data["TMK"].plot(ax = ax)

    ax.set_xticks(day_of_year_data.index)
    ax.set_xticklabels(x_axis_years, rotation = 90)
    # hide every second xtick label
    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)

    ax.set_ylim(-20, 45)
    plt.title("Mean Temperature C° " + context_info)
    plt.xlabel("Year")
    plt.ylabel("Temperature C°")
    img_base64_string = fig_to_base64(fig)
    html.append(base64_img_html.format(img_base64_string))

    # temperature min TNK
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    day_of_year_data["TNK"].plot(ax = ax)

    ax.set_xticks(day_of_year_data.index)
    ax.set_xticklabels(x_axis_years, rotation = 90)
    # hide every second xtick label
    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)

    ax.set_ylim(-20, 45)
    plt.title("Minimum Temperature C° " + context_info)
    plt.xlabel("Year")
    plt.ylabel("Temperature C°")
    img_base64_string = fig_to_base64(fig)
    html.append(base64_img_html.format(img_base64_string))

    # temperature max TXK
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    day_of_year_data["TXK"].plot(ax = ax)

    ax.set_xticks(day_of_year_data.index)
    ax.set_xticklabels(x_axis_years, rotation = 90)
    # hide every second xtick label
    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)

    ax.set_ylim(-20, 45)
    plt.title("Maximum Temperature C° " + context_info)
    plt.xlabel("Year")
    plt.ylabel("Temperature C°")
    img_base64_string = fig_to_base64(fig)
    html.append(base64_img_html.format(img_base64_string))

    # sun hours per day SDK
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    day_of_year_data["SDK"].plot(ax = ax)

    ax.set_xticks(day_of_year_data.index)
    ax.set_xticklabels(x_axis_years, rotation = 90)
    # hide every second xtick label
    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)

    ax.set_ylim(0, 24)
    plt.title("Sun hours per day " + context_info)
    plt.xlabel("Year")
    plt.ylabel("Hours")
    img_base64_string = fig_to_base64(fig)
    html.append(base64_img_html.format(img_base64_string))

    # precipitation mm RSK
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    day_of_year_data["RSK"].plot(ax = ax)

    ax.set_xticks(day_of_year_data.index)
    ax.set_xticklabels(x_axis_years, rotation = 90)
    # hide every second xtick label
    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)

    ax.set_ylim(0, 170)
    plt.title("Precipitation mm " + context_info)
    plt.xlabel("Year")
    plt.ylabel("Precipitation mm")
    img_base64_string = fig_to_base64(fig)
    html.append(base64_img_html.format(img_base64_string))

    # snow height SHK_TAG
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    day_of_year_data["SHK_TAG"].plot(ax = ax)

    ax.set_xticks(day_of_year_data.index)
    ax.set_xticklabels(x_axis_years, rotation = 90)
    # hide every second xtick label
    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)

    ax.set_ylim(0, 200)
    plt.title("Snow height cm " + context_info)
    plt.xlabel("Year")
    plt.ylabel("Snow height mm")
    img_base64_string = fig_to_base64(fig)
    html.append(base64_img_html.format(img_base64_string))

    # mean wind speed FM
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    day_of_year_data["FM"].plot(ax = ax)

    ax.set_xticks(day_of_year_data.index)
    ax.set_xticklabels(x_axis_years, rotation = 90)
    # hide every second xtick label
    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)

    ax.set_ylim(0, 40)
    plt.title("Mean Wind Speed m/s " + context_info)
    plt.xlabel("Year")
    plt.ylabel("Wind Speed m/s")
    img_base64_string = fig_to_base64(fig)
    html.append(base64_img_html.format(img_base64_string))

    # max wind speed FX
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    day_of_year_data["FX"].plot(ax = ax)

    ax.set_xticks(day_of_year_data.index)
    ax.set_xticklabels(x_axis_years, rotation = 90)
    # hide every second xtick label
    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)

    ax.set_ylim(0, 40)
    plt.title("Maximum Wind Speed m/s " + context_info)
    plt.xlabel("Year")
    plt.ylabel("Wind Speed m/s")
    img_base64_string = fig_to_base64(fig)
    html.append(base64_img_html.format(img_base64_string))


    return "".join(html)

def fig_to_base64(fig):
    out = BytesIO()
    fig.savefig(out, format="png")
    return base64.encodestring(out.getvalue()).decode('utf-8')
