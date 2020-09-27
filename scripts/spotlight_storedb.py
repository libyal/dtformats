#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Apple Spotlight store database files."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

from dfdatetime import cocoa_time as dfdatetime_cocoa_time

from dtformats import spotlight_storedb
from dtformats import output_writers


class TableView(object):
  """Table view."""

  def __init__(self, header=None):
    """Initializes a table view.

    Args:
      header (Optional[str]): table header.
    """
    super(TableView, self).__init__()
    self._header = header
    self._number_of_values = 0
    self._rows = []

  def AddRow(self, values):
    """Adds a row.

    Args:
      values (list[str]): values of the row.

    Raises:
      ValueError: if the number of values does not match with previous rows.
    """
    if self._number_of_values == 0:
      self._number_of_values = len(values)
    elif self._number_of_values != len(values):
      raise ValueError('Mismatch in number of values.')

    self._rows.append(values)

  def Write(self, output_writer):
    """Writes the table to the output.

    Args:
      output_writer (OutputWriter): output writer.
    """
    if self._header:
      output_text = '{0:s}\n'.format(self._header)
      output_writer.WriteText(output_text)

    column_widths = [0] * self._number_of_values
    value_strings_per_row = []
    for row in self._rows:
      value_strings = ['{0!s}'.format(value) for value in row]
      value_strings_per_row.append(value_strings)

      for column_index, value_string in enumerate(value_strings):
        column_width = len(value_string)
        column_width, remainder = divmod(column_width, 8)
        if remainder > 0:
          column_width += 1
        column_width *= 8

        column_widths[column_index] = max(
            column_widths[column_index], column_width)

    for value_strings in value_strings_per_row:
      output_text_parts = []
      for column_index, value_string in enumerate(value_strings):
        output_text_parts.append(value_string)

        if column_index < self._number_of_values - 1:
          column_width = column_widths[column_index] - len(value_string)
          while column_width > 0:
            output_text_parts.append('\t')
            column_width -= 8

      output_text_parts.append('\n')

      output_text = ''.join(output_text_parts)
      output_writer.WriteText(output_text)

    output_writer.WriteText('\n')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from Apple Spotlight store database files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      '-i', '--item', dest='item', type=int, action='store', default=None,
      metavar='FSID', help='file system identifier (FSID) of the item to show.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the Apple Spotlight store database file.')

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

  spotlight_store_database = spotlight_storedb.AppleSpotlightStoreDatabaseFile(
      debug=options.debug, output_writer=output_writer)
  spotlight_store_database.Open(options.source)

  if options.item is None:
    properties_plist = ''
    metadata_version = ''

    metadata_item = spotlight_store_database.GetMetadataItemByIdentifier(1)
    if metadata_item:
      metadata_attribute = metadata_item.attributes.get(
          'kMDStoreProperties', None)
      if metadata_attribute:
        properties_plist = metadata_attribute.value.decode('utf-8')

      metadata_attribute = metadata_item.attributes.get(
          '_kStoreMetadataVersion', None)
      if metadata_attribute:
        metadata_version = '{0:d}.{1:d}'.format(
            metadata_attribute.value >> 16, metadata_attribute.value & 0xffff)

    table_view = TableView(
        header='Apple Spotlight database information:')
    table_view.AddRow(['Metadata version:', metadata_version])
    table_view.AddRow([
        'Number of metadata items:',
        spotlight_store_database.number_of_metadata_items])

    table_view.Write(output_writer)

    if properties_plist:
      output_writer.WriteText('Properties:\n')
      output_writer.WriteText(properties_plist)
      output_writer.WriteText('\n')

  else:
    metadata_item = spotlight_store_database.GetMetadataItemByIdentifier(
        options.item)
    if not metadata_item:
      output_writer.WriteText('No such metadata item: {0:d}\n'.format(
          options.item))
    else:
      table_view = TableView()
      for name, metadata_attribute in sorted(metadata_item.attributes.items()):
        if metadata_attribute.value_type != 0x0c:
          value_string = '{0!s}'.format(metadata_attribute.value)
        else:
          date_time = dfdatetime_cocoa_time.CocoaTime(
              timestamp=metadata_attribute.value)
          value_string = date_time.CopyToDateTimeString()

          if value_string:
            value_string = '{0:s} UTC'.format(value_string)
          else:
            value_string = '{0:f}'.format(metadata_attribute.value)

        table_view.AddRow([name, value_string])

    table_view.Write(output_writer)

  spotlight_store_database.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
