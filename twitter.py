#!/usr/bin/env python3

import tweepy
import os
from time import sleep

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

def format_geopos_for_twitter(pos):
    return "{},{}".format(pos[0], pos[1]);

#washington_dc_geopos=(38.883333, -77);
#london_geopos=(51.5, -0.083333);
#cairo_geopos=(30.05, 31.25);
#berlin_geopos=(52.51666667, 13.4);
trendinaliaDE_geopos=(52.338079,13.088304);
freedomBdj_geopos=(52.5006,13.3989);
#ottawa_geopos=(45.41666667,-75.7);

for name, pos in [(k, v) for k, v in locals().items() if k.endswith("_geopos")]:

    results = api.search(q=" ", result_type="recent", geocode=format_geopos_for_twitter(pos) + ",1km")

    print("{}: {}".format(name, len(results)));

    for res in results:
        print(res);

    sleep(5)