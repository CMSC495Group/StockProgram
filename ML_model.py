import numpy as np  # linear algebra
import random
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
from pandas import datetime
import math, time
import itertools
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
import datetime
from operator import itemgetter
from sklearn.metrics import mean_squared_error
from math import sqrt
import torch
import torch.nn as nn
from torch.autograd import Variable

import os

for dirname, _, filenames in os.walk('/kaggle/input'):
    for i, filename in enumerate(filenames):
        if i < 5:
            print(os.path.join(dirname, filename))


def stocks_data(symbols, dates):
    df = pd.DataFrame(index=dates)
    for symbol in symbols:
        df_temp = pd.read_csv("../input/Data/Stocks/{}.us.txt".format(symbol), index_col='Date',
                              parse_dates=True, usecols=['Date', 'Close'], na_values=['nan'])
        df_temp = df_temp.rename(columns={'Close': symbol})
        df = df.join(df_temp)
    return df


dates = pd.date_range('2019-01-02', '2020-11-17', freq='B')
symbols = ['ACN', 'ADI', 'ADSK', 'AKAM', 'AMAT', 'AMD', 'ANET',
           'ANSS', 'APH', 'ASML', 'AVGO', 'AVLR', 'BKI', 'BR',
           'CAJ', 'CCC', 'CDAY', 'CDNS', 'CDW', 'CGNX', 'CHKP',
           'COUP', 'CRWD', 'CSCO', 'CTSH', 'CTXS', 'DDOG', 'DELL',
           'DNB', 'DOCU', 'DT', 'ENPH', 'EPAM', 'ERIC', 'FICO',
           'FIS', 'FISV', 'FLT', 'FTNT', 'FIV', 'GDDY', 'GDS',
           'GIB', 'GLW', 'GRMN', 'HPE', 'HPQ', 'HUBS', 'IBM',
           'INFY', 'INTC', 'INTU', 'IPGP', 'IT', 'JKHY', 'KEYS',
           'KLAC', 'LDOS', 'LOGI', 'LRCX', 'MCHP', 'MDB', 'MPWR',
           'MRVL', 'MSI', 'MU', 'MXIM', 'NET', 'NICE', 'NLOK',
           'NOK', 'NOW', 'NTAP', 'NXPI', 'OKTA', 'ON', 'ORCL',
           'OTEX', 'PAGS', 'PANW', 'PAYC', 'PCTY', 'PLTR', 'PTC',
           'QCOM', 'QRVO', 'RNG', 'SAP', 'SEDG', 'SHOP', 'SNE',
           'SNOW', 'SNPS', 'SPLK', 'SQ', 'SSNC', 'STM', 'STNE',
           'STX', 'SWKS', 'TDY', 'TEAM', 'TEL', 'TER', 'TRMB',
           'TTD', 'TXN', 'TYL', 'U', 'UBER', 'UI', 'UMC', 'VMW',
           'VRSN', 'WDAY', 'WDC', 'WIT', 'WIX', 'WORK', 'XLNX',
           'ZBRA', 'ZEN', 'ZI', 'ZS']
df = stocks_data(symbols, dates)
df.fillna(method='pad')
# print(df)
df.interpolate().plot()
plt.show()
df.head()

dates = pd.date_range('2019-01-02', '2020-11-17', freq='B')
df1 = pd.DataFrame(index=dates)
df_ACN = pd.read_csv("../input/Data/Stocks/ibm.us.txt", parse_dates=True, index_col=0)
df_ACN = df1.join(df_ACN)
df_ACN[['Close']].plot()
plt.ylabel("stock_price")
plt.title("ACN Stock")
plt.show()

df_ACN = df_ACN[['Close']]
df_ACN.info()

df_ACN = df_ACN.fillna(method='ffill')

scaler = MinMaxScaler(feature_range=(-1, 1))
df_ACN['Close'] = scaler.fit_transform(df_ACN['Close'].values.reshape(-1, 1))

# df_ CAN

# function to create train, test data given stock data and sequence length
def load_data(stock, look_back):
    data_raw = stock.as_matrix()  # convert to numpy array
    data = []

    # create all possible sequences of length seq_len
    for index in range(len(data_raw) - look_back):
        data.append(data_raw[index: index + look_back])

    data = np.array(data)
    test_set_size = int(np.round(0.2 * data.shape[0]))
    train_set_size = data.shape[0] - (test_set_size)

    x_train = data[:train_set_size, :-1, :]
    y_train = data[:train_set_size, -1, :]

    x_test = data[train_set_size:, :-1]
    y_test = data[train_set_size:, -1, :]

    return [x_train, y_train, x_test, y_test]


look_back = 20  # choose sequence length
x_train, y_train, x_test, y_test = load_data(df_ibm, look_back)
print('x_train.shape = ', x_train.shape)
print('y_train.shape = ', y_train.shape)
print('x_test.shape = ', x_test.shape)
print('y_test.shape = ', y_test.shape)

# make training and test sets in torch
x_train = torch.from_numpy(x_train).type(torch.Tensor)
x_test = torch.from_numpy(x_test).type(torch.Tensor)
y_train = torch.from_numpy(y_train).type(torch.Tensor)
y_test = torch.from_numpy(y_test).type(torch.Tensor)

# train_X = train_X.view([-1, x_train.shape[0], 1])
# test_X = test_X.view([-1, x_test.shape[0], 1])
# train_Y = train_Y.view([y_train.shape[0], 1])

y_train.size(), x_train.size()

n_steps = look_back - 1
batch_size = 1606
# n_iters = 3000
num_epochs = 100  # n_iters / (len(train_X) / batch_size)
# num_epochs = int(num_epochs)

train = torch.utils.data.TensorDataset(x_train, y_train)
test = torch.utils.data.TensorDataset(x_test, y_test)

train_loader = torch.utils.data.DataLoader(dataset=train,
                                           batch_size=batch_size,
                                           shuffle=False)

test_loader = torch.utils.data.DataLoader(dataset=test,
                                          batch_size=batch_size,
                                          shuffle=False)

#Model


class LSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim):
        super(LSTM, self).__init__()
        # Hidden dimensions
        self.hidden_dim = hidden_dim

        # Number of hidden layers
        self.num_layers = num_layers

        # Building your LSTM
        # batch_first=True causes input/output tensors to be of shape
        # (batch_dim, seq_dim, feature_dim)
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)

        # Readout layer
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        # Initialize hidden state with zeros
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).requires_grad_()

        # Initialize cell state
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).requires_grad_()

        # One time step
        # We need to detach as we are doing truncated backpropagation through time (BPTT)
        # If we don't, we'll backprop all the way to the start even after going through another batch
        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))

        # Index hidden state of last time step
        # out.size() --> 100, 28, 100
        # out[:, -1, :] --> 100, 100 --> just want last time step hidden states!
        out = self.fc(out[:, -1, :])
        # out.size() --> 100, 10
        return out


model = LSTM(input_dim=input_dim, hidden_dim=hidden_dim, output_dim=output_dim, num_layers=num_layers)

loss_fn = torch.nn.MSELoss(size_average=True)

optimiser = torch.optim.Adam(model.parameters(), lr=0.01)
print(model)
print(len(list(model.parameters())))
for i in range(len(list(model.parameters()))):
    print(list(model.parameters())[i].size())

# Train model
#####################

hist = np.zeros(num_epochs)

# Number of steps to unroll
seq_dim = look_back - 1

for t in range(num_epochs):
    # Initialise hidden state
    # Don't do this if you want your LSTM to be stateful
    # model.hidden = model.init_hidden()

    # Forward pass
    y_train_pred = model(x_train)

    loss = loss_fn(y_train_pred, y_train)
    if t % 10 == 0 and t != 0:
        print("Epoch ", t, "MSE: ", loss.item())
    hist[t] = loss.item()

    # Zero out gradient, else they will accumulate between epochs
    optimiser.zero_grad()

    # Backward pass
    loss.backward()

    # Update parameters
    optimiser.step()

plt.plot(y_train_pred.detach().numpy(), label="Preds")
plt.plot(y_train.detach().numpy(), label="Data")
plt.legend()
plt.show()

plt.plot(hist, label="Training loss")
plt.legend()
plt.show()

# make predictions
y_test_pred = model(x_test)

# invert predictions
y_train_pred = scaler.inverse_transform(y_train_pred.detach().numpy())
y_train = scaler.inverse_transform(y_train.detach().numpy())
y_test_pred = scaler.inverse_transform(y_test_pred.detach().numpy())
y_test = scaler.inverse_transform(y_test.detach().numpy())

# calculate root mean squared error
trainScore = math.sqrt(mean_squared_error(y_train[:, 0], y_train_pred[:, 0]))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = math.sqrt(mean_squared_error(y_test[:, 0], y_test_pred[:, 0]))
print('Test Score: %.2f RMSE' % (testScore))

# shift train predictions for plotting
trainPredictPlot = np.empty_like(df_ibm)
trainPredictPlot[:, :] = np.nan
trainPredictPlot[look_back:len(y_train_pred) + look_back, :] = y_train_pred

# shift test predictions for plotting
testPredictPlot = np.empty_like(df_ibm)
testPredictPlot[:, :] = np.nan
testPredictPlot[len(y_train_pred) + look_back - 1:len(df_ibm) - 1, :] = y_test_pred

# plot baseline and predictions
plt.figure(figsize=(15, 8))
plt.plot(scaler.inverse_transform(df_ibm))
plt.plot(trainPredictPlot)
plt.plot(testPredictPlot)
plt.show()
