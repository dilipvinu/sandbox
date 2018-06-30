import tweepy


def get_auth(consumer_key, consumer_secret, access_token, access_token_secret):
    # User level
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    return auth


def get_tweepy_api_app_level(consumer_key, consumer_secret, access_token, access_token_secret):
    # APP level
    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    tweepy_api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return tweepy_api


def get_tweepy_api_user_level(consumer_key, consumer_secret, access_token, access_token_secret):
    # user level
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    tweepy_api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return tweepy_api


def get_tweepy_api1():
    consumer_key = 'XiXHrBCRXxw29YoIoK0rCXFh1'
    consumer_secret = 'ig9rjkyou8Ygmp0dNjPlrU0DSdH9rKI5RgkXaxduJUFauGB0Ys'

    access_token = "884714902325043200-VnTNxeBHEcbSONdM2lPP4Yt9jHOpGAn"
    access_token_secret = "IwQpiJKtbmRroznYDjHPXMhXou5Oa92RSmmqqciDoNHPk"

    return get_tweepy_api_user_level(consumer_key, consumer_secret, access_token, access_token_secret)
