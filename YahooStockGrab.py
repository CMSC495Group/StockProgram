import requests
import bs4
import json
import pandas as pd
from datetime import datetime, timedelta

"""
    Grabs daily or weekly price data from finance.yahoo.com
"""

def getYahooData(ticker, startDate, endDate, interval):
    
    
    # have to convert each date to unix for the yahoo url
    # format for date will be 'DD-MM-YYYY'

    startDateUnix = int(datetime.strptime(startDate, '%d-%m-%Y').timestamp())
    endDateUnix = int(datetime.strptime(endDate, '%d-%m-%Y').timestamp())
    
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + ticker + '?symbol=' + ticker + '&period1=' + \
    str(startDateUnix) + '&period2=' + str(endDateUnix) + '&interval=' + interval
    
    res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})

    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    
    # sort through the nested dictionary mess and put each value in its own list
    
    newDictionary=json.loads(str(soup))
    try:
        newDictionary2 = newDictionary['chart']['result'][0]
    
        unixDates = newDictionary2['timestamp']
        
        dates = []
        
        # turn the unix timestamps back into dates
        for item in unixDates:
            dateFormat = datetime.fromtimestamp(item).date().strftime('%Y-%m-%d')
            dates.append(dateFormat)
        
        newDictionary3 = newDictionary2['indicators']['quote'][0]
        
        # convert each value into float so that we can only keep two places after the decimal
        
        strOpens = newDictionary3['open']
        
        opens = []
        
        for item in strOpens:
            if item == None:
                number = 0.00
                opens.append(number)
            else:
                number = round(float(item), 2)
                opens.append(number)
            
            
        strHighs = newDictionary3['high']
        
        highs = []
        
        for item in strHighs:
            if item == None:
                number = 0
                highs.append(number)
            else:
                number = round(float(item), 2)
                highs.append(number)
            
        strLows = newDictionary3['low']
        
        lows = []
        
        for item in strLows:
            if item == None:
                number = 0
                lows.append(number)
            else:
                number = round(float(item), 2)
                lows.append(number)
            
        strCloses = newDictionary3['close']
        
        closes = []
        
        for item in strCloses:
            if item == None:
                number = 0
                closes.append(number)
            else:
                number = round(float(item), 2)
                closes.append(number)
            
        strVolumes = newDictionary3['volume']

        volumes = []
        
        for item in strVolumes:
            if item == None:
                number = 0
                volumes.append(number)
            else:
                number = int(item)
                volumes.append(number)
                

        
        newDictionary4 = newDictionary2['indicators']['adjclose'][0]
        
        strAdjCloses = newDictionary4['adjclose']
        
        adjCloses = []
        
        for item in strAdjCloses:
            if item == None:
                 number = 0
            else:
                 number = round(float(item), 2)
                 adjCloses.append(number)
            
        # append them all to their own list so that each entry in the list is a full OHLC entry for the day
        
        newList = []
        finalList = []
        
        for i in range(0, len(dates)):
            newList.append(dates[i])
            newList.append(opens[i])
            newList.append(highs[i])
            newList.append(lows[i])
           # newList.append(closes[i])
            newList.append(adjCloses[i])
            newList.append(volumes[i])
            finalList.append(newList)
            newList = []

            #uncomment for a full return of all data. This was changed because mplfinance does not consider
            #displaying the Adj. close column so the 'Close' column of the return is the actual 'Adj. Close'
            #stockDf = pd.DataFrame(finalList, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj. Close', 'Volume'])

            stockDf = pd.DataFrame(finalList, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            
        return stockDf
    except:
        error = newDictionary['chart']['error']['description']
        print(error)


if __name__ == '__main__':
    print("Enter Ticker")
    ticker = input(":")
    print("Enter Start Date (DD-MM-YYYY)")
    sDate = input(":")
    print("Enter End Date (DD-MM-YYYY)")
    eDate = input(":")
    print("Enter time interval (1d, 1wk)")
    interval = input(":")
    print(getYahooData(ticker, sDate, eDate, interval))
