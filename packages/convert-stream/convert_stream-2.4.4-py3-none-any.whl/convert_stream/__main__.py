#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Configuração instalação:
 $ pip3 install -r requirements.txt

"""
import os
import sys

this_file = os.path.abspath(os.path.relpath(__file__))
dir_of_project = os.path.dirname(this_file)
sys.path.insert(0, dir_of_project)

from convert_stream import (
    __version__, __module_name__, __modify_date__
)


def main():
    print(f'  {__module_name__} V{__version__} {__modify_date__}')


if __name__ == '__main__':
    main()
