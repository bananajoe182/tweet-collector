from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pymongo
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
import logging
import time
import credentials

engine = create_engine(credentials.postgres_key)

# create a table in SQL database
create_query = '''
CREATE TABLE IF NOT EXISTS tweets (
timestamp VARCHAR(50),
text VARCHAR(400),
neg REAL,
neu REAL,
pos REAL,
compound REAL
);
'''

engine.execute(create_query)

#Start pymongo DB
client = pymongo.MongoClient("mongodb://mongodb:27017/")
db = client.mydb

s = SentimentIntensityAnalyzer()

def extract():
    '''Extract tweets from mongo'''
    texts = []
    timestamps = []

    #Get all unmarked tweets
    for doc in db.tweets.find({'marked' : {'$exists': False}}):
        texts.append(doc['text'])
        timestamps.append(doc['datetime'])

    #No mark all unmarked tweets 
    db.tweets.update_many({'marked' : {'$exists': False}},{ '$set': {"marked": True} })
    
    #Create pandas DF
    df = pd.DataFrame({'timestamp':timestamps, 'text':texts})

    return df


def transform(tweet_text):
    ''' Perform sentiment analysis'''

    df = tweet_text
    neg = []
    neu = []
    pos = []
    compound = []

    for text in df['text']:
        score = s.polarity_scores(text)
        neg.append(score['neg'])
        neu.append(score['neu'])
        pos.append(score['pos'])
        compound.append(score['compound'])

    df['neg'] = neg
    df['neu'] = neu
    df['pos'] = pos
    df['compound'] = compound

    return df

def load(transformed_data):
    ''' loads text, result, etc..to postgress'''
    transformed_data.to_sql('tweets', engine, if_exists = 'append', index = False)
    logging.critical('----INSERTED INTO postgres!------\n')

while True:
    tweet_text = extract()
    transformed_data = transform(tweet_text)
    load(transformed_data)
    time.sleep(30)

