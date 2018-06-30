import sys
import csv
from lxml import etree

MAX_DATE = 1510684200000
MIN_DATE = 1509647400000


class Event(object):
    def __init__(self, activity, timestamp, tweet_id=0, user_id=0, user_title=None):
        self.activity = activity
        self.timestamp = timestamp
        self.tweet_id = tweet_id
        self.user_id = user_id
        self.user_title = user_title

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.activity == other.activity and self.tweet_id == other.tweet_id and self.user_id == other.user_id
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.activity, self.tweet_id, self.user_id))


def get_html(filename):
    with open(filename, 'rb') as file:
        data = file.read()
    return data.decode('utf-8').replace('\n', '').replace('\r', '').lower()


def parse(html):
    with open('out2.txt', 'w', encoding='utf-8') as file:
        events = []
        tree = etree.HTML(html)
        list = tree.xpath('//*[@id="stream-items-id"]')[0]
        for item in reversed(list):
            activity = item.get('class').split()[-1]
            print("\nACTIVITY: {}".format(activity))
            file.write("\n\nACTIVITY: {}".format(activity))

            if activity in ['js-activity-generic']:
                continue
            if activity in ['js-activity-mention', 'js-activity-reply', 'js-activity-media_tagged', 'js-activity-quote']:
                timestamp = int(item.xpath('.//div/div[2]/div[1]/small/a/span[1]')[0].get('data-time-ms'))
            else:
                timestamp = int(item.xpath('.//div/div/div/div[2]/div[1]/div/div/span[1]')[0].get('data-time-ms'))
            print("Time: {}".format(timestamp))
            file.write("\nTime: {}".format(timestamp))

            if timestamp > MAX_DATE or timestamp < MIN_DATE:
                continue

            tweet_id = 0
            item_object = item.xpath('.//div/div/div/div[2]/div[2]/div/div/a')
            if item_object:
                tweet = item_object[0]
                tweet_id = tweet.get('data-conversation-id')
                print("Tweet Id: {}".format(tweet_id))
                file.write("\nTweet Id: {}".format(tweet_id))

            # if tweet_id in ['922505564067729408', '922506920774139904']:
            #     continue

            user_list = item.xpath('.//div/div/div/div[2]/ol[1]/li/a')
            if user_list:
                print("{} users".format(len(user_list)))
                for user in user_list:
                    user_id = user.get('data-user-id')
                    user_title = user.get('original-title')
                    print("{} {}".format(user_id, user_title.encode('utf-8')))
                    file.write("\n{} {}".format(user_id, user_title.encode('utf-8')))
                    event = Event(activity, timestamp, tweet_id, user_id, user_title)
                    events.append(event)
                user_count = item.xpath('.//div/div/div/div[2]/div[1]/span')
                if user_count:
                    if user_count[0].get('class') == 'count-wrap':
                        total_count = int(user_count[0].text) + 1
                        print("{} total users".format(total_count))
                        file.write("\n{} total users".format(total_count))
                        if total_count > len(user_list):
                            missed_count = total_count - len(user_list)
                            print("{} USERS MISSED OUT for {} with {}".format(missed_count, activity, tweet_id))
                            file.write("\n{} USERS MISSED OUT for {} with {}".format(missed_count, activity, tweet_id))
            else:
                event = Event(activity, timestamp, tweet_id)
                events.append(event)

        print("\n{} notifications".format(len(list)))
        file.write("\n\n{} notifications".format(len(list)))

        print("{} total events".format(len(events)))
        file.write("\n{} total events".format(len(events)))

        # unique_list = []
        # for event in events:
        #     if event not in unique_list:
        #         unique_list.append(event)
        # print(len(unique_list))

        unique_events = set(events)
        print("{} unique events".format(len(unique_events)))
        file.write("\n{} unique events".format(len(unique_events)))

        return unique_events


def write_events(events):
    with open('events.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['event', 'time', 'tweet id', 'user id', 'screen name'])
        for event in events:
            writer.writerow([event.activity, event.timestamp, event.tweet_id, event.user_id, event.user_title])


if __name__ == "__main__":
    filename = sys.argv[1]
    html = get_html(filename)
    events = parse(html)
    write_events(events)
