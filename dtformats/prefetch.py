#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to calculate Windows Prefetch hashes."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import sys


def CalculatePrefetchHashXP(path):
  """Calculates a Windows XP Prefetch hash.

  Args:
    path (str): path to calculate the Prefetch hash of.

  Returns:
    int: Prefetch hash.
  """
  hash_value = 0

  path = path.upper()

  for byte_value in path.encode('utf-16-le'):
    hash_value = ((hash_value * 37) + byte_value) % 0x100000000

  hash_value = (hash_value * 314159269) % 0x100000000

  if hash_value > 0x80000000:
    hash_value = 0x100000000 - hash_value

  return (abs(hash_value) % 1000000007) % 0x100000000


def CalculatePrefetchHashVista(path):
  """Calculates a Windows Vista Prefetch hash.

  Args:
    path (str): path to calculate the Prefetch hash of.

  Returns:
    int: Prefetch hash.
  """
  hash_value = 314159

  path = path.upper()

  for byte_value in path.encode('utf-16-le'):
    hash_value = ((hash_value * 37) + byte_value) % 0x100000000

  return hash_value


def CalculatePrefetchHash2008(path):
  """Calculates a Windows 2008 Prefetch hash.

  Args:
    path (str): path to calculate the Prefetch hash of.

  Returns:
    int: Prefetch hash.
  """
  hash_value = 314159

  path = path.upper().encode('utf-16-le')
  path_index = 0
  path_length = len(path)

  while path_index + 8 < path_length:
    character_value = path[path_index + 1]
    character_value *= 37
    character_value += path[path_index + 2]
    character_value *= 37
    character_value += path[path_index + 3]
    character_value *= 37
    character_value += path[path_index + 4]
    character_value *= 37
    character_value += path[path_index + 5]
    character_value *= 37
    character_value += path[path_index + 6]
    character_value *= 37
    character_value += path[path_index] * 442596621
    character_value += path[path_index + 7]

    hash_value = (character_value - (hash_value * 803794207)) % 0x100000000

    path_index += 8

  while path_index < path_length:
    hash_value = ((37 * hash_value) + path[path_index]) % 0x100000000

    path_index += 1

  return hash_value


def CalculatePrefetchHash10(path):
  """Calculates a Windows 10 Prefetch hash.

  Args:
    path (str): path to calculate the Prefetch hash of.

  Returns:
    int: Prefetch hash.
  """
  hash_value = 0

  path = path.upper().encode('utf-16-le')
  path_index = 0
  path_length = len(path)

  while path_index + 8 < path_length:
    character_value = 11623883
    character_value += path[path_index]
    character_value *= 37
    character_value = path[path_index + 1]
    character_value *= 37
    character_value += path[path_index + 2]
    character_value *= 37
    character_value += path[path_index + 3]
    character_value *= 37
    character_value += path[path_index + 4]
    character_value *= 37
    character_value += path[path_index + 5]
    character_value *= 37
    character_value += path[path_index + 6]
    character_value *= 37
    character_value += path[path_index + 7]
    character_value *= 37

    hash_value += character_value

    path_index += 8

  return hash_value


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
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

  prefetch_hash = CalculatePrefetchHashXP(options.path)
  print('\tWindows XP\t: 0x{0:08x}'.format(prefetch_hash))

  prefetch_hash = CalculatePrefetchHashVista(options.path)
  print('\tWindows Vista\t: 0x{0:08x}'.format(prefetch_hash))

  prefetch_hash = CalculatePrefetchHash2008(options.path)
  print('\tWindows 2008\t: 0x{0:08x}'.format(prefetch_hash))

  print('')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
