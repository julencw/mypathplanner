import pygame

from grid.node import Node, NodeType
from visualization.visualization import TaskSetting


class Grid:
    def __init__(
        self,
        rows: int,
        cols: int,
        task_setting: TaskSetting | None,
    ) -> None:
        self.rows = rows
        self.cols = cols
        self.grid = [[Node(node_id=row*cols + col, row=row, col=col)
                      for col in range(cols)] for row in range(rows)]
        self.start_node: None | Node = None
        self.end_node: None | Node = None
        self.task_setting = (
            task_setting if task_setting else TaskSetting.DEFAULT)
        self.waypoints: list[Node] = []
        self.number_of_waypoints: int = 0

    # Accessors
    def get_node(self, row: int, col: int) -> Node:
        return self.grid[row][col]

    def get_grid(self) -> list[list[Node]]:
        return self.grid

    def get_rows(self) -> int:
        return self.rows

    def get_cols(self) -> int:
        return self.cols

    def within_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_row_col(
        self,
        normalized_mouse_pos: tuple[int, int],
        board_sizes: tuple[int, int],
    ) -> tuple[int, int]:
        y, x = normalized_mouse_pos
        width, height = board_sizes
        x_gap = width // self.cols
        y_gap = height // self.rows
        row = x // x_gap
        col = y // y_gap
        return row, col

    def get_waypoints(self) -> list[Node]:
        return self.waypoints

    def get_number_of_waypoints(self) -> int:
        return len(self.waypoints)

    # Modifiers
    def set_number_of_waypoints(self, number_of_waypoints: int) -> None:
        self.number_of_waypoints = number_of_waypoints

    def set_waypoints(self, waypoints: list[Node]) -> None:
        self.waypoints = waypoints

    def set_task_setting(
        self,
        task_setting: TaskSetting,
        number_of_waypoints: int | None,
    ) -> None:
        self.task_setting = task_setting
        if self.task_setting == TaskSetting.WAYPOINT:
            if number_of_waypoints is None:
                print("Number of waypoints not provided")
                pygame.quit()  # TODO: raise an exception in a pop-up message
            else:
                self.number_of_waypoints = number_of_waypoints

    def update_grid(
        self,
        normalized_mouse_pos: tuple[int, int],
        board_sizes: tuple[int, int],
    ) -> None:
        row, col = self.get_row_col(normalized_mouse_pos, board_sizes)

        # check that the clicked position is within the grid
        # and that the clicked position is free
        if not self.within_bounds(row, col) or \
                (self.grid[row][col].get_type() != NodeType.FREE
                 and self.task_setting != TaskSetting.ELEVATION):
            return

        if not self.start_node:
            self.set_start_node(row, col)
        elif not self.end_node:
            self.set_end_node(row, col)
        elif self.task_setting == TaskSetting.WAYPOINT and \
                self.get_number_of_waypoints() < self.number_of_waypoints:
            self.waypoints.append(self.grid[row][col])
            self.grid[row][col].set_type(NodeType.WAYPOINT)
        elif self.task_setting == TaskSetting.ELEVATION:
            self.grid[row][col].increase_terrain_level()
        else:
            self.set_obstacle_node(row, col)

    def clear_cell(
            self,
            normalized_mouse_pos: tuple[int, int],
            board_sizes: tuple[int, int],
    ) -> None:
        row, col = self.get_row_col(normalized_mouse_pos, board_sizes)
        if not self.within_bounds(row, col):
            return
        if self.task_setting == TaskSetting.ELEVATION:
            if self.grid[row][col].get_terrain_level() > 0:
                self.grid[row][col].decrease_terrain_level()
                return
        if self.start_node and self.start_node.get_position() == (row, col):
            self.start_node = None
        elif self.end_node and self.end_node.get_position() == (row, col):
            self.end_node = None
        elif (self.task_setting == TaskSetting.WAYPOINT
              and self.get_number_of_waypoints() > 0
              and self.grid[row][col].node_type == NodeType.WAYPOINT):
            self.waypoints.remove(self.grid[row][col])
        self.grid[row][col].reset()

    def set_start_node(self, row: int, col: int) -> None:
        self.start_node = self.grid[row][col]
        self.start_node.set_type(NodeType.START)

    def set_end_node(self, row: int, col: int) -> None:
        self.end_node = self.grid[row][col]
        self.end_node.set_type(NodeType.END)

    def set_obstacle_node(self, row: int, col: int) -> None:
        self.grid[row][col].set_type(NodeType.OBSTACLE)

    def set_free_node(self, row: int, col: int) -> None:
        self.grid[row][col].set_type(NodeType.FREE)

    def set_terrain_level(self, row: int, col: int, terrain_level: int) -> None:
        self.grid[row][col].set_terrain_level(terrain_level)

    def reset(self) -> None:
        self.start_node = None
        self.end_node = None
        self.waypoints = []
        self.number_of_waypoints = 0
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[row][col].reset()

    def create_graph(self) -> None:
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[row][col].clear_neighbors()
                if self.grid[row][col].get_type() == NodeType.OBSTACLE:
                    continue
                if self.within_bounds(row - 1, col) and \
                        self.grid[row - 1][col].get_type() != NodeType.OBSTACLE:
                    self.grid[row][col].update_neighbors(
                        self.grid[row - 1][col])
                if self.within_bounds(row + 1, col) and \
                        self.grid[row + 1][col].get_type() != NodeType.OBSTACLE:
                    self.grid[row][col].update_neighbors(
                        self.grid[row + 1][col])
                if self.within_bounds(row, col - 1) and \
                        self.grid[row][col - 1].get_type() != NodeType.OBSTACLE:
                    self.grid[row][col].update_neighbors(
                        self.grid[row][col - 1])
                if self.within_bounds(row, col + 1) and \
                        self.grid[row][col + 1].get_type() != NodeType.OBSTACLE:
                    self.grid[row][col].update_neighbors(
                        self.grid[row][col + 1])
