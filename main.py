import pygame
import argparse

from grid.grid import Grid
from grid.node import Node, MAX_ALLOWED_TERRAIN_LEVEL, ELEVATION_STEP
from pathfinding.astar import AStar
from pathfinding.held_karp import HeldKarp
from pathfinding.ant_colony_opt import AntColonyOptimisation
from pathfinding.utils import rearrange_distance_matrix
from visualization.visualization import TaskSetting, Visualization
from utils import setup_parser

WINDOW_WIDTH: int = 900
WINDOW_HEIGHT: int = 960
TOPBAR_HEIGHT: int = 60


def run_algorithm(
    grid: Grid,
    astar: AStar,
    visualization: Visualization,
    start_node: Node,
    end_node: Node,
    waypoints: list[Node] | None = None,
    algorithm:  HeldKarp | AntColonyOptimisation | None = None,
) -> None:
    if waypoints:
        print(f"Running {algorithm.__class__.__name__} for waypoint setting")
    else:
        print(f"Running {algorithm.__class__.__name__} for default setting")

    grid.create_graph()
    graph = grid.get_grid()
    astar.set_graph(graph)

    if algorithm is not None and waypoints is not None:
        distance_matrix, paths = astar.compute_distance_matrix(
            start_node, end_node, waypoints)
        if isinstance(algorithm, AntColonyOptimisation):
            new_dist_matrix = rearrange_distance_matrix(
                distance_matrix, waypoints, start_node, end_node)
            algorithm.set_distance_matrix(new_dist_matrix)
            algorithm.set_precomputed_paths(paths)
            node_dict = {node.id: node for node in waypoints}
            node_dict[start_node.id] = start_node
            node_dict[end_node.id] = end_node
            algorithm.set_nodes(node_dict)
        else:  # HeldKarp
            algorithm.set_distance_matrix(distance_matrix)
            algorithm.set_precomputed_paths(paths)
            algorithm.set_waypoints(waypoints)

    if algorithm is None:
        path_found = astar.visualize_algorithm(
            visualization.draw_board,
            start_node,
            end_node,
        )
        if path_found:
            astar.reconstruct_path(
                start_node, end_node,
            )
        else:
            print("No path found")
    else:
        path_found = algorithm.visualize_algorithm(
            visualization.draw_board,
            start_node,
            end_node,
        )
        if path_found:
            algorithm.reconstruct_path(
                start_node, end_node,
            )
        else:
            print("No path found")


parser = argparse.ArgumentParser(description="Pathfinding algorithm")


def main() -> None:
    setup_parser(parser)
    args = parser.parse_args()

    grid = Grid(args.rows, args.rows, TaskSetting.DEFAULT)
    astar = AStar(args.K)
    held_karp = HeldKarp()
    ant_colony_opt = AntColonyOptimisation(
        epochs=int(args.epochs),
        number_ants=int(args.number_ants),
        rho=float(args.rho),
        Q=float(args.Q),
        alpha=float(args.alpha),
        beta=float(args.beta),
        ini_pheromone=float(args.ini_pheromone),
    )

    waypoint_alg: HeldKarp | AntColonyOptimisation | None = None
    if args.deterministic_waypoints:
        waypoint_alg = held_karp
    else:
        waypoint_alg = ant_colony_opt

    task_setting: TaskSetting | None = TaskSetting.DEFAULT
    visualization = Visualization(
        WINDOW_WIDTH, WINDOW_HEIGHT, TOPBAR_HEIGHT, task_setting,
        MAX_ALLOWED_TERRAIN_LEVEL, ELEVATION_STEP,
    )

    current_num_waypoints = None
    current_task_setting = TaskSetting.DEFAULT

    space_pressed = False  # Initialize flag

    while True:
        visualization.draw_board(grid.get_grid(), args.rows, args.rows)
        # Constantly checking gor user input
        task_setting, num_waypoints = visualization.draw_topbar()

        if task_setting == TaskSetting.QUIT:
            pygame.quit()
            return
        if task_setting is not None:
            grid = Grid(args.rows, args.rows, task_setting)
            current_task_setting = task_setting

        if task_setting == TaskSetting.DEFAULT:
            current_num_waypoints = None
            astar.set_task_setting(TaskSetting.DEFAULT)
        elif task_setting == TaskSetting.WAYPOINT:
            if num_waypoints is None:
                num_waypoints = 0
            current_num_waypoints = num_waypoints
            grid.set_number_of_waypoints(num_waypoints)
        elif task_setting == TaskSetting.ELEVATION:
            current_num_waypoints = None
            astar.set_task_setting(TaskSetting.ELEVATION)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            left_click = pygame.mouse.get_pressed()[0]
            right_click = pygame.mouse.get_pressed()[2]

            if left_click:
                mouse_position = visualization.normalize_mouse_position(
                    pygame.mouse.get_pos()
                )
                grid.update_grid(
                    mouse_position, (WINDOW_WIDTH,
                                     WINDOW_HEIGHT - TOPBAR_HEIGHT)
                )
            elif right_click:
                mouse_position = visualization.normalize_mouse_position(
                    pygame.mouse.get_pos()
                )
                grid.clear_cell(
                    mouse_position, (WINDOW_WIDTH,
                                     WINDOW_HEIGHT - TOPBAR_HEIGHT)
                )

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not space_pressed:
                    space_pressed = True  # Set the flag to True
                    start_node = grid.start_node
                    end_node = grid.end_node
                    if not start_node or not end_node:
                        continue

                    if current_task_setting in [TaskSetting.DEFAULT,
                                                TaskSetting.ELEVATION,
                                                TaskSetting.WAYPOINT]:
                        if current_task_setting == TaskSetting.WAYPOINT:
                            waypoints = grid.get_waypoints()
                            run_algorithm(
                                grid, astar, visualization,
                                start_node, end_node,
                                waypoints, waypoint_alg,
                            )
                        else:
                            run_algorithm(
                                grid, astar, visualization, start_node,
                                end_node,
                            )

                if event.key == pygame.K_c:
                    print('Clear Pressed')
                    grid.reset()
                    if (current_task_setting == TaskSetting.WAYPOINT
                            and not args.deterministic_waypoints):
                        ant_colony_opt.reset()
                    if current_num_waypoints is not None:
                        grid.set_number_of_waypoints(current_num_waypoints)

            elif event.type == pygame.KEYUP:
                # Reset the flag when the key is released
                if event.key == pygame.K_SPACE:
                    space_pressed = False


if __name__ == "__main__":
    main()
