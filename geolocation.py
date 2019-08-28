import requests
from math import cos, asin, sqrt

base_url = "https://nominatim.openstreetmap.org/search"

def address_to_geolocation(location_string, result_limit = 1):
    params = {
        "json": 1,
        "q": location_string,
        "format": "json",
        "limit": result_limit
    }

    response = requests.get(url = base_url, params = params)

    if response.status_code != 200:
        return False

    data = response.json()
    if len(data) > 0:
        return {
            "latitude": float(data[0]["lat"]),
            "longitude": float(data[0]["lon"])
        }

    return False

# calculates distance between two lat-long points in kilometers using haversine formula
# source: https://stackoverflow.com/a/21623206
def distance_between_geolocations_km(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295 # Pi/180
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))


# use main function as functional module test
if __name__ == "__main__":
    # distances checked with: https://www.geodatasource.com/distance-calculator
    d_1 = distance_between_geolocations_km(50.7827, 6.0941, 50.7285, 7.0839)
    if (not (69.87 <= d_1 and d_1 <= 69.89)):
        print("ERROR: calculation inaccurate! Expected:", 69.88, "Actual:", d_1)
    
    d_2 = distance_between_geolocations_km(48.0233, 7.8344, 52.5667, 13.1694)
    if (not (631.1 <= d_2 and d_2 <= 631.2)):
        print("ERROR: calculation inaccurate! Expected:", 631.15, "Actual:", d_2)

    res = address_to_geolocation("Schwetzinger Schloss")
    print("Expected (Google Maps): Latitude: 49.384367 Longitutde: 8.570510")
    print("Actual: Latitude:", res["latitude"], "Longitude:", res["longitude"])
    distance_expected_actual = distance_between_geolocations_km(49.384367, 8.570510, res["latitude"], res["longitude"])
    print("distance: ", distance_expected_actual, "km")

    
