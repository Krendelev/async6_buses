import json
import trio

from trio_websocket import open_websocket_url


async def main():
    erroneous_messages = [
        json.dumps({"lat": "55.7494", "lng": 37.621, "route": "670к"}),
        json.dumps("Not a Dict"),
        "Not a JSON",
    ]
    server_url = "ws://127.0.0.1:8080"
    async with open_websocket_url(server_url) as ws:
        for message in erroneous_messages:
            await ws.send_message(message)
            reply = await ws.get_message()
            print(json.loads(reply))
            await trio.sleep(0.5)


if __name__ == "__main__":
    trio.run(main)
