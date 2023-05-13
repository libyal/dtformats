#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Apple Unified Logging and Activity Tracing files."""

import argparse
import logging
import sys

from dtformats import output_writers
from dtformats import unified_logging


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from Apple Unified Logging and Activity Tracing '
      'files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None, help=(
          'path of the Apple Unified Logging and Activity Tracing file.'))

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
    file_signature = file_object.read(4)

  if file_signature == b'hcsd':
    unified_logging_file = unified_logging.DSCFile(
        debug=options.debug, output_writer=output_writer)

  elif file_signature == b'\x99\x88\x77\x66':
    unified_logging_file = unified_logging.UUIDTextFile(
        debug=options.debug, output_writer=output_writer)

  elif file_signature in (b'\xb0\xbb\x30\x00', b'Ts\x20\x00'):
    unified_logging_file = unified_logging.TimesyncDatabaseFile(
        debug=options.debug, output_writer=output_writer)

  else:
    unified_logging_file = unified_logging.TraceV3File(
        debug=options.debug, output_writer=output_writer)

  unified_logging_file.Open(options.source)

  output_writer.WriteText(
      'Apple Unified Logging and Activity Tracing information:\n')

  if file_signature == b'hcsd':
    for index, dsc_uuid in enumerate(unified_logging_file.uuids):
      output_writer.WriteText(f'uuid {index:d}:\n')

      sender_identifier_string = str(dsc_uuid.sender_identifier).upper()
      output_writer.WriteText(
          f'    uuid {index:d}:\t{sender_identifier_string:s}\n')

      text_end_offset = dsc_uuid.text_offset + dsc_uuid.text_size
      output_writer.WriteText((
          f'    dsc text:\t0x{dsc_uuid.text_offset:08x} .. '
          f'0x{text_end_offset:08x} ({dsc_uuid.text_size:d})\n'))
      output_writer.WriteText(f'    path:\t{dsc_uuid.path:s}\n')
      output_writer.WriteText('\n')

    for index, dsc_range in enumerate(unified_logging_file.ranges):
      output_writer.WriteText(f'Range {index:d}:\n')

      uuid_string = str(dsc_range.uuid).upper()
      output_writer.WriteText(
          f'    uuid {dsc_range.uuid_index:d}:\t{uuid_string:s}\n')

      range_end_offset = dsc_range.range_offset + dsc_range.range_size
      output_writer.WriteText((
          f'    dsc range:\t0x{dsc_range.range_offset:08x} .. '
          f'0x{range_end_offset:08x} ({dsc_range.range_size:d})\n'))
      output_writer.WriteText(f'    path:\t{dsc_range.path:s}\n')
      output_writer.WriteText('\n')

  unified_logging_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
