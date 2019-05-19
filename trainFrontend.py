#import packages
import pandas as pd
import numpy as np
import sys
import json
import argparse
import datetime as dt
import requests
from datetime import timedelta, date
#importing required libraries
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, model_from_json, load_model
from keras.layers import Dense, Dropout, LSTM 

#for normalizing data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

#lines = sys.stdin.readlines()
#ticker = json.loads(lines[0])

# ====================== Loading Data from Alpha Vantage ==================================
lines = sys.stdin.readlines()
ticker = json.loads(lines[0])

api_key = "LBG3YII29JOX2SSU"

#ticker = "AAPL"

# JSON file with all the stock market data for AAL from the last 20 years
url_string = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=%s&outputsize=full&apikey=%s"%(ticker,api_key)

# Save data to this file
file_to_save = 'stock_market_data-%s.csv'%ticker

# If you haven't already saved data,
# Go ahead and grab the data from the url
# And store date, low, high, volume, close, open values to a Pandas DataFrame


response = requests.get(url_string)
data = json.loads(response.text)
# extract stock market data
data = data['Time Series (Daily)']
df = pd.DataFrame(columns=['Date','Low','High','Close','Open'])
for k,v in data.items():
    date = dt.datetime.strptime(k, '%Y-%m-%d')
    data_row = [date.date(),float(v['3. low']),float(v['2. high']),
                float(v['4. close']),float(v['1. open'])]
    df.loc[-1,:] = data_row
    df.index = df.index + 1
   
	

# If the data is already there, just load it from the CSV


#print the head
df.head()

#setting index as date
df['Date'] = pd.to_datetime(df.Date,format='%Y-%m-%d')
df.index = df['Date']

#plot
#plt.figure(figsize=(16,8))
#plt.plot(df['Close'], label='Close Price history')

#
#LSTM Model Start
#
#creating dataframe
data = df.sort_index(ascending=True, axis=0)
new_data = pd.DataFrame(index=range(0,len(df)),columns=['Date', 'Close'])
for i in range(0,len(data)):
	new_data['Date'][i] = data['Date'][i]
	new_data['Close'][i] = data['Close'][i]

#setting index
new_data.index = new_data.Date
new_data.drop('Date', axis=1, inplace=True)

#creating train and test sets
dataset = new_data.values

train = dataset[len(dataset)-3000:,:]
valid = dataset[987:,:]

#converting dataset into x_train and y_train
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(dataset)

x_train, y_train = [], []
for i in range(60,len(train)):
	x_train.append(scaled_data[i-60:i,0])
	y_train.append(scaled_data[i,0])
x_train, y_train = np.array(x_train), np.array(y_train)

x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

file_name = 'model_%s.h5'%ticker

# create and fit the LSTM network
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1],1)))
model.add(LSTM(units=50))
model.add(Dense(1))

model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=0)

model.save(file_name)

file_log_name = 'log_%s.txt'%ticker
today = str(date.today().strftime("%Y-%m-%d"))
if not os.path.exists(file_log_name):
	with open(file_log_name, 'w') as modified: modified.write(today + ":" + str(len(dataset)) + "\n")
else:
	with open(file_log_name, 'r') as original: data = original.read()
	with open(file_log_name, 'w') as modified: modified.write(today + ":" + str(len(dataset)) + "\n" + data)

print(json.dumps("Training completed successfully."))

