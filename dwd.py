import requests
import os

from zipfile import ZipFile

import ftp_file_loader

# This module is used to download files from opendata.dwd.de

def get_stations_metadata(file_loader, data_path):
    return file_loader.load_file("KL_Tageswerte_Beschreibung_Stationen.txt", data_path + "KL_Tageswerte_Beschreibung_Stationen.txt")

def get_historical_daily_weather_data_for_station(file_loader, station_id, data_path):
    station_filename = format_station_filename(station_id)
    daily_weather_data_for_station_filename = file_loader.load_file_starts_with(station_filename)
    if (daily_weather_data_for_station_filename):
        return extract_file_from_zip_folder_starts_with(daily_weather_data_for_station_filename, "produkt_klima_tag_", data_path)
    return False

def format_station_filename(station_id):
    return f"tageswerte_KL_{station_id}_"

def extract_file_from_zip_folder_starts_with(zip_filename, filename, data_path):    
    with ZipFile(zip_filename, "r") as zipfile:
        for data_filename in zipfile.namelist():
            extracted_filename = data_path + data_filename
            if data_filename.startswith(filename):
                if not os.path.isfile(extracted_filename):
                    zipfile.extract(data_filename, path = data_path)
                    print("INFO: extracted " + data_filename + " from " + zip_filename + " into " + extracted_filename)
                return extracted_filename
    return False


# use main function as functional module test
if __name__ == "__main__":
    ftp_host = "opendata.dwd.de"
    ftp_cwd = "/climate_environment/CDC/observations_germany/climate/daily/kl/historical/"
    data_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep
    ftp_loader = ftp_file_loader.FTPFileLoader(ftp_host, ftp_cwd, "anonymous", "", data_path)

    if (get_historical_daily_weather_data_for_station(ftp_loader, "xyz", data_path) != False):
        print("ERROR: Station with ID 'xyz' shouldn't exist!")
        exit(1)

    get_stations_metadata(ftp_loader, data_path)
    get_historical_daily_weather_data_for_station(ftp_loader, "00091", data_path)

    if (extract_file_from_zip_folder_starts_with(data_path + "tageswerte_KL_00091_19781101_20181231_hist.zip", "xyz", data_path) != False):
        print("ERROR: file xyz shouldn't exist in tageswerte_KL_00091_19781101_20181231_hist.zip!")
        exit(1)

    
    extracted_filename = extract_file_from_zip_folder_starts_with(data_path + "tageswerte_KL_00091_19781101_20181231_hist.zip", "produkt_klima_tag_", data_path)
    if (extracted_filename != data_path + "produkt_klima_tag_19781101_20181231_00091.txt"):
        print("ERROR: file produkt_klima_tag_19781101_20181231_00091.txt should exist! Actual: " + extracted_filename)
        exit(1)
