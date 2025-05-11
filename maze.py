import random


class Maze:
    def __init__(self, width, height):
        """
        Initialize a maze with given dimensions.
        Width and height should be odd numbers.
        """
        self.width = width
        self.height = height
        self.grid = self._generate_maze()
        self.start_pos, self.exit_pos = self._set_start_and_exit()
        self.powerup_positions = self._place_powerups()

    def _generate_maze(self):
        """
        Generate a maze using recursive backtracking algorithm.
        Return a 2D grid where:
            1 = wall
            0 = path
        """
        # Initialize grid with walls
        grid = [[1 for _ in range(self.width)] for _ in range(self.height)]

        # Helper function for recursive backtracking
        def carve_passages(x, y, grid):
            # Mark current cell as path
            grid[y][x] = 0

            # Define possible directions to move: (dx, dy)
            directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
            random.shuffle(directions)

            # Try each direction
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy

                # Check if the new position is within bounds and is a wall
                if (
                    0 < new_x < self.width - 1
                    and 0 < new_y < self.height - 1
                    and grid[new_y][new_x] == 1
                ):
                    # Carve passage by making the wall between current and new cell a path
                    grid[y + dy // 2][x + dx // 2] = 0
                    # Continue from the new cell
                    carve_passages(new_x, new_y, grid)

        # Start from a random cell (must be odd coordinates)
        start_x = random.randrange(1, self.width - 1, 2)
        start_y = random.randrange(1, self.height - 1, 2)
        carve_passages(start_x, start_y, grid)

        # Braid the maze to add loops and multiple paths
        self._braid_maze(grid, braid_chance=0.12)
        return grid

    def _braid_maze(self, grid, braid_chance=0.12):
        """
        Randomly remove some walls to create loops and multiple paths.
        """
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if grid[y][x] == 1:
                    neighbors = []
                    if grid[y - 1][x] == 0:
                        neighbors.append((y - 1, x))
                    if grid[y + 1][x] == 0:
                        neighbors.append((y + 1, x))
                    if grid[y][x - 1] == 0:
                        neighbors.append((y, x - 1))
                    if grid[y][x + 1] == 0:
                        neighbors.append((y, x + 1))
                    if len(neighbors) == 2 and random.random() < braid_chance:
                        grid[y][x] = 0

    def _set_start_and_exit(self):
        """
        Set random start and exit positions at opposite ends of the maze.
        """
        # Find all valid path cells
        path_cells = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.grid[y][x] == 0
        ]

        # Choose two distant cells
        start_pos = random.choice(path_cells)

        # Find the farthest cell from start (approximation)
        farthest_cell = None
        max_distance = 0

        for cell in path_cells:
            # Manhattan distance
            distance = abs(cell[0] - start_pos[0]) + abs(cell[1] - start_pos[1])
            if distance > max_distance:
                max_distance = distance
                farthest_cell = cell

        return start_pos, farthest_cell

    def _place_powerups(self):
        """
        Place power-ups randomly in the maze.
        """
        from config import POWERUP_COUNT

        # Find valid path cells excluding start and exit
        path_cells = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.grid[y][x] == 0
            and (x, y) != self.start_pos
            and (x, y) != self.exit_pos
        ]

        # Choose random positions for power-ups
        if len(path_cells) < POWERUP_COUNT:
            return random.sample(path_cells, len(path_cells))
        else:
            return random.sample(path_cells, POWERUP_COUNT)

    def is_wall(self, x, y):
        """
        Check if the given position is a wall.
        """
        # Check if position is outside the maze bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True

        # Check if position is a wall
        return self.grid[y][x] == 1

    def is_valid_move(self, x, y):
        """
        Check if the given position is a valid move (not a wall).
        """
        return not self.is_wall(x, y)

    def get_neighbors(self, x, y):
        """
        Get valid neighboring cells (for pathfinding).
        """
        neighbors = []
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Up, Right, Down, Left
            nx, ny = x + dx, y + dy
            if self.is_valid_move(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
