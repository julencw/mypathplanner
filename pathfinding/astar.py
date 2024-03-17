from collections.abc import Callable
from queue import PriorityQueue
from typing import Any
from visualization.visualization import TaskSetting

import pygame

from grid.node import Node, NodeType
from pathfinding.path_finding_algorithm import PathFindingAlgorithm
from pathfinding.utils import correct_path


class AStar(PathFindingAlgorithm):
    def __init__(self, k: float) -> None:
        super().__init__()
        self.min_heap: PriorityQueue[tuple[float, int, Node]] = PriorityQueue()
        self.open_nodes: set[Node] = set()
        self.g_function: dict[int, float] = {}
        self.f_function: dict[int, float] = {}
        self.graph: list[list[Node]] = []
        self.task_setting: TaskSetting = TaskSetting.DEFAULT
        self.k = k
        self.path_dict: dict[int, Node] = {}

    def heuristic(self, node1: Node, node2: Node, **kwargs: Any) -> int:
        x1, y1 = node1.get_position()
        x2, y2 = node2.get_position()
        if self.task_setting == TaskSetting.ELEVATION:
            elevation_diff = abs(
                node1.get_terrain_level() - node2.get_terrain_level())
            manhattan_distance = abs(x1 - x2) + abs(y1 - y2)
            return pow(elevation_diff, self.k)*pow(manhattan_distance, 1-self.k)
        return abs(x1 - x2) + abs(y1 - y2)  # Default heuristic

    def reset_values(self) -> None:
        self.min_heap = PriorityQueue()
        self.open_nodes = set()
        self.path_dict = {}
        self.g_function = {}
        self.f_function = {}
        # self.graph = []

    def set_task_setting(self, task_setting: TaskSetting) -> None:
        self.task_setting = task_setting

    def set_graph(self, graph: list[list[Node]]) -> None:
        self.graph = graph

    def compute_distance_matrix(
        self,
        start_node: Node,
        end_node: Node,
        waypoints: list[Node],
    ) -> tuple[list[list[float]], dict[int, dict[int, dict[int, Node]]]]:
        distance_matrix: list[list[float]] = []
        paths: dict[int, dict[int, dict[int, Node]]] = {}

        # distance matrix for nodes: start, end, and waypoints
        # matrix should have dimensions (n+2)x(n+2) and first row and column
        # is for the start node, the last row and column is for the end node
        # and the rest of the matrix is for the waypoints

        # path matrix gives for each pair of nodes u, v, the entire path

        nodes = [start_node] + waypoints + [end_node]
        distance_matrix = [[float("inf")] * len(nodes)
                           for _ in range(len(nodes))]
        for node in nodes:
            paths[node.id] = {}

        # TODO: symmetric matrix, so only compute half
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes):
                if i == j:
                    distance_matrix[i][j] = 0
                    paths[node1.id][node2.id] = {}
                    continue
                distance, path = self.run_algorithm(node1, node2)
                distance_matrix[i][j] = distance
                paths[node1.id][node2.id] = path

        return distance_matrix, paths

    def run_algorithm(
        self,
        start_node: Node,
        end_node: Node,
    ) -> tuple[float, dict[int, Node]]:
        # run A-star algorithm to compute distance and path
        self.reset_values()

        # initialize g and f functions
        self.initialize_functions(self.graph)

        # initialize the start node
        self.g_function[start_node.id] = 0
        self.f_function[start_node.id] = self.heuristic(start_node, end_node)
        insertion_idx = 0
        self.min_heap.put((self.f_function[start_node.id],
                           insertion_idx,
                           start_node))
        self.open_nodes.add(start_node)

        while not self.min_heap.empty():
            _, _, current_node = self.min_heap.get()
            self.open_nodes.remove(current_node)

            if current_node == end_node:
                # Path reconstruction
                # self.reconstruct_path(start_node, end_node)
                return self.g_function[end_node.id], self.path_dict

            for neighbor in current_node.get_neighbors():
                aux_g = self.g_function[current_node.id] + 1

                if aux_g < self.g_function[neighbor.id]:
                    self.path_dict[neighbor.id] = current_node
                    self.g_function[neighbor.id] = aux_g
                    self.f_function[neighbor.id] = aux_g + \
                        self.heuristic(neighbor, end_node)

                    if neighbor not in self.open_nodes:
                        insertion_idx += 1
                        self.min_heap.put((self.f_function[neighbor.id],
                                           insertion_idx,
                                           neighbor))
                        self.open_nodes.add(neighbor)
        return float("inf"), {}

    def visualize_algorithm(
        self,
        draw_function: Callable,  # type: ignore
        start_node: Node,
        end_node: Node,
    ) -> bool:
        self.reset_values()

        # initialize g and f functions
        self.initialize_functions(self.graph)

        # initialize the start node
        self.g_function[start_node.id] = 0
        self.f_function[start_node.id] = self.heuristic(start_node, end_node)
        insertion_idx = 0
        self.min_heap.put((self.f_function[start_node.id],
                           insertion_idx,
                           start_node))
        self.open_nodes.add(start_node)

        while not self.min_heap.empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            _, _, current_node = self.min_heap.get()
            self.open_nodes.remove(current_node)

            if current_node == end_node:
                # Path reconstruction
                current_node.set_type(NodeType.END)
                # self.reconstruct_path(start_node, end_node)
                return True

            for neighbor in current_node.get_neighbors():
                aux_g = self.g_function[current_node.id] + 1

                if aux_g < self.g_function[neighbor.id]:
                    self.path_dict[neighbor.id] = current_node
                    self.g_function[neighbor.id] = aux_g
                    self.f_function[neighbor.id] = aux_g + \
                        self.heuristic(neighbor, end_node)

                    if neighbor not in self.open_nodes:
                        insertion_idx += 1
                        self.min_heap.put((self.f_function[neighbor.id],
                                           insertion_idx,
                                           neighbor))
                        self.open_nodes.add(neighbor)
                        neighbor.set_type(NodeType.OPEN)

            if current_node != start_node:
                current_node.set_type(NodeType.CLOSED)

            n_rows = len(self.graph)
            n_cols = len(self.graph[0])
            draw_function(self.graph, n_rows, n_cols)

        # the end node is not reachable
        return False

    def initialize_functions(self, graph: list[list[Node]]) -> None:
        for row in graph:
            for node in row:
                self.g_function[node.id] = float("inf")
                self.f_function[node.id] = float("inf")

    def reconstruct_path(
        self,
        start_node: Node,
        end_node: Node,
    ) -> None:
        self.path = correct_path(start_node, end_node,
                                 self.path_dict)
        super().reconstruct_path(start_node, end_node)
