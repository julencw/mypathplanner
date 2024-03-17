from collections.abc import Callable
from typing import Any

import itertools

from grid.node import Node
from pathfinding.utils import correct_path
from pathfinding.path_finding_algorithm import PathFindingAlgorithm


class HeldKarp(PathFindingAlgorithm):

    def __init__(self) -> None:
        super().__init__()
        self.distance_matrix: list[list[float]] = []
        self.precomputed_paths: dict[int, dict[int, dict[int, Node]]] = {}
        self.waypoints: list[Node] = []
        self.path_dict: dict[int, Node] = {}

    def heuristic(self, node1: Node, node2: Node, **kwargs: Any) -> int:
        return 0

    def reset_values(self) -> None:
        self.path_dict = {}

    def set_distance_matrix(self, distance_matrix: list[list[float]]) -> None:
        self.distance_matrix = distance_matrix

    def set_precomputed_paths(
        self, precomputed_paths: dict[int, dict[int, dict[int, Node]]]
    ) -> None:
        self.precomputed_paths = precomputed_paths

    def set_waypoints(self, waypoints: list[Node]) -> None:
        self.waypoints = waypoints

    def visualize_algorithm(
        self,
        draw_function: Callable,  # type: ignore
        start_node: Node,
        end_node: Node,
    ) -> bool:
        self.reset_values()

        # check if any distance between points is infinite
        for i in range(len(self.distance_matrix)):
            for j in range(len(self.distance_matrix[i])):
                if self.distance_matrix[i][j] == float("inf"):
                    return False

        cost, optimal_traversal = self.run_algorithm()

        print("Optimal cost:", cost)

        # optimal traversal is not in the correct format,
        # it should be a dictionary with keys being the actual node IDs
        # and the values being the parent nodes

        self.path_dict[end_node.id] = self.waypoints[optimal_traversal[0] - 1]
        for i in range(1, len(optimal_traversal)):
            self.path_dict[self.waypoints[optimal_traversal[i - 1] -
                                          1].id] = self.waypoints[
                optimal_traversal[i] - 1]

        self.path_dict[self.waypoints[optimal_traversal[-1] - 1].id] = start_node

        # now we have a path with the start, waypoints, and end nodes
        # however, we need to reconstruct the path from the start to the end
        # using the precomputed paths
        self.path = correct_path(start_node, end_node, self.path_dict,
                                 self.precomputed_paths)

        return True

    def run_algorithm(
        self,
    ) -> tuple[float, list[int]]:
        n = len(self.distance_matrix)

        DP: dict[tuple[int, int], tuple[float, int]] = {}

        # Base case
        for k in range(1, n):
            DP[(1 << k, k)] = (self.distance_matrix[0][k], 0)

        # Iterate over all subsets of increasing length
        # Fill DP table in a bottom-up manner
        for s_size in range(2, n):
            for S in itertools.combinations(range(1, n), s_size):
                bits = 0
                for bit in S:
                    bits |= 1 << bit

                # bits encoding the current subset

                for e in S:
                    S_i = bits & ~(1 << e)
                    # Specify the type of res as List[Tuple[float, int]]
                    res: list[tuple[float, int]] = []
                    for m in S:
                        if m == 0 or m == e:
                            continue
                        res.append(
                            (DP[(S_i, m)][0] + self.distance_matrix[m][e], m))
                    # default comparator is the first element of the tuple
                    DP[(bits, e)] = min(res)

        # Calculate optimal cost
        bits = (1 << n) - 1
        # substract 1 to remove the starting node
        bits -= 1
        opt_cost, parent = DP[(bits, n - 1)]  # n-1 is the end node
        bits = bits - (1 << (n - 1))

        # Backtrack to find full path
        path: list[int] = []  # Specify the type of path as list[int]
        for _ in range(n - 2):  # - 2 for start and end nodes
            path.append(parent)
            new_bits = bits & ~(1 << parent)
            _, parent = DP[(bits, parent)]
            bits = new_bits

        return opt_cost, path
