from enum import Enum

# -- Node --
# - it can be start, end (destination) or obstacle
# - if not obstacle, in addition: open or closed.
# - position in grid given by row and column
# - absolute position in window: x and y (for pygame)
# - terrain elevation (if applicable)
# - neighbors

MAX_ALLOWED_TERRAIN_LEVEL = 50
ELEVATION_STEP = 10


class NodeType(Enum):
    START = 1
    END = 2
    OBSTACLE = 3
    FREE = 4
    OPEN = 5
    CLOSED = 6
    PATH = 7
    WAYPOINT = 8


class Node:
    def __init__(self, node_id: int, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.node_type = NodeType.FREE
        self.neighbors: list["Node"] = []
        self.terrain_level = 0
        self.id = node_id

    # Accessors
    def get_position(self) -> tuple[int, int]:
        return self.row, self.col

    def get_type(self) -> NodeType:
        return self.node_type

    def get_neighbors(self) -> list["Node"]:
        return self.neighbors

    def get_terrain_level(self) -> int:
        return self.terrain_level

    # Modifiers
    def set_position(self, row: int, col: int) -> None:
        self.row = row
        self.col = col

    def set_type(self, node_type: NodeType) -> None:
        self.node_type = node_type

    def set_neighbors(self, neighbors: list["Node"]) -> None:
        self.neighbors = neighbors

    def clear_neighbors(self) -> None:
        self.neighbors = []

    def update_neighbors(self, adjacent_node: "Node") -> None:
        self.neighbors.append(adjacent_node)

    def set_terrain_level(self, terrain_level: int) -> None:
        self.terrain_level = terrain_level

    def increase_terrain_level(self) -> None:
        if self.terrain_level < MAX_ALLOWED_TERRAIN_LEVEL:
            self.terrain_level += ELEVATION_STEP

    def decrease_terrain_level(self) -> None:
        self.terrain_level -= ELEVATION_STEP

    def reset(self) -> None:
        self.node_type = NodeType.FREE
        self.neighbors = []
        self.terrain_level = 0

    def open(self) -> None:
        self.node_type = NodeType.OPEN

    def close(self) -> None:
        self.node_type = NodeType.CLOSED

    def __lt__(self, other: "Node") -> bool:
        return False  # required for PriorityQueue comparison
