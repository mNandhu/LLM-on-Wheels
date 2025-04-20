from ..config.constants import DEBUG_CONFIG

COLORED_OUTPUT = DEBUG_CONFIG.get("colored_output", True)


# ANSI color codes
class Colors:
    HEADER = "\033[95m" if COLORED_OUTPUT else ""
    BLUE = "\033[94m" if COLORED_OUTPUT else ""
    GREEN = "\033[92m" if COLORED_OUTPUT else ""
    YELLOW = "\033[93m" if COLORED_OUTPUT else ""
    RED = "\033[91m" if COLORED_OUTPUT else ""
    ENDC = "\033[0m" if COLORED_OUTPUT else ""
