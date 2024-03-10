#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse Windows Jump List files:
* .automaticDestinations-ms
* .customDestinations-ms
"""

import argparse
import logging
import sys

import pyfwps
import pyfwsi
import pyolecf

from dfdatetime import fat_date_time as dfdatetime_fat_date_time
from dfdatetime import filetime as dfdatetime_filetime

from dtformats import file_system
from dtformats import jump_list
from dtformats import output_writers
from dtformats import shell_property_keys

try:
  from dtformats import dfvfs_helpers
except ImportError:
  dfvfs_helpers = None


class StdoutWriter(output_writers.StdoutWriter):
  """Stdout output writer."""

  _LNK_DATA_BLOCK_DESCRIPTIONS = {
      0xa0000001: 'Environment variables location',
      0xa0000002: 'Console properties',
      0xa0000003: 'Distributed link tracker properties',
      0xa0000004: 'Console codepage',
      0xa0000005: 'Special folder location',
      0xa0000006: 'Darwin properties',
      0xa0000007: 'Icon location',
      0xa0000008: 'Shim layer properties',
      0xa0000009: 'Metadata property store',
      0xa000000b: 'Known folder location',
      0xa000000c: 'Shell item identifiers list'}

  def _FormatFATDateTimeValue(self, value):
    """Formats a FAT date time value.

    Args:
      value (int): FAT date time value.

    Returns:
      str: date time string.
    """
    if not value:
      date_time_string = 'Not set (0)'
    else:
      date_time = dfdatetime_fat_date_time.FATDateTime(fat_date_time=value)
      date_time_string = date_time.CopyToDateTimeString()
      if not date_time_string:
        date_time_string = f'0x{value:04x}'

    return date_time_string

  def _FormatFiletimeValue(self, value):
    """Formats a FILETIME timestamp value.

    Args:
      value (int): FILETIME timestamp value.

    Returns:
      str: date time string.
    """
    if value == 0:
      date_time_string = 'Not set (0)'
    elif value == 0x7fffffffffffffff:
      date_time_string = 'Never (0x7fffffffffffffff)'
    else:
      date_time = dfdatetime_filetime.Filetime(timestamp=value)
      date_time_string = date_time.CopyToDateTimeString()
      if date_time_string:
        date_time_string = f'{date_time_string:s} UTC'
      else:
        date_time_string = f'0x{value:08x}'

    return date_time_string

  def _WritePropertyStore(self, fwps_store):
    """Writes a property store to stdout.

    Args:
      fwps_store (pyfwps.store): property store.
    """
    for fwps_set in iter(fwps_store.sets):
      for fwps_record in iter(fwps_set.records):
        if fwps_record.value_type == 0x0001:
          value_string = '<VT_NULL>'
        elif fwps_record.value_type in (0x0003, 0x0013, 0x0014, 0x0015):
          value_string = str(fwps_record.get_data_as_integer())
        elif fwps_record.value_type in (0x0008, 0x001e, 0x001f):
          value_string = fwps_record.get_data_as_string()
        elif fwps_record.value_type == 0x000b:
          value_string = str(fwps_record.get_data_as_boolean())
        elif fwps_record.value_type == 0x0040:
          filetime = fwps_record.get_data_as_integer()
          value_string = self._FormatFiletimeValue(filetime)
        elif fwps_record.value_type == 0x0042:
          # TODO: add support
          value_string = '<VT_STREAM>'
        elif fwps_record.value_type == 0x0048:
          value_string = fwps_record.get_data_as_guid()
        elif fwps_record.value_type & 0xf000 == 0x1000:
          # TODO: add support
          value_string = '<VT_VECTOR>'
        else:
          raise RuntimeError(
              f'Unsupported value type: 0x{fwps_record.value_type:04x}')

        if fwps_record.entry_name:
          entry_string = fwps_record.entry_name
        else:
          entry_string = f'{fwps_record.entry_type:d}'

        property_key = f'{{{fwps_set.identifier:s}}}/{entry_string:s}'
        shell_property_key = shell_property_keys.SHELL_PROPERTY_KEYS.get(
            property_key, 'Unknown')
        self.WriteText(
            f'\t\tProperty: {property_key:s} ({shell_property_key:s})\n')

        self.WriteValue(
            f'\t\t\tValue (0x{fwps_record.value_type:04x})', value_string)

  def _WriteShellItem(self, fwsi_item):
    """Writes a shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    if isinstance(fwsi_item, pyfwsi.control_panel_category):
      shell_item_type = 'Control Panel Category'
    elif isinstance(fwsi_item, pyfwsi.control_panel_item):
      shell_item_type = 'Control Panel Item'
    elif isinstance(fwsi_item, pyfwsi.file_entry):
      shell_item_type = 'File Entry'
    elif isinstance(fwsi_item, pyfwsi.network_location):
      shell_item_type = 'Network Location'
    elif isinstance(fwsi_item, pyfwsi.root_folder):
      shell_item_type = 'Root Folder'
    elif isinstance(fwsi_item, pyfwsi.users_property_view):
      shell_item_type = 'Users Property View'
    elif isinstance(fwsi_item, pyfwsi.volume):
      shell_item_type = 'Volume'
    else:
      shell_item_type = f'Unknown (0x{fwsi_item.class_type:02x})'

    self.WriteValue('\t\t\tItem type', shell_item_type)

    if fwsi_item.delegate_folder_identifier:
      self.WriteValue(
          '\t\t\tDelegate folder', fwsi_item.delegate_folder_identifier)

    if isinstance(fwsi_item, pyfwsi.control_panel_category):
      self._WriteShellItemControlPanelCategory(fwsi_item)

    elif isinstance(fwsi_item, pyfwsi.control_panel_item):
      self._WriteShellItemControlPanelItem(fwsi_item)

    elif isinstance(fwsi_item, pyfwsi.file_entry):
      self._WriteShellItemFileEntry(fwsi_item)

    elif isinstance(fwsi_item, pyfwsi.network_location):
      self._WriteShellItemNetworkLocation(fwsi_item)

    elif isinstance(fwsi_item, pyfwsi.root_folder):
      self.WriteValue(
          '\t\t\tRoot shell folder identifier',
          fwsi_item.shell_folder_identifier)

    elif isinstance(fwsi_item, pyfwsi.users_property_view):
      self._WriteShellItemUsersPropertyView(fwsi_item)

    elif isinstance(fwsi_item, pyfwsi.volume):
      self._WriteShellItemVolume(fwsi_item)

    if fwsi_item.number_of_extension_blocks:
      for index, extension_block in enumerate(fwsi_item.extension_blocks):
        display_index = index + 1
        self.WriteText(f'\t\tExtension block: {display_index:d}\n')

        # TODO: print human readable description of signature
        self.WriteValue('\t\t\tSignature', f'0x{extension_block.signature:04x}')

        if isinstance(extension_block, pyfwsi.file_entry_extension):
          fat_date_time = extension_block.get_creation_time_as_integer()
          date_time_string = self._FormatFATDateTimeValue(fat_date_time)
          self.WriteValue('\t\t\tCreation time', date_time_string)

          fat_date_time = extension_block.get_access_time_as_integer()
          date_time_string = self._FormatFATDateTimeValue(fat_date_time)
          self.WriteValue('\t\t\tAccess time', date_time_string)

          self.WriteValue('\t\t\tLong name', extension_block.long_name)

          if extension_block.localized_name:
            self.WriteValue(
                '\t\t\tLocalized name', extension_block.localized_name)

          file_reference = extension_block.file_reference
          if file_reference is not None:
            if file_reference > 0x1000000000000:
              mft_entry = file_reference & 0xffffffffffff
              sequence_number = file_reference >> 48
              file_reference = f'{mft_entry:d}-{sequence_number:d}'
            else:
              file_reference = f'0x{file_reference:04x}'

            self.WriteValue('\t\t\tFile reference', file_reference)

        # TODO: add support for other extension blocks

    self.WriteText('\n')

  def _WriteShellItemControlPanelCategory(self, fwsi_item):
    """Writes a control panel category shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    self.WriteValue(
        '\t\t\tControl panel category identifier', f'{fwsi_item.identifier:d}')

  def _WriteShellItemControlPanelItem(self, fwsi_item):
    """Writes a control panel item shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    self.WriteValue('\t\t\tControl panel item identifier', fwsi_item.identifier)

  def _WriteShellItemFileEntry(self, fwsi_item):
    """Writes a file entry shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    self.WriteValue('\t\t\tFile size', f'{fwsi_item.file_size:d}')

    fat_date_time = fwsi_item.get_modification_time_as_integer()
    date_time_string = self._FormatFATDateTimeValue(fat_date_time)
    self.WriteValue('\t\t\tModification time', date_time_string)

    self.WriteValue(
        '\t\t\tFile attribute flags',
        f'0x08{fwsi_item.file_attribute_flags:08x}')

    self.WriteValue('\t\t\tName', fwsi_item.name)

  def _WriteShellItemNetworkLocation(self, fwsi_item):
    """Writes a network location shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    self.WriteValue('\t\t\tNetwork location', fwsi_item.location)

    if fwsi_item.description:
      self.WriteValue('\t\t\tDescription', fwsi_item.description)

    if fwsi_item.comments:
      self.WriteValue('\t\t\tComments', fwsi_item.comments)

  def _WriteShellItemUsersPropertyView(self, fwsi_item):
    """Writes an users property view item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    if fwsi_item.property_store_data:
      fwps_store = pyfwps.store()
      fwps_store.copy_from_byte_stream(fwsi_item.property_store_data)

      self._WritePropertyStore(fwps_store)

  def _WriteShellItemVolume(self, fwsi_item):
    """Writes a volume shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    if fwsi_item.name:
      self.WriteValue('\t\t\tVolume name', fwsi_item.name)

    if fwsi_item.identifier:
      self.WriteValue('\t\t\tVolume identifier', fwsi_item.identifier)

    if fwsi_item.shell_folder_identifier:
      self.WriteValue(
          '\t\t\tVolume shell folder identifier',
          fwsi_item.shell_folder_identifier)

  def _WriteShortcutDataBlock(self, lnk_data_block):
    """Writes a Windows Shortcut data block to stdout.

    Args:
      lnk_data_block (pylnk.data_block): Windows Shortcut data block.
    """
    description = self._LNK_DATA_BLOCK_DESCRIPTIONS.get(
        lnk_data_block.signature, None)
    if description:
      value_string = f'0x{lnk_data_block.signature:08x} ({description:s})'
    else:
      value_string = f'0x{lnk_data_block.signature:08x}'
    self.WriteValue('\t\tSignature', value_string)

    if lnk_data_block.signature in (0xa0000001, 0xa0000007):
      # TODO: handle unpaired surrogates in path string
      self.WriteValue('\t\tString', lnk_data_block.path_string)

    elif lnk_data_block.signature == 0xa0000006:
      self.WriteValue('\t\tString', lnk_data_block.string)

    elif lnk_data_block.signature == 0xa0000009:
      self._WriteShortcutMetadataPropertyStore(lnk_data_block)

    # TODO: print string/location data blocks
    # TODO: print distributed link tracker properties

    self.WriteText('\n')

  def _WriteShortcutDataFlags(self, data_flags):
    """Writes a Windows Shortcut data flags to stdout.

    Args:
      data_flags (int): Windows Shortcut data flags.
    """
    if data_flags & 0x00000001:
      self.WriteText('\t\tContains a link target identifier\n')

    if data_flags & 0x00000004:
      self.WriteText('\t\tContains a description string\n')
    if data_flags & 0x00000008:
      self.WriteText('\t\tContains a relative path string\n')
    if data_flags & 0x00000010:
      self.WriteText('\t\tContains a working directory string\n')
    if data_flags & 0x00000020:
      self.WriteText('\t\tContains a command line arguments string\n')
    if data_flags & 0x00000040:
      self.WriteText('\t\tContains an icon location string\n')

    if data_flags & 0x00000200:
      self.WriteText('\t\tContains an environment variables block\n')

    if data_flags & 0x00004000:
      self.WriteText('\t\tContains an icon location block\n')

    if data_flags & 0x00040000:
      self.WriteText('\t\tContains no distributed link tracking data block\n')

  def _WriteShortcutLinkInformation(self, lnk_file):
    """Writes a Windows Shortcut link information to stdout.

    Args:
      lnk_file (pylnk.file): Windows Shortcut file.
    """
    self.WriteText('\tLink information:\n')

    filetime = lnk_file.get_file_creation_time_as_integer()
    date_time_string = self._FormatFiletimeValue(filetime)
    self.WriteValue('\t\tCreation time', date_time_string)

    filetime = lnk_file.get_file_modification_time_as_integer()
    date_time_string = self._FormatFiletimeValue(filetime)
    self.WriteValue('\t\tModification time', date_time_string)

    filetime = lnk_file.get_file_access_time_as_integer()
    date_time_string = self._FormatFiletimeValue(filetime)
    self.WriteValue('\t\tAccesss time', date_time_string)

    self.WriteValue('\t\tFile size', f'{lnk_file.file_size:d}')
    self.WriteValue('\t\tIcon index', f'{lnk_file.icon_index:d}')
    self.WriteValue(
        '\t\tShow Window value', f'0x{lnk_file.show_window_value:08x}')
    self.WriteValue('\t\tHot Key value', f'{lnk_file.hot_key_value:d}')

    self.WriteValue(
        '\t\tFile attribute flags', f'0x{lnk_file.file_attribute_flags:08x}')
    # TODO: print human readable descriptions of file attribute flags.

    self.WriteValue('\t\tDescription', lnk_file.description or '')
    self.WriteValue('\t\tRelative path', lnk_file.relative_path or '')
    self.WriteValue('\t\tWorking directory', lnk_file.working_directory or '')
    self.WriteValue('\t\tIcon location', lnk_file.icon_location or '')

    self.WriteText('\n')

  def _WriteShortcutLinkTargetIdentifier(self, lnk_file):
    """Writes a Windows Shortcut link target identifier to stdout.

    Args:
      lnk_file (pylnk.file): Windows Shortcut file.
    """
    if lnk_file.link_target_identifier_data:
      self.WriteText('\tLink target identifier:\n')

      fwsi_item_list = pyfwsi.item_list()
      fwsi_item_list.copy_from_byte_stream(
          lnk_file.link_target_identifier_data)

      self.WriteText('\t\tShell item list:\n')
      self.WriteValue('\t\t\tNumber of items', fwsi_item_list.number_of_items)
      self.WriteText('\n')

      for item_index, fwsi_item in enumerate(fwsi_item_list.items):
        display_item_index = item_index + 1
        self.WriteText(f'\t\tShell item: {display_item_index:d}\n')

        self._WriteShellItem(fwsi_item)

  def _WriteShortcutMetadataPropertyStore(self, lnk_data_block):
    """Writes a Windows Shortcut metadata property store to stdout.

    Args:
      lnk_data_block (pylnk.data_block): Windows Shortcut data block.
    """
    if lnk_data_block.data:
      fwps_store = pyfwps.store()
      fwps_store.copy_from_byte_stream(lnk_data_block.data)

      self._WritePropertyStore(fwps_store)

  def WriteShortcut(self, lnk_file):
    """Writes a Windows Shortcut file to stdout.

    Args:
      lnk_file (pylnk.file): Windows Shortcut file.
    """
    self.WriteText('\tWindows Shortcut information:\n')

    self._WriteShortcutDataFlags(lnk_file.data_flags)

    self.WriteValue('\tNumber of data blocks', lnk_file.number_of_data_blocks)

    self.WriteText('\n')

    self._WriteShortcutLinkInformation(lnk_file)
    self._WriteShortcutLinkTargetIdentifier(lnk_file)

    for data_block_index, lnk_data_block in enumerate(lnk_file.data_blocks):
      display_data_block_index = data_block_index + 1
      self.WriteText(f'\tData block: {display_data_block_index:d}\n')

      self._WriteShortcutDataBlock(lnk_data_block)


def Main():
  """Entry point of console script to parse Windows Jump List files.

  Returns:
    int: exit code that is provided to sys.exit().
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from Windows Jump List files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  if dfvfs_helpers:
    dfvfs_helpers.AddDFVFSCLIArguments(argument_parser)

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the Windows Jump List file.')

  options = argument_parser.parse_args()

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  if dfvfs_helpers and getattr(options, 'image', None):
    file_system_helper = dfvfs_helpers.ParseDFVFSCLIArguments(options)
    if not file_system_helper:
      print('No supported file system found in storage media image.')
      print('')
      return 1

  else:
    if not options.source:
      print('Source file missing.')
      print('')
      argument_parser.print_help()
      print('')
      return 1

    file_system_helper = file_system.NativeFileSystemHelper()

  output_writer = StdoutWriter()

  try:
    output_writer.Open()
  except IOError as exception:
    print(f'Unable to open output writer with error: {exception!s}')
    print('')
    return 1

  file_object = file_system_helper.OpenFileByPath(options.source)
  if not file_object:
    print('Unable to open source file.')
    print('')
    return 1

  try:
    is_olecf = pyolecf.check_file_signature_file_object(file_object)
  finally:
    file_object.close()

  if is_olecf:
    jump_list_file = jump_list.AutomaticDestinationsFile(
        debug=options.debug, file_system_helper=file_system_helper,
        output_writer=output_writer)
  else:
    jump_list_file = jump_list.CustomDestinationsFile(
        debug=options.debug, file_system_helper=file_system_helper,
        output_writer=output_writer)

  jump_list_file.Open(options.source)

  jump_list_entries = list(jump_list_file.GetJumpListEntries())

  output_writer.WriteText('Windows Jump List information:\n')

  number_of_entries = len(jump_list_entries)
  output_writer.WriteValue('Number of entries', f'{number_of_entries:d}')

  output_writer.WriteText('\n')

  for entry_index, jump_list_entry in enumerate(jump_list_entries):
    display_entry_index = entry_index + 1
    output_writer.WriteText(f'Entry: {display_entry_index:d}\n')

    output_writer.WriteShortcut(jump_list_entry.lnk_file)

  jump_list_file.Close()

  output_writer.Close()

  return 0


if __name__ == '__main__':
  sys.exit(Main())
