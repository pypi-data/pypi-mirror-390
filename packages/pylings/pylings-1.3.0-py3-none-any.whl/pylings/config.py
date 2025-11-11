"""
Manages the Pylings configuration lifecycle using `pylings.toml`.

This module defines the `ConfigManager` class, which handles:
- Loading and reloading workspace configuration from `pylings.toml`.
- Tracking and persisting the user's current exercise path.
- Detecting first-time usage and displaying a welcome message.
- Extracting hints for exercises from the configuration file.
- Resolving relative paths for solution files within the workspace.

It uses the `toml` module for structured reading/writing of the TOML config file,
and integrates with command-line arguments via `PylingsUtils`.

Intended to be used internally by the Pylings CLI to manage user state and preferences.
"""
import logging
from os import path
from sys import argv
from toml import dump, load

from pylings.constants import (
    CLEAR_SCREEN,
    CONFIG_FILE,
    PYLINGS_TOML,
    HINT_TITLE,
    NO_EXERCISE_MESSAGE,
    NO_HINT_MESSAGE,
)
from pylings.utils import PylingsUtils

log = logging.getLogger(__name__)

class ConfigManager:
    """Handles loading, accessing, and updating the Pylings configuration from `pylings.toml`."""

    def __init__(self):
        """Initialize ConfigManager by loading the current configuration from disk."""
        log.debug("ConfigManager.__init__: Entered")
        self.config = self.load_config()

    def load_config(self):
        """Load and return the configuration from `CONFIG_FILE`."""
        log.debug("ConfigManager.load_config.CONFIG_FILE: %s", {CONFIG_FILE})
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return load(f)

    def check_first_time(self):
        """
        Check if the app is being run for the first time.

        - Reads the `firsttime` flag from `pylings.toml`.
        - Displays a welcome message if set.
        - Resets the `firsttime` flag to False.
        - Returns True if it was the first time, otherwise False.
        """
        log.debug("ConfigManager.check_first_time: Entered")
        args = PylingsUtils.parse_args()
        num_args = len(argv) - 1

        if num_args == 0 or args.debug or (args.command == "run" and hasattr(args, "file")):
            try:
                with open(PYLINGS_TOML, "r", encoding="utf-8") as f:
                    self.config = load(f)
                if self.config["workspace"].get("firsttime", False):
                    log.debug("ConfigManager.check_first_time: First time detected")
                    self.config["workspace"]["firsttime"] = False
                    with open(PYLINGS_TOML, "w", encoding="utf-8") as f:
                        dump(self.config, f)

                    self.config = self.load_config()
                    welcome_message = self.config["settings"].get(
                        "welcome_message", "Welcome to Pylings!"
                    )
                    print(CLEAR_SCREEN, end="", flush=True)
                    print("Welcome message:", welcome_message)
                    input("\nPress Enter to continue.")
                    return True
                return False
            except FileNotFoundError:
                print("Error: The file {PYLINGS_TOML} does not exist.")
                return False
        return False

    def get_lasttime_exercise(self):
        """
        Retrieve the last exercise path the user worked on.

        Returns:
            str: Relative path to the last exercise, or the default "00_intro/intro1.py" if not set.
        """
        log.debug("ConfigManager.get_lasttime_exercise: entered")
        try:
            with open(PYLINGS_TOML, "r", encoding="utf-8") as f:
                self.config = load(f)
            return self.config["workspace"].get("current_exercise", "00_intro/intro1.py")
        except FileNotFoundError:
            log.error("PYLINGS_TOML not found: %s", {PYLINGS_TOML})
            return "00_intro/intro1.py"

    def set_lasttime_exercise(self, current_exercise):
        """
        Save the path of the currently active exercise to `pylings.toml`.

        Args:
            current_exercise (Path or str): Full path to the current exercise file.
        """
        log.debug("ConfigManager.set_lasttime_exercise: entered")
        try:
            normalized_path = path.normpath(str(current_exercise))
            path_parts = normalized_path.split(path.sep + "exercises" + path.sep)
            relative_exercise = path_parts[1] if len(path_parts) > 1 else str(current_exercise)

            with open(PYLINGS_TOML, "r", encoding="utf-8") as f:
                self.config = load(f)
            self.config["workspace"]["current_exercise"] = relative_exercise
            with open(PYLINGS_TOML, "w", encoding="utf-8") as f:
                dump(self.config, f)
        except FileNotFoundError:
            log.error("PYLINGS_TOML not found: %s", {PYLINGS_TOML})

    def get_local_solution_path(self, solution_path):
        """
        Extract the relative path of a solution inside the `solutions/` directory.

        Args:
            solution_path (Path or str): Absolute or relative path to the solution.

        Returns:
            str: Path relative to `solutions/`, or fallback to "00_intro/intro1.py" on error.
        """
        log.debug("ConfigManager.get_local_solution_path: entered")
        try:
            normalized_path = path.normpath(str(solution_path))
            path_parts = normalized_path.split(path.sep + "solutions" + path.sep)
            local_path = path_parts[1] if len(path_parts) > 1 else str(solution_path)
            return local_path
        except (IndexError, AttributeError, TypeError) as e:
            log.error("ConfigManager.get_local_solution_path error: %s", e)
            return "00_intro/intro1.py"

    def get_hint(self, current_exercise):
        """
        Fetch the hint associated with the current exercise.

        Args:
            current_exercise (Path or str): Full path to the current exercise.

        Returns:
            str: Hint text, or a default message if none is available.
        """
        log.debug("ConfigManager.get_hint: entered")
        if not current_exercise:
            return NO_EXERCISE_MESSAGE

        base_name = path.basename(str(current_exercise))
        ce_name = path.splitext(base_name)[0].strip()

        for section, data in self.config.items():
            if section.startswith("exercise_"):
                exercise_name = data.get("name", "").strip('"')
                if exercise_name == ce_name:
                    hint = data.get("hint", "")
                    log.debug("Hint found: %s", {hint})
                    escaped_hint = hint.replace('[', '\\[')
                    return f"{HINT_TITLE}\n\n{escaped_hint}"

        log.debug("No hint for: %s", {ce_name})
        return NO_HINT_MESSAGE
# End-of-file (EOF)
