#!/usr/bin/env python3

import tweepy
import os
import datetime
import itertools
import queue

_CONSUMER_KEY = os.getenv("CONSUMER_KEY")
_CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")

_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
_ACCESS_SECRET = os.getenv("ACCESS_SECRET")

_auth = tweepy.OAuthHandler(_CONSUMER_KEY, _CONSUMER_SECRET)
_auth.set_access_token(_ACCESS_TOKEN, _ACCESS_SECRET)

_api = tweepy.API(_auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

_TWEET_BUFFER_LENGTH=10

def _format_geopos_for_twitter(pos):
    return "{},{}".format(pos[0], pos[1]);


def _get_tweets_stream(starting_since_id, loc_condition, ids):
    while True:
        batch_ids = []

        for i in range(_TWEET_BUFFER_LENGTH):
            try:
                batch_ids += [ids.get_nowait()]
            except queue.Empty:
                break;

        tweets = []
        results = _api.statuses_lookup(id_=batch_ids)
        print(batch_ids)
        print([r.created_at for r in results])
        for res in results:
            yield res

    return;


def create_tweets_generator(lat, lon, delta):
    # TODO Make sure timezone timezone difference is handled properly
    now = datetime.datetime.now();

    ids = queue.LifoQueue()

    cut_off = now - delta;
    pos = (lat, lon)
    radius = "10km"  # Smallest radius supported by twitter
    loc_condition = _format_geopos_for_twitter(pos) + "," + radius

    max_id = None;
    last_id = None;
    found = False;

    # Skip until first valid tweet
    while not found:
        print("Query with max_id={}".format(max_id))

        results = tweepy.Cursor(_api.search, q="*", result_type="recent", geocode=loc_condition).items()

        temp = []
        for res in filter(lambda x: not x.in_reply_to_status_id_str, results):
            #print(res.in_reply_to_status_id_str)
            print(res.id_str, res.created_at, res.text)
            ids.put_nowait(res.id_str)
            temp += [res.id_str]

            if (res.created_at < cut_off):
                print("Found first tweet older than {}".format(delta), res.created_at)
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
    print("Storing IDs of {} tweets".format(ids.qsize()));
    print("Only {} unique ids".format(len(set(temp))));
    print(max_id);

    # TODO hand over remaining tweets from loop #1 to loop #2 to save bandwidth and make the service faster
    for tweet in _get_tweets_stream(max_id, loc_condition, ids):
        yield tweet
