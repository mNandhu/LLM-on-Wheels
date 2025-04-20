# filepath: src/Simulator/simulation_core.py
import pygame
import pygame.freetype
import math
import heapq
from typing import List, Tuple, Optional, Dict, Any


# Helper functions
def _clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(val, max_val))


def circle_rect_collision(
    cx: float, cy: float, radius: float, rect: pygame.Rect
) -> bool:
    # Find the closest point on the rect to the circle center
    closest_x = _clamp(cx, rect.left, rect.right)
    closest_y = _clamp(cy, rect.top, rect.bottom)
    dx = cx - closest_x
    dy = cy - closest_y
    return (dx * dx + dy * dy) < (radius * radius)


# Simple robot representation
class Robot:
    def __init__(self, x: float, y: float, theta: float = 0.0, speed: float = 2.0):
        self.x = x
        self.y = y
        self.theta = theta
        self.speed = speed  # pixels per frame
        # Action execution attributes
        self.current_action: Optional[str] = None
        self.action_params: Dict[str, Any] = {}
        self.action_time_left: float = 0.0
        self.action_status: str = "IDLE"
        # Rotation speed (degrees per second)
        self.angular_speed: float = 90.0
        # path following attributes
        self.path: List[Tuple[float, float]] = []
        self.path_index: int = 0
        self.final_theta: float = theta
        self.nav_status: str = "IDLE"
        self.radius: float = 10.0  # collision radius

    def set_nav_goal(self, x: float, y: float, theta: float):
        # Placeholder: actual planning done in Simulation.send_nav_goal
        self.final_theta = theta
        self.nav_status = "PLANNING"

    def start_action(self, action: str, params: Dict[str, Any]):
        """
        Initiate an animated action: 'rotate' or 'move_forward'.
        """
        self.current_action = action
        self.action_params = params
        # Determine action duration
        if action == "rotate":
            angle = params.get("angle", 0.0)
            self.action_time_left = abs(angle) / self.angular_speed
        elif action == "move_forward":
            # duration provided directly
            self.action_time_left = params.get("duration", 0.0)
        else:
            self.action_time_left = 0.0
        self.action_status = "IN_PROGRESS"

    def update(self, dt: float):
        # Handle ongoing action first
        if self.current_action and self.action_status == "IN_PROGRESS":
            if self.current_action == "rotate":
                target_angle = (self.theta + self.action_params.get("angle", 0)) % 360
                # rotate step
                delta = self.angular_speed * dt
                # Compute minimal circular difference
                diff = (target_angle - self.theta + 540) % 360 - 180
                step = min(delta, abs(diff))
                self.theta = (self.theta + step * (1 if diff >= 0 else -1)) % 360
            elif self.current_action == "move_forward":
                # move step
                distance = self.speed * dt
                rad = math.radians(self.theta)
                self.x += math.cos(rad) * distance
                self.y -= math.sin(rad) * distance
            # decrement timer
            self.action_time_left -= dt
            if self.action_time_left <= 0:
                # Action completed
                self.action_status = "SUCCEEDED"
                self.current_action = None
            return
        # Follow computed path waypoints
        if not self.path or self.nav_status == "SUCCEEDED":
            return
        tx, ty = self.path[self.path_index]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        # Update heading to face movement direction
        if dist > 0:
            rad = math.atan2(-dy, dx)
            self.theta = math.degrees(rad) % 360
        if dist < self.speed:
            # reached waypoint
            self.x, self.y = tx, ty
            if self.path_index == len(self.path) - 1:
                # final goal reached
                self.theta = self.final_theta
                self.nav_status = "SUCCEEDED"
                self.path = []
                self.path_index = 0
            else:
                self.path_index += 1
                self.nav_status = "IN_PROGRESS"
        else:
            # move towards waypoint
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist
            self.nav_status = "IN_PROGRESS"

    def draw(self, surface: pygame.Surface, colors=None):
        # draw robot as a circle with heading indicator
        center = (int(self.x), int(self.y))
        radius = int(self.radius)

        # Use provided colors or defaults
        robot_color = colors.get("robot", (0, 160, 230)) if colors else (0, 160, 230)
        heading_color = (
            colors.get("heading", (255, 255, 255)) if colors else (255, 255, 255)
        )

        # Robot body with glow effect
        pygame.draw.circle(
            surface,
            (robot_color[0] // 2, robot_color[1] // 2, robot_color[2] // 2),
            center,
            radius + 3,
        )
        pygame.draw.circle(surface, robot_color, center, radius)
        pygame.draw.circle(surface, heading_color, center, radius, 1)  # White border

        # heading line
        rad = math.radians(self.theta)
        end_pos = (
            int(self.x + math.cos(rad) * radius * 2),
            int(self.y - math.sin(rad) * radius * 2),
        )
        pygame.draw.line(surface, heading_color, center, end_pos, 2)


# Path planning: simple grid-based A* avoiding rectangular obstacles
def plan_path(
    start: Tuple[float, float],
    goal: Tuple[float, float],
    obstacles: List[pygame.Rect],
    width: int,
    height: int,
    cell_size: int = 20,
) -> List[Tuple[float, float]]:
    cols = width // cell_size
    rows = height // cell_size

    # convert point to cell
    def to_cell(p):
        cx, cy = int(p[0]) // cell_size, int(p[1]) // cell_size
        return max(0, min(cx, cols - 1)), max(0, min(cy, rows - 1))

    # convert cell to center point
    def to_point(c):
        return (c[0] + 0.5) * cell_size, (c[1] + 0.5) * cell_size

    start_cell = to_cell(start)
    goal_cell = to_cell(goal)
    # occupancy grid
    grid = [[0] * rows for _ in range(cols)]
    for ox in range(cols):
        for oy in range(rows):
            cell_rect = pygame.Rect(
                ox * cell_size, oy * cell_size, cell_size, cell_size
            )
            if any(obs.colliderect(cell_rect) for obs in obstacles):
                grid[ox][oy] = 1
    # A* search
    open_set = []
    heapq.heappush(
        open_set,
        (
            0 + abs(goal_cell[0] - start_cell[0]) + abs(goal_cell[1] - start_cell[1]),
            0,
            start_cell,
            None,
        ),
    )
    came_from = {}
    cost_so_far = {start_cell: 0}
    while open_set:
        _, cost, current, parent = heapq.heappop(open_set)
        if current == goal_cell:
            came_from[current] = parent
            break
        if current in came_from:
            continue
        came_from[current] = parent
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nb = (current[0] + dx, current[1] + dy)
            if 0 <= nb[0] < cols and 0 <= nb[1] < rows and grid[nb[0]][nb[1]] == 0:
                new_cost = cost + 1
                if nb not in cost_so_far or new_cost < cost_so_far[nb]:
                    cost_so_far[nb] = new_cost
                    priority = (
                        new_cost + abs(goal_cell[0] - nb[0]) + abs(goal_cell[1] - nb[1])
                    )
                    heapq.heappush(open_set, (priority, new_cost, nb, current))
    # reconstruct path
    path = []
    node = goal_cell
    if node not in came_from:
        return []
    while node:
        path.append(to_point(node))
        node = came_from[node]
    path.reverse()
    return path


# Simple environment with obstacles
class Environment:
    def __init__(self, obstacles: List[pygame.Rect] = None):
        self.obstacles = obstacles or []

    def draw(self, surface: pygame.Surface, color=(200, 60, 80)):
        for obs in self.obstacles:
            pygame.draw.rect(surface, color, obs)
            pygame.draw.rect(surface, (255, 255, 255), obs, 1)  # White border


# Main simulation class
class Simulation:
    def __init__(self, width: int = 800, height: int = 600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        # store dimensions for rendering
        self.width = width
        self.height = height
        pygame.display.set_caption("LLM on Wheels - Exploration Simulation")
        self.clock = pygame.time.Clock()
        self.running = False
        # initialize robot in center
        self.robot = Robot(width / 2, height / 2)
        # example static obstacles
        obs1 = pygame.Rect(100, 100, 50, 50)
        obs2 = pygame.Rect(500, 300, 100, 20)
        self.env = Environment([obs1, obs2])
        # UI elements
        pygame.freetype.init()
        self.font = pygame.freetype.SysFont("Arial", 16)
        self.title_font = pygame.freetype.SysFont("Arial", 20, bold=True)
        self.button_font = pygame.freetype.SysFont("Arial", 16, bold=True)
        # Create a properly sized button - measure text first to ensure proper sizing
        text_rect = self.button_font.get_rect("Record Audio")
        button_width = text_rect.width + 30  # Add padding
        button_height = text_rect.height + 20  # Add padding
        self.record_button = pygame.Rect(20, 20, button_width, button_height)
        self.record_pressed = False
        # Initialize objects for detection (example static objects)
        cup_rect = pygame.Rect(200, 150, 20, 20)
        book_rect = pygame.Rect(600, 400, 30, 20)
        self.objects = [
            {"entry_id": "obj1", "rect": cup_rect, "label": "cup", "confidence": 0.92},
            {
                "entry_id": "obj2",
                "rect": book_rect,
                "label": "book",
                "confidence": 0.85,
            },
        ]
        # Memory storage for mapped objects
        self.memory_data: dict = {}
        # Create Map Area button below Record Audio
        map_text = "Map Area"
        text_rect2 = self.button_font.get_rect(map_text)
        map_w = text_rect2.width + 30
        map_h = text_rect2.height + 20
        self.map_button = pygame.Rect(20, self.record_button.bottom + 10, map_w, map_h)
        self.map_pressed = False

        # Color scheme for dark theme
        self.colors = {
            "background": (15, 15, 25),
            "grid": (30, 30, 40),
            "panel": (40, 40, 55, 220),
            "text": (220, 220, 230),
            "button": (60, 80, 140),
            "button_hover": (80, 100, 170),
            "button_text": (255, 255, 255),
            "robot": (0, 160, 230),
            "heading": (255, 255, 255),
            "obstacle": (200, 60, 80),
        }

    def handle_events(self) -> List[pygame.event.EventType]:
        """
        Poll events, handle quit, and return all events for external UI.
        """
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.record_button.collidepoint(event.pos):
                    self.record_pressed = True
                elif self.map_button.collidepoint(event.pos):
                    self.map_pressed = True
        return events

    def map_area(self):
        """
        Simulate object detection and build memory data.
        """
        data = {"object_instances": {}}
        for obj in self.objects:
            cx, cy = obj["rect"].center
            entry = {
                "entry_id": obj["entry_id"],
                "entry_type": "object",
                "label": obj["label"],
                "confidence": obj["confidence"],
                "map_coordinates": {"x": float(cx), "y": float(cy), "theta": 0.0},
                "timestamp": "",
                "detected_in_images": [],
            }
            data["object_instances"][obj["entry_id"]] = entry
        self.memory_data = data
        print(f"[Simulation] Mapped area: {len(self.objects)} objects detected")
        self.map_pressed = False

    def update(self, dt: float):
        prev_x, prev_y, prev_theta = self.robot.x, self.robot.y, self.robot.theta
        self.robot.update(dt)
        # Detect collision with any obstacle and revert if needed
        for obs in self.env.obstacles:
            if circle_rect_collision(
                self.robot.x, self.robot.y, self.robot.radius, obs
            ):
                # collision: revert position and cancel navigation
                self.robot.x, self.robot.y, self.robot.theta = (
                    prev_x,
                    prev_y,
                    prev_theta,
                )
                self.robot.nav_status = "FAILED"
                self.robot.path = []
                self.robot.path_index = 0
                break

    def draw(self):
        # clear background and draw grid
        self.screen.fill(self.colors["background"])
        grid_size = 50
        for x in range(0, self.width + grid_size, grid_size):
            pygame.draw.line(self.screen, self.colors["grid"], (x, 0), (x, self.height))
        for y in range(0, self.height + grid_size, grid_size):
            pygame.draw.line(self.screen, self.colors["grid"], (0, y), (self.width, y))

        # draw title
        title_text = "LLM on Wheels - Exploration Mode"
        title_rect = self.title_font.get_rect(title_text)
        title_pos = (self.width // 2 - title_rect.width // 2, 20)
        self.title_font.render_to(
            self.screen, title_pos, title_text, self.colors["text"]
        )

        # draw environment
        self.env.draw(self.screen, self.colors["obstacle"])
        # draw objects (detectable entities)
        for obj in self.objects:
            pygame.draw.rect(self.screen, (255, 200, 0), obj["rect"])
            # label above object
            label = obj["label"]
            pos = (obj["rect"].x, obj["rect"].y - 5)
            self.font.render_to(self.screen, pos, label, self.colors["text"])

        # draw planned path
        if self.robot.path:
            # connect waypoints
            for i in range(len(self.robot.path) - 1):
                start = (int(self.robot.path[i][0]), int(self.robot.path[i][1]))
                end = (int(self.robot.path[i + 1][0]), int(self.robot.path[i + 1][1]))
                pygame.draw.line(self.screen, (0, 255, 0), start, end, 2)
            # mark waypoints
            for wp in self.robot.path:
                pygame.draw.circle(
                    self.screen, (255, 255, 0), (int(wp[0]), int(wp[1])), 3
                )

        # draw robot
        self.robot.draw(self.screen, self.colors)

        # draw record button with rounded corners and hover effect
        is_hover = self.record_button.collidepoint(pygame.mouse.get_pos())
        btn_color = self.colors["button_hover"] if is_hover else self.colors["button"]

        # Draw button with glow effect when hovering
        if is_hover:
            glow_rect = self.record_button.inflate(6, 6)
            glow_surf = pygame.Surface(
                (glow_rect.width, glow_rect.height), pygame.SRCALPHA
            )
            glow_surf.fill((0, 0, 0, 0))
            pygame.draw.rect(
                glow_surf, (100, 140, 255, 150), glow_surf.get_rect(), border_radius=10
            )
            self.screen.blit(glow_surf, glow_rect.topleft)

        pygame.draw.rect(self.screen, btn_color, self.record_button, border_radius=8)
        pygame.draw.rect(
            self.screen, (255, 255, 255), self.record_button, 2, border_radius=8
        )

        # Center text in button
        button_text = "Record Audio"
        text_rect = self.button_font.get_rect(button_text)
        text_pos = (
            self.record_button.x + (self.record_button.width - text_rect.width) // 2,
            self.record_button.y + (self.record_button.height - text_rect.height) // 2,
        )
        self.button_font.render_to(
            self.screen,
            text_pos,
            button_text,
            self.colors["button_text"],
        )

        # draw map button
        is_hover_map = self.map_button.collidepoint(pygame.mouse.get_pos())
        btn_color_map = (
            self.colors["button_hover"] if is_hover_map else self.colors["button"]
        )
        pygame.draw.rect(self.screen, btn_color_map, self.map_button, border_radius=8)
        pygame.draw.rect(
            self.screen, (255, 255, 255), self.map_button, 2, border_radius=8
        )
        # map button text
        text_rect2 = self.button_font.get_rect("Map Area")
        text_pos2 = (
            self.map_button.x + (self.map_button.width - text_rect2.width) // 2,
            self.map_button.y + (self.map_button.height - text_rect2.height) // 2,
        )
        self.button_font.render_to(
            self.screen, text_pos2, "Map Area", self.colors["button_text"]
        )

        # draw info panel with semi-transparent background
        panel_width = 250
        panel_height = 100
        panel_rect = pygame.Rect(
            self.width - panel_width - 20, 20, panel_width, panel_height
        )
        panel_surf = pygame.Surface(
            (panel_rect.width, panel_rect.height), pygame.SRCALPHA
        )
        panel_surf.fill(self.colors["panel"])
        self.screen.blit(panel_surf, panel_rect.topleft)

        # Panel header
        panel_header = "Robot Status"
        self.button_font.render_to(
            self.screen,
            (panel_rect.x + 10, panel_rect.y + 10),
            panel_header,
            self.colors["text"],
        )

        # Panel content with more space
        pose_text = f"Position: {self.robot.x:.1f}, {self.robot.y:.1f}"
        angle_text = f"Heading: {self.robot.theta:.1f}°"
        status_text = f"Navigation: {self.robot.nav_status}"

        self.font.render_to(
            self.screen,
            (panel_rect.x + 10, panel_rect.y + 35),
            pose_text,
            self.colors["text"],
        )
        self.font.render_to(
            self.screen,
            (panel_rect.x + 10, panel_rect.y + 55),
            angle_text,
            self.colors["text"],
        )
        self.font.render_to(
            self.screen,
            (panel_rect.x + 10, panel_rect.y + 75),
            status_text,
            self.colors["text"],
        )

        # display mapped memory data below map button
        if self.memory_data.get("object_instances"):
            y0 = self.map_button.bottom + 10
            for i, entry in enumerate(self.memory_data["object_instances"].values()):
                txt = f"{entry['label']} @ ({entry['map_coordinates']['x']:.0f},{entry['map_coordinates']['y']:.0f})"
                self.font.render_to(
                    self.screen, (20, y0 + i * 20), txt, self.colors["text"]
                )

        pygame.display.flip()

    def step(self) -> List[pygame.event.EventType]:
        """
        Process one frame: poll events, update physics, draw, and return events.
        """
        dt = self.clock.tick(30) / 1000.0
        events = self.handle_events()
        # trigger mapping if requested
        if self.map_pressed:
            self.map_area()
        self.update(dt)
        self.draw()
        return events

    def run(self):
        self.running = True
        while self.running:
            self.step()

    def shutdown(self):
        pygame.quit()

    def get_and_clear_record_flag(self) -> bool:
        """
        Return and clear the record button press flag.
        """
        flag = self.record_pressed
        self.record_pressed = False
        return flag

    def send_nav_goal(self, x: float, y: float, theta: float):
        """
        Plan obstacle-avoiding path and set robot path.
        """
        # Debug: planning path
        print(
            f"[Simulation] send_nav_goal: planning from ({self.robot.x:.1f}, {self.robot.y:.1f}) to ({x:.1f}, {y:.1f})"
        )
        # compute path waypoints
        path = plan_path(
            (self.robot.x, self.robot.y),
            (x, y),
            self.env.obstacles,
            self.width,
            self.height,
        )
        if path:
            # Replace last waypoint (cell center) with exact goal to avoid half-cell offset
            path[-1] = (x, y)
            print(
                f"[Simulation] Path found with {len(path)} waypoints (adjusted final waypoint to exact target)"
            )
            self.robot.path = path
            self.robot.path_index = 0
            if theta is not None:
                self.robot.final_theta = theta
            self.robot.nav_status = "IN_PROGRESS"
        else:
            print("[Simulation] No path found, navigation failed")
            # no path found
            self.robot.nav_status = "FAILED"
