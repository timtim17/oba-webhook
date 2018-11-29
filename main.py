import json
import urllib

from datetime import datetime
from flask import Flask, request, make_response, jsonify
from os import getenv
from OBAAPIConnection import OBAAPIConnection

__OBA_KEY = getenv('oba-key')

app = Flask(__name__)
log = app.logger
api = OBAAPIConnection(__OBA_KEY)

_INTENT_BUS = "projects/assistant-kcmetro/agent/intents/3ca947d8-88c2-492c-ab84-1a2fd3b44c25"
_INTENT_NEARBY_STOPS = "projects/assistant-kcmetro/agent/intents/dffdd136-07f8-4ba7-afd4-6ebf7a806d39"
_INTENT_NEARBY_ROUTES = "projects/assistant-kcmetro/agent/intents/3ccaba9f-29eb-4038-bf62-f67943a47f7a"
_INTENT_STOP_INFO = "projects/assistant-kcmetro/agent/intents/bb1090db-7242-4e0b-8ae1-2b39681d4acb"

@app.route('/', methods=['POST'])
def webhook():
    if not __OBA_KEY:
        return 'unset api key'

    req = request.get_json(silent=True, force=True)
    print(req)
    intent = req['queryResult']['intent']['name']
    location = req['originalDetectIntentRequest']['payload']['device']['location']['coordinates']
    
    if intent == _INTENT_BUS:
        res = bus(location, req)
    elif intent == _INTENT_NEARBY_STOPS:
        res = nearby_stops(location)
    elif intent == _INTENT_NEARBY_ROUTES:
        res = nearby_routes(location)
    elif intent == _INTENT_STOP_INFO:
        res = stop_info(req)
    else:
        log.error('Unexpected action %s' % intent)
        res = 'Unexpected action %s' % req['queryResult']['intent']['displayName']
    
    print('Intent: %s' % intent)
    print('Response: %s' % res)

    return make_response(jsonify(res))

def bus(location, req):
    route = req['queryResult']['parameters']['bus_route']
    if type(route) is float:
        route = int(route) # drop decimal
    route = str(route)
    direction = req['queryResult']['parameters']['direction']
    direction = 1 if (direction == 'north' or direction == 'east') else 0
    api_res = api.nearby_stops(location)
    route_id = [x['id'] for x in api_res['data']['references']['routes'] if x['shortName'] == route]
    if len(route_id) > 0:
        route_id = route_id[0]
        trips = api.trips_for_route(route_id, include_schedule=True)
        stops = [x['id'] for x in api_res['data']['list'] if route_id in x['routeIds']]
        if len(stops) > 0:
            trip_objects = [x for x in trips['data']['references']['trips'] if x['directionId'] == direction and x['routeId'] == route_id]
            if len(trip_objects) > 0:
                trip_schedules = [x for x in trips['data']['list'] if x['tripId'] in [y['id'] for y in trip_objects]]
                for i in range(len(trip_schedules)):
                    schedule = trip_schedules[i]['schedule']['stopTimes']
                    for time in schedule:
                        stop_id = time['stopId']
                        if stop_id in stops:
                            trip_schedules[i] = (time['arrivalTime'], trip_schedules[i], datetime.fromtimestamp(float(trip_schedules[i]['serviceDate'] + time['arrivalTime'] * 1000) / 1000).strftime('%B, %-d at %-I:%M %p'), stop_id)
                            break
                trip_tup = trip_schedules.sort(key=lambda t: t[0])[0]
                trip_time = trip_tup[2]
                trip_id = trip_tup[1]['tripId']
                trip_desc = [x for x in trip_objects if x['id'] == trip_id][0]['tripHeadsign']
                stop = [x['name'] for x in api_res['data']['references']['stops'] if x['id'] == trip_tup[4]][0]
                return {'fulfillmentText': "Route %s will arrive at %s on %s" % (route, stop, trip_time)}
    return {'fulfillmentText': 'Sorry, it doesn\'t appear that that route is in operation near you right now.'}

def nearby_stops(location):
    api_res = api.nearby_stops(location)
    stops = api_res['data']['list']
    if len(stops) == 0:
        return {'fulfillmentText': "Sorry, there seems to be no bus stops nearby."}
    else:
        stops_as_str = [s['name'] for s in stops]
        resp_text = "The nearest bus stops are " + _list_to_str(stops_as_str)
        return {
            'fulfillmentText': resp_text,
            'payload': {
                'google': {
                    'expectUserResponse': True,
                    'richResponse': {
                        'items': [
                            {
                                "simpleResponse": {
                                    'textToSpeech': resp_text,
                                    'displayText': "Here are the nearest stops, tap one to find out more about it:"
                                }
                            }# ,
                            # {
                            #     "tableCard": {
                            #         'rows': [{"cells": [{"text": s['name']}]} for s in stops]
                            #     }
                            # }
                        ]
                    },
                    'systemIntent': {
                        'intent': 'actions.intent.OPTION',
                        "inputValueData": {
                            "@type": "type.googleapis.com/google.actions.v2.OptionValueSpec",
                            "listSelect": {
                                "title": "Bus Stops",
                                "items": [{
                                    "optionInfo": {
                                        "key": s['name']
                                    },
                                    "title": s['name']
                                } for s in stops]
                            }
                        }
                    }
                }
            }
        }

def stop_info(req):
    stop_name = req['originalDetectIntentRequest']['payload']['inputs'][0]['arguments'][0]['textValue']
    return {'payload': {
        'google': {
            'expectUserResponse': True,
            'richResponse': {
                'items': [
                    {
                        'simpleResponse': {
                            'textToSpeech': "Here's some more information about %s" % stop_name,
                            'displayText': "Okay, %s" % stop_name
                        }
                    },
                    {
                        'basicCard': {
                            "title": stop_name,
                            "formattedText": "%s is a bus stop." % stop_name,
                            "buttons": [
                                {
                                    "title": "Open in Maps",
                                    "openUrlAction": {
                                        "url": "https://www.google.com/maps/search/?api=1&%s" % urllib.parse.urlencode({"query": stop_name})
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }}

def nearby_routes(location):
    api_res = api.nearby_routes(location)
    routes = api_res['data']['references']['routes']
    if len(routes) == 0:
        return {'fulfillmentText': "Sorry, there seems to be no routes running near you right now."}
    else:
        routes_as_str = [((r['shortName'] + ": " + r['description']) if r['description'] else r['longName']) for r in routes if r['description']]
        resp_text = "The nearest routes right now are " + _list_to_str(routes_as_str if (len(routes_as_str) <= 5) else routes_as_str[:5])
        return {
            'fulfillmentText': resp_text,
            'payload': {
                'google': {
                    'expectUserResponse': True,
                    'richResponse': {
                        'items': [
                            {
                                "simpleResponse": {
                                    'textToSpeech': resp_text,
                                    'displayText': "Here are the nearest routes:"
                                }
                            },
                            {
                                "tableCard": {
                                    'rows': [{"cells": ([{"text": r['shortName']}, {"text": r['description']}]) if r['description'] else [{"text": r['longName']}, {"text": ""}]} for r in routes if (r['description'] or r['longName'])]
                                }
                            }
                        ]
                    }
                }
            }
        }

def _list_to_str(l):
    """
    Converts a list to a string in the format "list item 1, list item 2, ..., and list item n".
    Precondition: list expected to have length >= 1
    """
    res_string = l[0]
    list_size = len(l)
    if list_size > 1:
        for i in range(1, list_size - 1):
            res_string += ", " + l[i]
        res_string += ", and " + l[list_size - 1]
    return res_string

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=61294)
