#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Apple Unified Logging and Activity Tracing files."""

import argparse
import heapq
import logging
import re
import sys

from dfdatetime import posix_time as dfdatetime_posix_time

from dtformats import file_system
from dtformats import output_writers
from dtformats import unified_logging

try:
  from dtformats import dfvfs_helpers
except ImportError:
  dfvfs_helpers = None


class LogEntriesHeap(object):
  """Log entries heap."""

  def __init__(self):
    """Initializes a log entries heap."""
    super(LogEntriesHeap, self).__init__()
    self._heap = []

  def PopLogEntries(self):
    """Pops log entries from the heap.

    Yields:
      LogEntry: log entry.
    """
    log_entry = self.PopLogEntry()
    while log_entry:
      yield log_entry
      log_entry = self.PopLogEntry()

  def PopLogEntry(self):
    """Pops a log entry from the heap.

    Returns:
      LogEntry: log entry.
    """
    try:
      return heapq.heappop(self._heap)

    except IndexError:
      return None

  def PushLogEntry(self, log_entry):
    """Pushes a log entry onto the heap.

    Args:
      log_entry (LogEntry): log entry.
    """
    heapq.heappush(self._heap, log_entry)


def GetDateTimeString(timestamp):
  """Determines the date and time string.

  Args:
    timestamp (int): number of nanoseconds since January 1, 1970
        00:00:00.000000000.

  Returns:
    str: date and time string.
  """
  if timestamp is None:
    return 'YYYY-MM-DD hh:ss:mm.######+####'

  date_time = dfdatetime_posix_time.PosixTimeInNanoseconds(timestamp=timestamp)
  iso8601_string = date_time.CopyToDateTimeStringISO8601()
  return ''.join([
      iso8601_string[:10], ' ', iso8601_string[11:26],
      iso8601_string[29:32], iso8601_string[33:35]])


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
      '--format', dest='format', action='store', type=str,
      choices=['json', 'text'], default='text', metavar='FORMAT',
      help='output format.')

  if dfvfs_helpers:
    dfvfs_helpers.AddDFVFSCLIArguments(argument_parser)

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None, help=(
          'path of the Apple Unified Logging and Activity Tracing file.'))

  options = argument_parser.parse_args()

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  if dfvfs_helpers and getattr(options, 'image', None):
    file_system_helper = dfvfs_helpers.ParseDFVFSCLIArguments(options)
    if not file_system_helper:
      print('No supported file system found in storage media image.')
      print('')
      return False

  else:
    if not options.source:
      print('Source file missing.')
      print('')
      argument_parser.print_help()
      print('')
      return False

    file_system_helper = file_system.NativeFileSystemHelper()

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

      image_identifier_string = str(dsc_uuid.image_identifier).upper()
      output_writer.WriteText(
          f'    uuid {index:d}:\t{image_identifier_string:s}\n')

      text_end_offset = dsc_uuid.text_offset + dsc_uuid.text_size
      output_writer.WriteText((
          f'    dsc text:\t0x{dsc_uuid.text_offset:08x} .. '
          f'0x{text_end_offset:08x} ({dsc_uuid.text_size:d})\n'))
      output_writer.WriteText(f'    path:\t{dsc_uuid.image_path:s}\n')
      output_writer.WriteText('\n')

    for index, dsc_range in enumerate(unified_logging_file.ranges):
      output_writer.WriteText(f'Range {index:d}:\n')

      uuid_string = str(dsc_range.image_identifier).upper()
      output_writer.WriteText(
          f'    uuid {dsc_range.uuid_index:d}:\t{uuid_string:s}\n')

      range_end_offset = dsc_range.range_offset + dsc_range.range_size
      output_writer.WriteText((
          f'    dsc range:\t0x{dsc_range.range_offset:08x} .. '
          f'0x{range_end_offset:08x} ({dsc_range.range_size:d})\n'))
      output_writer.WriteText(f'    path:\t{dsc_range.image_path:s}\n')
      output_writer.WriteText('\n')

  elif file_signature == b'\x99\x88\x77\x66':
    # TODO: implement.
    pass

  elif file_signature in (b'\xb0\xbb\x30\x00', b'Ts\x20\x00'):
    for record in unified_logging_file.ReadRecords():
      # TODO: implement.
      _ = record

  else:
    log_entries_heap = LogEntriesHeap()
    for log_entry in unified_logging_file.ReadLogEntries():
      log_entries_heap.PushLogEntry(log_entry)

    escape_regex = re.compile(r'([\\/"])', re.MULTILINE)

    if options.format == 'json':
      print('[{')
    else:
      print((
          'Timestamp                       Thread     Type        '
          'Activity             PID    TTL'))

    parent_per_activity_identifier = {}
    for index, log_entry in enumerate(log_entries_heap.PopLogEntries()):
      if options.format == 'json' and index > 0:
        print('},{')

      activity_identifier = log_entry.activity_identifier or 0
      date_time_string = GetDateTimeString(log_entry.timestamp)
      process_identifier = log_entry.process_identifier or 0
      sender_program_counter = log_entry.sender_program_counter or 0
      thread_identifier = log_entry.thread_identifier or 0

      if options.format == 'json':
        boot_identifier = str(log_entry.boot_identifier).upper()
        category = log_entry.category or ''
        event_type = log_entry.event_type or ''
        sub_system = log_entry.sub_system or ''

        event_message = log_entry.event_message or ''
        event_message = event_message.rstrip()
        if len(event_message) >= 1085:
          event_message = ''.join([event_message[:1087], '<…>'])

        event_message = escape_regex.sub(r'\\\1', event_message)
        event_message = event_message.replace('\n', '\\n')
        event_message = event_message.replace('\t', '\\t')

        creator_activity_identifier = log_entry.creator_activity_identifier

        if creator_activity_identifier is not None:
          # The format string for an activityCreateEvent is empty.
          format_string = ''
        else:
          format_string = log_entry.format_string or ''
          format_string = escape_regex.sub(r'\\\1', format_string)
          format_string = format_string.replace('\n', '\\n')
          format_string = format_string.replace('\t', '\\t')

        process_image_identifier = ''
        if log_entry.process_image_identifier:
          process_image_identifier = str(
              log_entry.process_image_identifier).upper()

        process_image_path = log_entry.process_image_path or ''
        process_image_path = escape_regex.sub(r'\\\1', process_image_path)

        sender_image_identifier = ''
        if log_entry.sender_image_identifier:
          sender_image_identifier = str(
              log_entry.sender_image_identifier).upper()

        sender_image_path = log_entry.sender_image_path or ''
        sender_image_path = sender_image_path.replace('"', '\\"')
        sender_image_path = sender_image_path.replace('/', '\\/')

        if event_type == 'timesyncEvent':
          lines = [
              f'  "bootUUID" : "{boot_identifier:s}",',
              f'  "category" : "{category:s}",',
              f'  "processImageUUID" : "{process_image_identifier:s}",',
              f'  "eventType" : "{event_type:s}",',
              f'  "threadID" : {thread_identifier:d},',
              f'  "timestamp" : "{date_time_string:s}",',
              f'  "activityIdentifier" : {activity_identifier:d},',
              f'  "senderProgramCounter" : {sender_program_counter:d},',
              '  "parentActivityIdentifier" : 0,',
              f'  "machTimestamp" : {log_entry.mach_timestamp:d},',
              f'  "processID" : {process_identifier:d},',
              f'  "subsystem" : "{sub_system:s}",',
              '  "timezoneName" : "",',
              f'  "traceID" : {log_entry.trace_identifier:d},',
              f'  "eventMessage" : "{event_message:s}",',
              f'  "formatString" : "{format_string:s}",',
              f'  "processImagePath" : "{process_image_path:s}",',
              f'  "senderImageUUID" : "{sender_image_identifier:s}",',
              f'  "senderImagePath" : "{sender_image_path:s}"']

        else:
          lines = [f'  "traceID" : {log_entry.trace_identifier:d},']

          if (creator_activity_identifier is None and
              log_entry.loss_count is None and
              log_entry.signpost_identifier is None):
            lines.append(f'  "eventMessage" : "{event_message:s}",')

          lines.append(f'  "eventType" : "{event_type:s}",')

          if log_entry.loss_count is not None:
            # TODO: improve support for lossCountSaturated
            lines.extend([
                f'  "lossCount" : {log_entry.loss_count:d},',
                '  "lossCountSaturated" : true,'])

          if log_entry.signpost_identifier is not None:
            signpost_scope = log_entry.signpost_scope or ''

            lines.extend([
                f'  "signpostID" : {log_entry.signpost_identifier:d},',
                f'  "signpostScope" : "{signpost_scope:s}",'])

          if (creator_activity_identifier is None and
              log_entry.loss_count is None):
            # TODO: implement source support.
            lines.append('  "source" : null,')

          lines.append(f'  "formatString" : "{format_string:s}",')

          if log_entry.loss_count is not None:
            lines.append((
                f'  "lossEndMachContinuousTimestamp" : '
                f'{log_entry.loss_end_mach_timestamp:d},'))

          lines.extend([
              f'  "activityIdentifier" : {activity_identifier:d},',
              f'  "subsystem" : "{sub_system:s}",',
              f'  "category" : "{category:s}",',
              f'  "threadID" : {thread_identifier:d},',
              f'  "senderImageUUID" : "{sender_image_identifier:s}",'])

          if log_entry.signpost_identifier is not None:
            signpost_type = log_entry.signpost_type or ''

            lines.append(f'  "signpostType" : "{signpost_type:s}",')

          if log_entry.backtrace_frames:
            lines.extend([
                '  "backtrace" : {',
                '    "frames" : [',
                '      {'])

            for index, backtrace_frame in enumerate(log_entry.backtrace_frames):
              if index > 0:
                lines.extend([
                    '      },',
                    '      {'])

              image_identifier = str(backtrace_frame.image_identifier).upper()

              lines.extend([
                  f'        "imageOffset" : {backtrace_frame.image_offset:d},',
                  f'        "imageUUID" : "{image_identifier:s}"'])

            lines.extend([
                '      }',
                '    ]',
                '  },'])

          lines.extend([
              f'  "bootUUID" : "{boot_identifier:s}",',
              f'  "processImagePath" : "{process_image_path:s}",',
              f'  "timestamp" : "{date_time_string:s}",',
              f'  "senderImagePath" : "{sender_image_path:s}",'])

          if creator_activity_identifier is not None:
            parent_per_activity_identifier[activity_identifier] = (
                creator_activity_identifier &
                unified_logging_file.ACTIVITY_IDENTIFIER_BITMASK)

            lines.append(
                f'  "creatorActivityID" : {creator_activity_identifier:d},')

          elif log_entry.loss_count is not None:
            start_time_string = GetDateTimeString(
                log_entry.loss_start_timestamp)
            end_time_string = GetDateTimeString(log_entry.loss_end_timestamp)

            lines.extend([
                (f'  "lossStartMachContinuousTimestamp" : '
                 f'{log_entry.loss_start_mach_timestamp:d},'),
                f'  "lossEndTimestamp" : "{end_time_string:s}",',
                f'  "lossStartTimestamp" : "{start_time_string:s}",'])

          elif log_entry.signpost_identifier is not None:
            signpost_name = log_entry.signpost_name or ''

            lines.append(f'  "signpostName" : "{signpost_name:s}",')

          lines.append(f'  "machTimestamp" : {log_entry.mach_timestamp:d},')

          if (creator_activity_identifier is not None or
              log_entry.loss_count is not None or
              log_entry.signpost_identifier is not None):
            lines.append(f'  "eventMessage" : "{event_message:s}",')
          else:
            message_type = log_entry.message_type or ''

            lines.append(f'  "messageType" : "{message_type:s}",')

          if log_entry.parent_activity_identifier:
            parent_activity_identifier = log_entry.parent_activity_identifier
          else:
            parent_activity_identifier = parent_per_activity_identifier.get(
                activity_identifier, None) or 0

          if parent_activity_identifier == creator_activity_identifier:
            parent_activity_identifier = 0

          lines.extend([
              f'  "processImageUUID" : "{process_image_identifier:s}",',
              f'  "processID" : {process_identifier:d},',
              f'  "senderProgramCounter" : {sender_program_counter:d},',
              f'  "parentActivityIdentifier" : {parent_activity_identifier:d},',
              '  "timezoneName" : ""'])

        print('\n'.join(lines))

      else:
        event_message_parts = []

        if log_entry.process_image_path:
          _, _, basename = log_entry.process_image_path.rpartition('/')
          event_message_parts.append(f'{basename:s}:')

        if log_entry.sender_image_path:
          _, _, basename = log_entry.sender_image_path.rpartition('/')
          event_message_parts.append(f'({basename:s})')

        if log_entry.sub_system and log_entry.category:
          event_message_parts.append(
              f'[{log_entry.sub_system:s}:{log_entry.category:s}]')

        event_message_parts.append(log_entry.event_message)
        event_message = ' '.join(event_message_parts)

        ttl = log_entry.ttl or 0

        print((
            f'{date_time_string:s}\t0x{thread_identifier:<8x}\t'
            f'{log_entry.event_type:11s}\t0x{activity_identifier:<18x}\t'
            f'{process_identifier:<6d}\t{ttl:<4d}\t{event_message:s}'))

    if options.format == 'json':
      print('}]', end='')

  unified_logging_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
