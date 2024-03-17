import numpy as np

from collections.abc import Callable
from typing import Any
from visualization.visualization import TaskSetting


from grid.node import Node
from pathfinding.path_finding_algorithm import PathFindingAlgorithm
from pathfinding.utils import correct_path


class Ant:
    def __init__(
            self,
            start_node: Node,
            end_node: Node,
            alpha: float,
            beta: float
    ) -> None:
        self.start_node = start_node
        self.end_node = end_node
        self.current_node = start_node
        self.alpha = alpha
        self.beta = beta
        self.path = [start_node]
        self.visited_nodes: set[int] = {start_node.id}
        self.distance = 0

    def get_path(self) -> list[Node]:
        return self.path

    def get_distance(self) -> int:
        return self.distance

    def get_current_node(self) -> Node:
        return self.current_node

    def move_to_node(self, node: Node) -> None:
        self.path.append(node)
        self.visited_nodes.add(node.id)
        self.distance += 1
        self.current_node = node

    def reset(self) -> None:
        self.current_node = self.start_node
        self.path = [self.start_node]
        self.distance = 0
        self.visited_nodes = {self.start_node.id}


class AntColonyOptimisation(PathFindingAlgorithm):
    def __init__(self, epochs: int,
                 number_ants: int, rho: float, Q: float,
                 alpha: float, beta: float, ini_pheromone: float,
                 ) -> None:
        super().__init__()
        self.task_setting: TaskSetting = TaskSetting.WAYPOINT

        # Hyper parameters
        self.epochs = epochs
        self.number_ants = number_ants
        self.rho = rho
        self.Q = Q
        self.alpha = alpha
        self.beta = beta
        self.ini_pheromone = ini_pheromone

        # DS required for the algorithm
        self.ants: list[Ant] = []
        self.distance_matrix: dict[int, dict[int, float]] = {}
        self.pheromone_matrix: dict[int, dict[int, float]] = {}
        self.path_dict: dict[int, Node] = {}
        self.best_path: list[Node] = []
        self.best_path_length: float = float("inf")
        self.precomputed_paths: dict[int, dict[int, dict[int, Node]]] = {}

    def set_distance_matrix(
        self,
        distance_matrix: dict[int, dict[int, float]],
    ) -> None:
        self.distance_matrix = distance_matrix
        self.setup_pheromone_matrix()

    def set_nodes(self, nodes: dict[int, Node]) -> None:
        self.nodes = nodes

    def set_precomputed_paths(
        self, precomputed_paths: dict[int, dict[int, dict[int, Node]]]
    ) -> None:
        self.precomputed_paths = precomputed_paths

    def setup_pheromone_matrix(self) -> None:
        for node1 in self.distance_matrix:
            self.pheromone_matrix[node1] = {}
            for node2 in self.distance_matrix[node1]:
                self.pheromone_matrix[node1][node2] = self.ini_pheromone

    def populate_ants(self) -> None:
        for _ in range(self.number_ants):
            self.ants.append(
                Ant(self.start_node, self.end_node, self.alpha, self.beta))

    def heuristic(self, node1: Node, node2: Node, **kwargs: Any) -> int:
        return 0

    def reset_values(self) -> None:
        self.path_dict = {}
        self.best_path = []
        self.best_path_length = float("inf")
        self.populate_ants()

    def set_task_setting(self, task_setting: TaskSetting) -> None:
        self.task_setting = task_setting

    def fit(self) -> None:
        best_path: list[Node] = []
        best_path_length = float("inf")
        for epoch in range(self.epochs):
            epoch_paths: list[list[Node]] = []
            for ant in self.ants:
                ant.reset()  # set the ant back to the start node

                while ant.current_node != self.end_node:
                    next_node = self.choose_next_node(ant)
                    ant.move_to_node(self.nodes[next_node])

                epoch_paths.append(ant.get_path())

            epoch_best_path, epoch_best_path_length = self.pheromone_update(
                epoch_paths)
            print(
                f"Epoch {epoch}: Best path of length: {epoch_best_path_length}")
            print(f"Best path: {[node.id for node in epoch_best_path]}")

            if epoch_best_path_length < best_path_length:
                best_path = epoch_best_path
                best_path_length = epoch_best_path_length

        self.best_path = best_path
        self.best_path_length = best_path_length

    def get_unvisited_nodes(self, ant: Ant) -> list[int]:
        unvisited_nodes = [
            node for node in self.nodes
            if node not in ant.visited_nodes and node != ant.end_node.id
        ]
        # end node must be the last node to visit
        if not unvisited_nodes:
            unvisited_nodes = [ant.end_node.id]
        return unvisited_nodes

    def compute_probabilities(
        self, current_node: Node, unvisited_nodes: list[int]
    ) -> dict[int, float]:
        normalizer = 0.0
        probabilities: dict[int, float] = {}
        for node in unvisited_nodes:
            thau = self.pheromone_matrix[current_node.id][node]
            eta = 1 / self.distance_matrix[current_node.id][node]
            normalizer += thau ** self.alpha * eta ** self.beta
            probability = (thau ** self.alpha * eta ** self.beta)
            probabilities[node] = probability

        for node in probabilities:
            probabilities[node] /= normalizer

        return probabilities

    def select_next_node(self, probabilities: dict[int, float]) -> int:
        # Select a node randomly based on probabilities
        return np.random.choice(list(probabilities.keys()),
                                p=list(probabilities.values()))

    def choose_next_node(self, ant: Ant) -> int:
        unvisited_nodes = self.get_unvisited_nodes(ant)
        probabilities = self.compute_probabilities(
            ant.get_current_node(), unvisited_nodes)
        next_node = self.select_next_node(probabilities)
        return next_node

    def pheromone_evaporation(self) -> None:
        for node1 in self.pheromone_matrix:
            for node2 in self.pheromone_matrix[node1]:
                self.pheromone_matrix[node1][node2] *= (1 - self.rho)

    def pheromone_update(
            self,
            epoch_paths: list[list[Node]]
    ) -> tuple[list[Node], float]:
        self.pheromone_evaporation()

        best_distance = float("inf")
        best_path: list[Node] = []

        for path in epoch_paths:
            path_length = len(path)
            total_distance = 0.0
            for i in range(path_length - 1):
                node1 = path[i].id
                node2 = path[i + 1].id
                self.pheromone_matrix[node1][node2] += self.Q / \
                    self.distance_matrix[node1][node2]
                total_distance += self.distance_matrix[node1][node2]

            if total_distance < best_distance:
                best_distance = total_distance
                best_path = path
        return best_path, best_distance

    def visualize_algorithm(
        self,
        draw_function: Callable,  # type: ignore
        start_node: Node,
        end_node: Node,
    ) -> bool:
        # check if any distance between points is infinite
        for node in self.distance_matrix:
            for neighbor in self.distance_matrix[node]:
                if self.distance_matrix[node][neighbor] == float("inf"):
                    return False

        self.start_node = start_node
        self.end_node = end_node
        self.reset_values()

        self.fit()

        return True

    def reconstruct_path(
        self,
        start_node: Node,
        end_node: Node,
    ) -> None:
        self.best_path = list(reversed(self.best_path))
        for i in range(len(self.best_path) - 1):
            self.path_dict[self.best_path[i].id] = self.best_path[i + 1]

        self.path = correct_path(self.start_node, self.end_node,
                                 self.path_dict, self.precomputed_paths)
        super().reconstruct_path(start_node, end_node)

    def reset(self) -> None:
        self.ants = []
        self.distance_matrix = {}
        self.pheromone_matrix = {}
        self.path_dict = {}
        self.best_path = []
        self.best_path_length = float("inf")
        self.precomputed_paths = {}
