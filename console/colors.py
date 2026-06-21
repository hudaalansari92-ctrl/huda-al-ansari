"""Thin colorama wrapper so the rest of the package can stay readable."""
from colorama import Fore, Back, Style, init as _init

_init(autoreset=True)


def cyan(text: str) -> str:
    return f'{Fore.CYAN}{text}{Style.RESET_ALL}'


def green(text: str) -> str:
    return f'{Fore.GREEN}{text}{Style.RESET_ALL}'


def yellow(text: str) -> str:
    return f'{Fore.YELLOW}{text}{Style.RESET_ALL}'


def red(text: str) -> str:
    return f'{Fore.RED}{text}{Style.RESET_ALL}'


def magenta(text: str) -> str:
    return f'{Fore.MAGENTA}{text}{Style.RESET_ALL}'


def blue(text: str) -> str:
    return f'{Fore.BLUE}{text}{Style.RESET_ALL}'


def bold(text: str) -> str:
    return f'{Style.BRIGHT}{text}{Style.RESET_ALL}'


def header(text: str, char: str = '═', width: int = 70) -> str:
    """Big banner — used between stages."""
    bar = char * width
    return f'\n{Fore.CYAN}{bar}\n  {Style.BRIGHT}{text}{Style.NORMAL}\n{bar}{Style.RESET_ALL}'


def subheader(text: str, char: str = '─', width: int = 70) -> str:
    bar = char * width
    return f'{Fore.BLUE}{bar}\n  {text}\n{bar}{Style.RESET_ALL}'


def risk_color(level: str) -> str:
    """Pick a band colour for a final risk label."""
    up = (level or '').upper()
    if up in ('CRITICAL', 'HIGH'):
        return red(level)
    if up in ('MODERATE-HIGH', 'MODERATE', 'MEDIUM', 'BORDERLINE'):
        return yellow(level)
    return green(level)
