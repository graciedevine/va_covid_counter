import tweepy
import textwrap
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from twitter_keys import consumer_key, consumer_key_secret, access_token, access_token_secret


def request_va_data():
    """Calls API for daily COVID-19 data"""

    # Make an API call and store the response.
    url = "https://api.covidtracking.com/v1/states/va/current.json"
    response = requests.get(url)

    # Store an API response in a variable.
    response_dict = response.json()
    return response_dict


def write_tweet(data):
    """Uses daily COVID-19 data to write/format tweet"""
    
    # Convert the dates for yesterday and the day before into strings.
    yesterday = datetime.today().date() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%b %d")
    prev_day = yesterday - timedelta(days=1)
    prev_day_str = prev_day.strftime("%b %d")

    # Format the tweet.
    tweet = textwrap.dedent(f'''
        Positive Cases on {yesterday_str}: {data["positive"]:,} 
        ( +{data["positiveIncrease"]:,} from {prev_day_str})
        Hospitalized on {yesterday_str}: {data["hospitalized"]:,} ( +{data["deathIncrease"]:,} from {prev_day_str})
        Deaths on {yesterday_str}: {data['death']:,} ( +{data["hospitalizedIncrease"]:,} from {prev_day_str})
    
        Data taken from: The COVID Tracking Project
        *The COVID Tracking Project is ending all data collection on March 7, 2021.
    ''').strip()
    # Hyperlink not included because the Twitter card is huge and annoying.
    return tweet


def graph_14d_ma():
    """Calls API for historic COVID-19 data and plots 14-day moving average"""

    url = "https://api.covidtracking.com/v1/states/va/daily.json"
    r = requests.get(url)
    daily_data = r.json()

    # Convert from dict to pandas dataframe.
    daily_data = pd.DataFrame(daily_data).head(120)

    # Convert datetime to string.
    daily_data['date'] = pd.to_datetime(daily_data['date'], format='%Y%m%d')
    daily_data = daily_data.set_index("date")

    # Positive Cases and 14-day Moving Average.
    daily_data['New Positive Cases'] = daily_data['positive'].diff() * -1
    daily_data['New 14-day Moving Average'] = daily_data['New Positive Cases'].rolling(14).mean()
    daily_data[['New Positive Cases', 'New 14-day Moving Average']].plot()

    # Label the graph.
    plt.title("DAILY POSITIVE COVID-19 CASES IN VIRGINIA")
    plt.ylabel("Increase in Positive Cases from Previous Day")
    plt.xlabel("Dates (last 120 days")
    plt.savefig("graph.png")


graph_14d_ma()


def send_tweet(text):
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Create API object
    api = tweepy.API(auth)

    # Test credentials
    try:
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")
    
    # Upload image of graph to tweet
    image = api.media_upload('graph.png')
    
    # Create tweet
    api.update_status(text, media_ids=[image.media_id, ])


data = request_va_data()
tweet = write_tweet(data)
send_tweet(tweet)
