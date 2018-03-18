#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Windows Jump List files:
* .automaticDestinations-ms
* .customDestinations-ms
"""

from __future__ import print_function
from __future__ import unicode_literals

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
    print('Unable to open output writer with error: {0!s}'.format(exception))
    print('')
    return False

  if pyolecf.check_file_signature(options.source):
    jump_list_file = jump_list.AutomaticDestinationsFile(
        debug=options.debug, output_writer=output_writer)
  else:
    jump_list_file = jump_list.CustomDestinationsFile(
        debug=options.debug, output_writer=output_writer)

  jump_list_file.Open(options.source)

  print('Windows Jump List information:')
  print('Number of entries:\t\t{0:d}'.format(len(jump_list_file.entries)))
  print('Number of recovered entries:\t{0:d}'.format(
      len(jump_list_file.recovered_entries)))
  print('')

  for lnk_file_entry in jump_list_file.entries:
    print('LNK file entry: {0:s}'.format(lnk_file_entry.identifier))

    for shell_item in lnk_file_entry.GetShellItems():
      print('Shell item: 0x{0:02x}'.format(shell_item.class_type))

    print('')

  jump_list_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
