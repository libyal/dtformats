#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Windows Recycler INFO2 files."""

import argparse
import logging
import sys

from dtformats import output_writers
from dtformats import recycler


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from Windows Recycler INFO2 files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the Recycler INFO2 file.')

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

  info2_file = recycler.RecyclerInfo2File(
      debug=options.debug, output_writer=output_writer)

  info2_file.Open(options.source)

  print('Recycler INFO2 file information:')

  # TODO: print file information.
  # TODO: print file entries.

  print('')

  info2_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
