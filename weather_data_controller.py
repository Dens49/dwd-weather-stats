import os
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

base64_img_html = '<img src="data:image/png;base64, {}" />'

# the whole workflow is run from this function
def yearly_day_of_year_analysis(address, date):
    day_of_year_data = get_data(address, date)
    cleaned_data = clean_data(day_of_year_data)
    html = build_analysis_html(cleaned_data)    
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

def build_analysis_html(day_of_year_data):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    day_of_year_data[" TMK"].plot(ax = ax)
    img_base64_string = fig_to_base64(fig)
    return base64_img_html.format(img_base64_string)

def fig_to_base64(fig):
    out = BytesIO()
    fig.savefig(out, format="png")
    return base64.encodestring(out.getvalue()).decode('utf-8')
