import numpy as np
import pandas as pd
import os

import dwd
import ftp_file_loader
import geolocation

# this file is used to transfrom data from module dwd (which loads files from opendata.dwd.de) into usable pandas dataframes

# TODO: implement caching of dataframes?

def get_and_prepare_stations(file_loader, data_path):
    cols = ["Stations_id", "geoBreite", "geoLaenge"]
    stations_metadata_filename = dwd.get_stations_metadata(file_loader, data_path)

    stations = pd.read_csv(stations_metadata_filename, sep = "\s+", usecols = cols)
    stations.drop(0, inplace = True) # remove row with only hyphens -------

    stations["geoBreite"] = pd.to_numeric(stations["geoBreite"])
    stations["geoLaenge"] = pd.to_numeric(stations["geoLaenge"])

    stations.rename(columns = {
        "Stations_id": "station_id",
        "geoBreite": "latitude",
        "geoLaenge": "longitude"
    }, inplace = True)

    return stations

def get_and_prepare_daily_weather_data_for_station(file_loader, station, data_path):
    historical_data_filename = dwd.get_historical_daily_weather_data_for_station(
        file_loader,
        station["station_id"].item(),
        data_path
    )
    # TODO: merge historical data with current year's data (if that data is available)

    daily_weather = pd.read_csv(historical_data_filename, sep = ";")
    daily_weather["MESS_DATUM"] = pd.to_datetime(daily_weather["MESS_DATUM"], format = "%Y%m%d")
    daily_weather.rename(columns = {
        "STATIONS_ID": "station_id",
        "MESS_DATUM": "date"
    }, inplace = True)

    # remove leading whitespaces in column names
    for col in daily_weather.columns:
        if (col.startswith(" ")):
            daily_weather.rename(columns = {col: col.strip()}, inplace = True)

    # remove columns that will definitely not be used
    daily_weather.drop(["eor"], axis = 1, inplace = True)

    return daily_weather

# adds new column temporarily to the dataframe and groups by that column
def extract_weather_data_for_day_of_year(daily_weather, date):
    daily_weather["tmp_date_md"] = daily_weather["date"].apply(format_datetime, without_year = True)
    grouped = daily_weather.groupby("tmp_date_md")
    target_month_day = format_datetime(date, without_year = True)
    day_of_year_data = grouped.get_group(target_month_day)
    
    day_of_year_data.drop("tmp_date_md", axis = 1, inplace = True) # triggers a SettingWithCopyWarning but is false positive in this case
    daily_weather.drop("tmp_date_md", axis = 1, inplace = True)

    return day_of_year_data

# this function can handle a datetime string, integer unix timestamp, np.datetime64
# use parameter unit to set the timestamps unit when it's an integer timestamp. see pd.Timestamp(...)
# use parameter without_year to only get month and day
def format_datetime(date, unit = None, without_year = False):
    if (unit is None):
        ts = pd.Timestamp(date)
    else:
        ts = pd.Timestamp(date, unit = unit)
    
    if (without_year):
        time_format = "%m%d"
    else:
        time_format = "%Y%m%d"

    return ts.strftime(time_format)

# add new temporariy column with distance to the specified geolocation
# and find closest station with that
def get_closest_station_to_geolocation(stations, latitude, longitude):
    calculate_distance = lambda x: geolocation.distance_between_geolocations_km(latitude, longitude, x["latitude"], x["longitude"])
    stations["tmp_distance"] = stations.apply(calculate_distance, axis = 1)
    sorted_by_distance = stations.sort_values("tmp_distance", ascending = True)
    
    sorted_by_distance.drop("tmp_distance", axis = 1, inplace = True) # triggers a SettingWithCopyWarning but is false positive in this case
    stations.drop("tmp_distance", axis = 1, inplace = True)
    
    return sorted_by_distance.head(1)


# use main function as functional module test
if __name__ == "__main__":
    ftp_host = "opendata.dwd.de"
    ftp_cwd = "/climate_environment/CDC/observations_germany/climate/daily/kl/historical/"
    data_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep
    ftp_loader = ftp_file_loader.FTPFileLoader(ftp_host, ftp_cwd, "anonymous", "", data_path)

    stations = get_and_prepare_stations(ftp_loader, data_path)
    test_station = stations[stations["station_id"] == "00091"]
    daily_weather = get_and_prepare_daily_weather_data_for_station(ftp_loader, test_station, data_path)

    print(stations.head(5))
    print(test_station)
    print(daily_weather.tail(5))

    weather_day_of_year = extract_weather_data_for_day_of_year(daily_weather, "20190614")
    print(weather_day_of_year.head(5))

    # Freiburg with station_id 01443. Data taken from KL_Tageswerte_Beschreibung_Stationen.txt so the closest distance should be very close or equal to 0.0
    closest_station = get_closest_station_to_geolocation(stations, 48.0233, 7.8344)
    print(closest_station)
