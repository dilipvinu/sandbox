import json
import tweepy_config


tweepy_api = tweepy_config.get_tweepy_api1()
list_id = "964111598108356608"
# status = tweepy_api.get_status(id=960896296264650752, tweet_mode="extended")
# status = tweepy_api.create_list(name="test-list", mode="private")
list_members = ["BBCWorld", "SkyNews", "CNN", "ABC", "NBCNews", "BBCNews", "Reuters", "abcnews", "FoxNews",
                "BBCBreaking", "CBSNews", "googlenews"]
# status = tweepy_api.add_list_members(list_id=list_id, screen_name=list_members)
should_page = True
max_id = None
count = 0
while should_page:
    kwargs = {
        "list_id": list_id,
        "include_rts": False,
        "count": 200
    }
    if max_id:
        kwargs["max_id"] = max_id
    results = tweepy_api.list_timeline(**kwargs)
    if results:
        last_status = results[-1]
        last_status_id = last_status.id
        max_id = str(last_status_id - 1)
        print(last_status.created_at)
    count += len(results)
    print("Fetched {} tweets".format(count))
    should_page = len(results) > 0
