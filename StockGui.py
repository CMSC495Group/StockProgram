from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QComboBox
from PyQt5.QtWidgets import QPushButton, QTableWidget, QScrollArea
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtChart import *
from PyQt5.QtGui import QColor, QPainter
import sys
import time
from datetime import date, datetime
from GuiController import GuiCtrl
from PyQt5 import QtCore
import numpy as np


# create main window

class StockGui(QMainWindow):
    
    def __init__(self):

        super().__init__()
        self.setWindowTitle('StockGUI')
        self.setFixedSize(1160, 680)

        # set central widget and general layout
        # we will use a grid layout for the general layout
        self.generalLayout = QGridLayout()
        self.generalLayout.setRowStretch(0, 1)
        self.generalLayout.setRowStretch(1, 0)
        self.centralWidget = QWidget(self)
        self.centralWidget.setStyleSheet("background-color: #FFFFFF;")
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.generalLayout)

        # the central widget will have three smaller widgets inside
        # add leftWidget, rightWidget, and indexWidget to central widget

        self.createIndexWidget()
        self.createLeftWidget()
        self.createRightWidget()

        # some variables to help with the candlestick panning
        self.mousePressed = False
        self.mousePrevXPos = None
        self.mousePrevYPos = None

    """ Creates the panel that displays information for
        variaous market indices """

    def createIndexWidget(self):
        self.indexWidget = QWidget()
        self.indexLayout = QHBoxLayout()
        self.indexWidget.setLayout(self.indexLayout)
        self.indexWidget.setStyleSheet("border: 3px solid black;")
        self.indexWidget.setFixedSize(1142, 35)

        self.indexLabelOne = QLabel("Dow Jones: Loading...")
        self.indexLabelOne.setFixedSize(245, 20)
        self.indexLabelOne.setStyleSheet("font-size: 14px;\
                                          border: none;")

        self.indexLabelTwo = QLabel("S&P 500: Loading...")
        self.indexLabelTwo.setFixedSize(245, 20)
        self.indexLabelTwo.setStyleSheet("font-size: 14px;\
                                          border: none;")

        self.indexLabelThree = QLabel("Nasdaq: Loading...")
        self.indexLabelThree.setFixedSize(235, 20)
        self.indexLabelThree.setStyleSheet("font-size: 14px;\
                                            border: none;")

        self.indexLayout.addWidget(self.indexLabelOne)
        self.indexLayout.addWidget(self.indexLabelTwo)
        self.indexLayout.addWidget(self.indexLabelThree)

        self.generalLayout.addWidget(self.indexWidget, 0, 0)

    """ Creates the left main widget that holds
        the chart widget and the news widget """
    def createLeftWidget(self):
        self.leftMainWidget = QWidget()
        self.leftMainLayout = QVBoxLayout()
        self.leftMainWidget.setLayout(self.leftMainLayout)
        self.leftMainWidget.setStyleSheet("border: None;")
        self.leftMainWidget.setFixedSize(675, 625)

        # create chart widget
        self.createChartWidget()

        # create news widget
        self.createNewsWidget()

        self.generalLayout.addWidget(self.leftMainWidget, 1, 0)

    def createChartWidget(self):
        self.chartWidget = QWidget()
        self.chartWidget.setFixedSize(655, 400)
        self.chartWidgetLayout = QVBoxLayout()
        self.chartWidget.setLayout(self.chartWidgetLayout)
        self.chartWidget.setStyleSheet("border:3px solid black;")

        self.chartTheme = QChart.ChartThemeLight

        # create the actual QChart that will display the candlestick chart
        self.candleChart = QChart()

        # set the theme of the chart
        self.candleChart.setTheme(self.chartTheme)

        # hide the legend
        self.candleChart.legend().setVisible(False)

        # add the chart into a view
        self.chartView = QChartView(self.candleChart)
        self.chartView.setRenderHint(QPainter.Antialiasing)

        # handle moust moving events when we do start tracking it
        self.chartView.mouseMoveEvent = self.chartMouseMoveEventHandler

        # handle mouse wheel events
        self.chartView.wheelEvent = self.chartMouseWheelEventHandler

        # handle mouse press events
        self.chartView.mousePressEvent = self.chartMousePressEventHandler

        # handle mouse release events
        self.chartView.mouseReleaseEvent = self.chartMouseReleaseEventHandler
    
        self.chartWidgetLayout.addWidget(self.chartView)
                    
        self.leftMainLayout.addWidget(self.chartWidget)

    def updateChartSeries(self):

        # remove all current series
        self.candleChart.removeAllSeries()

        # create a new series of data that will hold the stock data
        self.candleChartSeries = QCandlestickSeries()
        self.candleChartSeries.setIncreasingColor(QColor(0, 255, 0, 255)) #RGB+Alpha
        self.candleChartSeries.setDecreasingColor(QColor(255, 0, 0, 255))

        # create the set structure that holds one OHLCV day of data
        self.candleChartSet = QCandlestickSet()

        for x in range(6, len(self.cellList), 6):
            candleChartSet = QCandlestickSet()
            # Date as timestamp
            candleChartSet.setTimestamp(float(time.mktime(datetime.strptime(self.cellList[x].text(), " %Y-%m-%d ").timetuple())))
            candleChartSet.setOpen(float(self.cellList[x+1].text()[1:])) # Open
            candleChartSet.setHigh(float(self.cellList[x+2].text()[1:])) # High
            candleChartSet.setLow(float(self.cellList[x+3].text()[1:])) # Low
            candleChartSet.setClose(float(self.cellList[x+4].text()[1:])) # Close
            #ohlcList.append(self.cellList[x+5]) # Volume 

            self.candleChartSeries.append(candleChartSet)
        
        self.candleChart.addSeries(self.candleChartSeries)
        #self.candleChart.setAnimationOptions(QChart.SeriesAnimations)

        # create default axes for chart
        self.candleChart.createDefaultAxes()

        self.candleChart.axes()[0].setGridLineVisible(False)

        """# set the x axis as date (DOES NOT WORK YET)

        self.axisX = QDateTimeAxis()
        
        dateEnd = QtCore.QDate()
        dateEnd.setDate(int(self.cellList[6].text()[1:5]), # year
                          int(self.cellList[6].text()[6:8]), # month
                          int(self.cellList[6].text()[9:11])) # day

        axisEnd = QtCore.QDateTime()
        axisEnd.setDate(dateEnd)

        dateBegin = QtCore.QDate()
        dateBegin.setDate(int(self.cellList[len(self.cellList)-6].text()[1:5]),
                        int(self.cellList[len(self.cellList)-6].text()[6:8]),
                        int(self.cellList[len(self.cellList)-6].text()[9:11]))
        
        axisBegin = QtCore.QDateTime()
        axisBegin.setDate(dateBegin)
        
        self.axisX.setRange(axisBegin, axisEnd)
        self.axisX.setFormat("yyyy-MM-dd")

        self.candleChart.setAxisX(self.axisX, self.candleChartSeries) """

    """ Controls how pressing the mouse button down and moving the
        mouse makes the chart move """
    def chartMousePressEventHandler(self, e):
        self.mousePressed = True
        self.mousePrevXPos = e.x()
        self.mousePrevYPos = e.y()

    def chartMouseReleaseEventHandler(self, e):
        self.mousePressed = False

    def chartMouseMoveEventHandler(self, e):

        panSpeed = 10
        
        if(self.mousePressed):
            newMouseXPos = e.x()
            newMouseYPos = e.y()
            if newMouseXPos < self.mousePrevXPos and newMouseYPos == self.mousePrevYPos:
                # moving right
                self.candleChart.scroll(panSpeed, 0)
            elif newMouseXPos > self.mousePrevXPos and newMouseYPos == self.mousePrevYPos:
                # moving left
                self.candleChart.scroll(panSpeed*-1, 0)
            elif newMouseXPos == self.mousePrevXPos and newMouseYPos < self.mousePrevYPos:
                # moving down
                self.candleChart.scroll(0, panSpeed*-1)
            elif newMouseXPos == self.mousePrevXPos and newMouseYPos > self.mousePrevYPos:
                # moving up
                self.candleChart.scroll(0, panSpeed)
            elif newMouseXPos < self.mousePrevXPos and newMouseYPos < self.mousePrevYPos:
                # moving left up diagonal
                self.candleChart.scroll(panSpeed, panSpeed*-1)
            elif newMouseXPos > self.mousePrevXPos and newMouseYPos < self.mousePrevYPos:
                # moving right up diagonal
                self.candleChart.scroll(panSpeed*-1, panSpeed*-1)
            elif newMouseXPos < self.mousePrevXPos and newMouseYPos > self.mousePrevYPos:
                # moving left down diagonal
                self.candleChart.scroll(panSpeed, panSpeed)
            elif newMouseXPos > self.mousePrevXPos and newMouseYPos > self.mousePrevYPos:
                # moving right down diagonal
                self.candleChart.scroll(panSpeed*-1, panSpeed)

            self.mousePrevXPos = newMouseXPos
            self.mousePrevYPos = newMouseYPos


    """ Controls how the mouse wheel effects chart zoom """
    def chartMouseWheelEventHandler(self, e):
        # positive number means zoom in
        if e.angleDelta().y() > 0:
            self.candleChart.zoom((e.angleDelta().y() / 120) + .001)
        elif e.angleDelta().y() < 0:
            # negative number means zoom out
            self.candleChart.zoom((e.angleDelta().y() / 120) + 1.9)
                    
    def createNewsWidget(self):
        self.newsWidget = QWidget()
        self.newsWidget.setFixedSize(655, 205)
        self.newsWidget.setStyleSheet("border: 3px solid black;")

        self.leftMainLayout.addWidget(self.newsWidget)
        
    """ Creates the right main widget that holds
        the price table and the company ticker buttons """
    def createRightWidget(self):
        self.rightMainWidget = QWidget()
        self.rightMainLayout = QVBoxLayout()
        self.rightMainWidget.setLayout(self.rightMainLayout)
        self.rightMainWidget.setStyleSheet("border: 3px solid black;")
        self.rightMainWidget.setFixedSize(455, 605)

        self.createTickerSelectorWidget()
        self.createPredictedCloseWidget()
        self.createPriceTableWidget()

        self.generalLayout.addWidget(self.rightMainWidget, 1, 1)

    def createTickerSelectorWidget(self):
        self.tickerSelectorWidget = QWidget()
        self.tickerSelectorWidget.setFixedSize(430, 50)
        self.tickerSelectorLayout = QHBoxLayout()
        self.tickerSelectorWidget.setLayout(self.tickerSelectorLayout)
        self.tickerSelectorWidget.setStyleSheet("border: None;")

        # ticker combobox
        self.createTickerComboBoxWidget()

        # go button
        self.createScanButton()
        
        self.rightMainLayout.addWidget(self.tickerSelectorWidget)

    def createTickerComboBoxWidget(self):

        self.tickerComboBoxWidget = QWidget()
        self.tickerComboBoxWidget.setFixedSize(170, 40)
        self.tickerComboBoxWidgetLayout = QHBoxLayout() # this can really just be any layout so we can add others widgets
        self.tickerComboBoxWidget.setLayout(self.tickerComboBoxWidgetLayout)
        self.tickerComboBoxWidget.setStyleSheet("border: None;")
        
         # ticker combobox
        self.tickerComboBox = QComboBox()
        
        # list of tickers that the program will support
        # list was taken from url
        # https://finviz.com/screener.ashx?v=211&f=cap_large,sec_technology
        # last updated: Nov 3, 2020

        tickerList = ['ACN', 'ADI', 'ADSK', 'AKAM', 'AMAT', 'AMD', 'ANET',
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
                                
        self.tickerComboBox.addItems(tickerList)
        self.tickerComboBox.setEditable(True)

        self.tickerComboBox.setStyleSheet("font-size: 15px;\
                                           border: 3px solid black;")
        
        self.tickerComboBoxWidgetLayout.addWidget(self.tickerComboBox)
        
        self.tickerSelectorLayout.addWidget(self.tickerComboBoxWidget)

    def createScanButton(self):
        self.scanButtonWidget = QWidget()
        self.scanButtonWidget.setFixedSize(170, 40)
        self.scanButtonWidgetLayout = QHBoxLayout() # this can really just be any layout so we can add other widgets
        self.scanButtonWidget.setLayout(self.scanButtonWidgetLayout)

        self.scanButton = QPushButton("GO")

        self.scanButton.setStyleSheet("font-size: 15px;\
                                       border: 3px solid black;")

        self.scanButtonWidgetLayout.addWidget(self.scanButton)

        self.tickerSelectorLayout.addWidget(self.scanButtonWidget)

    def createPredictedCloseWidget(self):
        self.predictedCloseWidget = QWidget()
        self.predictedCloseWidget.setFixedSize(430 , 50)
        self.predictedCloseWidgetLayout = QHBoxLayout()
        self.predictedCloseWidget.setLayout(self.predictedCloseWidgetLayout)
        self.predictedCloseWidget.setStyleSheet("border: None;")
        
        self.predictedLabel = QLabel("Next Predicted Close: $5.00 (-0.02)")
        self.predictedLabel.setStyleSheet("font-size: 15px; \
                                           padding-left: 70px;\
                                           border: 3px solid black;")

        self.predictedCloseWidgetLayout.addWidget(self.predictedLabel)

        self.rightMainLayout.addWidget(self.predictedCloseWidget)

    def createPriceTableWidget(self):

        # we are using labels to represent the price tables
        # since it is easier than trying to use a custom QTableView

        self.numberOfRows = 253 # number of trading days in 2020
                                # this number might be different for other years
                                # due to leap day
        numberOfCells = self.numberOfRows * 6 # 6 for the number of columns
        
        self.priceTableWidget = QWidget()
        self.priceTableWidget.setFixedSize(415, 9000)
        self.priceTableWidgetLayout = QGridLayout()
        self.priceTableWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.priceTableWidgetLayout.setHorizontalSpacing(0)
        self.priceTableWidgetLayout.setVerticalSpacing(0)
        self.priceTableWidget.setLayout(self.priceTableWidgetLayout)

        # scroll widget for making the widget container scollable
        self.scrollBar = QScrollArea()

        self.scrollBar.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollBar.setStyleSheet("border: none;")
        self.scrollBar.setWidget(self.priceTableWidget)

        # set minimum row height for all of the rows

        for x in range(0, self.numberOfRows):
            self.priceTableWidgetLayout.setRowMinimumHeight(x, 500)


        
        self.cellList = []

        # create cells
        for x in range(0, numberOfCells):
            self.cellList.append(QLabel())
            self.cellList[x].setAlignment(QtCore.Qt.AlignCenter)

        # set values and styles for header cells
        # this should be the first 6 cells in the list
        for x in range(0, 6):
            if x == 0:
                self.cellList[x].setText("Date")
            elif x == 1:
                self.cellList[x].setText("Open")
            elif x == 2:
                self.cellList[x].setText("High")
            elif x == 3:
                self.cellList[x].setText("Low")
            elif x == 4:
                self.cellList[x].setText("Close")
            elif x == 5:
                self.cellList[x].setText("Volume")
            else:
                print("ERROR SETTING PRICE TABLE HEADERS")

            self.cellList[x].setStyleSheet("font-size: 16px;\
                                            border-left: 3px solid black;\
                                            border-bottom: 3px solid black;\
                                            border-top: 3px solid black;\
                                            font-weight: bold;")

        # add text to the rest of the cells for testing purposes
        cellCount = 0 # used to figure out what cell we are on
        for x in range(6, numberOfCells):
            if not cellCount == 6:
                if cellCount == 0:
                    # date cell
                    self.cellList[x].setText("")
                    cellCount += 1
                elif cellCount == 1:
                    # open cell
                    self.cellList[x].setText("")
                    cellCount += 1
                elif cellCount == 2:
                    # high cell
                    self.cellList[x].setText("")
                    cellCount += 1
                elif cellCount == 3:
                    # low cell
                    self.cellList[x].setText("")
                    cellCount += 1
                elif cellCount == 4:
                    # close cell
                    self.cellList[x].setText("")
                    cellCount += 1
                elif cellCount == 5:
                    self.cellList[x].setText("")
                    cellCount = 0

        # set the style for the rest of the cells

        for x in range(6, numberOfCells):
            self.cellList[x].setStyleSheet("font-size: 14px;\
                                             border-left: 3px solid black;\
                                             border-bottom: 3px solid black;")
        # add the cells to the grid layout
        rowNumber = 0
        columnNumber = 0
        for x in range(0, numberOfCells):
            self.priceTableWidgetLayout.addWidget(self.cellList[x], rowNumber, columnNumber)
            if not columnNumber == 5:
                columnNumber += 1
            else:
                columnNumber = 0
                # go to the next row once all the columns have cells
                rowNumber += 1
        
            
        self.rightMainLayout.addWidget(self.scrollBar)


def main():
    """ Main function """
    stockProgram = QApplication([])
    stockGui = StockGui()
    guiCtrl = GuiCtrl(stockGui)

    # this line tells the program to stop the running threads
    # before exiting
    stockProgram.aboutToQuit.connect(guiCtrl.stopThreads)
    # show the gui through the controller
    guiCtrl.display()

    # execute Stock Program Application
    sys.exit(stockProgram.exec())


if __name__ == '__main__':

    main()
