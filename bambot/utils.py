# bambot/utils.py
import random
import string
import logging
from colorama import Fore, Style
from halo import Halo
import docker
from contextlib import contextmanager


def generate_app_name():
    # Simplified structure with less verbosity
    prefix = "bambot"
    # Combine adjectives and nouns for more combinations with fewer parts
    descriptors = ["cool", "smart", "super", "zap", "zip", "jet", "jam", "pod"]
    # Generate a two-digit number to reduce length but maintain uniqueness
    number = random.choices(string.digits, k=2)
    return f"{prefix}-{random.choice(descriptors)}-{'' .join(number)}"

def setup_logging():
    """Set up colored logging for better visual feedback"""
    logger = logging.getLogger("bam_logger")
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter("[%(levelname)s] %(message)s"))
    logger.addHandler(console_handler)

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        super().__init__(msg)
        self.use_color = use_color

    def format(self, record):
        level_color = {
            "DEBUG": Fore.CYAN,
            "INFO": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.RED + Style.BRIGHT
        }
        if self.use_color and record.levelname in level_color:
            record.msg = level_color[record.levelname] + record.msg + Style.RESET_ALL
        return super().format(record)

def echo_info(message, spinner=None):
    """Print an informational message with a spinner"""
    if spinner:
        spinner.start(text=message)
    else:
        print(Fore.GREEN + "[*] " + str(message) + Style.RESET_ALL)

def echo_success(message):
    """Print a success message"""
    print(Fore.GREEN + "[✓] " + str(message) + Style.RESET_ALL)

def echo_warning(message):
    """Print a warning message"""
    print(Fore.YELLOW + "[!] " + str(message) + Style.RESET_ALL)

def echo_error(message):
    """Print an error message"""
    print(Fore.RED + "[✗] " + str(message) + Style.RESET_ALL)

@contextmanager
def contextmanager_spinner(message):
    """Context manager for displaying a spinner"""
    spinner = Halo(text=message, spinner="dots")
    spinner.start()
    try:
        yield spinner
    finally:
        spinner.stop()

def confirm_with_style(message, default=False):
    """Prompt the user for confirmation with a styled message"""
    prompt = f"{Fore.YELLOW}[?]{Style.RESET_ALL} {message} "
    if default:
        prompt += f"[{Fore.GREEN}Y{Style.RESET_ALL}/{Fore.RED}n{Style.RESET_ALL}]"
    else:
        prompt += f"[{Fore.RED}y{Style.RESET_ALL}/{Fore.GREEN}N{Style.RESET_ALL}]"

    while True:
        user_input = input(f"{prompt}? ").strip().lower()
        if user_input in ("y", "yes"):
            return True
        elif user_input in ("n", "no"):
            return False
        elif not user_input and default is not None:
            return default

def prune_system():
    """Prune unused Docker resources"""
    docker_client = docker.from_env()
    docker_client.containers.prune()
    docker_client.images.prune()
    docker_client.networks.prune()
    docker_client.volumes.prune()
    echo_success("Unused Docker resources cleaned up successfully!")