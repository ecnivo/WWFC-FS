from datetime import datetime as d

MASTERtimeString = '2020-05-04T15:00:00+00:00Z'

timeString = "2020-05-04T150000+0000"
format = "%Y-%m-%dT%H%M%S%z"
timeString = MASTERtimeString.replace(":","").replace("Z","")

print(str(d.strptime(timeString, format)))
