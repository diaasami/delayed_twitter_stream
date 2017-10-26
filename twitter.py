#!/usr/bin/env python3

import tweepy
import os
from time import sleep
import datetime
import sys

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

def format_geopos_for_twitter(pos):
    return "{},{}".format(pos[0], pos[1]);

def create_tweets_generator(lat, lon, delta):
    # TODO Handle timezone difference properly
    now = datetime.datetime.now();

    cut_off = now - delta;
    pos = (lat, lon)
    radius = "1km"
    radius_suffix = "," + radius

    location_search = format_geopos_for_twitter(pos) + ",1km"
    print(location_search)

    max_id = None;
    last_id = None;
    done = False;
    found = False;

    # Skip until first valid tweet
    while not found:
        print("Query with max_id={}".format(max_id))

        if (max_id):
            results = api.search( q="*", result_type="recent", max_id=max_id, geocode=location_search, count="100")
        else:
            results = api.search( q="*", result_type="recent", geocode=location_search)

        #print("{}: {}".format(name, len(results)));

        for res in results:
            #print(res.created_at)

            if (res.created_at < cut_off):
                print("Found first tweet older than 24 hours", res.created_at)
                max_id = res.id_str
                found = True;
                break;
            last_id = res.id_str

        if (not found):
            max_id = last_id

    # No valid tweets
    if (not max_id):
        return;
    print(max_id);

    # TODO hand over remaining tweets from loop #1 to loop #2 somehow to save some bandwidth and make the service faster
    #input("First tweet found, Press Enter to continue")
    skip_first = False;
    while True:
        results = api.search( q="*", result_type="recent", max_id=max_id, geocode=location_search)

        if (len(results)) == 0:
            return;

        for res in results:
            if skip_first:
                skip_first=False;
                continue
            #print(res.created_at, ":", res.text);
            yield (res.created_at, res.text)
            max_id = res.id_str
            #input("Press Enter to continue")
        skip_first = True

