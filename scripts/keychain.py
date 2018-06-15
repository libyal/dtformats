#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse MacOS keychain database files."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

from dtformats import keychain
from dtformats import output_writers


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from MacOS keychain database files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the keychain database file.')

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

  keychain_file = keychain.KeychainDatabaseFile(
      debug=options.debug, output_writer=output_writer)

  keychain_file.Open(options.source)

  print('Keychain database file schema:')

  for table in keychain_file.tables:
    print('Table: {0:s} (0x{1:08x})'.format(
        table.relation_name, table.relation_identifier))
    print('\tColumns:')

    for column in table.columns:
      print('\t\t: {0!s}'.format(column.attribute_name or ''))

    print('')

  print('')

  keychain_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
