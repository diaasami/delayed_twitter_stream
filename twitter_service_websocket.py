import asyncio
import websockets
from urllib.parse import urlparse, parse_qs
import os, sys
from datetime import timedelta

sys.path.append(os.path.dirname(__file__))

import twitter

mandatory_parameters = ("lat", "lon")

async def handle_request(websocket, path):
    url_components = urlparse(path);

    if (not url_components.path== "/"):
        print("Invalid path: {}".format(url_components.path));
        return

    params = parse_qs(url_components.query);

    try:
        lat, lon = params[mandatory_parameters[0]][0], params[mandatory_parameters[1]][0]

        lat, lon = float(lat), float(lon)
    except (ValueError, KeyError) as e:
        print("Invalid parameters");
        print("Parameters ({}) are required".format(", ".join(mandatory_parameters)));
        return

    for tweet in twitter.create_tweets_generator(lat, lon, timedelta(days=1)):
        msg = "{}".format(tweet)
        await websocket.send(msg)
        print("> {}".format(msg))

        # wait for something, anything
        received = await websocket.recv()
        print("< {}".format(received));

def run_server():
    start_server = websockets.serve(handle_request, '0.0.0.0', 8080)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

run_server();
