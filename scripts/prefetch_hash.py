#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to calculate Windows Prefetch hashes."""

import argparse
import sys

from dtformats import prefetch


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Calculate Windows Prefetch hashes'))

  argument_parser.add_argument(
      'path', nargs='?', action='store', metavar='PATH',
      default=None, help='path to calculate the Prefetch hash of.')

  options = argument_parser.parse_args()

  if not options.path:
    print('Path missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  print('Windows Prefetch hashes:')

  hash_value = prefetch.CalculatePrefetchHashXP(options.path)
  print(f'\tWindows XP\t: 0x{hash_value:08x}')

  hash_value = prefetch.CalculatePrefetchHashVista(options.path)
  print(f'\tWindows Vista\t: 0x{hash_value:08x}')

  hash_value = prefetch.CalculatePrefetchHash2008(options.path)
  print(f'\tWindows 2008\t: 0x{hash_value:08x}')

  print('')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
