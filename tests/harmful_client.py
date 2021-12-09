import json
import trio

from trio_websocket import open_websocket_url


async def main():
    erroneous_messages = [
        json.dumps({"msgType": "newBounds"}),
        json.dumps(
            {
                "msgType": "newBounds",
                "data": {
                    "south_lat": "55.73078331708113",
                    "north_lat": 55.76918654596013,
                    "west_lng": 37.53822326660157,
                    "east_lng": 37.66181945800782,
                },
            }
        ),
        json.dumps(
            {
                "data": {
                    "south_lat": 55.73078331708113,
                    "north_lat": 55.76918654596013,
                    "west_lng": 37.53822326660157,
                },
            }
        ),
        json.dumps("Not a Dict"),
        "Not a JSON",
    ]
    server_url = "ws://127.0.0.1:8000"
    async with open_websocket_url(server_url) as ws:
        for message in erroneous_messages:
            await ws.send_message(message)
            reply = await ws.get_message()
            print(json.loads(reply))
            await trio.sleep(0.5)


if __name__ == "__main__":
    trio.run(main)
