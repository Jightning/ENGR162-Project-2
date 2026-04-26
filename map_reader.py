import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

PATH = 1
HEAT = 2
MAGNET = 3
EXIT = 4
ORIGIN = 5

def get_position(pos) -> Tuple[int, int]:
	x = int(pos[0])
	y = int(pos[1])

	return (x, y)

def event_value(event: Dict[str, Any]) -> int:
	if event.get("exit_point", False):
		return EXIT
	if event.get("magnetic_source", False):
		return MAGNET
	if event.get("heat_source", False):
		return HEAT
	return PATH


def to_index(x: int, y: int, min_x: int, max_y: int) -> Tuple[int, int]:
	col = x - min_x
	row = max_y - y
	return row, col


def build_grid(events: Iterable[Dict[str, Any]]) -> List[List[int]]:
	normalized_events = []
	x_vals = [0]
	y_vals = [0]

	for event in events:
		x, y = int(event["pos"][0]), int(event["pos"][1])
		normalized_events.append((x, y, event))
		x_vals.append(x)
		y_vals.append(y)

	min_x = min(x_vals)
	max_x = max(x_vals)
	min_y = min(y_vals)
	max_y = max(y_vals)

	width = max_x - min_x + 1
	height = max_y - min_y + 1

	grid = [[0 for _ in range(width)] for _ in range(height)]

	for x, y, event in normalized_events:
		row, col = to_index(x, y, min_x, max_y)
		grid[row][col] = max(grid[row][col], event_value(event))

	origin_row, origin_col = to_index(0, 0, min_x, max_y)
	grid[origin_row][origin_col] = ORIGIN

	return grid

def main():
	with open("maze.json", "r", encoding="utf-8") as file:
		data = json.load(file)
		
	grid = build_grid(data)

	print(json.dumps(grid, indent=4))

	with open("maze_output", "w", encoding="utf-8") as file:
		json.dump(grid, file, indent=4)


if __name__ == "__main__":
	main()
