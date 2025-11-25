#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to parse IndexedDB database files."""

import argparse
import logging
import sys

from dtformats import file_system
from dtformats import indexeddb
from dtformats import output_writers

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
      'Extracts information from IndexedDB database files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  if dfvfs_helpers:
    dfvfs_helpers.AddDFVFSCLIArguments(argument_parser)

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the IndexedDB database file.')

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

  indexeddb_file = indexeddb.IndexedDBDatabaseTableFile(
      debug=options.debug, output_writer=output_writer)

  indexeddb_file.Open(options.source)

  print('IndexedDB database file information:')

  for table_entry in indexeddb_file.ReadEntries():
    if table_entry.value_type == 0:
      value_type_string = 'del'
    elif table_entry.value_type == 1:
      value_type_string = 'val'
    else:
      value_type_string = 'UNKNOWN'

    key = ', '.join(table_entry.key_segments)

    # Print value without leading b
    value = repr(table_entry.value)[1:]

    print((f'<<{key:s}>> @ {table_entry.sequence_number:d} : '
           f'{value_type_string:s} => {value:s}'))

  print('')

  indexeddb_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
