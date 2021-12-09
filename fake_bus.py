import json
import os
from contextlib import suppress
from itertools import islice
from random import choice, randrange, sample
from urllib.parse import urlunsplit

import trio
from trio_websocket import open_websocket_url

from utils import parse_bus_args, relaunch_on_disconnect, set_logging


async def load_routes(routedir, num_routes=0):
    routes = os.listdir(routedir)
    for name in sample(routes, num_routes):
        if name.endswith(".json"):
            with open(os.path.join(routedir, name)) as file:
                yield json.load(file)
                await trio.sleep(0)


@relaunch_on_disconnect
async def send_updates(server_url, channel):
    async with open_websocket_url(server_url) as ws:
        async for bus_info in channel:
            await ws.send_message(json.dumps(bus_info, ensure_ascii=False))


async def transpond(path, start, delay):
    points = islice(path, start, None)
    while True:
        try:
            yield next(points)
        except StopIteration:
            points = iter(path)
        else:
            await trio.sleep(delay)


async def run_bus(route, channel):
    path = route["coordinates"]
    start = randrange(0, len(path))
    bus_id = f"{args.emid}-{route['name']}-{start}"
    async for lat, long in transpond(path, start, args.delay):
        message = {
            "busId": bus_id,
            "lat": lat,
            "lng": long,
            "route": route["name"],
        }
        await channel.send(message)


async def spawn_buses(hub, channels):
    async for route in load_routes(args.routes, args.routnum):
        for _ in range(args.enroute):
            hub.start_soon(run_bus, route, choice(channels).clone())


async def main():
    server_url = urlunsplit(("ws", f"{args.host}:{args.listen}", "", "", ""))
    channel_pool = [trio.open_memory_channel(0) for _ in range(args.wsnum)]
    send_channels, receive_channels = zip(*channel_pool)
    try:
        async with trio.open_nursery() as hub:
            hub.start_soon(spawn_buses, hub, send_channels)
            for channel in receive_channels:
                hub.start_soon(send_updates, server_url, channel)

    except (FileNotFoundError, OSError, ValueError) as err:
        logger.error(err)


if __name__ == "__main__":
    args = parse_bus_args()
    logger = set_logging(args.verbosity)
    with suppress(KeyboardInterrupt):
        trio.run(main)
