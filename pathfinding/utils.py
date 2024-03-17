from grid.node import Node


def correct_path(
    start_node: Node,
    end_node: Node,
    path_dict: dict[int, Node],
    precomputed_paths: dict[int, dict[int, dict[int, Node]]] = {},
) -> list[Node]:
    path: list[Node] = []

    if not precomputed_paths:
        current_node = end_node
        while current_node != start_node:
            path.append(current_node)
            current_node = path_dict[current_node.id]
        path.append(start_node)
        return path

    current_node = end_node
    waypoint_parent = path_dict[current_node.id]
    path.append(current_node)

    while waypoint_parent != start_node:
        # reconstruct actual path from prev way point to current way point
        path_current_to_parent = precomputed_paths[
            waypoint_parent.id][current_node.id]
        parent = path_current_to_parent[current_node.id]
        while parent != waypoint_parent:
            path_dict[current_node.id] = parent
            path.append(parent)
            current_node = parent
            parent = path_current_to_parent[current_node.id]

        path_dict[current_node.id] = waypoint_parent
        path.append(waypoint_parent)

        current_node = waypoint_parent
        waypoint_parent = path_dict[current_node.id]

    path_current_to_parent = precomputed_paths[
        waypoint_parent.id][current_node.id]
    parent = path_current_to_parent[current_node.id]
    while parent != waypoint_parent:
        path_dict[current_node.id] = parent
        path.append(parent)
        current_node = parent
        parent = path_current_to_parent[current_node.id]

    path_dict[current_node.id] = start_node
    path.append(start_node)

    return path


def rearrange_distance_matrix(
        distance_matrix: list[list[float]],
        waypoints: list[Node],
        start_node: Node,
        end_node: Node,
) -> dict[int, dict[int, float]]:
    new_distance_matrix: dict[int, dict[int, float]] = {}
    nodes = [start_node] + waypoints + [end_node]
    for i, node1 in enumerate(nodes):
        new_distance_matrix[node1.id] = {}
        for j, node2 in enumerate(nodes):
            new_distance_matrix[node1.id][node2.id] = distance_matrix[i][j]

    return new_distance_matrix
