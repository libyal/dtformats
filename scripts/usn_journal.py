#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to parse USN change journal records."""

import argparse
import logging
import sys

from dtformats import usn_journal
from dtformats import output_writers


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from USN change journal records.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the USN change journal records.')

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

  usn_records = usn_journal.USNRecords(
      debug=options.debug, output_writer=output_writer)
  usn_records.Open(options.source)

  output_writer.WriteText('USN journal records information:')
  output_writer.WriteText(','.join([
      'Date and time', 'Name', 'File reference', 'Parent file reference']))
  for usn_record in usn_records.ReadRecords():
    # pylint: disable=protected-access
    date_time = usn_record._FormatIntegerAsFiletime(usn_record.timestamp)

    mft_entry = usn_record.file_reference & ((1 << 48) - 1)
    sequence_number = usn_record.file_reference >> 48
    file_reference = f'{mft_entry:d}-{sequence_number:d}'

    mft_entry = usn_record.parent_file_reference & ((1 << 48) - 1)
    sequence_number = usn_record.parent_file_reference >> 48
    parent_file_reference = f'{mft_entry:d}-{sequence_number:d}'

    output_writer.WriteText(','.join([
        date_time, usn_record.name, file_reference, parent_file_reference]))

  usn_records.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
