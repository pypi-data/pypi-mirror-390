import sys, time
from pyfiglet import Figlet
from colorama import init, Fore, Style

init(autoreset=True)

def animated_banner(title="ghost", font="slant", version="1.6", subtitle="Smart CLI Assistant"):
    fig = Figlet(font=font)
    banner = fig.renderText(title)
    colors = [Fore.CYAN, Fore.MAGENTA, Fore.BLUE, Fore.GREEN, Fore.YELLOW]

    for i, line in enumerate(banner.splitlines()):
        color = colors[i % len(colors)]
        print(color + line)
        time.sleep(0.05)

    print(Fore.CYAN + Style.BRIGHT + f"Version {version} — {subtitle}\n")
    time.sleep(0.3)

def render_menu():
    print(Fore.YELLOW + "Select an option:")
    print(Fore.MAGENTA + "[1] Start Smart Talk (voice + text)")
    print(Fore.MAGENTA + "[2] Start Smart Corrector (shell assist)")
    print(Fore.MAGENTA + "[3] Exit")
