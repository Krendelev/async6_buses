import json
from contextlib import suppress
from dataclasses import asdict
from functools import partial
from json.decoder import JSONDecodeError

import trio
from trio_websocket import ConnectionClosed, serve_websocket

from interface import Bus, WindowBounds
from utils import parse_server_args, set_logging
from validator import MessageValidationError, validate

buses_online = set()


async def listen_to_buses(request):
    ws = await request.accept()
    while True:
        try:
            message = await ws.get_message()
            bus_info = json.loads(message)
            validate(bus_info, Bus)
            bus = Bus(**bus_info)
            # `bus` is hashable with hash derived from `busId`
            buses_online.discard(bus)
            buses_online.add(bus)

        except JSONDecodeError:
            message = {"msgType": "Errors", "errors": "Requires valid JSON"}
            await ws.send_message(json.dumps(message))
        except MessageValidationError as err:
            message = {"msgType": "Errors", "errors": err.args}
            await ws.send_message(json.dumps(message))
        except ConnectionClosed:
            break


async def send_buses_info(socket, bounds):
    while True:
        buses = [
            asdict(bus) for bus in buses_online if bounds.contain(bus.lat, bus.lng)
        ]
        reply = json.dumps({"msgType": "Buses", "buses": buses}, ensure_ascii=False)
        try:
            await socket.send_message(reply)
        except ConnectionClosed:
            break
        else:
            await trio.sleep(args.delay)


async def listen_to_browser(socket, bounds):
    while True:
        try:
            message = await socket.get_message()
            current_bounds = json.loads(message)
            validate(current_bounds, WindowBounds)
            bounds.update(**current_bounds["data"])

        except JSONDecodeError:
            message = {"msgType": "Errors", "errors": "Requires valid JSON"}
            await socket.send_message(json.dumps(message))
        except MessageValidationError as err:
            message = {"msgType": "Errors", "errors": err.args}
            await socket.send_message(json.dumps(message))
        except ConnectionClosed:
            break


async def talk_to_browser(request):
    ws = await request.accept()
    wb = WindowBounds()
    async with trio.open_nursery() as communicator:
        communicator.start_soon(send_buses_info, ws, wb)
        communicator.start_soon(listen_to_browser, ws, wb)


async def main():
    serve_ws = partial(serve_websocket, ssl_context=None)
    async with trio.open_nursery() as dispatcher:
        dispatcher.start_soon(serve_ws, listen_to_buses, args.host, args.listen)
        dispatcher.start_soon(serve_ws, talk_to_browser, args.host, args.talk)


if __name__ == "__main__":
    args = parse_server_args()
    logger = set_logging(args.verbosity)
    with suppress(KeyboardInterrupt):
        trio.run(main)
