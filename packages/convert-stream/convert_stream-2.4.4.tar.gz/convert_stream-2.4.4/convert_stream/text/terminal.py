#!/usr/bin/env python3
import os
from enum import Enum


class Colors(Enum):

    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    DARK_RED = '\033[91m'
    DARK_GREEN = '\033[92m'
    DARK_YELLOW = '\033[93m'
    VOID = '\033[0m'
    END = '\033[0m'


def print_line(char: str = '=', *, color: Colors = Colors.VOID):
    """
        Imprime uma linha na tela.
    """
    try:
        num_size = os.get_terminal_size().columns
    except:
        num_size = 80
    print(f'{color.value}{char}{Colors.END.value}' * num_size)


def print_title(title: str, char: str = '='):
    """
        Imprime um título na tela.
    """
    try:
        num_size = os.get_terminal_size().columns
    except:
        num_size = 80

    # print_line(char)
    print(title.center(num_size, char))


def msg(text: str, *, color: Colors = Colors.VOID):
    print(f'{color.value}{text}{Colors.END.value}')


def show_warning(text: str, *, line: bool = True):
    if line:
        print_line('-')
    print(f'{Colors.DARK_YELLOW}[?] WARNING:{Colors.END.value} {text}')


def show_error(text: str, *, line: bool = True):
    if line:
        print_line('-')
    print(f'{Colors.DARK_YELLOW}[!] ERRO:{Colors.END.value} {text}')


def show_info(text: str, *, line: bool = True):
    if line:
        print_line('-')
    print(f'{Colors.DARK_YELLOW}[+] INFO:{Colors.END.value} {text}')
