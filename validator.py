from dataclasses import fields

from interface import Bus, WindowBounds


class MessageValidationError(Exception):
    pass


def validate(message, model):

    if not isinstance(message, dict):
        raise MessageValidationError("Requires message to be of type <class 'dict'>")

    errors = []
    if model is WindowBounds:
        valid_keys = {"msgType", "data"}
        if missing := valid_keys - message.keys():
            errors.append(f"Requires {missing} specified")
        message = message.get("data", {})

    for field in fields(model):
        if (value := message.get(field.name)) is None:
            errors.append(f"Requires {field.name} specified")
        elif type(value) != field.type:
            errors.append(f"Requires {field.name} to be of type {field.type}")

    if errors:
        raise MessageValidationError(*errors)


if __name__ == "__main__":
    window = {
        "data": {
            "south_lat": "55.73078331708113",
            "north_lat": 55.76918654596013,
            "west_lng": 37.53822326660157,
            "east_lng": 37.66181945800782,
        },
    }
    bus = {"lat": "55.7494", "lng": 37.621, "route": "670к"}
    try:
        validate(window, WindowBounds)
    except MessageValidationError as err:
        print(err)
    try:
        validate(bus, Bus)
    except MessageValidationError as err:
        print(err)
