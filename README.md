
# 🧭 PathPlanning

An interactive Python tool for exploring different path planning algorithms in a grid-based environment — featuring A*, Ant Colony Optimization (ACO), and Held-Karp.

---

## 🚀 Overview

This project provides a visual and configurable platform to simulate and compare pathfinding techniques across three task settings:

1. **Shortest Path**: A* search between a start and goal position.
2. **Waypoint Navigation**: Travel through a user-defined set of waypoints using Held-Karp or ACO.
3. **Relief-Aware Pathfinding**: Navigate a terrain with elevation, adjusting path preferences based on terrain flatness.

Great for educational, experimentation, and demonstration purposes!

---

## 🛠️ Installation

Install all required dependencies with:

```bash
pip install -r requirements.txt
```

> ⚠️ `requirements-dev.txt` is used only for internal development/testing — it can be ignored.

---

## 🧪 Usage

Run the app with:

```bash
python main.py
```

To explore the available options:

```bash
python main.py --help
```

### Common Arguments

- `--window_size`: GUI window size (default: 700x700 pixels).
- `--rows`: Grid size (rows = cols).
- `--K`: Heuristic weight for terrain influence in relief tasks.
- `--deterministic_waypoints`: Use Held-Karp for optimal waypoint path (default is ACO).
- `--epochs`, `--number_ants`, `--rho`, `--Q`, `--alpha`, `--beta`, `--ini_pheromone`: ACO hyperparameters.

---

## 🕹️ Task Modes

### 🟩 Task 1: Shortest Path

Use A* to find the shortest path from start to goal.

- **Left-click** to place start, goal, and obstacles.
- **Right-click** to remove them.
- Press `Space` to run A*.
- Press `C` to clear the grid.

Color scheme:
- Start: 🟣 | Goal: 🟢 | Obstacles: ⚫
- Open nodes: 🔵 (light) | Closed nodes: 🔵 (dark)  | Path: 🟩

| Default Grid | Solved Path |
|--------------|-------------|
| <img src="images/setting1_empty.png" width="225"/> | <img src="images/tasksetting1_hiwiexample.png" width="225"/> |

---

### 📍 Task 2: Waypoint Navigation

Find the optimal route from start to goal while visiting a number of intermediate waypoints.

- **Left-click** to set start, goal, and waypoints.
- Use either:
  - [Held-Karp](https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm) for guaranteed optimality.
  - [Ant Colony Optimization](https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms) as a heuristic.
- Press `Space` to run algorithm.
- Press `C` to reset.

ACO defaults:
- Epochs: 100, Ants: 10, ρ: 0.1, Q: 1, α: 1, β: 1, Initial pheromone: 1

| Default Grid | Solved Path |
|--------------|-------------|
| <img src="images/setting2_empty.png" width="225"/> | <img src="images/setting2_hiwiexample.png" width="225"/> |

---

### ⛰️ Task 3: Relief-Aware Pathfinding

In this scenario, the grid has elevation — requiring the algorithm to trade off between path length and terrain flatness.

- **Left-click** to raise terrain.
- **Right-click** to lower it.
- `--K` controls the trade-off:
  - `K=0`: prioritize shortest path (ignore relief)
  - `K=1`: prioritize flatness

| Terrain Map | K=0 Result | K=1 Result |
|-------------|------------|------------|
| <img src="images/setting3_k0_exampleA.png" width="225"/> | <img src="images/setting3_k0_exampleB.png" width="225"/> | <img src="images/setting3_k0_exampleC.png" width="225"/> |

---

## 🐞 Known Issues

- Switching to **Waypoint Task** a second time may cause UI input to freeze — restart as a workaround.
- Holding clicks too long can result in unintended cell changes.
- Performance degradation with >30 waypoints is due to path reconstruction inefficiencies, not algorithmic limitations.
- ACO performance depends heavily on hyperparameters, which may require tuning.

---

## 📄 Report

For a full explanation of the algorithms and design rationale, see [`report.pdf`](report.pdf).

---