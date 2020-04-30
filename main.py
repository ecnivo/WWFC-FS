from flask import json


def fulfillment(request):
    """Handles fulfillment of actions from DialogFlow using Flask
    args: the HTTP(s) Flask request object (class flask.Request)
    returns: Response HTTP; intended to be a JSON object -- see DialogFlow fulfillment for details"""

    print("fulfillment function activated!")  # DEBUG
    contentType = request.headers['content-type']
    requestType = request.method
    jsonRequest = request.get_json(silent=True)

    # checks if the request is valid
    print(" request type " + str(requestType))  # DEBUG
    print("JSON request is: " + jsonRequest)  # DEBUG
    if not (requestType == "POST" and jsonRequest):
        print("Aborted! not valid JSON")
        return abort(405)

    # TODO implement more checks??

    action = jsonRequest["queryResult"]["action"]
    print("Action parsed " + str(action))  # DEBUG

    re = {"fulfillment_messages": null}
    if action == "welcome":
        # first interaction
        re["fulfillment_messages"] = {"text": {"text": "TESTING: DO YOU HEAR THIS??"}}  # TESTING
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
        return abort(400)

    responseMsg = json.jsonify(re, indent=1)
    print("Response message formed " + str(responseMsg))
    return responseMsg
