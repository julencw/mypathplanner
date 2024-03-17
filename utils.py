import argparse


def setup_parser(parser: argparse.ArgumentParser) -> None:

    parser.add_argument(
        "--rows",
        type=int,
        required=False,
        default=15,
        help="Number of rows and columns in the grid",
    )

    parser.add_argument(
        "--K",
        type=float,
        required=False,
        default=1,
        help="K value for A* algorithm heuristic",
    )

    parser.add_argument(
        "--deterministic_waypoints",
        required=False,
        action="store_true",
        help="Whether to use the Held-Karp algorithm to find "
        "the optimal path in the Waypoint task",
    )

    parser.add_argument(
        "--epochs",
        type=int,
        required=False,
        default=100,
        help="Number of epochs for the ant colony optimisation algorithm",
    )

    parser.add_argument(
        "--number_ants",
        type=int,
        required=False,
        default=10,
        help="Number of ants for the ant colony optimisation algorithm",
    )

    parser.add_argument(
        "--rho",
        type=float,
        required=False,
        default=0.1,
        help="Rho value for the ant colony optimisation algorithm",
    )

    parser.add_argument(
        "--Q",
        type=float,
        required=False,
        default=1,
        help="Q value for the ant colony optimisation algorithm",
    )

    parser.add_argument(
        "--alpha",
        type=float,
        required=False,
        default=1,
        help="Alpha value for the ant colony optimisation algorithm",
    )

    parser.add_argument(
        "--beta",
        type=float,
        required=False,
        default=1,
        help="Beta value for the ant colony optimisation algorithm",
    )

    parser.add_argument(
        "--ini_pheromone",
        type=float,
        required=False,
        default=0.1,
        help="Initial pheromone value for the"
        " ant colony optimisation algorithm",
    )
