#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Apple Spotlight store database files."""

import argparse
import logging
import sys

from dfdatetime import cocoa_time as dfdatetime_cocoa_time

from dtformats import file_system
from dtformats import spotlight_storedb
from dtformats import output_writers

try:
  from dtformats import dfvfs_helpers
except ImportError:
  dfvfs_helpers = None


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
      output_writer.WriteText(f'{self._header:s}\n')

    column_widths = [0] * self._number_of_values
    value_strings_per_row = []
    for row in self._rows:
      value_strings = [f'{value!s}' for value in row]
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

  if dfvfs_helpers:
    dfvfs_helpers.AddDFVFSCLIArguments(argument_parser)

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the Apple Spotlight store database file.')

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

  source_lower = options.source.lower()
  if source_lower.endswith('.map.header'):
    streams_map_header = spotlight_storedb.AppleSpotlightStreamsMapHeaderFile(
        debug=options.debug, file_system_helper=file_system_helper,
        output_writer=output_writer)
    streams_map_header.Open(options.source)

    data_size = streams_map_header.data_size
    number_of_entries = streams_map_header.number_of_entries

    streams_map_header.Close()

    path = ''.join([options.source[:-6], 'offsets'])
    streams_map_offsets = spotlight_storedb.AppleSpotlightStreamsMapOffsetsFile(
        number_of_entries, debug=options.debug,
        file_system_helper=file_system_helper, output_writer=output_writer)
    streams_map_offsets.Open(path)

    offsets = streams_map_offsets.offsets

    streams_map_offsets.Close()

    path = ''.join([options.source[:-6], 'data'])
    streams_map_data = spotlight_storedb.AppleSpotlightStreamsMapDataFile(
        data_size, offsets, debug=options.debug,
        file_system_helper=file_system_helper, output_writer=output_writer)
    streams_map_data.Open(path)

    # TODO: print streams map.

    streams_map_data.Close()

  else:
    spotlight_store_database = (
        spotlight_storedb.AppleSpotlightStoreDatabaseFile(
            debug=options.debug, file_system_helper=file_system_helper,
            output_writer=output_writer))
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
          major_version = metadata_attribute.value >> 16
          minor_version = metadata_attribute.value & 0xffff
          metadata_version = f'{major_version:d}.{minor_version:d}'

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
        output_writer.WriteText(f'No such metadata item: {options.item:d}\n')
      else:
        table_view = TableView()
        for name, metadata_attribute in sorted(
              metadata_item.attributes.items()):
          if metadata_attribute.value_type != 0x0c:
            value_string = f'{metadata_attribute.value!s}'
          else:
            date_time = dfdatetime_cocoa_time.CocoaTime(
                timestamp=metadata_attribute.value)
            value_string = date_time.CopyToDateTimeString()

            if value_string:
              value_string = f'{value_string:s} UTC'
            else:
              value_string = f'{metadata_attribute.value:f}'

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
