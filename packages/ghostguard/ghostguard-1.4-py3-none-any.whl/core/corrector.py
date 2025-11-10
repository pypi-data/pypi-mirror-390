# Core module for Smart Corrector

from colorama import Fore, Style
from .ai import fix_code, suggest_completion
from .voice import speak  # import TTS

# Windows compatibility for readline
try:
    import readline  # Unix/Linux
except ImportError:
    try:
        import pyreadline3 as readline  # Windows
    except ImportError:
        readline = None
        print(Fore.RED + "[Warning] readline/pyreadline not installed. TAB completion disabled.")

def ai_completer(text, state):
    """Provide AI-generated suggestions for TAB completion."""
    if state == 0:
        ai_completer.matches = suggest_completion(text)
    try:
        return ai_completer.matches[state]
    except IndexError:
        return None

def run_corrector():
    print(Fore.GREEN + Style.BRIGHT + "\n Ghost AI Corrector Mode [v1.1]")
    print(Fore.YELLOW + "Type Python or shell commands. Press TAB for AI suggestions (if available).")
    print(Fore.YELLOW + "Type 'exit' to quit.\n")

    # Setup completer if readline is available
    if readline:
        readline.set_completer(ai_completer)
        readline.parse_and_bind("tab: complete")

    while True:
        try:
            user_input = input(Fore.CYAN + ">>> " + Style.RESET_ALL)
            if user_input.strip().lower() == "exit":
                print(Fore.RED + " Exiting Ghost Corrector...")
                speak("Exiting Ghost Corrector. Goodbye!")
                break

            fixed_code = fix_code(user_input)
            if fixed_code != user_input:
                print(Fore.MAGENTA + f" Ghost fixed → {fixed_code}")
                speak(f"Ghost suggests: {fixed_code}")  # speak correction

            try:
                exec(fixed_code, globals())
            except Exception as e:
                print(Fore.RED + f"Runtime error: {e}")
                speak(f"Runtime error: {e}")  # speak runtime errors

        except KeyboardInterrupt:
            print("\n" + Fore.RED + "Goodbye!")
            speak("Goodbye!")
            break
