#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse UTMP files."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

from dtformats import output_writers
from dtformats import utmp


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from UTMP files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the UTMP file.')

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
    print('Unable to open output writer with error: {0!s}'.format(exception))
    print('')
    return False

  utmp_file = utmp.UTMPFile(
      debug=options.debug, output_writer=output_writer)
  utmp_file.Open(options.source)

  output_writer.WriteText('UTMP information:')

  utmp_file.Close()

  output_writer.WriteText('')
  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
