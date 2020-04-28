import https, json, cgi

class MyHandler(https.server.BaseHTTPRequestHandler):
    def _set_headers(self, response_code):
        self.send_response(response_code) #send "OK"
        self.send_header('content-type','application/json') #sends JSON header
        self.end_headers() #send

    def do_HEAD(self):
        self._set_headers(200) #HEAD request only needs header

    def do_GET(self):
        self._set_headers(405) #why would you send a GET? Sends 405 code for incorrect method

    def do_POST():
        #parse incoming Webhook Request
        contentType, pdict = cgi.parse_header(self.headers.getheader("content-type"))

        #not in JSON format, for some reason?
        if (contentType != "application/json"):
            self.send_response(400) #incorrect
            self.end_headers()
            return

        len = int(self.headers.getheader("content-length"))
        msg = json.loads(self.rfile.read(len)) #msg is type 'dict'

        #TODO: build in protection for bad JSON message / formatting? Throw an error?
        qR = msg["queryResult"]
        intent = msg ["action"]

        if (intent == "GetStatusWelcome"):
            #first interaction
        elif (intent == "ExtraInfo"):
            #get when the status was updated, get relevant limiting weather
        elif (intent == "FullWeather"):
            #get full weather brief
            #yike @ needing to decode
        elif (intent == "SummaryWx"):
            #just the "likely" limiting weather
        elif (intent == "UpdateTime"):
            #time twitter updated
        else:
            #yike, throw an error

        #wrap it up, write return header, encode and write return JSON message
        self._set_headers(200)
        self.wfile.write(json.dumps(message))

class TweetRetrieval():
    def __init__():


    #uhhh do things??
