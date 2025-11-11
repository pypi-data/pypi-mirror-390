from colorama import Fore, Style
from ghostguard.core.corrector import run_corrector
from ghostguard.core.talk import run_smart_talk
from ghostguard.utils.formatter import animated_banner, render_menu

def main():
    """
    Launch Ghost interactive CLI with animated banner and menu.
    This is the entry point for the console script.
    """
    animated_banner(title="ghost", version="1.6", subtitle="Smart CLI Assistant")

    while True:
        render_menu()
        choice = input(Fore.CYAN + "\nEnter choice > " + Style.RESET_ALL).strip()

        if choice == "1":
            run_smart_talk()
        elif choice == "2":
            run_corrector()
        elif choice == "3":
            print(Fore.RED + "\nGoodbye ")
            break
        else:
            print(Fore.YELLOW + "Invalid choice — try again.\n")
