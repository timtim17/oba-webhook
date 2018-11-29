import requests

_OBA_URL = "http://api.pugetsound.onebusaway.org"
_OBA_PREFIX = "/api/where/"

_OBA_FUNCTIONS = {
    "stops_for_location": "stops-for-location",
    "routes_for_stop": "arrivals-and-departures-for-stop",
    "route": "route",
    "routes_for_location": "routes-for-location"
}

class OBAAPIConnection:
    def __init__(self, apiKey):
        self.apiKey = apiKey
    
    def _call_func(self, func, params):
        param_str = ""
        for key in params.keys():
            param_str += "&%s=%s" % (key, params[key])
        
        path = _OBA_PREFIX + func + ".json?key=" + self.apiKey + param_str
        print("API Request: %s" % path)

        return requests.get(_OBA_URL + path).json()
    
    def nearest_stop(location):
        return None
    
    def routes_for_stop(stop_id):
        return None
    
    def route_time(route_id, stop_id):
        return None

