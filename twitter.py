from rauth import OAuth1Service

TWITTER_CONSUMER_KEY = 'qQIHu3dQ43VnGxrL8d7h1dRru'
TWITTER_CONSUMER_SECRET = 'IVT34lGmab46ivKLuAC4dPOsaQm9RJ24QDUz4G1ypxVtLtirDf'
TWITTER_ACCESS_TOKEN = '619775841-XMMQFXknZphmKRz7unESrSVqXOA5qwcjQRe6MD05'
TWITTER_ACCESS_TOKEN_SECRET = 'IrwR3UXAAHSYAYETRLAUNZ3voBP4e2pYf87qRu5VXEVBy'
TWITTER_BASE_URL = 'https://api.twitter.com/1.1/'

tweet_ids = ['875078490529419267', '875077236034068483']

twitter_client = OAuth1Service(name='twitter',
                               consumer_key=TWITTER_CONSUMER_KEY,
                               consumer_secret=TWITTER_CONSUMER_SECRET,
                               base_url=TWITTER_BASE_URL)

twitter_session = twitter_client.get_session((TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET))
url = '{}statuses/lookup.json'.format(TWITTER_BASE_URL)

response = twitter_session.get(url, params={'id': ','.join(tweet_ids)})
tweets = response.json()
print(len(tweets), 'tweets')
for tweet in tweets:
    print(tweet['id_str'], tweet['text'])
