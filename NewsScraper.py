import requests
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')
import pandas as pd

"""
    Using finviz.com and an input ticker, headlines and time stamps are loaded into a dictionary, which sentiment analysis is then performed on.
"""

def getNews(ticker):
    
    urlstart = 'https://finviz.com/quote.ashx?t='
    newsData = {}
    dataDictionary = {}

    url = urlstart + ticker
    req = requests.get(url=url, headers={'user-agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(req.text, 'html.parser')
    newsData = soup.find(id='news-table')
    dataDictionary[ticker] = newsData 
            

    newsList = []

    for ticker, newsData in dataDictionary.items():
            for row in newsData.findAll('tr'):
                    title = row.a.get_text()
                    timestamp = row.td.text.split(' ')
                    if len(timestamp) == 1:
                        time = timestamp[0]
                    else:
                        date =  timestamp[0]
                        time = timestamp [1]
                        
                    newsList.append([date,time[:7],title])
                    
    dataframe = pd.DataFrame(newsList, columns=['date','time','title'])
    vader = SentimentIntensityAnalyzer()

    narrow = lambda title: vader.polarity_scores(title)['compound']
    dataframe['compound'] = dataframe['title'].apply(narrow)
    
    return dataframe.head(50)





