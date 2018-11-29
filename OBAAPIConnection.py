import requests

_OBA_URL = "http://api.pugetsound.onebusaway.org"
_OBA_PREFIX = "/api/where/"

_OBA_FUNCTIONS = {
    "stops_for_location": "stops-for-location",
    "routes_for_stop": "arrivals-and-departures-for-stop",
    "route": "route",
    "routes_for_location": "trips-for-location"
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
    
    def nearby_stops(self, location, max_count=3):
        return self._call_func(_OBA_FUNCTIONS['stops_for_location'], {"lat": location['latitude'], "lon": location['longitude'], "maxCount": max_count})
    
    def nearby_routes(self, location, max_count=None, lat_span=0.05, lon_span=0.05):
        params = {"lat": location['latitude'], "lon": location['longitude'], "latSpan": lat_span, "lonSpan": lon_span}
        if max_count:
            params['maxCount'] = max_count
        return self._call_func(_OBA_FUNCTIONS['routes_for_location'], params)
    
    def route_time(self, route_id, stop_id):
        return None

