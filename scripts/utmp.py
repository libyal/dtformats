#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse utmp files."""

import argparse
import logging
import os
import sys

from dtformats import output_writers
from dtformats import utmp


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from utmp files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the utmp file.')

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

  with open(options.source, 'rb') as file_object:
    file_object.seek(0, os.SEEK_SET)
    utmp_signature = file_object.read(11)

  if utmp_signature == b'utmpx-1.00\x00':
    utmp_file = utmp.MacOSXUtmpxFile(
        debug=options.debug, output_writer=output_writer)
  else:
    utmp_file = utmp.LinuxLibc6UtmpFile(
        debug=options.debug, output_writer=output_writer)

  utmp_file.Open(options.source)

  output_writer.WriteText('utmp information:')

  utmp_file.Close()

  output_writer.WriteText('')
  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
