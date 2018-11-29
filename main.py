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
    
    if intent == _INTENT_BUS:
        res = bus(req)
    elif intent == _INTENT_NEARBY_STOPS:
        res = nearby_stops(req)
    else:
        log.error('Unexpected action %s' % intent)
        res = 'Unexpected action %s' % req['queryResult']['intent']['displayName']
    
    print('Intent: %s' % intent)
    print('Response: %s' % res)

    return make_response(jsonify({'fulfillmentText': res}))

def bus(req):
    parameters = req['queryResult']['parameters']
    return api._call_func("stops-for-location", {"lat": 47.653435, "lon": -122.305641})

def nearby_stops(req):
    return req['originalDetectIntentRequest']['device']['location']

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=61294)
