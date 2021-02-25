import numpy as np
import pandas as pd
import re
from datetime import datetime, date
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from collections import Counter
pd.options.mode.chained_assignment = None

STOPWORDS = set(stopwords.words('english'))
STOPWORDS_IT = set(stopwords.words('italian'))
#--------------------------------

def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


def remove_stopwords(text):
    return " ".join([word for word in str(text).split() if word not in STOPWORDS])

def remove_stopwords_it(text):
    return " ".join([word for word in str(text).split() if word not in STOPWORDS_IT])


#------------------------------------------------




def clean(data):
    df = pd.DataFrame()
    df = data

    df['text']= df['text'].apply(lambda x: re.split(r'https:\/\/.*', str(x))[0])
    df['text'] = df['text'].apply(lambda x: re.split(r'http:\/\/.*', str(x))[0])
    df['text'] = df['text'].apply(lambda x: re.split(r'www:\/\/.*', str(x))[0])
    df['text'] = df['text'].apply(lambda x: re.split(r'html:\/\/.*', str(x))[0])
    df['text'] = df['text'].str.replace(r'\S*twitter.com\S*', '')
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.date
    df = df.sort_values(["date"], ascending=True)    
    return df

def by_date(data, date1, date2):
    df = pd.DataFrame()
    df = data   
    date_1 = pd.to_datetime(date1).date()
    date_2 = pd.to_datetime(date2).date()
    df['date']=pd.to_datetime(df['date'], format='%Y/%m/%d')

    df = df.sort_values(["date"], ascending=True)

    date_1 = datetime.strptime(date1, '%Y-%m-%d')
    date_2 = datetime.strptime(date2, '%Y-%m-%d')

    df = df.loc[(df['date']>date_1) & (df['date']<date_2)]
    df = df.sort_values(["date"], ascending=True)
    df.reset_index(drop=True, inplace=True)
    df['date'] = df['date'].apply(str)    
    return df

def by_date_stream_between(data, date1, date2):
    df = pd.DataFrame()
    df = data   
    date_1 = pd.to_datetime(date1).date()
    date_2 = pd.to_datetime(date2).date()
    df['date']=pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

    df = df.sort_values(["date"], ascending=True)

    date_1 = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
    date_2 = datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')

    df = df.loc[(df['date']>date_1) & (df['date']<date_2)]
    df = df.sort_values(["date"], ascending=True)
    df.reset_index(drop=True, inplace=True)
    df['date'] = df['date'].apply(str)    
    return df
def by_date_stream_before(data, date1):
    df = pd.DataFrame()
    df = data   
    date_1 = pd.to_datetime(date1).date()
    df['date']=pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

    df = df.sort_values(["date"], ascending=True)

    date_1 = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')

    df = df.loc[(df['date']<date_1)]
    df = df.sort_values(["date"], ascending=False)
    df.reset_index(drop=True, inplace=True)
    df['date'] = df['date'].apply(str)    
    return df

def by_date_stream_after(data, date1):
    df = pd.DataFrame()
    df = data   
    date_1 = pd.to_datetime(date1).date()
    df['date']=pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

    df = df.sort_values(["date"], ascending=True)

    date_1 = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')

    df = df.loc[(df['date']>date_1)]
    df = df.sort_values(["date"], ascending=True)
    df.reset_index(drop=True, inplace=True)
    df['date'] = df['date'].apply(str)    
    return df

def by_date_one(data, hour):
    df = pd.DataFrame()
    df = data   
    today = date.today()    
    hour_r = datetime.strptime(hour, '%H:%M:%S').time()
    a =str(today) + " " + str(hour_r)

    datetime_object = datetime.strptime(a, '%Y-%m-%d %H:%M:%S') 
    df['date']=pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

    df = df.sort_values(["date"], ascending=True)
    df = df.loc[(df['date']>datetime_object)]
    df = df.sort_values(["date"], ascending=True)
    df.reset_index(drop=True, inplace=True)
    df['date'] = df['date'].apply(str)

    return df


def find_no_re(data):
    df = pd.DataFrame()
    df = data   

    df = df[~df['text'].str.contains("RT", na=True)]
    return df

def find_re(data):
    df = pd.DataFrame()
    df = data   

    df = df[df['text'].str.contains("RT", na=True)]
    return df


def get_frequent_words(data):
    df = pd.DataFrame()
    df = find_no_re(data)
    df['text'] = df['text'].apply(str)

    #remove emoji
    df['text'] = df['text'].apply(remove_emoji)

    #remove links, urls, twitter.com and html
    df['text'] = df['text'].apply(lambda x: re.split(r'https:\/\/.*', str(x))[0])
    df['text'] = df['text'].apply(lambda x: re.split(r'http:\/\/.*', str(x))[0])
    df['text'] = df['text'].apply(lambda x: re.split(r'www:\/\/.*', str(x))[0])
    df['text'] = df['text'].apply(lambda x: re.split(r'html:\/\/.*', str(x))[0])
    df['text'] = df['text'].str.replace(r'\S*twitter.com\S*', '')
    df['text'] = df['text'].str.replace(r'RT', '')

    #remove everthing but characther
    df['text'] = df['text'].str.replace('[^a-zA-Z]', ' ')

    #remove words with only one characther and blank space
    df['text']= df['text'].str.replace(r'\b\w\b','').str.replace(r'\s+', ' ')

    #everthing on lowercase
    df['text']  = df['text'].str.lower()

    #remove stopwords
    df["text"] = df["text"].apply(remove_stopwords)
    df["text"] = df["text"].apply(remove_stopwords_it)
    cnt = Counter()
    for text in df["text"].values:
        for word in text.split():
            cnt[word] += 1
    cnt.most_common(10) 
    freq = set([w for (w, wc) in cnt.most_common(10)])
    return freq


def define_hour(data):
    df = pd.DataFrame()
    df = data   
    df['hour'] = pd.to_datetime(df['hour'])
    df['hour'] = df['hour'].dt.hour
    print(df['hour'])

    df['hour']=pd.to_datetime(df['hour'], format='%H')
    df['hour'] = df['hour'].dt.strftime('%H:%M:%S')
    dfx = pd.DataFrame()
    dfx = df.groupby(['hour']).size().reset_index(name='counts')    
    print(dfx)
    return dfx

def today(data):
    df = pd.DataFrame()
    df = data      
    today = date.today() 
    df['date'] = df['date'].apply(str)

    df = df[df['date'].str.contains(str(today), na=True)]
    print(df)
    return df