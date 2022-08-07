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
    print('Unable to open output writer with error: {0!s}'.format(exception))
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

  else:
    unified_logging_file = unified_logging.TraceV3File(
        debug=options.debug, output_writer=output_writer)

  unified_logging_file.Open(options.source)

  output_writer.WriteText(
      'Apple Unified Logging and Activity Tracing information:\n')

  if file_signature == b'hcsd':
    for index, dsc_uuid in enumerate(unified_logging_file.uuids):
      output_writer.WriteText('uuid {0:d}:\n'.format(index))
      output_writer.WriteText('    uuid {0:d}:\t{1!s}\n'.format(
          index, str(dsc_uuid.sender_identifier).upper()))
      output_writer.WriteText(
          '    dsc text:\t0x{0:08x} .. 0x{1:08x} ({2:d})\n'.format(
              dsc_uuid.text_offset, dsc_uuid.text_offset + dsc_uuid.text_size,
              dsc_uuid.text_size))
      output_writer.WriteText('    path:\t{0:s}\n'.format(dsc_uuid.path))
      output_writer.WriteText('\n')

    for index, dsc_range in enumerate(unified_logging_file.ranges):
      output_writer.WriteText('Range {0:d}:\n'.format(index))
      output_writer.WriteText('    uuid {0:d}:\t{1!s}\n'.format(
          dsc_range.uuid_index, str(dsc_range.uuid).upper()))
      output_writer.WriteText(
          '    dsc range:\t0x{0:08x} .. 0x{1:08x} ({2:d})\n'.format(
              dsc_range.range_offset,
              dsc_range.range_offset + dsc_range.range_size,
              dsc_range.range_size))
      output_writer.WriteText('    path:\t{0:s}\n'.format(dsc_range.path))
      output_writer.WriteText('\n')

  unified_logging_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
