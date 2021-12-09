from dataclasses import dataclass, field


@dataclass(frozen=True)
class Bus:
    busId: str
    lat: float = field(compare=False)
    lng: float = field(compare=False)
    route: str = field(compare=False)


@dataclass
class WindowBounds:
    south_lat: float = 0.0
    north_lat: float = 0.0
    west_lng: float = 0.0
    east_lng: float = 0.0

    def update(self, south_lat, north_lat, west_lng, east_lng):
        self.south_lat = south_lat
        self.north_lat = north_lat
        self.west_lng = west_lng
        self.east_lng = east_lng

    def contain(self, lat, lng):
        return (
            self.south_lat <= lat <= self.north_lat
            and self.west_lng <= lng <= self.east_lng
        )
