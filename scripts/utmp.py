#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to parse UTMP files."""

from __future__ import print_function
import argparse
import datetime
import logging
import sys

from dtformat import output_writers
from dtformat import utmp

import data_format


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Extracts information from UTMP files.'))

  argument_parser.add_argument(
      u'-d', u'--debug', dest=u'debug', action=u'store_true', default=False,
      help=u'enable debug output.')

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH',
      default=None, help=u'path of the UTMP file.')

  options = argument_parser.parse_args()

  if not options.source:
    print(u'Source file missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  output_writer = output_writers.StdoutWriter()

  try:
    output_writer.Open()
  except IOError as exception:
    print(u'Unable to open output writer with error: {0!s}'.format(exception))
    print(u'')
    return False

  utmp_file = utmp.UTMPFile(
      debug=options.debug, output_writer=output_writer)
  utmp_file.Open(options.source)

  output_writer.WriteText(u'UTMP information:')

  utmp_file.Close()

  output_writer.WriteText(u'')
  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
