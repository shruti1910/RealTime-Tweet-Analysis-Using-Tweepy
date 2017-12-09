
# coding: utf-8

# # Real-time Twitter Sentiment Analysis

# ### Import modules
# - tweepy: Twitter Python API
# - textblob: Text and Sentiment Analysis

# In[ ]:


import tweepy
from textblob import TextBlob
import sys
import re
import pickle


# ### Twitter Authenetication

# In[ ]:


consumer_key = 'Shm6Jmp3gDX706ZGIpjhdvYer'
consumer_secret = 'Zr2Ui2mg3AaSEDiaCDNctDvKDnpDrOT7BsbyldnOQxRtzVKvjK'
access_token = '937385084126085121-K8VoGlQ7y6KeW6j6Tl3JMfzRKJGOviB'
access_token_secret = '2pPtxYEdbgCWBz6HKeJ1tyQ0yZN9xlVp3AmUVGz5y4kQ8'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


# ### Tweepy Basics

# In[ ]:


user = api.me()

print user.name


# ### Sentiment Analysis using textblob
# 
# ```
# text = "This would be nice, don't you think ?"
# 
# analysis = TextBlob(text)
# > print analysis.sentiment
# Sentiment(polarity=0.6, subjectivity=1.0)```
# 
# ```
# > print analysis.sentiment.polarity
# 0.6```

# In[ ]:


print TextBlob('This has been a wonderful day !').sentiment.polarity
print TextBlob('My phone broke yesterday.').sentiment.polarity
print TextBlob('Pizza from that place are awfully bad').sentiment.polarity


# ### Twitter Analyser
# 
# call NTLK library using:
# ``` analysis = TextBlob(text)
# analysis.sentiment.polarity is the score in the range [-1,-1]```

# In[ ]:


class TweetAnalyser(object):
    def __init__(self):
        pass
    
    def clean_tweet(self, tweet):
        # reference: https://dev.to/rodolfoferro/sentiment-analysis-on-trumpss-tweets-using-python-
        tweet = tweet.text
        cleaned_tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
        cleaned_tweet = cleaned_tweet.encode('utf-8')
        return cleaned_tweet

    def get_sentiment_score(self, tweet):
        text = self.clean_tweet(tweet)
        analysis = TextBlob(text)
        return round(analysis.sentiment.polarity, 3)


# # Streaming Twitter Data

# ### Tweepy Search Tweets
# 
# ---
# #### Sample data for a tweet:
# ```
# created_at: 2017-12-09 03:45:24
# geo: None
# id: 939340175846625280
# lang: en
# place: None
# text: @Garurusama Take out payday loans and use them to buy bitcoin
# ```
# 
# 
# ---
# ### Search for tweets on a particular topic
# ```tweets = tweepy.Cursor(api.search, q='Bitcoin', lang='en').items(max_count)```
# 
# 
# ```API.search(q[, lang][, locale][, rpp][, page][, since_id][, geocode][, show_user])```
# 
# Returns tweets that match a specified query.
# 
# ---
# #### Parameters:	
# - `q` – the search query string
# - `lang` – Restricts tweets to the given language, given by an ISO 639-1 code.
# - `locale` – Specify the language of the query you are sending. This is intended for language-specific clients and the default should work in the majority of cases.
# - `rpp` – The number of tweets to return per page, up to a max of 100.
# - `page` – The page number (starting at 1) to return, up to a max of roughly 1500 results (based on rpp * page.
# - `since_id` – Returns only statuses with an ID greater than (that is, more recent than) the specified ID.
# - `geocode` – Returns tweets by users located within a given radius of the given latitude/longitude. The location is preferentially taking from the Geotagging API, but will fall back to their Twitter profile. The parameter value is specified by “latitide,longitude,radius”, where radius units must be specified as either “mi” (miles) or “km” (kilometers). Note that you cannot use the near operator via the API to geocode arbitrary locations; however you can use this geocode parameter to search near geocodes directly.
# - `show_user` – When true, prepends “<user>:” to the beginning of the tweet. This is useful for readers that do not display Atom’s author field. The default is false.
# ```
# 

# In[ ]:


max_count = 1
tweets = tweepy.Cursor(api.search, q='Bitcoin', lang='en').items(max_count)

for data in tweets:
    print 'created_at:', data.created_at
    print 'geo:', data.geo
    print 'id:', data.id
    print 'lang:', data.lang
    print 'place:', data.place
    print 'text:', data.text


# ### Stream Listener

# In[ ]:


GEOBOX_WORLD = [-180,-90,180,90]

class CustomListener(tweepy.StreamListener):
    MAX_COUNT = 1000
    
    def __init__(self, api):
        self.api = api
        self.num_tweets = 0
        self.tweet_analyzer = TweetAnalyser()
        
        self.results = []

    def on_status(self, tweet):
        data = {} # initialize empty dictionary
        
        # consider tweets only if they have geo locations
        if tweet.coordinates is not None:
            data['text'] = tweet.text
            data['coordinates'] = tweet.coordinates['coordinates'] # add coordinate to date
            data['score'] = self.tweet_analyzer.get_sentiment_score(tweet)
            
            self.num_tweets += 1
            if self.num_tweets > self.MAX_COUNT:
                return False

            print data['text']
            print data['coordinates']
            self.results.append(data)            

    # error handling
    def on_error(self, status):
        print >> sys.stderr, 'Error: ', status
        return True
    
    # error handling
    def on_timeout(self):
        print >> sys.stderr, 'Stream timeout'
        return True


# ### Start Twitter Streaming

# In[ ]:


GEOBOX_WORLD = [-180,-90,180,90]
GEOBOX_UNITED_STATES = [120,50,70,30]

US_LEFT = -124.804
US_RIGHT = -83.58
US_TOP = 47.541
US_BOTTOM = 31.608
SOUTH_WEST = [US_BOTTOM, US_BOTTOM]
NORTH_EAST = [US_RIGHT, US_TOP]

GEOBOX_UNITED_STATES = SOUTH_WEST + NORTH_EAST

customer_listener = CustomListener(api)
listener = tweepy.Stream(auth, customer_listener)
# listener.filter(locations=GEOBOX_WORLD, track=['Donald Trump'])
listener.filter(locations=GEOBOX_WORLD)

print 'starting...'
print customer_listener.results
print 'completed !'


# ### Pickle Results for processing
# #### Use Pickle to store data offline

# #### Load data from pickled object

# In[ ]:


bitcoin_data = pickle.load(open('bitcoin_data.pickle', 'rb'))


# ## Folium Maps
# 
# Folium makes it easy to visualize data that’s been manipulated in Python on an interactive `Leaflet` map. It enables both the binding of data to a map for choropleth visualizations as well as passing `Vincent/Vega visualizations` as markers on the map.
# 
# The library has a number of built-in tilesets from `OpenStreetMap`, `Mapbox`, and `Stamen`, and supports custom tilesets with Mapbox or Cloudmade API keys. Folium supports both `GeoJSON` and `TopoJSON` overlays, as well as the binding of data to those overlays to create choropleth maps with color-brewer color schemes.
# 
# ```Documentation: http://folium.readthedocs.io/en/latest/quickstart.html```

# In[142]:


import folium

m = folium.Map(location=[38, -102], zoom_start=4)
m


# ### Add locations to the map
# 
# We start by creating an instance of `folium.Map` object, specifying `centre` of the map as [latitude, longiture], followed by `zoom`
# 
# ```
# folium.Marker([45.3288, -121.6625], 
#               popup='Mt. Hood Meadows', 
#               icon=folium.Icon(color='green')).add_to(m)
# first param : list of [latitude, longitude]
# second param: @popup tool_tip name (set to the tweet text)
# third param : icon color
# ```

# In[143]:


m = folium.Map(location=[38, -102], 
               tiles='Mapbox Bright', 
               zoom_start=4)

folium.Marker([45.3288, -121.6625], 
              popup='Hello there from Oregon !', 
              icon=folium.Icon(color='green')).add_to(m)
folium.Marker([47.3288, -115.6625], 
              popup='Its too cold out here !!', 
              icon=folium.Icon(color='blue')).add_to(m)
folium.Marker([40.3288, -90.6625], 
              popup='Chicago, here I come :)', 
              icon=folium.Icon(color='red')).add_to(m)
m


# In[147]:


m = folium.Map(location=[38, -102], zoom_start=4)

bitcoin_data = pickle.load(open('bitcoin_data.pickle', 'rb'))

# get a sample from the data to put them on map
sample_list = []
sample_size = 10
from random import randint
for _ in range(sample_size):
    index = randint(0, len(bitcoin_data))
    sample_list.append(bitcoin_data[index])

# plot the locations on the map, with color coded sentiments, 
# and tweet's text as the popup
for data in sample_list:
    
    score = data['score']
    if score < 0:
        color = 'red'
    elif score > 0:
        color = 'green'
    else:
        color = 'blue'
    
    folium.Marker(data['location'], 
              popup=data['text'], 
              icon=folium.Icon(color=color)).add_to(m)
#     print data['location']
    
m


# ## References
# ---
# #### Tweepy
#     - `github`: https://github.com/tweepy/tweepy
#     - `searchAPI`: http://docs.tweepy.org/en/v3.5.0/api.html#API.search
#     - `me`: http://docs.tweepy.org/en/v3.5.0/api.html#API.me
#     - `streaming code`: https://github.com/tweepy/tweepy/blob/master/tweepy/streaming.py
#     - `StreamListener`: https://github.com/tweepy/tweepy/blob/master/tweepy/streaming.py#L31
#     - `filter`: https://github.com/tweepy/tweepy/blob/master/tweepy/streaming.py#L31
#     - `on_status`: https://github.com/tweepy/tweepy/blob/master/tweepy/streaming.py#L45
# 
# ---
# #### TextBlob 
#     - http://textblob.readthedocs.io/en/dev/
# 
# ---
# #### Folium
#     - Github: https://github.com/python-visualization/folium
#     - Documentation: http://python-visualization.github.io/folium/
# ---
# #### Pickle
#     - Documentation: https://docs.python.org/2/library/pickle.html
