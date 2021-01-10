#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse MacOS keychain database files."""

import argparse
import logging
import sys

from dtformats import keychain
from dtformats import output_writers


ATTRIBUTE_DATA_TYPES = {
    0: 'String with size',
    1: 'Integer 32-bit signed',
    2: 'Integer 32-bit unsigned',
    3: 'CSSM_DB_ATTRIBUTE_FORMAT_BIG_NUM',
    4: 'Floating-point 64-bit',
    5: 'Date and time',
    6: 'Binary data',
    7: 'CSSM_DB_ATTRIBUTE_FORMAT_MULTI_UINT32',
    8: 'CSSM_DB_ATTRIBUTE_FORMAT_COMPLEX'}


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from MacOS keychain database files.'))

  argument_parser.add_argument(
      '-c', '--content', dest='content', action='store_true', default=False,
      help='export database content instead of schema.')

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

  if not options.content:
    print('Keychain database file schema:')

    for table in keychain_file.tables:
      print('Table: {0:s} (0x{1:08x})'.format(
          table.relation_name, table.relation_identifier))

      number_of_columns = len(table.columns)
      print('\tNumber of columns:\t{0:d}'.format(number_of_columns))
      print('\tColumn\tIdentifier\tName\tType')

      for index, column in enumerate(table.columns):
        if column.attribute_identifier >= number_of_columns:
          attribute_identifier = ''
        else:
          attribute_identifier = '{0:d}'.format(column.attribute_identifier)

        attribute_data_type = ATTRIBUTE_DATA_TYPES.get(
            column.attribute_data_type,
            '0x{0:08x}'.format(column.attribute_data_type))

        print('\t{0:d}\t{1:s}\t{2:s}\t{3:s}'.format(
            index, attribute_identifier, column.attribute_name or 'NULL',
            attribute_data_type))

      print('')

    print('')

  else:
    for table in keychain_file.tables:
      print('Table: {0:s} (0x{1:08x})'.format(
          table.relation_name, table.relation_identifier))

      print('\t'.join([column.attribute_name for column in table.columns]))

      for record in table.records:
        record_values = []
        for value in record.values():
          if value is None:
            record_values.append('NULL')
          else:
            record_values.append('{0!s}'.format(value))

        print('\t'.join(record_values))

      print('')

  keychain_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
