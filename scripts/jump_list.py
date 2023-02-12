#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Windows Jump List files:
* .automaticDestinations-ms
* .customDestinations-ms
"""

import argparse
import logging
import sys

import pyolecf

from dtformats import jump_list
from dtformats import output_writers


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from Windows Jump List files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the Windows Jump List file.')

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

  if pyolecf.check_file_signature(options.source):
    jump_list_file = jump_list.AutomaticDestinationsFile(
        debug=options.debug, output_writer=output_writer)
  else:
    jump_list_file = jump_list.CustomDestinationsFile(
        debug=options.debug, output_writer=output_writer)

  jump_list_file.Open(options.source)

  jump_list_entries = list(jump_list_file.GetJumpListEntries())

  print('Windows Jump List information:')

  number_of_entries = len(jump_list_entries)
  print(f'Number of entries:\t\t{number_of_entries:d}')

  print('')

  for jump_list_entry in jump_list_entries:
    print(f'Entry: {jump_list_entry.identifier:s}')

    print_header = True
    for shell_item in jump_list_entry.GetShellItems():
      if print_header:
        print('\tShell items:')
        print_header = False

      print(f'\t\t0x{shell_item.class_type:02x}')

    print_header = True
    for format_identifier, property_record in jump_list_entry.GetProperties():
      if print_header:
        print('\tProperties:')
        print_header = False

      print(f'\t\t{{{format_identifier:s}}}/{property_record.entry_type:d}')

    print('')

  jump_list_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
