import os
import platform

def has_gui() -> bool:
    # Check if DISPLAY environment variable is set (common in Unix-like systems)
    if os.name == 'posix' and 'DISPLAY' not in os.environ:
        return False
    # Windows and macOS are generally running under a GUI
    elif os.name == 'nt' or platform.system() == 'Darwin':
        return True
    return False


def get_arch_and_system() -> [str, str]:
    import platform
    machine = platform.machine()  # Gets CPU architecture (e.g., 'x86_64', 'arm64')
    system = platform.system()  # Gets OS name (e.g., 'Linux', 'Darwin', 'Windows')

    return [machine, system]
