# filepath: src/main_simulation.py
"""
Main orchestrator for running the exploration simulation alongside the GraphAgent.
"""

import pygame
from src.Simulator.simulation_api import (
    initialize_simulation,
    shutdown_simulation,
    step_simulation,
    get_and_clear_record_flag,
)
from src.GraphAgent.core.graph import WorkFlow
from src.GraphAgent.utils.audio import record_audio


def main():
    # Initialize simulation and agent
    initialize_simulation()
    wf = WorkFlow()
    print(wf.display_graph())
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
                audio = None  # record_audio()
                result = wf.invoke(audio, {}, debugMode=False)
                # Print agent response
                resp = result.get("llm_response_text") or result.get(
                    "final_response_text"
                )
                print(f"\nAI> {resp}")
    except KeyboardInterrupt:
        print("\n[Main] Interrupted by user. Shutting down...")
    finally:
        shutdown_simulation()


if __name__ == "__main__":
    main()
