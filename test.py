from datetime import datetime
from OBAAPIConnection import OBAAPIConnection

__OBA_KEY = 'TEST'

api = OBAAPIConnection(__OBA_KEY)

_INTENT_BUS = "projects/assistant-kcmetro/agent/intents/3ca947d8-88c2-492c-ab84-1a2fd3b44c25"
_INTENT_NEARBY_STOPS = "projects/assistant-kcmetro/agent/intents/dffdd136-07f8-4ba7-afd4-6ebf7a806d39"
_INTENT_NEARBY_ROUTES = "projects/assistant-kcmetro/agent/intents/3ccaba9f-29eb-4038-bf62-f67943a47f7a"
_INTENT_STOP_INFO = "projects/assistant-kcmetro/agent/intents/bb1090db-7242-4e0b-8ae1-2b39681d4acb"


def bus(location, req):
    route = req['queryResult']['parameters']['bus_route']
    if type(route) is float:
        route = int(route) # drop decimal
    route = str(route)
    direction = req['queryResult']['parameters']['direction']
    direction = "1" if (direction == 'north' or direction == 'east') else "0"
    api_res = api.nearby_stops(location)
    route_id = [x['id'] for x in api_res['data']['references']['routes'] if x['shortName'] == route]
    if len(route_id) > 0:
        route_id = route_id[0]
        stops = [x['id'] for x in api_res['data']['list'] if route_id in x['routeIds']]
        if len(stops) > 0:
            trips = api.trips_for_route(route_id, include_schedule=True)
            trip_objects = [x for x in trips['data']['references']['trips'] if x['directionId'] == direction and x['routeId'] == route_id]
            if len(trip_objects) > 0:
                trip_schedules = [x for x in trips['data']['list'] if x['tripId'] in [y['id'] for y in trip_objects]]
                for i in range(len(trip_schedules)):
                    schedule = trip_schedules[i]['schedule']['stopTimes']
                    for time in schedule:
                        stop_id = time['stopId']
                        if stop_id in stops:
                            trip_schedules[i] = (time['arrivalTime'], trip_schedules[i], datetime.fromtimestamp(float(trip_schedules[i]['serviceDate'] + time['arrivalTime'] * 1000) / 1000).strftime('%B, %d at %H:%M %p'), stop_id)
                            break
                trip_tup = sorted(trip_schedules, key=lambda t: t[0])[0]
                trip_time = trip_tup[2]
                trip_id = trip_tup[1]['tripId']
                trip_desc = [x for x in trip_objects if x['id'] == trip_id][0]['tripHeadsign']
                stop = [x['name'] for x in api_res['data']['list'] if x['id'] == trip_tup[3]]
                return {'fulfillmentText': "Route %s will arrive at %s on %s" % (route, stop, trip_time)}
    return {'fulfillmentText': 'Sorry, it doesn\'t appear that that route is in operation near you right now.'}

bus({'latitude': 47.6595, 'longitude': -122.3045}, {'responseId': '4121aa9e-fffc-49ad-960b-fd6e60585a98', 'queryResult': {'queryText': 'bus 372 north', 'parameters': {'bus_route': 372.0, 'bus_stop': '', 'direction': 'northbound'}, 'allRequiredParamsPresent': True, 'fulfillmentText': "If this was real, we'd look up northbound 372 stop times.", 'fulfillmentMessages': [{'text': {'text': ["If this was real, we'd look up northbound 372 stop times."]}}], 'outputContexts': [{'name': 'projects/assistant-kcmetro/agent/sessions/ABwppHFBUCrxhjtgh-qkdCvW4yQvJ1IMwuLJvt1lsK8vgSayCoc5jl7XZv7KdSW-j5S7elU3gCTkuWxcMi59-VU/contexts/actions_capability_screen_output', 'parameters': {'direction.original': 'north', 'bus_route': 372.0, 'bus_stop.original': '', 'bus_stop': '', 'bus_route.original': '372', 'direction': 'northbound'}}, {'name': 'projects/assistant-kcmetro/agent/sessions/ABwppHFBUCrxhjtgh-qkdCvW4yQvJ1IMwuLJvt1lsK8vgSayCoc5jl7XZv7KdSW-j5S7elU3gCTkuWxcMi59-VU/contexts/actions_capability_audio_output', 'parameters': {'direction.original': 'north', 'bus_route': 372.0, 'bus_stop.original': '', 'bus_stop': '', 'bus_route.original': '372', 'direction': 'northbound'}}, {'name': 'projects/assistant-kcmetro/agent/sessions/ABwppHFBUCrxhjtgh-qkdCvW4yQvJ1IMwuLJvt1lsK8vgSayCoc5jl7XZv7KdSW-j5S7elU3gCTkuWxcMi59-VU/contexts/google_assistant_input_type_keyboard', 'parameters': {'direction.original': 'north', 'bus_route': 372.0, 'bus_stop.original': '', 'bus_stop': '', 'bus_route.original': '372', 'direction': 'northbound'}}, {'name': 'projects/assistant-kcmetro/agent/sessions/ABwppHFBUCrxhjtgh-qkdCvW4yQvJ1IMwuLJvt1lsK8vgSayCoc5jl7XZv7KdSW-j5S7elU3gCTkuWxcMi59-VU/contexts/actions_capability_media_response_audio', 'parameters': {'direction.original': 'north', 'bus_route': 372.0, 'bus_stop.original': '', 'bus_stop': '', 'bus_route.original': '372', 'direction': 'northbound'}}, {'name': 'projects/assistant-kcmetro/agent/sessions/ABwppHFBUCrxhjtgh-qkdCvW4yQvJ1IMwuLJvt1lsK8vgSayCoc5jl7XZv7KdSW-j5S7elU3gCTkuWxcMi59-VU/contexts/actions_capability_web_browser', 'parameters': {'direction.original': 'north', 'bus_route': 372.0, 'bus_stop.original': '', 'bus_stop': '', 'bus_route.original': '372', 'direction': 'northbound'}}], 'intent': {'name': 'projects/assistant-kcmetro/agent/intents/3ca947d8-88c2-492c-ab84-1a2fd3b44c25', 'displayName': 'bus'}, 'intentDetectionConfidence': 0.99, 'languageCode': 'en-us'}, 'originalDetectIntentRequest': {'source': 'google', 'version': '2', 'payload': {'isInSandbox': True, 'surface': {'capabilities': [{'name': 'actions.capability.WEB_BROWSER'}, {'name': 'actions.capability.AUDIO_OUTPUT'}, {'name': 'actions.capability.MEDIA_RESPONSE_AUDIO'}, {'name': 'actions.capability.SCREEN_OUTPUT'}]}, 'requestType': 'SIMULATOR', 'inputs': [{'rawInputs': [{'query': 'bus 372 north', 'inputType': 'KEYBOARD'}], 'arguments': [{'rawText': 'bus 372 north', 'textValue': 'bus 372 north', 'name': 'text'}], 'intent': 'actions.intent.TEXT'}], 'user': {'lastSeen': '2018-11-29T10:13:29Z', 'permissions': ['DEVICE_PRECISE_LOCATION'], 'locale': 'en-US', 'userId': 'ABwppHHHnyJbL3QctzVaSYaOrVWsoIdUChC2QlHB0x9M10lbOzreQib1GjZjCIjJPftNVnlEKpYtvLpkpdw4X7w'}, 'device': {'location': {'coordinates': {'latitude': 47.659486099999995, 'longitude': -122.30447160000001}}}, 'conversation': {'conversationId': 'ABwppHFBUCrxhjtgh-qkdCvW4yQvJ1IMwuLJvt1lsK8vgSayCoc5jl7XZv7KdSW-j5S7elU3gCTkuWxcMi59-VU', 'type': 'ACTIVE', 'conversationToken': '[]'}, 'availableSurfaces': [{'capabilities': [{'name': 'actions.capability.WEB_BROWSER'}, {'name': 'actions.capability.AUDIO_OUTPUT'}, {'name': 'actions.capability.SCREEN_OUTPUT'}]}]}}, 'session': 'projects/assistant-kcmetro/agent/sessions/ABwppHFBUCrxhjtgh-qkdCvW4yQvJ1IMwuLJvt1lsK8vgSayCoc5jl7XZv7KdSW-j5S7elU3gCTkuWxcMi59-VU'})
