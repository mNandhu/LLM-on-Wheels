# filepath: src/main_simulation.py
"""
Main orchestrator for running the exploration simulation alongside the GraphAgent.
"""

import pygame
import threading
from src.Simulator.simulation_api import (
    initialize_simulation,
    shutdown_simulation,
    step_simulation,
    get_and_clear_record_flag,
)
from src.GraphAgent.core.graph import WorkFlow


def main():
    # Initialize simulation and agent
    initialize_simulation()
    wf = WorkFlow()
    print(wf.display_graph())

    # Helper to run the agent flow without blocking the simulation
    def run_agent(audio):
        result = wf.invoke(audio, {}, debugMode=False)
        resp = result.get("llm_response_text") or result.get("final_response_text")
        print(f"\nAI> {resp}")

    try:
        # Main loop: step simulation, handle record button
        while True:
            events = step_simulation()
            # Exit on window close
            for e in events:
                if e.type == pygame.QUIT:
                    return
            # If record button pressed, capture audio and invoke agent
            if get_and_clear_record_flag():
                audio = None  # placeholder for audio input
                # Launch agent flow in background thread to keep simulation updating
                threading.Thread(target=run_agent, args=(audio,), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[Main] Interrupted by user. Shutting down...")
    finally:
        shutdown_simulation()


if __name__ == "__main__":
    main()
