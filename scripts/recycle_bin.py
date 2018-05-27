#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Windows Recycle.Bin metadata ($I) files."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

from dfdatetime import filetime as dfdatetime_filetime

from dtformats import output_writers
from dtformats import recycle_bin


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from Windows Recycle.Bin metadata ($I) files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the Recycle.Bin metadata ($I) file.')

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

  metadata_file = recycle_bin.RecycleBinMetadataFile(
      debug=options.debug, output_writer=output_writer)

  metadata_file.Open(options.source)

  print('Recycle.Bin metadata ($I) file information:')

  print('\tFormat version\t\t: {0:d}'.format(metadata_file.format_version))

  if metadata_file.deletion_time == 0:
    date_time_string = 'Not set'
  elif metadata_file.deletion_time == 0x7fffffffffffffff:
    date_time_string = 'Never'
  else:
    date_time = dfdatetime_filetime.Filetime(
        timestamp=metadata_file.deletion_time)
    date_time_string = date_time.CopyToDateTimeString()
    if date_time_string:
      date_time_string = '{0:s} UTC'.format(date_time_string)
    else:
      date_time_string = '0x{08:x}'.format(metadata_file.deletion_time)

  print('\tDeletion time\t\t: {0:s}'.format(date_time_string))
  print('\tOriginal filename\t: {0:s}'.format(metadata_file.original_filename))
  print('\tOriginal file size\t: {0:d}'.format(
      metadata_file.original_file_size))
  print('')

  metadata_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
