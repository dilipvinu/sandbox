"""
    This script is written to do sentimental analysis on mandarin tweets,
    this uses TextBlob to translate and gauge the sentiment.
    Author: Farhaan Bukhsh <farhaan.bukhsh@clootrack.com>
"""
import argparse
import csv

import textblob
from textblob import TextBlob


def predict_sentiments(text):
    try:
        blob = TextBlob(text).translate(to="en")
    except textblob.exceptions.NotTranslated:
        blob = TextBlob(text)

    if blob.sentiment.polarity > 0.4:
        return "Positive", blob.sentiment.polarity
    elif blob.sentiment.polarity < -0.63:
        return "Negative", blob.sentiment.polarity
    else:
        return "Neutral", blob.sentiment.polarity


def read_posts(input_file):
    with open(input_file, 'r') as datafile:
        reader = csv.reader(datafile)
        header = next(reader)
        posts = [row for row in reader]
    return header, posts


def calculate_sentiment_score(posts):
    for index, data in enumerate(posts):
        post_content = data[7]
        print("Row number:" + str(index) + "\n" + post_content)
        sentiment, polarity = predict_sentiments(post_content)
        data.extend([sentiment, polarity])


def write_to_file(file_name, header, rows):
    with open(file_name, 'w') as outfile:
        writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def write_sentiment_output(file_name, header, posts):
    header = header + ['sentiment', 'polarity score']
    write_to_file(file_name, header, posts)


def overwrite_posts_with_sentiment(file_name, header, posts):
    # Remove last 2 column data. sentiment type and scores
    # and set sentiment type
    for post in posts:
        sentiment = post[-2]
        del post[-2:]
        post[8] = sentiment
    file_name = file_name.replace(".csv", "") + "_sentiment_type.csv"
    write_to_file(file_name, header, posts)


def csv_read_write(input_file, output_file):
    header, posts = read_posts(input_file)
    calculate_sentiment_score(posts)
    write_sentiment_output(output_file, header, posts)
    overwrite_posts_with_sentiment(input_file, header, posts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputFile', help='Input csv file which has tweets')
    parser.add_argument(
        '--outputFile', help='Output file csv that has sentiments and polarity')
    args = parser.parse_args()
    csv_read_write(input_file=args.inputFile, output_file=args.outputFile)
