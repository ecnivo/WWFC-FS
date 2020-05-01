from flask import json, Flask, abort
import sys, os
import tweepy as t
from google.cloud import secretmanager

app = Flask(__name__)
project_id = os.environ["GCP_PROJECT"]

TWEET_DEPTH = 50


# TWEET_DEPTH dictates how deep to search for tweets. Occasionally, @wwfcstatus will post non-flight status tweets, so
# this is the maximum number of non-flight-status-related tweets in a row


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
    print("Received a request to contact Twitter!", file=sys.stdout)

    client = secretmanager.SecretManagerServiceClient()
    apiKey = client.secret_version_path(project_id, "TWITTER_API_KEY", "latest")
    apiSecret = client.secret_version_path(project_id, "TWITTER_SECRET_KEY", "latest")
    accessToken = client.secret_version_path(project_id, "TWITTER_ACCESS_TOKEN", "latest")
    secretToken = client.secret_version_path(project_id, "TWITTER_TOKEN_SECRET", "latest")
    if apiKey and apiSecret and accessToken and secretToken:
        print("Got the keys!")

    auth = t.AppAuthHandler(accessToken, secretToken)
    # api = t.API(auth_handler=auth, parser=t.parsers.JSONParser())
    api = t.API(auth_handler=auth)
    statusesJSON = api.user_timeline(user="wwfcstatus", count=TWEET_DEPTH)
    print("DEBUG: got JSON statuses here... " + str(statusesJSON))
    # statusesList = []
    # for s in statusesJSON:
    #     statusesList.append(json.loads(s._json))
    #
    # print("Statuses retrieved: " + str(statusesList), file=sys.stdout)  # DEBUG

    return "FLY ONLY"  # TODO make this lol
