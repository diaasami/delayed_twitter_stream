import asyncio
import websockets
from urllib.parse import urlparse, parse_qs
import os, sys
from datetime import timedelta, datetime
from time import sleep

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

    for tweet in twitter.create_tweets_generator(lat, lon, timedelta(days=1)):
        #print((tweet.created_at, tweet.text))
        while True:
            time_remaining = tweet.created_at - (datetime.now() - delta)
            time_remaining = time_remaining.total_seconds()
            # Skip tweet
            if (time_remaining < 0):
                break;
            elif (time_remaining == 0):
                msg = "{}".format(tweet)
                await websocket.send(msg)
                print("> {}".format(msg).encode("utf-8"))
                break;
            elif (time_remaining > sleep_period):
                print("Sleeping 5")
                sleep(sleep_period)
                websocket.ping()
            else:
                sleep(1)

def run_server():
    start_server = websockets.serve(handle_request, '0.0.0.0', 8080)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


run_server();
