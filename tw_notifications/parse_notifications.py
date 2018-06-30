import sys
import html2text
from bs4 import BeautifulSoup

old_date_range = ["nov 2", "nov 1", "oct 31", "oct 30", "oct 29", "oct 28", "oct 27", "oct 26", "oct 25",
                  "oct 24", "oct 23"]


def get_html(filename):
    with open(filename, 'rb') as file:
        data = file.read()
    return data.decode('utf-8').replace('\n', '').replace('\r', '').lower()


def write_text(filename, text):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)


def get_section(content, index):
    pattern = " {}.     1.".format(index)
    beg = content.find(pattern)
    if beg == -1:
        pattern = " {}. [".format(index)
        beg = content.find(pattern)
        if beg == -1:
            return "", -1

    index += 1
    pattern = " {}.     1.".format(index)
    end = content.find(pattern, beg)
    if end != -1:
        return content[beg:end], index

    pattern = " {}. [".format(index)
    end = content.find(pattern, beg)
    if end != -1:
        return content[beg:end], index

    return content[beg:], -1


def generate_patterns(seed):
    patterns = [
        seed + " your tweet",
        seed + " your\ntweet",
        seed + "\nyour tweet",
        seed + " your retweet",
        seed + " your\nretweet",
        seed + "\nyour retweet",
        seed + " your reply",
        seed + " your\nreply",
        seed + "\nyour reply",
        seed + " your replies",
        seed + " your\nreplies",
        seed + "\nyour replies"
    ]
    return patterns


def match_pattern(section, patterns):
    for pattern in patterns:
        if pattern in section:
            pos = section.find(pattern)
            return pattern, pos
    return '', -1


def get_count(section, action, patterns=True):
    count = 0
    if patterns:
        action_patterns = generate_patterns(action)
        action_pattern, pos = match_pattern(section, action_patterns)
    else:
        action_pattern = None
        pos = section.find(action)
        if pos != -1:
            action_pattern = action
    if action_pattern:
        pos -= 1
        count = 1
        sub_pos = section.rfind("others", 0, pos)
        if sub_pos != -1 and pos - sub_pos == 6:
            num_pos = section.rfind(" ", 0, sub_pos - 1)
            count += int(section[num_pos:sub_pos - 1])
        else:
            sub_pos = section.rfind(" ", 0, pos)
            if sub_pos > 4:
                if section[sub_pos - 3:sub_pos] == "and":
                    count += 1
                    sub_pos = section.rfind(" ", 0, sub_pos - 4)
                    if sub_pos > 4:
                        if section[sub_pos - 1:sub_pos] == ",":
                            count += 1
    return count


def parse_section(section):
    likes = get_count(section, "liked")
    retweets = get_count(section, "retweeted")
    follows = get_count(section, "followed you", patterns=False)
    mentions = 0
    if "replying to" in section:
        if "add to new moment" in section:
            mentions = 1
    return likes, retweets, mentions, follows


def analyze_content(content):
    new_likes = 0
    new_retweets = 0
    new_mentions = 0
    new_follows = 0
    old_likes = 0
    old_retweets = 0
    old_mentions = 0
    old_follows = 0
    index = 1
    while index != -1:
        section, index = get_section(content, index)
        likes, retweets, mentions, follows = parse_section(section)
        if any(date in section for date in old_date_range):
            old_likes += likes
            old_retweets += retweets
            old_mentions += mentions
            old_follows += follows
        else:
            new_likes += likes
            new_retweets += retweets
            new_mentions += mentions
            new_follows += follows
    print("{} new likes".format(new_likes))
    print("{} new retweets".format(new_retweets))
    print("{} new mentions".format(new_mentions))
    print("{} new follows".format(new_follows))
    print("{} old likes".format(old_likes))
    print("{} old retweets".format(old_retweets))
    print("{} old mentions".format(old_mentions))
    print("{} old follows".format(old_follows))


if __name__ == "__main__":
    filename = sys.argv[1]
    html = get_html(filename)
    text = html2text.html2text(html)
    # text = BeautifulSoup(html, 'html.parser').text
    write_text('out.txt', text)
    analyze_content(text)
