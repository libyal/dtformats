#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Apple Unified Logging and Activity Tracing files."""

import argparse
import logging
import sys

from dfdatetime import posix_time as dfdatetime_posix_time

from dtformats import file_system
from dtformats import output_writers
from dtformats import unified_logging

try:
  from dtformats import dfvfs_helpers
except ImportError:
  dfvfs_helpers = None


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

  if dfvfs_helpers:
    dfvfs_helpers.AddDFVFSCLIArguments(argument_parser)

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None, help=(
          'path of the Apple Unified Logging and Activity Tracing file.'))

  options = argument_parser.parse_args()

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  if not dfvfs_helpers:
    if not options.source:
      print('Source file missing.')
      print('')
      argument_parser.print_help()
      print('')
      return False

    file_system_helper = file_system.NativeFileSystemHelper()

  else:
    file_system_helper = dfvfs_helpers.ParseDFVFSCLIArguments(options)
    if not file_system_helper:
      print('No supported file system found in storage media image.')
      print('')
      return False

  output_writer = output_writers.StdoutWriter()

  try:
    output_writer.Open()
  except IOError as exception:
    print(f'Unable to open output writer with error: {exception!s}')
    print('')
    return False

  file_object = file_system_helper.OpenFileByPath(options.source)
  if not file_object:
    print('Unable to open source file.')
    print('')
    return False

  try:
    file_signature = file_object.read(4)
  finally:
    file_object.close()

  if file_signature == b'hcsd':
    unified_logging_file = unified_logging.DSCFile(
        debug=options.debug, file_system_helper=file_system_helper,
        output_writer=output_writer)

  elif file_signature == b'\x99\x88\x77\x66':
    unified_logging_file = unified_logging.UUIDTextFile(
        debug=options.debug, file_system_helper=file_system_helper,
        output_writer=output_writer)

  elif file_signature in (b'\xb0\xbb\x30\x00', b'Ts\x20\x00'):
    unified_logging_file = unified_logging.TimesyncDatabaseFile(
        debug=options.debug, file_system_helper=file_system_helper,
        output_writer=output_writer)

  else:
    unified_logging_file = unified_logging.TraceV3File(
        debug=options.debug, file_system_helper=file_system_helper,
        output_writer=output_writer)

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

  elif file_signature == b'\x99\x88\x77\x66':
    # TODO: implement.
    pass

  elif file_signature in (b'\xb0\xbb\x30\x00', b'Ts\x20\x00'):
    for record in unified_logging_file.ReadRecords():
      # TODO: implement.
      _ = record

  else:
    # TODO: add JSON support
    print('Timestamp\t\t\tThread\tType\tActivity\tPID\tTTL')

    for log_entry in unified_logging_file.ReadLogEntries():
      if log_entry.timestamp is None:
        time_string = 'YYYY-MM-DD hh:ss:mm.######+####'
      else:
        date_time = dfdatetime_posix_time.PosixTimeInNanoseconds(
            timestamp=log_entry.timestamp)
        iso8601_string = date_time.CopyToDateTimeStringISO8601()
        time_string = ''.join([
            iso8601_string[:10], ' ', iso8601_string[11:26],
            iso8601_string[29:32], iso8601_string[33:35]])

      event_message_parts = []
      # TODO: processImagePath basename
      # TODO: senderImagePath basename
      if log_entry.sub_system and log_entry.category:
        event_message_parts.append(
            f'[{log_entry.sub_system:s}:{log_entry.category:s}]')

      event_message_parts.append(log_entry.event_message)
      event_message = ' '.join(event_message_parts)

      print((
          f'{time_string:s}\t'
          f'0x{log_entry.thread_identifier:x}\t'
          f'{log_entry.event_type:s}\t'
          f'0x{log_entry.activity_identifier:x}\t'
          f'{log_entry.process_identifier:d}\t'
          f'{log_entry.ttl:d}\t'
          f'{event_message:s}'))

  unified_logging_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
