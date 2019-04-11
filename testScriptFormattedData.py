import requests
from time import sleep
import json
import argparse
from collections import OrderedDict
from time import sleep
import sys

lines = sys.stdin.readlines()
ticker = json.loads(lines[0])
url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={0}&outputsize=full&apikey=LBG3YII29JOX2SSU".format(
    ticker)
response = requests.get(url)
json_loaded = json.loads(response.text)
if('Error Message' in json_loaded.keys()):
    print(json.dumps("Error: Please input correct stock symbol."))
else:
    summaryDataList = []
    timeSeries = json_loaded["Time Series (Daily)"]
    xList = list(timeSeries.keys())
    yListValues = list(timeSeries.values())

    for i in range(len(yListValues)):
        summaryDataList.append(
            {'x': xList[i], 'Open': float(yListValues[i]['1. open']), 'Close': float(yListValues[i]['4. close']), 'High': float(yListValues[i]['2. high']), 'Low': float(yListValues[i]['3. low']), 'Volume': float(yListValues[i]['5. volume'])})
        if (xList[i] == "2017-03-20"):
            break

    #print("Grabbing data from alphavantage for %s" % (ticker))
    #print ("Writing data to output file")
    # with open('%s-data.json' % (ticker), 'w') as fp:
    #    json.dump(summaryDataList, fp, indent=4)
    print(json.dumps(summaryDataList))
