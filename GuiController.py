from PyQt5.QtCore import QThread, pyqtSignal
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from YahooStockGrab import getYahooData, getIndicesGoogle
import database_module as db
from PyQt5.QtChart import *
from PyQt5.QtGui import QColor, QPainter
from PyQt5 import QtCore
import time
import random
from LSTM import LSTMPredictor
from NewsScraper import getNews

""" Controller class that is primarily used to
    handle the different threads that run in the application """
class GuiCtrl():

    def __init__(self, gui):
        # give the class an instance of the gui so that it can
        # do things with it
        self.gui = gui

        self.updateFlashColor = "#999900"

        # establish a connection to the database
        self.dbConn = db.create_connection('stocksDB.db')

        # a variable to set true if a chart has been displayed
        # we will use this variable to delete the chart and display another
        # when the user selects a different ticker
        self.chartDisplayed = False

        self.currentNews = None

        # create instances of each thread
        self.goButtonThread = GoButtonThread(gui, self)
        self.indexThread = IndexThread(self)
        self.updateThread = UpdateThread(gui, self)
        self.lstmThread = LSTMThread(self.gui)

        # start certain threads at runtime
        self.indexThread.start()

        self.connectSignals()

    def display(self):
        self.gui.show()

    """ This function has all of the signals that need to be dealt with
        as they are called. Connects them to their respective functions """
    def connectSignals(self):
        self.gui.scanButton.clicked.connect(self.startGoButtonThread)
        self.goButtonThread.populateTableSig.connect(self.populateTable)
        self.goButtonThread.populateNewsSig.connect(self.populateNews)
        self.goButtonThread.lstmSig.connect(self.lstmThread.setStockData)
        self.goButtonThread.errorSig.connect(self.showMessageBox)
        self.updateThread.updateCloseSig.connect(self.updateTable)
        self.updateThread.updateNewsSig.connect(self.populateNews)
        self.updateThread.errorSig.connect(self.showMessageBox)
        self.lstmThread.readyToPredictSig.connect(self.startLSTMThread)
        self.lstmThread.predictionSig.connect(self.updatePredictedPrice)
        self.lstmThread.errorSig.connect(self.showMessageBox)
        self.indexThread.errorSig.connect(self.showMessageBox)

    def startGoButtonThread(self):
        self.goButtonThread.start()
        self.goButtonThread.quit()
        
        if(self.updateThread.isRunning()):
            self.stopUpdateThread()

        self.startUpdateThread()

    def startUpdateThread(self):
        self.updateThread.running = True
        self.updateThread.start()

    def stopUpdateThread(self):
        self.updateThread.running = False
        self.updateThread.ticker = None
        self.updateThread.quit()

    def startLSTMThread(self):
        self.lstmThread.start()

    """ This function is called when the user exits the application
        to ensure the each thread we have running is stopped. If not, it
        will continue to run. """
    def stopThreads(self):
        if(self.indexThread.isRunning()):
            self.indexThread.running = False
            self.indexThread.quit()
        if(self.updateThread.isRunning()):
            self.updateThread.running = False
            self.updateThread.quit()

    """ gets and returns a dataframe of stock prices for a given ticker """
    def getTickerPrices(self, ticker):

        self.gui.predictedLabel.setText("              Retrieving Data...")

        # get today's date
        todayDate = date.today()
        todayDate = todayDate + relativedelta(days=1)
        lastYearDate = todayDate - relativedelta(years=1, days=1)

        todayDate = todayDate.strftime('%d-%m-%Y')
        lastYearDate = lastYearDate.strftime('%d-%m-%Y')

        # grab a year's worth of data
        stockData = getYahooData(ticker, lastYearDate, todayDate, "1d")
        
        return stockData

    def getLastClose(self, ticker):

        todayDate = date.today()
        todayDate = todayDate + relativedelta(days=1)
        lastYearDate = todayDate - relativedelta(days=10)

        todayDate = todayDate.strftime('%d-%m-%Y')
        lastYearDate = lastYearDate.strftime('%d-%m-%Y')

        # grab a year's worth of data
        stockData = getYahooData(ticker, lastYearDate, todayDate, "1d")

        return stockData

    """ puts price data from the database into the table on the GUI """
    def populateTable(self, ticker):

        # clear what is currently in the table
        self.clearTable()

        # get the stockData from the database
        stockData = db.select_all(self.dbConn, ticker)

        # Set the date cells in the table
        rowNum = 6 # start at the second row on the table
        pandaRowNum = len(stockData)-1
        for x in range(pandaRowNum, -1, -1):
            # set date cells
            # first make visible in case we've previously made it unvisible
            self.gui.cellList[rowNum].setVisible(True)
            self.gui.cellList[rowNum].setText(" " + stockData.loc[pandaRowNum][0] + " ")

            # set open cells
            self.gui.cellList[rowNum+1].setVisible(True)
            self.gui.cellList[rowNum+1].setText("$" + str(stockData.loc[pandaRowNum][1]))

            # set high cells
            self.gui.cellList[rowNum+2].setVisible(True)
            self.gui.cellList[rowNum+2].setText("$" + str(stockData.loc[pandaRowNum][2]))

            # set low cells
            self.gui.cellList[rowNum+3].setVisible(True)
            self.gui.cellList[rowNum+3].setText("$" + str(stockData.loc[pandaRowNum][3]))

            # set close cells
            self.gui.cellList[rowNum+4].setVisible(True)
            self.gui.cellList[rowNum+4].setText("$" + str(stockData.loc[pandaRowNum][4]))

            # set volume cells
            self.gui.cellList[rowNum+5].setVisible(True)
            self.gui.cellList[rowNum+5].setText(" " + str(stockData.loc[pandaRowNum][5]))
                            
            rowNum += 6
            pandaRowNum -= 1

        # for the cells that we did not set a value for
        # make them disappear
        pandaRowNum = len(stockData)
        for x in range(pandaRowNum, 254):

            # set date cells
            self.gui.cellList[rowNum].setVisible(False)

            # set open cells
            self.gui.cellList[rowNum+1].setVisible(False)

            # set high cells
            self.gui.cellList[rowNum+2].setVisible(False)

            # set low cells
            self.gui.cellList[rowNum+3].setVisible(False)

            # set close cells
            self.gui.cellList[rowNum+4].setVisible(False)

            # set volume cells
            self.gui.cellList[rowNum+5].setVisible(False)
                            
            rowNum += 6


        # update the candlestick chart
        self.gui.updateChartSeries()

        # at this point the go button should still be disabled from the
        # go button thread. Enable it now
        self.gui.scanButton.setEnabled(True)

    """ updates the close price of the last row in the table"""
    def updateTable(self, ticker):
        stockData = db.select_last_row(self.dbConn, ticker)

        if(str(stockData[4]) != self.gui.cellList[10].text()[1:]):
            self.gui.cellList[10].setText("$" + str(stockData[4]))
            self.startLSTMThread()

    def populateNews(self):

        fontColor = "rgba(0,0,0,0);"
        
        for count in range(0, len(self.currentNews)):
            self.gui.headLineList[count].setText(self.currentNews['date'][count] + " " +
                                                 self.currentNews['time'][count] + " " +
                                                 self.currentNews['title'][count])

            # change the text to green if it is a positive sentiment, red if it is negative

            if(self.currentNews['compound'][count] > 0):
                fontColor = "rgba(153,0,0,255);"
                
            elif(self.currentNews['compound'][count] < 0):
                fontColor = "rgba(0,153,0,255);"

            self.gui.headLineList[count].setStyleSheet("font-size: 11px;\
                                                    font-weight: bold;\
                                                    border: none;\
                                                    background-color: rgba(255,255,255,0);\
                                                    color: " + fontColor)

    def clearTable(self):
        for x in range(6, self.gui.numberOfCells):
            self.gui.cellList[x].setText("")


    def updateIndexLabels(self, data):
        self.gui.indexLabelOne.setText(data[0])
        self.gui.indexLabelTwo.setText(data[1])
        self.gui.indexLabelThree.setText(data[2])

        # decide on the color of the label now
        labelOneColor = None
        labelTwoColor = None
        labelThreeColor = None

        if(data[0][3][0] == "+"):
            labelOneColor = "#009900"
        else:
            labelOneColor = "#990000"

        if(data[1][3][0] == "+"):
            labelTwoColor = "#009900"
        else:
            labelTwoColor = "#990000"

        if(data[2][3][0] == "+"):
            labelThreeColor = "#009900"
        else:
            labelThreeColor = "#990000"

        # update the css for each label to give them a simple flash animation
        self.gui.indexLabelOne.setStyleSheet("font-size: 14px;\
                                              border: none;\
                                              background-color: rgba(255,255,255,0);\
                                              color: " + self.updateFlashColor + ";")

        self.gui.indexLabelTwo.setStyleSheet("font-size: 14px;\
                                              border: none;\
                                              background-color: rgba(255,255,255,0);\
                                              color: " + self.updateFlashColor + ";")

        self.gui.indexLabelThree.setStyleSheet("font-size: 14px;\
                                                border: none;\
                                                background-color: rgba(255,255,255,0);\
                                                color: " + self.updateFlashColor + ";")

        time.sleep(.5)

        # change them back to either red or green
        # the way we will determine this is using the increase amount
        # that google provides for us. They put a '+' for green and a
        # '-' for red

        self.gui.indexLabelOne.setStyleSheet("font-size: 14px;\
                                              border: none;\
                                              background-color: rgba(255,255,255,0);\
                                              color: " + labelOneColor)

        self.gui.indexLabelTwo.setStyleSheet("font-size: 14px;\
                                              border: none;\
                                              background-color: rgba(255,255,255,0);\
                                              color: " + labelTwoColor)

        self.gui.indexLabelThree.setStyleSheet("font-size: 14px;\
                                                border: none;\
                                                background-color: rgba(255,255,255,0);\
                                                color: " + labelThreeColor)

    def updatePredictedPrice(self, price):
        self.gui.predictedLabel.setText("      Next Predicted Close: $" + str(round(price, 2)))

    # this function is used by the other threads to show a popup if and when an error
    # occurs during execution
    def showMessageBox(self, msg, details=None):
        self.gui.messageBox.setText(msg)
        if(details != None):
            self.gui.messageBox.setDetailedText(details)
        self.gui.predictedLabel.setText("")
        self.gui.messageBox.exec()
        
    
""" Thread that handles making the initial price data pull,
    updating the database. It then sends the signal to let the
    controller know its time to update the price table and chart"""
class GoButtonThread(QThread):

    populateTableSig = pyqtSignal(str)
    populateNewsSig = pyqtSignal()
    lstmSig = pyqtSignal(str)
    errorSig = pyqtSignal(str, str)

    def __init__(self, gui, ctrl):
        QThread.__init__(self)
        self.gui = gui
        self.controller = ctrl


    def run(self):

        # disable the go button while things are going on so the user
        # cant spam it and break it

        self.gui.scanButton.setEnabled(False)
        
        ticker = self.gui.tickerComboBox.currentText()

        try:
        
            stockPrices = self.controller.getTickerPrices(ticker)
            self.controller.currentNews = getNews(ticker)
        
            # establish a connection to the database
            self.dbConn = db.create_connection('stocksDB.db')

            # put the prices in the database
            db.insert_df(self.dbConn, ticker, stockPrices)

            # send the signal to update the table, update the news,
            # and start the lstm model
            self.populateTableSig.emit(ticker)
            self.populateNewsSig.emit()
            self.lstmSig.emit(ticker)

        except Exception as e:
            errorMsg = "Unable to retrieve data for ticker: " + ticker
            self.gui.scanButton.setEnabled(True)
            self.errorSig.emit(errorMsg, str(e))


class UpdateThread(QThread):

    updateCloseSig = pyqtSignal(str)
    updateNewsSig = pyqtSignal(str)
    errorSig = pyqtSignal(str, str)
    
    def __init__(self, gui, ctrl):
        QThread.__init__(self)
        self.controller = ctrl
        self.running = True
        self.gui = gui
        self.ticker = None

    def run(self):
        while(self.running):
            time.sleep(30)
            if(self.ticker == None):
                self.ticker = self.gui.tickerComboBox.currentText()

            try:
                stockData = self.controller.getLastClose(self.ticker)

                self.dbConn = db.create_connection('stocksDB.db')

                # get the last row so we know which date to use
                lastRow = db.select_last_row(self.dbConn, self.ticker)
                    
                db.update_cell(self.dbConn, self.ticker, lastRow[0], stockData.iloc[-1]['Close'])

                self.updateCloseSig.emit(self.ticker)

                # get the news also, if the last headline does not match what we have in the corresponding
                # label widget then update it

                currentNews = getNews(self.ticker)

                latestHeadline = currentNews['date'].iloc[0] + " " + currentNews['time'].iloc[0] + " " + currentNews['title'].iloc[0]

                if latestHeadline != self.gui.headLineList[0].text():
                    self.controller.currentNews = currentNews
                    self.updateNewsSig.emit()
            except Exception as e:
                pass
                

""" This thread starts when the application is launched and runs until the user
    closes the program. The thread reaches out to Google Finance to update
    the S&P 500, DOW 30, and NASDAQ stock indices every few seconds """
class IndexThread(QThread):

    errorSig = pyqtSignal(str, str)

    def __init__(self, ctrl):
        QThread.__init__(self)
        self.controller = ctrl
        self.running = True

    def run(self):
        while(self.running):
            # sleep for a random time between 10 and 20 seconds so google
            # thinks we are a bit more human
            sleepTime = random.randint(10, 20)
            time.sleep(sleepTime)

            
            # get the updated information
            try:
                indexData = getIndicesGoogle()
            except Exception as e:
                pass

            # do something with the data
            if(indexData):
                self.controller.updateIndexLabels(indexData)

""" This thread controls everything that happens with the
    LSTM Model for prediction """
class LSTMThread(QThread):

    readyToPredictSig = pyqtSignal()
    predictionSig = pyqtSignal(float)
    errorSig = pyqtSignal(str, str)

    def __init__(self, gui):
        QThread.__init__(self)
        self.lstm = LSTMPredictor()
        self.gui = gui

    def setStockData(self, ticker):

        # reset the network so that it does a full train
        self.lstm.initialTrain = False
        
        # create connection to database, get the data for the
        # given ticker, and then set it as the data to use for the model
        self.dbConn = db.create_connection('stocksDB.db')
        data = db.select_all(self.dbConn, ticker)
        self.lstm.setStockData(data)
        self.lstm.setTrainData()
        self.lstm.buildNetwork()
        self.readyToPredictSig.emit()
        
        
    def run(self):
        try:
            self.gui.predictedLabel.setText("              Making Prediction...")
            self.lstm.trainNetwork()
            previousClosePrice = self.lstm.stockData['Close'][len(self.lstm.stockData['Close'])-1]
            predictedPrice = self.lstm.predict(previousClosePrice)
            self.predictionSig.emit(predictedPrice)
        except Exception as e:
            errorMsg = "Something went wrong while making prediction"
            self.gui.predictedLabel.setText(errorMsg)
                                
    


        




