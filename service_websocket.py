#!/usr/bin/env python3

#import asyncio
#import websockets

async def handle(websocket, path):
    for i in range(20):
        msg = "{}".format(i)

        await websocket.send(msg)
        print("> {}".format(msg))

        # wait for something, anything
        received = await websocket.recv()
        print("< {}".format(received));

def run_server():
    start_server = websockets.serve(handle, 'localhost', 8000)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

run_server();