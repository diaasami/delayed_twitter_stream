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

#washington_dc_geopos=(38.883333, -77);
#london_geopos=(51.5, -0.083333);
#cairo_geopos=(30.05, 31.25);
#berlin_geopos=(52.51666667, 13.4);
#trendinaliaDE_geopos=(52.338079,13.088304);
freedomBdj_geopos=(52.5006,13.3989);
#ottawa_geopos=(45.41666667,-75.7);

delta = datetime.timedelta(days=1)
now = datetime.datetime.now();

cut_off = now - delta;

max_id = None;
last_id = None;
done = False;
found = False;

#Skip until first valid tweet

while not found:
    for name, pos in [(k, v) for k, v in locals().items() if k.endswith("_geopos")]:
        print("Query with max_id={}".format(max_id))

        if (max_id):
            results = api.search( q="*", result_type="recent", max_id = max_id, geocode=format_geopos_for_twitter(pos) + ",1km", count="100")
        else:
            results = api.search( q="*", result_type="recent", geocode=format_geopos_for_twitter(pos) + ",1km")

        print("{}: {}".format(name, len(results)));

        for res in results:
            #print(res);
            print(res.created_at)

            if (res.created_at < cut_off):
                print("Found first tweet older than 24 hours", res.created_at)
                max_id = res.id_str
                found = True;
                break;
            last_id = res.id_str

        sys.stdout.flush();
        sleep(5)

    if (not found):
        max_id = last_id

print(max_id);

input("First tweet found, Press Enter to continue")
while True:
    results = api.search( q="*", result_type="recent", max_id = max_id, geocode=format_geopos_for_twitter(pos) + ",1km", count="10")

    if (len(results)) == 0:
        break;

    for res in results:
        print(res.created_at, ":", res.text);
        max_id = res.id_str
        sys.stdout.flush();
        input("Press Enter to continue")