import sys


def confirm_authorized(target: str, flag_provided: bool) -> bool:
    """
    Checks if the user has authorized scanning the target.
    If the --i-have-authorization flag is provided, returns True.
    Otherwise, if the session is interactive, prompts the user.
    If not interactive and no flag, returns False.
    """
    if flag_provided:
        return True

    # Check if we are running in an interactive terminal
    if not sys.stdout.isatty():
        return False

    print(f"\n[WARNING] You are about to initiate a scan against: {target}")
    print("This tool is for educational purposes and authorized testing only.")
    print("Do you have explicit permission to scan this target?")

    try:
        response = input("Type 'y' to confirm or 'N' to cancel [y/N]: ").strip().lower()
        return response == "y"
    except (EOFError, KeyboardInterrupt):
        return False
