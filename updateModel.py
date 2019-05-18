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

#to plot within notebook
import matplotlib.pyplot as plt

#setting figure size
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 20,10

#for normalizing data
from sklearn.preprocessing import MinMaxScaler

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
file_log_name = 'log_%s.txt'%ticker
file_model_name = 'model_%s.h5'%ticker

f = open(file_log_name)
strStrip = f.readline().rstrip("\n")
latestDate = strStrip.split(':')[0]
oldDataLen = int(strStrip.split(':')[1])

today = str(date.today())
if(latestDate == today):
	print("Model is already up-to-date!")

else:
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
	df.to_csv('stock_market_data2-AAPL.csv')

	#print the head
	df.head()
	
	df['Date'] = pd.to_datetime(df.Date,format='%Y-%m-%d')
	df.index = df['Date']

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

	b = dt.datetime.strptime(today, '%Y-%m-%d')
	a = dt.datetime.strptime(latestDate, '%Y-%m-%d')
	daysDiff = (b - a).days

	train = dataset[oldDataLen-60:,:]

	#converting dataset into x_train and y_train
	scaler = MinMaxScaler(feature_range=(0, 1))
	scaled_data = scaler.fit_transform(train)

	x_train, y_train = [], []
	'''for i in range(60,len(train)):
		x_train.append(scaled_data[i-60:i,0])
		y_train.append(scaled_data[i,0])
		print("Run ", i)
		print(train[i-60:i,0])
		print(train[i,0])
	x_train, y_train = np.array(x_train), np.array(y_train)

	x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))
	print(x_train.shape)'''

	model = load_model(file_model_name)

	for i in range(0,len(dataset) - oldDataLen):
		x_train, y_train = [], []
		x_train.append(scaled_data[i:i+60,0])
		y_train.append(scaled_data[i+60,0])
		print("Run ", i)
		print(train[i:i+60,0])
		print(train[i+60,0])
		x_train, y_train = np.array(x_train), np.array(y_train)
		x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))
		print(x_train.shape)
		model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=1)

	# serialize model to JSON
	#  the keras model which is trained is defined as 'model' in this example
	model.save('model_AAPL2.h5')
	print("Model trained and updated successfully!")

	with open(file_log_name, 'r') as original: data = original.read()
	with open(file_log_name, 'w') as modified: modified.write(today + ":" + str(len(dataset)) + "\n" + data)