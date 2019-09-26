import json
import sys
import os
import traceback

from http.server import HTTPServer, BaseHTTPRequestHandler
from  urllib.parse import parse_qsl
from io import BytesIO

import weather_data_controller

web_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "web"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        responseCode = 200
        self.respond("", responseCode)

    def do_GET(self):
        queryParams = None
        if "?" in self.path:
            path_parts = self.path.split("?")
            self.path = path_parts[0]
            query = path_parts[1]
            queryParams = dict(parse_qsl(query, True))

        responseString, responseCode = handleGet(self.path, queryParams)
        self.respond(responseString, responseCode)

    def respond(self, responseString, responseCode):
        response = BytesIO()
        if isinstance(responseString, str):
            response.write(stringMsgToBytes(responseString))
        else:
            response.write(responseString)
        self.send_response(responseCode)
        self.addContentTypeHeader()
        self.end_headers()
        self.wfile.write(response.getvalue())

    def addContentTypeHeader(self):
        if self.path.endswith(".html") or self.path.startswith("/api/html"): # api response formatted as html
            self.send_header("Content-Type", "text/html")
        elif self.path.endswith(".css"):
            self.send_header("Content-Type", "text/css")
        elif self.path.endswith(".png") or self.path.endswith(".PNG"):
            self.send_header("Content-Type", "image/png")
        elif self.path.startswith("/api/json"): # api response formatted as json (not implemented)
            self.send_header("Content-Type", "application/json")
        elif self.path.endswith(".js"):
            self.send_header("Content-Type", "application/javascript")

def handleGet(path, queryParams = None):
    response = False
    responseCode = 404

    print("INFO: webserver request GET:" , path, queryParams, flush = True)

    try:
        # get index page
        if path in ["/", "/index", "/index.html"]:
            response = index(path)
            responseCode = 200
        # handle user request for weather data
        elif queryParams != None and path == "/api/html/weather_for_day_of_year_at_address":
            response = getWeatherForDayOfYearAtAddress(queryParams)
            responseCode = 200
        # handle other files
        elif not "/.." in path:
            response = readFile(path)
            responseCode = 200

        if not response or response == "":
            responseCode = 404
            response = ""
        return response, responseCode
    except Exception as err:
        print("ERROR: Exception:", err, flush = True)
        traceback.print_exc()
        return str(err), 500

def index(path):
    return readFile("/index.html")

# reads binary
def readFile(path):
    try:
        f = open(web_path + path, "rb")
        data = f.read()
        f.close()
        return data
    except:
        return False

def getWeatherForDayOfYearAtAddress(params):
    if not "address" in params or not "date" in params:
        return False
    result = weather_data_controller.yearly_day_of_year_analysis(params["address"], params["date"])
    return result

def bytesMsgToString(byteMsg):
    return str(byteMsg, "utf-8")

def stringMsgToBytes(stringMsg):
    return bytes(stringMsg, "utf-8")

def jsonStringToDict(jsonString):
    try:
        jsonObject = json.loads(jsonString)
    except ValueError:
        return False, None
    return True, jsonObject

def toJsonString(msg):
    return json.dumps(msg)

if __name__ == '__main__':
    # defaults
    host = "0.0.0.0"
    port = 8080

    argc = len(sys.argv)
    if (argc >= 2):
        host = sys.argv[1]
    if (argc >= 3):
        port = int(sys.argv[2])
    print("INFO: Webserver Listening on %s:%d" % (host, port), flush = True)

    httpd = HTTPServer((host, port), SimpleHTTPRequestHandler)
    httpd.serve_forever()
