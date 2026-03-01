import pygame
import heapq
import math
import random
import time

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
LIGHT_BG = (240, 240, 240)

CELL_SIZE = 30


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = float("inf")
        self.h = 0
        self.f = float("inf")
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f


def heuristic(a, b, type="manhattan"):
    if type == "manhattan":
        return abs(a.x - b.x) + abs(a.y - b.y)
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def get_neighbors(grid, node, rows, cols):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []

    for dx, dy in directions:
        nx, ny = node.x + dx, node.y + dy
        if 0 <= nx < rows and 0 <= ny < cols and not grid[nx][ny].is_wall:
            neighbors.append(grid[nx][ny])

    return neighbors


def search(grid, start, goal, algorithm="a_star", heur_type="manhattan"):
    for row in grid:
        for node in row:
            node.g = float("inf")
            node.f = float("inf")
            node.parent = None

    start.g = 0
    start.h = heuristic(start, goal, heur_type)
    start.f = start.g + start.h if algorithm == "a_star" else start.h

    open_set = []
    heapq.heappush(open_set, start)
    open_hash = {start}
    closed = set()
    expanded = 0

    while open_set:
        current = heapq.heappop(open_set)
        open_hash.remove(current)
        closed.add(current)
        expanded += 1

        if current == goal:
            return reconstruct_path(current), expanded

        for neighbor in get_neighbors(grid, current, len(grid), len(grid[0])):
            if neighbor in closed:
                continue

            tentative_g = current.g + 1

            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                neighbor.h = heuristic(neighbor, goal, heur_type)
                neighbor.f = (
                    neighbor.g + neighbor.h
                    if algorithm == "a_star"
                    else neighbor.h
                )

                if neighbor not in open_hash:
                    heapq.heappush(open_set, neighbor)
                    open_hash.add(neighbor)

    return None, expanded


def reconstruct_path(current):
    path = []
    while current:
        path.append(current)
        current = current.parent
    return path[::-1]


class GridNode(Node):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.is_wall = False
        self.is_start = False
        self.is_goal = False

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class PathFinder:
    def __init__(self, rows=20, cols=20):
        pygame.init()

        self.rows = rows
        self.cols = cols
        self.sidebar_width = 320
        
        self.grid_width = cols * CELL_SIZE
        self.grid_height = rows * CELL_SIZE

        self.window_height = max(self.grid_height, 750)
        self.window_width = self.grid_width + self.sidebar_width

        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height)
        )
        
        pygame.display.set_caption("Dynamic Pathfinding Agent")

        self.clock = pygame.time.Clock()

        self.grid = [[GridNode(i, j) for j in range(cols)] for i in range(rows)]

        self.start = self.grid[0][0]
        self.start.is_start = True

        self.goal = self.grid[rows - 1][cols - 1]
        self.goal.is_goal = True

        self.algorithm = "a_star"
        self.heuristic = "manhattan"
        self.obstacle_density = 0.3
        self.dynamic_mode = False
        self.edit_mode = False

        self.path = None
        self.current_pos = self.start

        self.spawn_prob = 0.01
        self.last_move_time = 0
        self.move_delay = 200

        self.metrics = {
            "nodes_visited": 0,
            "path_cost": 0,
            "exec_time": 0,
        }

        self.running = True

    def generate_map(self):
        for row in self.grid:
            for node in row:
                if node != self.start and node != self.goal:
                    node.is_wall = random.random() < self.obstacle_density

    def run_search(self):
        start_time = time.time()
        self.path, self.metrics["nodes_visited"] = search(
            self.grid,
            self.current_pos,
            self.goal,
            self.algorithm,
            self.heuristic,
        )
        self.metrics["exec_time"] = (time.time() - start_time) * 1000
        self.metrics["path_cost"] = len(self.path) - 1 if self.path else 0

    def simulate_movement(self):
        if not self.path or self.current_pos == self.goal:
            return

        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_delay:
            return

        self.last_move_time = now

        idx = self.path.index(self.current_pos) + 1
        if idx >= len(self.path):
            return

        next_node = self.path[idx]

        if self.dynamic_mode and random.random() < self.spawn_prob:
            empty = [
                n
                for row in self.grid
                for n in row
                if not n.is_wall
                and n not in (self.start, self.goal, self.current_pos)
            ]
            if empty:
                random.choice(empty).is_wall = True
                self.run_search()
                return

        if not next_node.is_wall:
            self.current_pos = next_node
        else:
            self.run_search()

    def handle_click(self, pos):
        if not self.edit_mode:
            return

        x = pos[1] // CELL_SIZE
        y = pos[0] // CELL_SIZE

        if 0 <= x < self.rows and 0 <= y < self.cols:
            node = self.grid[x][y]
            if node not in (self.start, self.goal):
                node.is_wall = not node.is_wall

    def draw_grid(self):
        for i in range(self.rows):
            for j in range(self.cols):
                node = self.grid[i][j]
                color = WHITE

                if node.is_wall:
                    color = BLACK
                elif node.is_start:
                    color = GREEN
                elif node.is_goal:
                    color = RED
                elif self.path and node in self.path:
                    color = (180, 255, 180)

                pygame.draw.rect(
                    self.screen,
                    color,
                    (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )
                pygame.draw.rect(
                    self.screen,
                    GRAY,
                    (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                    1,
                )

        if self.current_pos:
            pygame.draw.rect(
                self.screen,
                BLUE,
                (
                    self.current_pos.y * CELL_SIZE,
                    self.current_pos.x * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                ),
            )

        sidebar_x = self.cols * CELL_SIZE
        self.screen.fill(
            LIGHT_BG,
            (sidebar_x, 0, self.sidebar_width, self.rows * CELL_SIZE),
        )

        title_font = pygame.font.SysFont("arial", 28, bold=True)
        section_font = pygame.font.SysFont("arial", 22, bold=True)
        text_font = pygame.font.SysFont("arial", 20)

        y = 20

        title = title_font.render("Pathfinding Panel", True, BLACK)
        self.screen.blit(title, (sidebar_x + 20, y))
        y += 50

        section = section_font.render("Settings", True, BLACK)
        self.screen.blit(section, (sidebar_x + 20, y))
        y += 35

        settings = [
            f"Algorithm: {self.algorithm.upper()}",
            f"Heuristic: {self.heuristic.capitalize()}",
            f"Obstacle Density: {int(self.obstacle_density * 100)}%",
            f"Dynamic Mode: {'ON' if self.dynamic_mode else 'OFF'}",
            f"Edit Mode: {'ON' if self.edit_mode else 'OFF'}",
        ]

        for s in settings:
            self.screen.blit(text_font.render(s, True, BLACK), (sidebar_x + 30, y))
            y += 30

        y += 20

        section = section_font.render("Controls", True, BLACK)
        self.screen.blit(section, (sidebar_x + 20, y))
        y += 35

        controls = [
            "G - Generate Map",
            "A - Toggle Algorithm",
            "H - Toggle Heuristic",
            "D - Toggle Dynamic Mode",
            "E - Toggle Edit Mode",
            "S - Start Search",
            "Q - Quit",
        ]

        for c in controls:
            self.screen.blit(text_font.render(c, True, BLACK), (sidebar_x + 30, y))
            y += 28

        y += 20

        section = section_font.render("Metrics", True, BLACK)
        self.screen.blit(section, (sidebar_x + 20, y))
        y += 35

        metrics = [
            f"Nodes Visited: {self.metrics['nodes_visited']}",
            f"Path Cost: {self.metrics['path_cost']}",
            f"Execution Time: {self.metrics['exec_time']:.2f} ms",
        ]

        for m in metrics:
            self.screen.blit(text_font.render(m, True, BLACK), (sidebar_x + 30, y))
            y += 30

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        self.generate_map()
                    elif event.key == pygame.K_a:
                        self.algorithm = (
                            "gbfs"
                            if self.algorithm == "a_star"
                            else "a_star"
                        )
                    elif event.key == pygame.K_h:
                        self.heuristic = (
                            "euclidean"
                            if self.heuristic == "manhattan"
                            else "manhattan"
                        )
                    elif event.key == pygame.K_d:
                        self.dynamic_mode = not self.dynamic_mode
                    elif event.key == pygame.K_e:
                        self.edit_mode = not self.edit_mode
                    elif event.key == pygame.K_s:
                        self.current_pos = self.start
                        self.run_search()
                    elif event.key == pygame.K_q:
                        self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.simulate_movement()

            self.screen.fill(WHITE)
            self.draw_grid()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    app = PathFinder(rows=20, cols=20)
    app.run()