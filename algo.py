import heapq
import json
from pathlib import Path


STEP_LENGTH_M = 0.7
WALKING_SPEED_MPS = 1.2          


_HERE = Path(__file__).resolve().parent
MAP_PATH = next(
    (p for p in (_HERE / "Maps.json", _HERE.parent / "Maps.json") if p.exists()),
    _HERE / "Maps.json",
)


def load_map():
    with MAP_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def is_lift(node):
    """Lifts (E001, E101 ...) are ignored for now."""
    return node.startswith("E")


def is_corridor(node):
    """Only junctions (J...) and stairs (S...) can be walked THROUGH.
    Rooms, toilets etc. can only be a start or a destination."""
    return node.startswith(("J", "S"))


def floor_of(node):
    """A003 -> 0, B318 -> 3, J105 -> 1, G11 -> 1 (2nd character is the floor)."""
    return int(node[1])


def dijkstra(building_map, start, destination):
    for place in (start, destination):
        if place not in building_map:
            raise ValueError(f"Unknown location: {place}")
        if is_lift(place):
            raise ValueError("Lifts are not supported yet. Pick a room, junction or stairs.")

    distances = {node: float("inf") for node in building_map}
    previous = {}
    distances[start] = 0
    queue = [(0, start)]

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        
        if current_distance != distances[current_node]:
            continue

        if current_node == destination:
            break

      
        if current_node != start and not is_corridor(current_node):
            continue

        for neighbour, weight in building_map[current_node].items():
            if is_lift(neighbour):
                continue

            new_distance = current_distance + weight

            if new_distance < distances[neighbour]:
                distances[neighbour] = new_distance
                previous[neighbour] = current_node
                heapq.heappush(queue, (new_distance, neighbour))

    if distances[destination] == float("inf"):
        raise ValueError(f"No route exists from {start} to {destination}.")

    path = [destination]
    while path[-1] != start:
        path.append(previous[path[-1]])

    path.reverse()
    return path, distances[destination]



djikstra = dijkstra


def to_real_units(units):
    """Convert counted steps to (metres, steps, seconds)."""
    steps = units                      # edge weights are counted steps
    metres = steps * STEP_LENGTH_M
    seconds = metres / WALKING_SPEED_MPS
    return metres, steps, seconds


def get_location(building_map, prompt):
    while True:
        location = input(prompt).strip().upper()

        if location in {"Q", "QUIT", "EXIT"}:
            return None

        if location in building_map and not is_lift(location):
            return location

        print("Invalid location code. Try A003, B318, J001, etc. (lifts not supported)")
        print("Type Q to quit.")


def main():
    building_map = load_map()

    print("PathPilot : CAMPUS25 PATH FINDER")
    print("Enter Q at any time to exit.")

    while True:
        start = get_location(building_map, "\nYour current location: ")
        if start is None:
            break

        destination = get_location(building_map, "Destination: ")
        if destination is None:
            break

        try:
            path, units = dijkstra(building_map, start, destination)
            metres, steps, seconds = to_real_units(units)

            
            print("SHORTEST ROUTE")
            

            print(" -> ".join(path))

            if floor_of(start) != floor_of(destination):
                print(f"\nFloor change: {floor_of(start)} -> {floor_of(destination)} (via stairs)")

            print(f"\nDistance (counted steps) : {steps:g} steps")
            print(f"Approx. in metres        : {metres:.0f} m  (at {STEP_LENGTH_M} m per step)")
            print(f"Approx. walking time     : {seconds / 60:.1f} min ({seconds:.0f} s)")
            

        except ValueError as error:
            print(f"\n{error}")

        again = input("\nFind another route? [Y/n]: ").strip().lower()
        if again not in {"", "y", "yes"}:
            break

    print("\nThank you for using Apostasi.")


if __name__ == "__main__":
    main()