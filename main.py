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

    response = {}
    responseWords = "Yikes, something went wrong. Contact the developer for help?"  # This is the default response text
    if action == "welcome":
        # first interaction. Quickly get the status
        responseWords = "Hi, the current status is: " + str(getStatus())
        # TODO add something dealing with setting the dialogflow context to the flight status
    elif action == "extrainfo":
        responseWords = "The current status, " + str(
            getStatus()) + ", means that you cannot go outside"  # TODO obviously, make this work
    elif action == "wxfull":
        # get full weather brief
        # yike @ needing to decode a METAR
        responseWords = "The local weather at CYKF is "  # TODO get weather information from METAR, make this work?
    elif action == "wxsummary":
        # just the "likely" limiting weather
        responseWords = "The status is likely " + str(
            getStatus()) + " because of"  # TODO some way to get navcanada weather
    elif action == "updatetime":
        # time twitter updated
        responseWords = "The twitter was last updated at "  # TODO do a "pretty time" (ie.
    else:
        # yike, throw an error (server fault)
        abort(400)
        return

    response["fulfillmentMessages"] = [{"text": {"text": [responseWords]}}]
    response["payload"] = {"google": {"expectUserResponse": True, "richResponse": {
        "items": [{"simpleResponse": {"textToSpeech": responseWords, "displayText": responseWords}}]}}}
    responseData = json.jsonify(response)
    print("Response formed: " + str(responseData))  # DEBUG
    return responseData


def getStatus():
    """This uses the Twitter API to get the latest flight status update.
    Returns a string for the current flight status"""
    return "FLY ONLY" #TODO make this lol
