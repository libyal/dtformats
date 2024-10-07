#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Firefox cache version 1 files."""

import argparse
import logging
import os
import sys

from dtformats import output_writers
from dtformats import firefox_cache1


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from Firefox cache version 1 files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the Firefox cache version 1 file.')

  options = argument_parser.parse_args()

  if not options.source:
    print('Source file missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  output_writer = output_writers.StdoutWriter()

  try:
    output_writer.Open()
  except IOError as exception:
    print(f'Unable to open output writer with error: {exception!s}')
    print('')
    return False

  filename = os.path.basename(options.source)
  if filename == '_CACHE_MAP_':
    cache_file = firefox_cache1.CacheMapFile(
        debug=options.debug, output_writer=output_writer)
  elif filename.startswith('_CACHE_00'):
    cache_file = firefox_cache1.CacheBlockFile(
        debug=options.debug, output_writer=output_writer)
  else:
    print('Unsupported Firefox cache version 1 file name.')
    print('')
    return False

  cache_file.Open(options.source)

  print('Firefox cache version 1 information:')
  print('')

  cache_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
