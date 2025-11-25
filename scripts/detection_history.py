#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to parse Windows Defender scan DetectionHistory files."""

import argparse
import logging
import sys

from dtformats import detection_history
from dtformats import output_writers


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from a Windows Defender scan DetectionHistory '
      'file.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None, help=(
          'path of the Windows Defender scan DetectionHistory file.'))

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

  detection_history_file = (
      detection_history.WindowsDefenderScanDetectionHistoryFile(
          debug=options.debug, output_writer=output_writer))
  detection_history_file.Open(options.source)

  output_writer.WriteText('Windows Defender scan DetectionHistory information:')
  # TODO: print information.

  detection_history_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
