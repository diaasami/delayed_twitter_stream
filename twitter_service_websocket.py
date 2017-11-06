#!/usr/bin/env python3

import asyncio
import websockets
from urllib.parse import urlparse, parse_qs
import os, sys
from datetime import timedelta, datetime
from time import sleep
import json

sys.path.append(os.path.dirname(__file__))

import twitter

mandatory_parameters = ("lat", "lon")


async def handle_request(websocket, path):
    url_components = urlparse(path);

    if (not url_components.path == "/"):
        error = "Invalid path: {}".format(url_components.path);
        await websocket.send(error);
        print(error);
        return

    params = parse_qs(url_components.query);

    try:
        lat, lon = params[mandatory_parameters[0]][0], params[mandatory_parameters[1]][0]

        lat, lon = float(lat), float(lon)
    except (ValueError, KeyError) as e:
        error = "Floating-point parameters ({}) are required".format(", ".join(mandatory_parameters))
        print(error);
        await websocket.send(error);
        return

    sleep_period = 5  # in seconds
    delta = timedelta(days=1)


    while True:
        # TODO Make sure timezone timezone difference is handled properly
        cut_off = datetime.utcnow() - delta;
        for tweet in twitter.create_tweets_generator(lat, lon, cut_off):
            print("Next tweet", (tweet.id_str, tweet.created_at, tweet.text))
            while True:
                time_remaining = tweet.created_at - (datetime.utcnow() - delta)
                time_remaining = int(time_remaining.total_seconds())
                # Skip tweet
                if (time_remaining < 0):
                    break;
                elif (time_remaining == 0):
                    await websocket.send(json.dumps({'created_at': str(tweet.created_at),
                                                     'id_str': tweet.id_str,
                                                     'text': tweet.text}))
                    print("> {}".format((tweet.created_at, tweet.id_str, tweet.text)).encode("utf-8"))
                    break;
                elif (time_remaining > sleep_period):
                    print("Sleeping 5, time_remaining: {}".format(time_remaining))
                    await asyncio.sleep(sleep_period)
                    websocket.ping()

def run_server():
    start_server = websockets.serve(handle_request, '0.0.0.0', 8080)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


run_server();
