#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse LevelDB database files."""

import argparse
import logging
import os
import sys

from dtformats import file_system
from dtformats import leveldb
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
      'Extracts information from LevelDB database files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  if dfvfs_helpers:
    dfvfs_helpers.AddDFVFSCLIArguments(argument_parser)

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the LevelDB database file.')

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
    file_object.seek(-8, os.SEEK_END)
    file_signature = file_object.read(8)
  finally:
    file_object.close()

  path_segments = file_system_helper.SplitPath(options.source)

  if file_signature == b'\x57\xfb\x80\x8b\x24\x75\x47\xdb':
    leveldb_file = leveldb.LevelDBDatabaseTableFile(
        debug=options.debug, output_writer=output_writer)

  elif path_segments[-1].startswith('MANIFEST'):
    leveldb_file = leveldb.LevelDBDatabaseDescriptorFile(
        debug=options.debug, output_writer=output_writer)

  else:
    leveldb_file = leveldb.LevelDBDatabaseLogFile(
        debug=options.debug, output_writer=output_writer)

  leveldb_file.Open(options.source)

  print('LevelDB database file information:')

  print('')

  leveldb_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
