# filepath: src/Simulator/simulation_api.py
import pygame
import math
from typing import List

from .simulation_core import Simulation

# Global simulation instance
_simulation: Simulation = None


def initialize_simulation():
    """
    Initialize the simulation.
    """
    global _simulation
    if _simulation is None:
        _simulation = Simulation(width=1920, height=1080)


def shutdown_simulation():
    """
    Signal the simulation to stop.
    """
    global _simulation
    if _simulation is not None:
        _simulation.shutdown()


def get_current_pose_from_sim() -> tuple:
    """
    Return the current pose (x, y, theta) of the simulated robot.
    """
    global _simulation
    if _simulation is None:
        return (0.0, 0.0, 0.0)
    r = _simulation.robot
    return (r.x, r.y, r.theta)


def send_nav_goal_to_sim(x: float, y: float, theta: float) -> None:
    """
    Send a navigation goal to the simulated robot.
    """
    global _simulation
    if _simulation is not None:
        # Use Simulation.send_nav_goal to perform path planning
        _simulation.send_nav_goal(x, y, theta)


def get_nav_status_from_sim() -> str:
    """
    Get the current navigation status of the simulated robot.
    """
    global _simulation
    if _simulation is None:
        return "UNKNOWN"
    return _simulation.robot.nav_status


def execute_robot_action_in_sim(action: str, params: dict) -> str:
    """
    Execute a direct robot action in simulation (e.g., rotate).

    Returns a status string.
    """
    global _simulation
    if _simulation is None:
        return "SIM_NOT_INITIALIZED"
    # Initiate animated action on robot
    if action in ("rotate", "move_forward"):
        _simulation.robot.start_action(action, params)
        return "IN_PROGRESS"
    # Unknown action
    return "UNKNOWN_ACTION"


def get_and_clear_record_flag() -> bool:
    """
    Return and clear the record button press flag from the simulation.
    """
    global _simulation
    if _simulation is None:
        return False
    return _simulation.get_and_clear_record_flag()


def step_simulation() -> List[pygame.event.Event]:
    """
    Advance the simulation by one frame: process events, update, draw, and return the events list.
    """
    global _simulation
    if not _simulation:
        return []
    return _simulation.step()


def get_memory_data_from_sim() -> dict:
    """
    Return the mapped memory data collected by the simulation.
    """
    global _simulation
    if _simulation is None or not hasattr(_simulation, "memory_data"):
        return {}
    return _simulation.memory_data
