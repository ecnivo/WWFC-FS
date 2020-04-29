import cgi
import http.server
import json
import logging


class MyHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, response_code):
        self.send_response(response_code)  # send "OK"
        self.send_header('content-type', 'application/json')  # sends JSON header
        self.end_headers()  # send

    def do_HEAD(self):
        self._set_headers(200)  # HEAD request only needs header

    def do_GET(self):
        self._set_headers(405)  # why would you send a GET? Sends 405 code for incorrect method

    def do_POST():
        # parse incoming Webhook Request
        contentType, pdict = cgi.parse_header(self.headers.getheader("content-type"))

        # not in JSON format, for some reason?
        if (contentType != "application/json"):
            self.send_response(400)  # incorrect
            self.end_headers()
            return

        len = int(self.headers.getheader("content-length"))
        msg = json.loads(self.rfile.read(len))  # msg is type 'dict'

        # TODO: build in protection for bad JSON message / formatting? Throw an error?
        qR = msg["queryResult"]
        action = lower(msg["action"])

        re = {}
        if action == "welcome":
            # first interaction
            re["fulfillment_messages"] = {
                "text": ["TestResponse; this is to be filled with actual information in the future"]}  # TESTING
        elif (action == "extrainfo"):
            # get when the status was updated, get relevant limiting weather
            return
        elif (action == "wxfull"):
            # get full weather brief
            # yike @ needing to decode
            return
        elif (action == "wxsummary"):
            # just the "likely" limiting weather
            return
        elif (action == "updatetime"):
            # time twitter updated
            return
        else:
            # yike, throw an error
            return

        # wrap it up, write return header, encode and write return JSON message
        self._set_headers(200)
        self.wfile.write(json.dumps(re))


class TweetRetrieval():
    def __init__():
        return

    # uhhh do things??


def dialogflowFirebaseFulfillment(server_class=http.server.HTTPServer, handler_class=MyHandler, port=8000):
    serverAddress = ('', port)
    httpd = server_class(serverAddress, handler_class)
    logging.debug("Server started on port ", port)
    httpd.serve_forever()


if (__name__ == "__main__"):
    from sys import argv

    if len(argv) == 2:
        dialogflowFirebaseFulfillment(port=int(argv[1]))
    else:
        dialogflowFirebaseFulfillment()
