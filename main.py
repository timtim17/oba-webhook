import json

from flask import Flask, request, make_response, jsonify
from OBAAPIConnection import OBAAPIConnection

# SECRET SECRET SECRET SECRET #
__OBA_KEY = "TEST"
#  END SECRET END SECRET END  #

app = Flask(__name__)
log = app.logger
api = OBAAPIConnection(__OBA_KEY)

_INTENT_BUS = "projects/assistant-kcmetro/agent/intents/3ca947d8-88c2-492c-ab84-1a2fd3b44c25"

@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    try:
        intent = req.get('queryResult').get('intent').get('name')
    except AttributeError:
        return 'json error'

    print(json.dumps(req, indent=4))
    
    if intent == _INTENT_BUS:
        res = bus(req)
    else:
        log.error('Unexpected action %s' % intent)
        res = 'Unexpected action %s' % req['queryResult']['intent']['displayName']
    
    print('Intent: %s' % intent)
    print('Response: %s' % res)

    return make_response(jsonify({'fulfillmentText': res}))

def bus(req):
    parameters = req['queryResult']['parameters']
    print("Dialogflow Parameters:")
    print(json.dumps(parameters, indent=4))

    return api._call_func("stops-for-location", {"lat": 47.653435, "lon": -122.305641})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=61294)
