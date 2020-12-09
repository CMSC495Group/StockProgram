import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras import models, layers
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM

class LSTMPredictor():

    def __init__(self):
        self.stockData = None
        self.trainData = None
        self.xTrain = None
        self.yTrain = None
        self.network = None
        self.initialTrain = False
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def setStockData(self, data):
        self.stockData = data

        # delete all of the columns that we do not need
        del(self.stockData['Date'])
        del(self.stockData['Open'])
        del(self.stockData['High'])
        del(self.stockData['Low'])
        del(self.stockData['Volume'])

    def setTrainData(self):
        
        # train on 100% of the data
        self.trainStockData = self.stockData[0:len(self.stockData)]

        self.trainStockData = np.array(self.trainStockData)

        self.xTrain = []
        self.yTrain = []

        for count in range(0, len(self.trainStockData)-1):
            self.xTrain.append(self.trainStockData[count])
            self.yTrain.append(self.trainStockData[count+1])

        self.xTrain = np.array(self.xTrain)
        self.xTrain = self.scaler.fit_transform(self.xTrain)
        self.xTrain = self.xTrain.reshape(-1, 1, 1)

        self.yTrain = np.array(self.yTrain)
        self.yTrain = self.scaler.fit_transform(self.yTrain)
        self.yTrain = self.yTrain.reshape(-1, 1, 1)

        # ensure that xTrain and yTrain are the same length
        if(self.xTrain.shape[0] != self.yTrain.shape[0]):
            self.xTrain = np.delete(self.xTrain, len(self.xTrain)-1, 0)

    """ appends a new price to the training data """
    def appendToTrain(self, data):
        self.stockData = self.stockData.append(pd.DataFrame([data], columns=['Close']), ignore_index=True)

    def buildNetwork(self):
        
        self.network = Sequential()
        self.network.add(Dense(10000, activation='relu',
                               input_shape=(self.xTrain.shape[1], self.xTrain.shape[2])))
        self.network.add(LSTM(1000, activation='relu', return_sequences=True))
        self.network.add(Dropout(.9))
        self.network.add(Dense(1))

        self.network.compile(optimizer='adam', loss='mse', metrics=['acc'])

    def trainNetwork(self):
        if not(self.initialTrain):
            epochNum = 5
            self.initialTrain = True
        else:
            epochNum = 1
            
        self.network.fit(self.xTrain, self.yTrain, epochs=epochNum, verbose=0)


    """ d parameter is the last close price that is used to predict
        the next close price """
    def predict(self, d):

        predictData = np.array(float(d))
        predictData = predictData.reshape(-1, 1)
        predictData = self.scaler.fit_transform(predictData)
        predictData = predictData.reshape(-1, 1, 1)

        prediction = self.network.predict(predictData)
        prediction = prediction.reshape(-1, 1)
        prediction = self.scaler.inverse_transform(prediction)

        return prediction[0][0]


    

        
        
            
