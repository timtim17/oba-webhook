import json

from flask import Flask, request, make_response, jsonify
from OBAAPIConnection import OBAAPIConnection

# SECRET SECRET SECRET SECRET #
__OBA_KEY = "TEST"
#  END SECRET END SECRET END  #

app = Flask(__name__)
log = app.logger
api = OBAAPIConnection(__OBA_KEY)

@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    try:
        action = req.get('queryResult').get('action')
    except AttributeError:
        return 'json error'

    print(json.dumps(req, indent=4))
    
    if action == 'bus':
        res = bus(req)
    else:
        log.error('Unexpected action %s' % action)
    
    print('Action: %s' % action)
    print('Respone: %s' % res)

    return make_response(jsonify({'fulfillmentText': res}))

def bus(req):
    parameters = req['queryResult']['parameters']
    print("Dialogflow Parameters:")
    print(json.dumps(parameters, indent=4))

    return api._call_func("stops-for-location", {lat: 47.653435,lon: -122.305641})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=61294, ssl_context='adhoc')
