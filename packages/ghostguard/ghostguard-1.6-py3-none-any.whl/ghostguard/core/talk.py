from colorama import Fore, Style
from .ai import fix_code
from .voice import speak

def run_smart_talk():
    """
    Smart Talk CLI with both female voice and text output.
    """
    print(Fore.GREEN + Style.BRIGHT + "\n Ghost Smart Talk Mode [v1.1]")
    print(Fore.YELLOW + "Type your prompt below. Type 'exit' to quit.\n")

    while True:
        user_input = input(Fore.CYAN + "You: " + Style.RESET_ALL)
        if user_input.lower() == "exit":
            print(Fore.RED + " Exiting Smart Talk...")
            break

        response = fix_code(user_input)
        print(Fore.MAGENTA + "Ghost: " + Fore.WHITE + response)
        speak(response, female=True)
