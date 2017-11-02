#!/usr/bin/env python3

import tweepy
import os
import queue
from operator import attrgetter

_TWEET_BUFFER_LENGTH = 10
_RADIUS = "1km"  # Smallest radius supported by twitter

_CONSUMER_KEY = os.getenv("CONSUMER_KEY")
_CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")

_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
_ACCESS_SECRET = os.getenv("ACCESS_SECRET")

_auth = tweepy.OAuthHandler(_CONSUMER_KEY, _CONSUMER_SECRET)
_auth.set_access_token(_ACCESS_TOKEN, _ACCESS_SECRET)

_api = tweepy.API(_auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def _format_geopos_for_twitter(pos):
    return "{},{}".format(pos[0], pos[1]);


def _get_tweets_stream(loc_condition, ids):
    while True:
        batch_ids = []

        for i in range(_TWEET_BUFFER_LENGTH):
            try:
                batch_ids += [ids.get_nowait()]
            except queue.Empty:
                break;

        if (len(batch_ids) == 0):
            break;

        # Get tweet information
        results = _api.statuses_lookup(id_=batch_ids)
        for res in sorted(results, key=attrgetter("created_at")):
            yield res

    return;


def create_tweets_generator(lat, lon, cut_off):
    ids = queue.LifoQueue()
    loc_condition = _format_geopos_for_twitter((lat, lon)) + "," + _RADIUS

    # Skip until first valid tweet
    print("Issuing search query")

    results = tweepy.Cursor(_api.search, q="*", result_type="recent", geocode=loc_condition).items()

    for res in results:
        print(res.id_str, res.created_at, res.text)
        ids.put_nowait(res.id_str)

        if (res.created_at < cut_off):
            print("Found first tweet older than {}".format(cut_off), res.created_at)
            yield res
            break;

    print("Storing IDs of {} tweets".format(ids.qsize()));

    for tweet in _get_tweets_stream(loc_condition, ids):
        yield tweet
