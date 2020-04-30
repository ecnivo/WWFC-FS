import json
import requests

jsonDict = {"queryResult": {"action": "welcome"}}

googleURL = "https://us-central1-wwfc-fs.cloudfunctions.net/dialogflowFirebaseFulfillment"
myIP = "http://localhost:5000"

curlCommand = """curl -X POST https://us-central1-wwfc-fs.cloudfunctions.net/dialogflowFirebaseFulfillment -H "content-type:application/json" -d  '{"queryResult":{"action":"welcome"}}'"""

headers = {"content-type": "application/json"}

jsonData = json.dumps(jsonDict)
response = requests.post(myIP, json=jsonDict, headers=headers)
print(response.text)