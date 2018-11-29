import json

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

@app.route('/', methods=['POST'])
def webhook():
    if not __OBA_KEY:
        return 'unset api key'

    req = request.get_json(silent=True, force=True)
    try:
        intent = req.get('queryResult').get('intent').get('name')
    except AttributeError:
        return 'json error'

    print(req)

    location = req['originalDetectIntentRequest']['payload']['device']['location']['coordinates']
    
    if intent == _INTENT_BUS:
        res = bus(location)
    elif intent == _INTENT_NEARBY_STOPS:
        res = nearby_stops(location)
    elif intent == _INTENT_NEARBY_ROUTES:
        res = nearby_routes(location)
    else:
        log.error('Unexpected action %s' % intent)
        res = 'Unexpected action %s' % req['queryResult']['intent']['displayName']
    
    print('Intent: %s' % intent)
    print('Response: %s' % res)

    return make_response(jsonify(res))

def bus(location):
    return "nothing"

def nearby_stops(location):
    api_res = api.nearby_stops(location)
    stops = api_res['data']['list']
    if len(stops) == 0:
        return {'fulfillmentText': "Sorry, there seems to be no bus stops nearby."}
    else:
        return {'fulfillmentText': "The nearest bus stops are " + _list_to_str([s['name'] for s in stops])}

def nearby_routes(location):
    api_res = api.nearby_routes(location)
    routes = api_res['data']['references']['routes']
    if len(routes) == 0:
        return {'fulfillmentText': "Sorry, there seems to be no routes running near you right now."}
    else:
        routes_as_str = [((r['shortName'] + ": " + r['description']) if r['description'] else r['longName']) for r in routes if r['description']
        resp_text = "The nearest routes right now are "
                        + _list_to_str(routes_as_str)
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
                                "basicCard": {
                                    'formattedText': "\n".join([('- ' + r) for r in routes_as_str])
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
