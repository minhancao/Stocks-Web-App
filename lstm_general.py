#import packages
import pandas as pd
import numpy as np
import sys
import json
import argparse
import datetime as dt
import requests
from datetime import timedelta
#importing required libraries
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, model_from_json, load_model
from keras.layers import Dense, Dropout, LSTM

#to plot within notebook
import matplotlib.pyplot as plt

#setting figure size
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 20,10

#for normalizing data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

#lines = sys.stdin.readlines()
#ticker = json.loads(lines[0])

# ====================== Loading Data from Alpha Vantage ==================================

api_key = "LBG3YII29JOX2SSU"

# American Airlines stock market prices
ticker = "AAPL"

# JSON file with all the stock market data for AAL from the last 20 years
url_string = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=%s&outputsize=full&apikey=%s"%(ticker,api_key)

# Save data to this file
file_to_save = 'stock_market_data-%s.csv'%ticker

# If you haven't already saved data,
# Go ahead and grab the data from the url
# And store date, low, high, volume, close, open values to a Pandas DataFrame
if not os.path.exists(file_to_save):
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
    print('Data saved to : %s'%file_to_save)        
    df.to_csv(file_to_save)

# If the data is already there, just load it from the CSV
else:
    print('File already exists. Loading data from CSV')
    df = pd.read_csv(file_to_save)

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

#defining length of training set
train = dataset[0:987,:]
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

file_name = 'model_%s.json'%ticker
file_name2 = 'model_%s.h5'%ticker
file_name3 = 'model_%s.hdf5'%ticker

if(os.path.isfile(file_name2) is False):
	# create and fit the LSTM network
	model = Sequential()
	model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1],1)))
	model.add(LSTM(units=50))
	model.add(Dense(1))

	model.compile(loss='mean_squared_error', optimizer='adam')
	model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=1)

	# serialize model to JSON
	#  the keras model which is trained is defined as 'model' in this example
	model.save(file_name2)
	print("Model created and saved successfully.")

else:
	model = load_model(file_name2)

	#predict 1 new value, insert into end of input set, and then delete the beginning element of input set of 60
	#predicting 246 values, using past 60 from the train data

	#grab last current 60 data pts for inputs
	dataset = np.vstack([dataset, [202.9]])
	dataset = np.vstack([dataset, [200.72]])
	inputs2 = new_data[len(new_data)-60:].values

	
	for i in range(0,60):
		#creating train and test sets

		#defining length of training set
		
		#converting dataset into x_train and y_train
		scaled_data = scaler.fit_transform(dataset)

		x_train, y_train = [], []
		x_train.append(scaled_data[len(scaled_data)-60:len(scaled_data),0])
		y_train.append(scaled_data[len(scaled_data)-1])
		
		x_train, y_train = np.array(x_train), np.array(y_train)

		x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

		
		model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=1)

		inputsNorm2 = inputs2.reshape(-1,1)
		inputsNorm2 = scaler.transform(inputs2)

		X_test2 = []
		for i in range(0,inputsNorm2.shape[0]):
		    X_test2.append(inputsNorm2[i,0])
		X_test2 = np.array(X_test2)
		X_test2 = np.reshape(X_test2, (1,60,1))

		closing_price = model.predict(X_test2)
		closing_price = scaler.inverse_transform(closing_price)
		#add new data to the input set and remove the beginning data pt in the input set
		nextDataToAdd = closing_price[0]
		dataset = np.vstack([dataset, nextDataToAdd])
		inputs2 = dataset[len(dataset)-60:]
		print(closing_price)


	print(closing_price)
	print(inputs2)

	new_data2 = pd.DataFrame(index=range(0,len(inputs2)),columns=['Date', 'Close'])
	#j = len(new_data)-3
	for i in range(0,len(inputs2)-57):
	    new_data2['Date'][i] = data['Date'][len(new_data)-1] + timedelta(days=i) 
	    new_data2['Close'][i] = inputs2[i+57,0]
	    #j=j+1

	#setting index
	new_data2.index = new_data2.Date
	new_data2.drop('Date', axis=1, inplace=True)

	plt.plot(new_data['Close'], 'b')
	plt.plot(new_data2['Close'], 'g')
	plt.show()

	#rms=np.sqrt(np.mean(np.power((valid-closing_price),2)))
	#print(rms)

	
	"""train = new_data[:987]
	valid = new_data[987:]
	part1 = closing_price[0:4383]
	print(len(valid))
	print(len(part1))
	
	print(closing_price)
	valid['Date'] = valid.index.strftime('%Y-%m-%d')
	valid['Predictions'] = part1
	valid['Predictions'] = valid['Predictions'].apply(lambda x: round(x, 2))
	#json_valid = valid.to_json(orient='records')
	#print(json_valid)
	#print(valid)
	plt.plot(train['Close'], 'b')
	plt.plot(valid['Close'], 'g')
	plt.plot(valid['Predictions'], 'r')
	plt.show()"""
	