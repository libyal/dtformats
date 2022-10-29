#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Windows Restore Point change.log files."""

import argparse
import logging
import sys

from dtformats import output_writers
from dtformats import rp_change_log


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from Windows Restore Point change.log files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the Windows Restore Point change.log file.')

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

  change_log_file = rp_change_log.RestorePointChangeLogFile(
      debug=options.debug, output_writer=output_writer)

  change_log_file.Open(options.source)

  print('Windows Restore Point change.log information:')
  print(f'Volume path:\t{change_log_file.volume_path:s}')
  print('')

  for change_log_entry in change_log_file.entries:
    flags = []
    for flag, description in change_log_file.LOG_ENTRY_TYPES.items():
      if change_log_entry.entry_type & flag:
        flags.append(description)

    flags_string = ', '.join(flags)
    print(f'Entry type:\t\t{flags_string:s}')

    flags = []
    for flag, description in change_log_file.LOG_ENTRY_FLAGS.items():
      if change_log_entry.entry_flags & flag:
        flags.append(description)

    flags_string = ', '.join(flags)
    print(f'Entry flags:\t\t{flags_string:s}')

    print(f'Sequence number:\t{change_log_entry.sequence_number:d}')
    print(f'Process name:\t\t{change_log_entry.process_name:s}')

    print('')

  change_log_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
