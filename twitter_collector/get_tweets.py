import credentials
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
import json
import logging
import pymongo

client = pymongo.MongoClient("mongodb://mongodb:27017/")
db = client.mydb

def authenticate():
    """Function for handling Twitter Authentication. Please note
       that this script assumes you have a file called credentials.py
       which stores the 4 required authentication tokens:

       1. CONSUMER_API_KEY
       2. CONSUMER_API_SECRET
       3. ACCESS_TOKEN
       4. ACCESS_TOKEN_SECRET

    See course material for instructions on getting your own Twitter credentials.
    """
    auth = OAuthHandler(credentials.CONSUMER_API_KEY, credentials.CONSUMER_API_SECRET)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)

    return auth


class TwitterListener(StreamListener):

    def on_data(self, data):
        """Whatever we put in this method defines what is done with
        every single tweet as it is intercepted in real-time"""

        t = json.loads(data)  # t is just a regular python dictionary.

        tweet = {'text': t['text'], 'datetime' : t['created_at']}


        logging.critical(f'\n\n\nTWEET INCOMING: {tweet["text"]}\n\n\n')
        db.tweets.insert_one(tweet)
        logging.critical('----INSERTED INTO mongodb!------\n')

    def on_error(self, status):

        if status == 420:
            print(status)
            return False


if __name__ == '__main__':

    auth = authenticate()
    listener = TwitterListener()
    stream = Stream(auth, listener)
    
    #Define a keyword for the tweets
    stream.filter(track=['Tesla'], languages=['en'])
