#!/usr/bin/env python3

import tweepy
import os
import datetime
import itertools

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def _skip_first_element(iterable):
    return itertools.islice(iterable, 1, None);


def _format_geopos_for_twitter(pos):
    return "{},{}".format(pos[0], pos[1]);


def _get_tweets_stream(starting_since_id, loc_condition):
    since_id = starting_since_id

    while True:
        # new search request
        print("New search request(since_id:{})".format(since_id))
        results = api.search(q="*", result_type="recent", since_id=since_id, geocode=loc_condition, count=10)

        for res in _skip_first_element(results):
            yield res
            since_id = res.id_str

    return;


def create_tweets_generator(lat, lon, delta):
    # TODO Make sure timezone timezone difference is handled properly
    now = datetime.datetime.now();

    cut_off = now - delta;
    pos = (lat, lon)
    radius = "1km"  # Smallest radius supported by twitter
    loc_condition = _format_geopos_for_twitter(pos) + "," + radius

    max_id = None;
    last_id = None;
    found = False;

    # Skip until first valid tweet
    while not found:
        print("Query with max_id={}".format(max_id))

        if (max_id):
            results = api.search(q="*", result_type="recent", max_id=max_id,
                                 geocode=loc_condition, count="100")
        else:
            results = api.search(q="*", result_type="recent", geocode=loc_condition)


        for res in results:
            #print(res.id_str, res.created_at, res.text)

            if (res.created_at < cut_off):
                print("Found first tweet older than 24 hours", res.created_at)
                max_id = res.id_str
                found = True;
                yield res
                break;
            last_id = res.id_str

        if (not found):
            max_id = last_id

    # No valid tweets
    if (not max_id):
        return;
    print(max_id);

    # TODO hand over remaining tweets from loop #1 to loop #2 to save bandwidth and make the service faster
    for tweet in _get_tweets_stream(max_id, loc_condition):
        yield tweet
