from flask import Flask, request, Response
import tweepy 
import pandas as pd
from pre_processing import clean,define_hour,by_date,by_date_one,find_no_re,find_re, get_frequent_words, today, by_date_stream_between, by_date_stream_before,by_date_stream_after
from dotenv import load_dotenv
import os
import json
from datetime import datetime, date
pd.options.mode.chained_assignment = None

#import from dotenv
load_dotenv()
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DEBUG = os.getenv("DEBUG")


consumer_key = os.getenv("consumer_key")
consumer_secret = os.getenv("consumer_secret")
access_key = os.getenv("access_key")
access_secret = os.getenv("access_secret")

#twitter autentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)


app = Flask(__name__)

def get_username(name):
    user_objects = api.search_users(q = name, page="1",count=10)
    return user_objects


def get_info_user(name):
    user_objects = api.get_user(screen_name = name)
    return user_objects

def get_tweets(name,number):    
    tweet_objects = api.user_timeline(screen_name = name, count = number)
    return  tweet_objects
def get_tweets_no_re(name,number):    
    tweet_objects = api.user_timeline(screen_name = name, count = number, exclude_replies=True)
    return  tweet_objects

def get_tweets_once(name):    
    tweet_objects = api.user_timeline(screen_name = name, count = 100) #exclude_replies=True
    return  tweet_objects
def all_tweets(name):    
    tweet_objects = api.user_timeline(screen_name = name, count=5000)
    return tweet_objects
def all_tweets_no_re(name):    
    tweet_objects = api.user_timeline(screen_name = name, count=2000, exclude_replies=True)
    return tweet_objects

#-----------------------------------------------------------------------------------------------------------------

@app.route("/searchuser", methods = ['GET'])
def user():
    users = request.args.get('username')
    user_list = get_username(users)
    user_name = [user.name for user in user_list]  
    user_screen = [user.screen_name for user in user_list]
    description = [user.description for user in user_list]
    verified = [user.verified for user in user_list]
    followers_count  = [user.followers_count for user in user_list]  
    profile_image = [user.profile_image_url for user in user_list]  
    
    df = pd.DataFrame()
    df['user_name'] = user_name
    df['user_screen'] = user_screen
    df['description'] = description
    df['verified'] = verified
    df['followers_count'] = followers_count
    df['profile_image'] = profile_image
    r = df.to_json(orient='records')
    
    resp = Response(response=r, status=200, mimetype="application/json")
    return resp

@app.route("/<username_screen_name>/getweets", methods = ['GET'])
def username(username_screen_name):
    username = username_screen_name
    number = request.args.get('number')
    tweet_objects = get_tweets(username,number)
    text = [tweet.text for tweet in tweet_objects]
    dates = [tweet.created_at for tweet in tweet_objects]
    retweet_count = [tweet.retweet_count for tweet in tweet_objects]
    favorite_count = [tweet.favorite_count for tweet in tweet_objects]
    df = pd.DataFrame()
    df['date'] = dates
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")    
    df['text'] = text
    df['retweet_count'] = retweet_count
    df['like'] = favorite_count  
    df['date'] = df['date'].apply(str)
    r = df.to_json(orient='records')
    resp = Response(response=r, status=200, mimetype="application/json")
    return resp

@app.route("/<username_screen_name>/getweets/date", methods = ['GET'])
def date_do(username_screen_name):
    username = username_screen_name
    date1 = request.args.get('from')
    date2= request.args.get('to')
    tweet_objects = all_tweets(username)
    text = [tweet.text for tweet in tweet_objects]
    date = [tweet.created_at for tweet in tweet_objects]
    retweet_count = [tweet.retweet_count for tweet in tweet_objects]
    favorite_count = [tweet.favorite_count for tweet in tweet_objects]    
    df = pd.DataFrame()
    df['date'] = date
    df['text'] = text
    df['retweet_count'] = retweet_count
    df['like'] = favorite_count      
    df = by_date(df,date1,date2)
    r = df.to_json(orient='records')    
    resp = Response(response=r, status=200, mimetype="application/json")
    return resp
@app.route("/<username_screen_name>/tweetoday", methods = ['GET'])
def date_do_one(username_screen_name):
    username = username_screen_name
    tweet_objects = get_tweets_once(username)
    text = [tweet.text for tweet in tweet_objects]
    date = [tweet.created_at for tweet in tweet_objects]
    retweet_count = [tweet.retweet_count for tweet in tweet_objects]
    favorite_count = [tweet.favorite_count for tweet in tweet_objects]    
    df = pd.DataFrame()
    df['date'] = date
    df['text'] = text
    df['retweet_count'] = retweet_count
    df['like'] = favorite_count      
    df = today(df)
    r = df.to_json(orient='records')    
    resp = Response(response=r, status=200, mimetype="application/json")
    return resp

@app.route("/<username_screen_name>/tweetoday/hour", methods = ['GET'])
def tweet_today(username_screen_name):
    username = username_screen_name
    hour1 = request.args.get('hour')
    tweet_objects = get_tweets_once(username)
    text = [tweet.text for tweet in tweet_objects]
    date = [tweet.created_at for tweet in tweet_objects]
    retweet_count = [tweet.retweet_count for tweet in tweet_objects]
    favorite_count = [tweet.favorite_count for tweet in tweet_objects]    
    df = pd.DataFrame()
    df['date'] = date
    df['text'] = text
    df['retweet_count'] = retweet_count
    df['like'] = favorite_count      
    df = by_date_one(df,hour1)
    r = df.to_json(orient='records')    
    resp = Response(response=r, status=200, mimetype="application/json")
    return resp


@app.route("/<username_screen_name>/countsbydate", methods = ['GET'])
def all_tweet(username_screen_name):
    username = username_screen_name
    tweet_objects = all_tweets(username)
    text = [tweet.text for tweet in tweet_objects]
    date = [tweet.created_at for tweet in tweet_objects]
    df = pd.DataFrame()
    df['date'] = date
    df['text'] = text
    df  = clean(df)
    df = df.groupby(['date']).size().reset_index(name='counts')
    df = df.sort_values(["date"], ascending=True)    
    df = df.reset_index(drop=True)    


    df['date'] = df['date'].apply(str)
    json = df.to_json(orient="records")
    resp = Response(response=json, status=200, mimetype="application/json")
    return resp


@app.route("/<username_screen_name>/like", methods = ['GET'])
def get_like(username_screen_name):
    username = username_screen_name
    tweet_objects = all_tweets_no_re(username)
    text = [tweet.text for tweet in tweet_objects]
    date = [tweet.created_at for tweet in tweet_objects]    
    retweet_count = [tweet.retweet_count for tweet in tweet_objects]
    favorite_count = [tweet.favorite_count for tweet in tweet_objects]

    df = pd.DataFrame()
    df['date'] = date
    df['text'] = text    
    df['retweet_count'] = retweet_count
    df['like'] = favorite_count
    df['date'] = df['date'].apply(str)
    df = df.sort_values(["date"], ascending=True)  
    df = df.reset_index(drop=True)  

    json = df.to_json(orient="records")
    resp = Response(response=json, status=200, mimetype="application/json")
    return resp   
     
@app.route("/<username_screen_name>/getfriends")
def friends(username_screen_name):
    username = username_screen_name
    tweet_objects = api.friends(username, count="100")#, count=100 
    screen = [tweet.screen_name for tweet in tweet_objects]  
    r = json.dumps(screen)
    resp = Response(response=r, status=200, mimetype="application/json")
    return resp


@app.route("/<username_screen_name>/noretweet", methods = ['GET'])
def get_no_retweet(username_screen_name):
    username = username_screen_name
    number = request.args.get('number')
    tweet_objects = get_tweets_no_re(username, number)
    text = [tweet.text for tweet in tweet_objects]
    date = [tweet.created_at for tweet in tweet_objects]
    retweet_count = [tweet.retweet_count for tweet in tweet_objects]
    favorite_count = [tweet.favorite_count for tweet in tweet_objects]    
    df = pd.DataFrame()
    df['date'] = date
    df['text'] = text
    df['retweet_count'] = retweet_count
    df['like'] = favorite_count      
    df = find_no_re(df)
    df['date'] = df['date'].apply(str)
    r = df.to_json(orient='records') 
    resp = Response(response=r, status=200, mimetype="application/json")
    return resp

@app.route("/<username_screen_name>/retweet", methods = ['GET'])
def get_retweet(username_screen_name):
    username = username_screen_name
    number = request.args.get('number')
    tweet_objects = get_tweets(username, number)
    text = [tweet.text for tweet in tweet_objects]
    date = [tweet.created_at for tweet in tweet_objects]
    retweet_count = [tweet.retweet_count for tweet in tweet_objects]
    favorite_count = [tweet.favorite_count for tweet in tweet_objects]    
    df = pd.DataFrame()
    df['date'] = date
    df['text'] = text
    df['retweet_count'] = retweet_count
    df['like'] = favorite_count    
    df = find_re(df)

    df['date'] = df['date'].apply(str)
    r = df.to_json(orient='records') 
    resp = Response(response=r, status=200, mimetype="application/json")
    return resp

@app.route("/<username_screen_name>/fwords", methods = ['GET'])
def get_f_words(username_screen_name):
    username = username_screen_name
    tweet_objects = all_tweets(username)
    text = [tweet.text for tweet in tweet_objects]
    df = pd.DataFrame()
    df['text'] = text 
    l = []
    l = get_frequent_words(df)
    l = list(l)
    r = json.dumps(l)
    resp = Response(response=r, status=200, mimetype="application/json")
    return resp

@app.route("/<username_screen_name>/countsbyhour", methods = ['GET'])
def get_hour_f(username_screen_name):
    username = username_screen_name
    tweet_objects = all_tweets(username)
    text = [tweet.text for tweet in tweet_objects]
    date = [tweet.created_at for tweet in tweet_objects]
    df = pd.DataFrame()
    df['hour'] = date
    df['text'] = text 
    df = define_hour(df)
    df = df.sort_values(['hour'], ascending=True)
    df = df.reset_index(drop=True)    
    json = df.to_json(orient="records")
    resp = Response(response=json, status=200, mimetype="application/json")
    return resp


@app.route("/<username_screen_name>/infouser", methods = ['GET'])
def info_user(username_screen_name):
    username = username_screen_name
    user_objects = get_info_user(username)
    name = user_objects.name 
    screen_name =  user_objects.screen_name
    location = user_objects.location
    profile_location = user_objects.profile_location 
    description = user_objects.description   
    verified = user_objects.verified    
    followers_count  = user_objects.followers_count    
    friends_count = user_objects.friends_count    
    profile_image = user_objects.profile_image_url

    jsonOb = {}
    jsonOb['user_name'] = name
    jsonOb['screen_name'] = screen_name
    jsonOb['location'] = location
    jsonOb['profile_location'] = profile_location
    jsonOb['description'] = description
    jsonOb['verified'] = verified
    jsonOb['followers_count'] = followers_count
    jsonOb['friends_count'] = friends_count
    jsonOb['profile_image'] = profile_image

    r = json.dumps(jsonOb)
    resp = Response(response=r, status=200, mimetype="application/json")
    return resp

@app.route("/<username_screen_name>/tweetstream/between/date", methods = ['GET'])
def stream_tweet_between(username_screen_name):
    username = username_screen_name
    date1 = request.args.get('from')
    date2= request.args.get('to')
    tweet_objects = all_tweets(username)
    text = [tweet.text for tweet in tweet_objects]
    date = [tweet.created_at for tweet in tweet_objects]
    retweet_count = [tweet.retweet_count for tweet in tweet_objects]
    like = [tweet.favorite_count for tweet in tweet_objects]
    
    df = pd.DataFrame()
    df['date'] = date
    df['text'] = text
    df['retweet_count'] = retweet_count
    df['like'] = like

    dx = pd.DataFrame()

    dx = by_date_stream_between(df,date1,date2)
    r = dx.to_json(orient='records')    

    resp = Response(response=r, status=200, mimetype="application/json")
    return resp

@app.route("/<username_screen_name>/tweetstream/before/date", methods = ['GET'])
def stream_tweet_before(username_screen_name):
    username = username_screen_name
    date1 = request.args.get('from')
    tweet_objects = all_tweets(username)
    text = [tweet.text for tweet in tweet_objects]
    date = [tweet.created_at for tweet in tweet_objects]
    df = pd.DataFrame()
    retweet_count = [tweet.retweet_count for tweet in tweet_objects]
    like = [tweet.favorite_count for tweet in tweet_objects]
    df['date'] = date
    df['text'] = text
    df['retweet_count'] = retweet_count
    df['like'] = like
    dx = pd.DataFrame()
    dx = by_date_stream_before(df,date1)
    dx = dx[0:10]
    b = dx.to_json(orient='records')
    resp = Response(response=b, status=200, mimetype="application/json")
    return resp

@app.route("/<username_screen_name>/tweetstream/after/date", methods = ['GET'])
def stream_tweet_after(username_screen_name):
    username = username_screen_name
    date1 = request.args.get('from')
    tweet_objects = all_tweets(username)
    text = [tweet.text for tweet in tweet_objects]
    date = [tweet.created_at for tweet in tweet_objects]
    retweet_count = [tweet.retweet_count for tweet in tweet_objects]
    like = [tweet.favorite_count for tweet in tweet_objects]

    df = pd.DataFrame()
    df['date'] = date
    df['text'] = text
    df['retweet_count'] = retweet_count
    df['like'] = like

    dx = pd.DataFrame()
    dx = by_date_stream_after(df,date1)
    dx = dx[0:10]
    a = dx.to_json(orient='records')
    resp = Response(response=a, status=200, mimetype="application/json")
    return resp
#-----------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app.run(HOST,PORT,DEBUG)
