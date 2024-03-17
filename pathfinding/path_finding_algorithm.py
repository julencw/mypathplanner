import abc
from collections.abc import Callable
from typing import Any

from grid.node import Node, NodeType


class PathFindingAlgorithm(abc.ABC):
    def __init__(self) -> None:
        self.path: list[Node] = []

    @abc.abstractmethod
    def visualize_algorithm(
        self,
        draw_function: Callable,  # type: ignore
        start_node: Node,
        end_node: Node,
    ) -> bool:
        ...

    @abc.abstractmethod
    def heuristic(self, node1: Node, node2: Node, **kwargs: Any) -> int:
        ...

    def reconstruct_path(
        self,
        start_node: Node,
        end_node: Node,
    ) -> None:
        for node in self.path:
            if (
                node.get_type() != NodeType.START
                and node.get_type() != NodeType.END
                and node.get_type() != NodeType.WAYPOINT
            ):
                node.set_type(NodeType.PATH)
