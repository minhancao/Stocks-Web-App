#import packages
import pandas as pd
import numpy as np
import sys
import json
import argparse
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

#read the file
df = pd.read_csv('NSE-TATAGLOBAL11.csv')

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

if(os.path.isfile("model_nse.json") is False):
	# create and fit the LSTM network
	model = Sequential()
	model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1],1)))
	model.add(LSTM(units=50))
	model.add(Dense(1))

	model.compile(loss='mean_squared_error', optimizer='adam')
	model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=2)

	# serialize model to JSON
	#  the keras model which is trained is defined as 'model' in this example
	model_json = model.to_json()

	with open("model_nse.json", "w") as json_file:
	    json_file.write(model_json)

	# serialize weights to HDF5
	model.save_weights("model_nse.h5")
	#print("Model created and saved successfully.")

else:
	# load json and create model
	json_file = open('model_nse.json', 'r')

	loaded_model_json = json_file.read()
	json_file.close()
	model = model_from_json(loaded_model_json)

	# load weights into new model
	model.load_weights("model_nse.h5")
	#print("Loaded model from disk")

	model.save('model_nse.hdf5')
	model=load_model('model_nse.hdf5')

	#predicting 246 values, using past 60 from the train data
	#print(len(new_data))
	#print(len(valid))
	inputs = new_data[len(new_data) - len(valid) - 60:].values
	inputs = inputs.reshape(-1,1)
	inputs  = scaler.transform(inputs)
	X_test = []
	for i in range(60,inputs.shape[0]):
	    X_test.append(inputs[i-60:i,0])
	X_test = np.array(X_test)

	X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))
	closing_price = model.predict(X_test)
	closing_price = scaler.inverse_transform(closing_price)

	rms=np.sqrt(np.mean(np.power((valid-closing_price),2)))
	#print(rms)

	#for plotting
	train = new_data[:987]
	valid = new_data[987:]
	valid['Date'] = valid.index.strftime('%Y-%m-%d')
	valid['Predictions'] = closing_price
	valid['Predictions'] = valid['Predictions'].apply(lambda x: round(x, 2))
	json_valid = valid.to_json(orient='records')
	print(json_valid)
	#print(valid)