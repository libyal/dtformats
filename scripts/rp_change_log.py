#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to parse Windows Restore Point change.log files."""

from __future__ import print_function
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
      u'Extracts information from Windows Restore Point change.log files.'))

  argument_parser.add_argument(
      u'-d', u'--debug', dest=u'debug', action=u'store_true', default=False,
      help=u'enable debug output.')

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH',
      default=None, help=u'path of the Windows Restore Point change.log file.')

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

  change_log_file = rp_change_log.RestorePointChangeLogFile(
      debug=options.debug, output_writer=output_writer)

  change_log_file.Open(options.source)

  print(u'Windows Restore Point change.log information:')
  print(u'Volume path:\t{0:s}'.format(change_log_file.volume_path))
  print(u'')

  for change_log_entry in change_log_file.entries:
    flags = []
    for flag, description in change_log_file.LOG_ENTRY_TYPES.items():
      if change_log_entry.entry_type & flag:
        flags.append(description)

    print(u'Entry type:\t\t{0:s}'.format(u', '.join(flags)))

    flags = []
    for flag, description in change_log_file.LOG_ENTRY_FLAGS.items():
      if change_log_entry.entry_flags & flag:
        flags.append(description)

    print(u'Entry flags:\t\t{0:s}'.format(u', '.join(flags)))

    print(u'Sequence number:\t{0:d}'.format(change_log_entry.sequence_number))
    print(u'Process name:\t\t{0:s}'.format(change_log_entry.process_name))

    print(u'')

  change_log_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
