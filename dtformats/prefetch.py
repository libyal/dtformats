# -*- coding: utf-8 -*-
"""Script to calculate Windows Prefetch hashes."""

from __future__ import unicode_literals


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
    block_value = path[path_index + 1]
    block_value *= 37
    block_value += path[path_index + 2]
    block_value *= 37
    block_value += path[path_index + 3]
    block_value *= 37
    block_value += path[path_index + 4]
    block_value *= 37
    block_value += path[path_index + 5]
    block_value *= 37
    block_value += path[path_index + 6]
    block_value *= 37
    block_value += path[path_index + 7]

    block_value += path[path_index] * 442596621

    hash_value = (block_value - (hash_value * 803794207)) % 0x100000000

    path_index += 8

  while path_index < path_length:
    hash_value = ((37 * hash_value) + path[path_index]) % 0x100000000

    path_index += 1

  return hash_value
