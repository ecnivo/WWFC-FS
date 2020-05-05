from flask import json, Flask, abort
import sys, os
import tweepy as t
from google.cloud import secretmanager
from datetime import datetime, timedelta
from random import random
import requests
from pytz import timezone

app = Flask(__name__)
project_id = os.environ["GCP_PROJECT"]

TWEET_DEPTH = 10  # TWEET_DEPTH dictates how deep to search for tweets. Occasionally, @wwfcstatus will post
# non-flight status tweets, sothis is the maximum number of non-flight-status-related tweets in a row

client = secretmanager.SecretManagerServiceClient()

toronto = timezone("America/Toronto")

@app.route('/')
def fulfillment(request: Flask.request_class):
    """Handles fulfillment of actions from DialogFlow using Flask
    args: the HTTP(s) Flask request object (class flask.Request)
    returns: Response HTTP; intended to be a JSON object -- see DialogFlow fulfillment for details"""

    requestType = request.method
    jsonRequest = request.get_json(silent=True)

    # checks if the request is valid
    if not (requestType == "POST" and jsonRequest):
        print("Aborted! not valid JSON")
        abort(405)
        return

    # TODO implement more checks??

    action = jsonRequest["queryResult"]["action"]
    print("Action parsed is: " + str(action), file=sys.stdout)  # DEBUG

    response = {}
    speechResponse = "Yikes, something went wrong. Contact the developer for help?"  # This is the default response text
    if action == "welcome":
        # first interaction. Quickly get the status (Done)
        flightStatus = getFlightStatus()
        updateTime = flightStatus['time']
        if updateTime.date() == toronto.localize(datetime.today()).date():  # was updated today
            speechResponse = "Hi, the status is currently " + flightStatus['status']
            displayResponse = flightStatus['status']
        else:  # status not current as of today
            speechResponse = "Hi, the status hasn't yet been updated today. It was last " + flightStatus[
                'status'] + " as of " + formatDatesAndTimesTheWayIWantThem(updateTime)
            displayResponse = flightStatus['status'] + " as of " + formatDatesAndTimesTheWayIWantThem(updateTime)

    elif action == "extrainfo":
        # description of the flight status (Done)
        flightStatus = getFlightStatus()['status']
        speechResponse = "The current status, " + flightStatus + ", means "
        displayResponse = flightStatus + " means: "
        if flightStatus == "No Fly":
            speechResponse += "nobody is allowed to go flying."
            displayResponse += "nobody is allowed to go flying."
        elif flightStatus == "Dual Only":
            speechResponse += "you may only fly with an instructor"
            displayResponse += "you may only fly with an instructor"
        elif flightStatus == "Circuits Only for Students":
            speechResponse += "during the day, if you are not licensed, you can only be signed out to the circuit. " \
                              "If it is nighttime and you are not night rated, you can only be signed out for night" \
                              " circuits."
            displayResponse += "Day: Not licensed - solo circuits only. Night: no night rating - night circuits only." \
                               " Any time: Licensed - no restrictions"
        elif flightStatus == "No Student Solo":
            speechResponse += "you may not go flying unless you are licensed."
            displayResponse += "licensed pilots only. Students must be with an instructor."
        elif flightStatus == "No Student Solo Cross-Country":
            speechResponse += "you may only go to the circuit or practice area if you are not licensed."
            displayResponse += "No license - circuit or practice area"
        elif flightStatus == "No Restrictions":
            speechResponse += "everybody may go flying so long as they are current."
            displayResponse += "everybody may go flying!"

        displayResponse += " For more information, call dispatch at 519-648-2213"

    elif action == "wxfull":
        # get full weather brief (Done)
        weather = getWeather()
        weatherUpdateTime = toronto.localize(datetime.strptime(weather['time']['dt'][0:18],"%Y-%m-%dT%H:%M:%S"))
        speechResponse = "The local weather at CYKF as of " + formatDatesAndTimesTheWayIWantThem(weatherUpdateTime) \
                         + " has winds at " + weather['wind_direction']['spoken'] + " at " + str(weather['wind_speed'][
                             'value']) + ", visibility " + str(weather['visibility']['value']) + ", clouds " + \
                         weather['translate']['clouds'].replace(" - Reported AGL", "") + ", temperature " + weather[
                             'temperature']['spoken'] + " and altimeter <say-as interpret-as=\"characters\">" + \
                         weather['altimeter']['repr'].replace("A", "") + "</say-as>"
        if random() < 0.2:
            speechResponse += ". <break time=\"400ms\" strength\"x-strong\"/> For more information, give London FIC a" \
                              "call at 1-866-WX-BRIEF"
        displayResponse = weather['sanitized']

    elif action == "wxsummary": #TODO this section needs to be re-done to deal with ... everything.
        # just the "likely" limiting weather
        status = getFlightStatus()
        weather = getWeather()

        if status['time'].date() == toronto.localize(datetime.today()).date():
            speechResponse = "The status is likely " + status['status'] + " because of " + weather[
                'speech']
        else:
            speechResponse = "The limiting "

        if random() < 0.4:  # sometimes
            speechResponse += " For more up-to-date info, call dispatch at 519-648-2213."

        displayResponse = weather['text']

    elif action == "updatetime":
        # time twitter updated
        status = getFlightStatus()
        updateTime = status['time']  # datetime.datetime object
        speechResponse = "The flight status was updated " + formatDatesAndTimesTheWayIWantThem(updateTime)
        displayResponse = status['status'] + " as of " + formatDatesAndTimesTheWayIWantThem(updateTime)

    else:
        # yike, throw an error (server fault)
        abort(400)
        return

    response["fulfillmentMessages"] = [{"text":
                                            {"text":
                                                 [speechResponse]
                                             }
                                        }]
    response["payload"] = {"google":
                               {"expectUserResponse": True,
                                "richResponse":
                                    {"items":
                                        [{"simpleResponse":
                                            {
                                                "textToSpeech": "<prosody rate=\"fast\" pitch=\"+1st\">" + \
                                                                speechResponse + "</prosody>",
                                                "displayText": displayResponse}
                                        }
                                        ]
                                    }
                                }
                           }
    responseData = json.jsonify(response)
    # print("Response formed: " + response)  # DEBUG
    return responseData


def getFlightStatus():
    """This uses the Twitter API to get the latest flight status update.

    :returns: a dictionary with 'status' for a string for the flight status,'time' for the time the tweet was
    created, 'text' for original tweet text"""

    # print("Received a request to contact Twitter!", file=sys.stdout)  # DEBUG

    # Gets the API Access keys from Google Secrets
    APIkeyLoc = client.secret_version_path(project_id, "TWITTER_API_KEY", "latest")
    APIsecretLoc = client.secret_version_path(project_id, "TWITTER_SECRET_KEY", "latest")
    apiKeyEncoded = client.access_secret_version(APIkeyLoc)
    apiSecretEncoded = client.access_secret_version(APIsecretLoc)
    apiKey = apiKeyEncoded.payload.data.decode("UTF-8")
    apiSecret = apiSecretEncoded.payload.data.decode("UTF-8")

    auth = t.AppAuthHandler(apiKey, apiSecret)
    api = t.API(auth)
    statusObjects = api.user_timeline("wwfcstatus", count=TWEET_DEPTH)
    tweets = []
    flightStatus = None
    for s in statusObjects:

        stripText = s.text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
        lowerText = stripText.lower()
        if "no" in lowerText and "fly" in lowerText:
            flightStatus = "No Fly"
        elif "dual" in lowerText:
            flightStatus = "Dual Only"
        elif "circuits" in lowerText:
            flightStatus = "Circuits Only for Students"
        elif ("solo" in lowerText) and not ("xc" in lowerText) and not ("cross" in lowerText):
            flightStatus = "No Student Solo"
        elif "xc" in lowerText or "cross" in lowerText:
            flightStatus = "No Student Solo Cross-Country"
        elif "no" in lowerText and "rest" in lowerText:
            flightStatus = "No Restrictions"
        else:
            # print("Skipped a non-status tweet: " + stripText) #DEBUG
            continue

        if flightStatus:
            return {'text': stripText, 'time': toronto.localize(s.created_at), 'status': flightStatus}

    if not flightStatus:
        return {'status': "ERROR"}  # TODO handle errors gracefully


def getWeather():
    """Returns limiting weather as a dictionary (from JSON) for CYKF. Uses AVWX here:
    https://github.com/avwx-rest/avwx-api"""
    avwxKey = client.access_secret_version(
        client.secret_version_path(project_id, "AVWX_TOKEN", 'latest')).payload.data.decode(
        "UTF-8")  # Gets the API key for auth

    requestStr = "https://avwx.rest/api/metar/CYKF?options=translate,summary," \
                 "speech&airport=true&reporting=true&format=json&onfail=cache"
    weather = requests.get(requestStr, headers={"Authorization": avwxKey}).json()

    print(str(weather)) #DEBUG
    return weather


def formatDatesAndTimesTheWayIWantThem(t: datetime):
    """Formats the date and time in a easy-to-hear manner to the way I want! Because str-format-time
     is a pain in the derrière!
     PLEASE PLEASE PLEASE make sure times are in Eastern before formatting!
    :returns: a string."""
    date = t.date()
    now = toronto.localize(datetime.now())
    today = toronto.localize(datetime.today()).date()
    if date == today:  # special formatting for today
        hoursAgo = round((now - t).total_seconds() / 3600, ndigits=1)
        if hoursAgo < 1:
            return str(int(round((now - t).total_seconds() / 60))) + " minutes ago"
        elif hoursAgo < 3:
            return str(hoursAgo) + " hours ago"
        else:
            return " at " + t.strftime("%H") + ":" + t.strftime("%M%p")
    elif date == (today - timedelta(days=1)):
        return " yesterday at " + t.strftime("%H") + " " + t.strftime("%p")
    else:
        return t.strftime("%b") + " " + t.strftime("%d")
