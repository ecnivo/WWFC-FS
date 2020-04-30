from flask import json, Flask, abort
import sys

app = Flask(__name__)


@app.route('/')
def fulfillment(request):
    """Handles fulfillment of actions from DialogFlow using Flask
    args: the HTTP(s) Flask request object (class flask.Request)
    returns: Response HTTP; intended to be a JSON object -- see DialogFlow fulfillment for details"""

    print("fulfillment function activated!", file=sys.stdout)  # DEBUG
    requestType = request.method
    jsonRequest = request.get_json(silent=True)

    # checks if the request is valid
    print("Request type is:" + str(requestType))  # DEBUG
    print("JSON request is: " + str(jsonRequest))  # DEBUG
    if not (requestType == "POST" and jsonRequest):
        print("Aborted! not valid JSON")
        abort(405)
        return

    # TODO implement more checks??

    action = jsonRequest["queryResult"]["action"]
    print("Action parsed is: " + str(action))  # DEBUG

    response = {"fulfillment_messages": None}
    if (action == "welcome"):
        # first interaction
        response["fulfillment_messages"] = {"text": {"text": "TESTING: DO YOU HEAR THIS??"}}  # DEBUG
    elif (action == "extrainfo"):
        # get when the status was updated, get relevant limiting weather
        return  # TODO REMOVE THIS
    elif (action == "wxfull"):
        # get full weather brief
        # yike @ needing to decode
        return  # TODO REMOVE THIS
    elif (action == "wxsummary"):
        # just the "likely" limiting weather
        return  # TODO REMOVE THIS
    elif (action == "updatetime"):
        # time twitter updated
        return  # TODO REMOVE THIS
    else:
        # yike, throw an error (server fault)
        abort(400)
        return

    responseData = json.jsonify(response)
    print("Response message formed: " + str(responseData))  # DEBUG
    return responseData
