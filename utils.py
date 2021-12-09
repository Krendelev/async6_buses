import logging
from functools import wraps

import configargparse
import trio
from trio_websocket import HandshakeError, ConnectionClosed


def parse_bus_args():
    parser = configargparse.ArgParser(default_config_files=["configs/bus.ini"])
    parser.add_argument("-r", "--routes", help="path to directory containing routes")
    parser.add_argument("-n", "--routnum", type=int, help="number of routes to load")
    parser.add_argument("-e", "--enroute", type=int, help="number of buses en route")
    parser.add_argument("-i", "--emid", type=int, default=0, help="bus emulator id")
    parser.add_argument("-d", "--delay", type=float, help="sending bus data interval")
    parser.add_argument("-o", "--host", help="URL of a dispatcher server")
    parser.add_argument("-l", "--listen", type=int, help="port to send data from buses")
    parser.add_argument("-w", "--wsnum", type=int, help="number of websockets to open")
    parser.add_argument(
        "-v",
        dest="verbosity",
        action="count",
        default=0,
        help="Logger verbosity, from zero to -vvv",
    )
    return parser.parse_args()


def parse_server_args():
    parser = configargparse.ArgParser(default_config_files=["configs/server.ini"])
    parser.add_argument(
        "-d", "--delay", default=1.0, type=float, help="sending data to client interval"
    )
    parser.add_argument("-o", "--host", help="URL of a dispatcher server")
    parser.add_argument(
        "-t", "--talk", type=int, help="port to communicate with client"
    )
    parser.add_argument(
        "-l", "--listen", type=int, help="port to collect data from buses"
    )
    parser.add_argument(
        "-v",
        dest="verbosity",
        action="count",
        default=0,
        help="Logger verbosity, from zero to -vvv",
    )
    return parser.parse_args()


def set_logging(verbosity):
    levels = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
    }
    logging.basicConfig(format="%(asctime)s  %(levelname)s  %(message)s")
    logger = logging.getLogger(__name__)
    logger.setLevel(levels.get(verbosity, 3))
    return logger


def relaunch_on_disconnect(func):
    @wraps(func)
    async def wrapper(*args):
        while True:
            try:
                return await func(*args)
            except (HandshakeError, ConnectionClosed):
                await trio.sleep(1)

    return wrapper
