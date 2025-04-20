# filepath: src/Simulator/simulation_core.py
import pygame
import pygame.freetype
import math
from typing import List, Tuple, Optional


# Simple robot representation
class Robot:
    def __init__(self, x: float, y: float, theta: float = 0.0, speed: float = 2.0):
        self.x = x
        self.y = y
        self.theta = theta
        self.speed = speed  # pixels per frame
        self.nav_target: Optional[Tuple[float, float, float]] = None
        self.nav_status: str = "IDLE"

    def set_nav_goal(self, x: float, y: float, theta: float):
        self.nav_target = (x, y, theta)
        self.nav_status = "PLANNING"

    def update(self):
        if not self.nav_target:
            return
        tx, ty, ttheta = self.nav_target
        # simple straight-line movement
        dx, dy = tx - self.x, ty - self.y
        dist = (dx**2 + dy**2) ** 0.5
        if dist < self.speed:
            # reached target
            self.x, self.y, self.theta = tx, ty, ttheta
            self.nav_status = "SUCCEEDED"
            self.nav_target = None
        else:
            # move towards target
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist
            self.nav_status = "IN_PROGRESS"

    def draw(self, surface: pygame.Surface, colors=None):
        # draw robot as a circle with heading indicator
        center = (int(self.x), int(self.y))
        radius = 10

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
        obs2 = pygame.Rect(400, 300, 100, 20)
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
        return events

    def update(self, dt: float):
        self.robot.update()

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

        # draw environment and robot
        self.env.draw(self.screen, self.colors["obstacle"])
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

        pygame.display.flip()

    def step(self) -> List[pygame.event.EventType]:
        """
        Process one frame: poll events, update physics, draw, and return events.
        """
        dt = self.clock.tick(30) / 1000.0
        events = self.handle_events()
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
