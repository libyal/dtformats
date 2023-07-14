# -*- coding: utf-8 -*-
"""Windows Jump List files:
* .automaticDestinations-ms
* .customDestinations-ms
"""

import logging
import os

import pyfwps
import pyfwsi
import pylnk
import pyolecf

from dtformats import data_format
from dtformats import data_range
from dtformats import errors


class JumpListEntry(object):
  """Jump list entry.

  Attributes:
    identifier (str): identifier.
    lnk_file (pylnk.file): LNK file.
  """

  def __init__(self, identifier):
    """Initializes the jump list entry.

    Args:
      identifier (str): identifier.
    """
    super(JumpListEntry, self).__init__()
    self.identifier = identifier
    self.lnk_file = None

  def __del__(self):
    """Destroys the jump list entry."""
    if self.lnk_file:
      self.lnk_file.close()
      self.lnk_file = None

  def GetProperties(self):
    """Retrieves the propertirs.

    Yields:
      tuple[str, pyfwps.record]: property set identifier and property record.
    """
    for lnk_data_block in iter(self.lnk_file.data_blocks):
      if lnk_data_block.signature == 0xa0000009:
        fwps_store = pyfwps.store()
        fwps_store.copy_from_byte_stream(lnk_data_block.data)

        for fwps_set in iter(fwps_store.sets):
          for fwps_record in iter(fwps_set.records):
            yield fwps_set.identifier, fwps_record

  def GetShellItems(self):
    """Retrieves the shell items.

    Yields:
      pyfswi.item: shell item.
    """
    if self.lnk_file.link_target_identifier_data:  # pylint: disable=using-constant-test
      fwsi_item_list = pyfwsi.item_list()
      fwsi_item_list.copy_from_byte_stream(
          self.lnk_file.link_target_identifier_data)

      yield from iter(fwsi_item_list.items)

  def ReadFileObject(self, file_object):
    """Reads the LNK file from a file-like object.

    Args:
      file_object (file): file-like object that contains the LNK file
          entry data.
    """
    self.lnk_file = pylnk.file()
    self.lnk_file.open_file_object(file_object)


class AutomaticDestinationsFile(data_format.BinaryDataFile):
  """Automatic Destinations Jump List (.automaticDestinations-ms) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('jump_list.yaml')

  # TODO: add custom formatter for pin status.
  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'jump_list.debug.yaml', custom_format_callbacks={
          'filetime': '_FormatIntegerAsFiletime',
          'path_size': '_FormatIntegerAsPathSize'})

  def __init__(self, debug=False, file_system_helper=None, output_writer=None):
    """Initializes an Automatic Destinations Jump List file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      file_system_helper (Optional[FileSystemHelper]): file system helper.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(AutomaticDestinationsFile, self).__init__(
        debug=debug, file_system_helper=file_system_helper,
        output_writer=output_writer)
    self._format_version = None
    self._olecf_file = None

  def _FormatIntegerAsPathSize(self, integer):
    """Formats an integer as a path size.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as path size.
    """
    number_of_bytes = integer * 2
    return f'{integer:d} characters ({number_of_bytes:d} bytes)'

  def _ReadDestList(self, root_item):
    """Reads the DestList stream.

    Args:
      root_item (pyolecf.item): OLECF root item.

    Raises:
      ParseError: if the root item or DestList stream is missing.
    """
    if not root_item:
      raise errors.ParseError('Missing OLECF root item')

    olecf_item = root_item.get_sub_item_by_name('DestList')
    if not olecf_item:
      raise errors.ParseError('Missing DestList stream.')

    # The DestList stream can be of size 0 if the Jump List is empty.
    if olecf_item.size > 0:
      self._ReadDestListHeader(olecf_item)

      stream_offset = olecf_item.get_offset()
      stream_size = olecf_item.get_size()
      while stream_offset < stream_size:
        entry_size = self._ReadDestListEntry(olecf_item, stream_offset)
        stream_offset += entry_size

  def _ReadDestListEntry(self, olecf_item, stream_offset):
    """Reads a DestList stream entry.

    Args:
      olecf_item (pyolecf.item): OLECF item.
      stream_offset (int): stream offset of the entry.

    Returns:
      int: entry data size.

    Raises:
      ParseError: if the DestList stream entry cannot be read.
    """
    if self._format_version == 1:
      data_type_map = self._GetDataTypeMap('dest_list_entry_v1')
      description = 'dest list entry v1'

    elif self._format_version >= 2:
      data_type_map = self._GetDataTypeMap('dest_list_entry_v2')
      description = 'dest list entry v2'

    dest_list_entry, entry_data_size = self._ReadStructureFromFileObject(
        olecf_item, stream_offset, data_type_map, description)

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('dest_list_entry', None)
      self._DebugPrintStructureObject(dest_list_entry, debug_info)

    return entry_data_size

  def _ReadDestListHeader(self, olecf_item):
    """Reads the DestList stream header.

    Args:
      olecf_item (pyolecf.item): OLECF item.

    Raises:
      ParseError: if the DestList stream header cannot be read.
    """
    stream_offset = olecf_item.tell()
    data_type_map = self._GetDataTypeMap('dest_list_header')

    dest_list_header, _ = self._ReadStructureFromFileObject(
        olecf_item, stream_offset, data_type_map, 'dest list header')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('dest_list_header', None)
      self._DebugPrintStructureObject(dest_list_header, debug_info)

    if dest_list_header.format_version not in (1, 2, 3, 4):
      raise errors.ParseError(
          f'Unsupported format version: {dest_list_header.format_version:d}')

    self._format_version = dest_list_header.format_version

  def _ReadJumpListEntry(self, olecf_item):
    """Reads a jump list entry.

    Args:
      olecf_item (pyolecf.item): OLECF item.

    Returns:
      JumpListEntry: a jump list entry.

    Raises:
      ParseError: if the jump list entry cannot be read.
    """
    if self._debug:
      self._DebugPrintText(f'Reading LNK file from stream: {olecf_item.name:s}')

    jump_list_entry = JumpListEntry(olecf_item.name)

    try:
      jump_list_entry.ReadFileObject(olecf_item)
    except IOError as exception:
      raise errors.ParseError((
          f'Unable to parse LNK file from stream: {olecf_item.name:s} '
          f'with error: {exception!s}'))

    if self._debug:
      self._DebugPrintText('\n')

    return jump_list_entry

  def Close(self):
    """Closes an Automatic Destinations Jump List file.

    Raises:
      IOError: if the file is not opened.
      OSError: if the file is not opened.
    """
    if self._olecf_file:
      self._olecf_file.close()
      self._olecf_file = None

    super(AutomaticDestinationsFile, self).Close()

  def GetJumpListEntries(self):
    """Retrieves jump list entries.

    Yields:
      JumpListEntry: a jump list entry.
    """
    for olecf_item in iter(self._olecf_file.root_item.sub_items):  # pylint: disable=no-member
      if olecf_item.name != 'DestList':
        yield self._ReadJumpListEntry(olecf_item)

  def ReadFileObject(self, file_object):
    """Reads an Automatic Destinations Jump List file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    olecf_file = pyolecf.file()
    olecf_file.open_file_object(file_object)

    self._ReadDestList(olecf_file.root_item)

    self._olecf_file = olecf_file


class CustomDestinationsFile(data_format.BinaryDataFile):
  """Custom Destinations Jump List (.customDestinations-ms) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('jump_list.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'jump_list.debug.yaml', custom_format_callbacks={})

  _FILE_FOOTER_SIGNATURE = 0xbabffbab

  _LNK_GUID = (
      b'\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46')

  def __init__(self, debug=False, file_system_helper=None, output_writer=None):
    """Initializes a Custom Destinations Jump List file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      file_system_helper (Optional[FileSystemHelper]): file system helper.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(CustomDestinationsFile, self).__init__(
        debug=debug, file_system_helper=file_system_helper,
        output_writer=output_writer)

  def _ReadFileFooter(self, file_object):
    """Reads the file footer.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('custom_file_footer')

    file_footer, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file footer')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('custom_file_footer', None)
      self._DebugPrintStructureObject(file_footer, debug_info)

    if file_footer.signature != self._FILE_FOOTER_SIGNATURE:
      raise errors.ParseError(
          f'Invalid footer signature at offset: 0x{file_offset:08x}.')

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('custom_file_header')

    file_header, file_offset = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'file header')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('custom_file_header', None)
      self._DebugPrintStructureObject(file_header, debug_info)

    if file_header.unknown1 != 2:
      raise errors.ParseError(
          f'Unsupported unknown1: {file_header.unknown1:d}.')

    if file_header.header_values_type > 2:
      raise errors.ParseError(
          f'Unsupported header value type: {file_header.header_values_type:d}.')

    if file_header.header_values_type == 0:
      data_type_map_name = 'custom_file_header_value_type_0'
    else:
      data_type_map_name = 'custom_file_header_value_type_1_or_2'

    data_type_map = self._GetDataTypeMap(data_type_map_name)

    file_header_value, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'custom file header value')

    if self._debug:
      if file_header.header_values_type == 0:
        self._DebugPrintValue(
            'Number of characters',
            f'{file_header_value.number_of_characters:d}')

        # TODO: print string.

      self._DebugPrintValue(
          'Number of entries', f'{file_header_value.number_of_entries:d}')

      self._DebugPrintText('\n')

  def _ReadJumpListEntry(self, file_object):
    """Reads a jump list entry.

    Args:
      file_object (file): file-like object.

    Returns:
      JumpListEntry: a jump list entry.

    Raises:
      ParseError: if the jump list entry cannot be read.
    """
    file_offset = file_object.tell()
    if self._debug:
      self._DebugPrintText(
          f'Reading LNK file at offset: 0x{file_offset:08x}\n')

    jump_list_entry = JumpListEntry(f'0x{file_offset:08x}')

    try:
      jump_list_entry.ReadFileObject(file_object)
    except IOError as exception:
      raise errors.ParseError((
          f'Unable to parse LNK file at offset: 0x{file_offset:08x} '
          f'with error: {exception!s}'))

    if self._debug:
      self._DebugPrintText('\n')

    return jump_list_entry

  def GetJumpListEntries(self):
    """Retrieves jump list entries.

    Yields:
      JumpListEntry: a jump list entry.

    Raises:
      ParseError: if the jump list entries cannot be read.
    """
    file_offset = self._file_object.tell()
    remaining_file_size = self._file_size - file_offset
    data_type_map = self._GetDataTypeMap('custom_entry_header')

    # The Custom Destination file does not have a unique signature in the file
    # header that is why we use the first LNK class identifier (GUID) as
    # a signature.
    first_guid_checked = False
    while remaining_file_size > 4:
      try:
        entry_header, _ = self._ReadStructureFromFileObject(
            self._file_object, file_offset, data_type_map, 'entry header')

      except errors.ParseError as exception:
        error_message = (
            f'Unable to parse file entry header at offset: 0x{file_offset:08x} '
            f'with error: {exception!s}')

        if not first_guid_checked:
          raise errors.ParseError(error_message)

        logging.warning(error_message)
        break

      if entry_header.guid != self._LNK_GUID:
        error_message = f'Invalid entry header at offset: 0x{file_offset:08x}.'

        if not first_guid_checked:
          raise errors.ParseError(error_message)

        self._file_object.seek(-16, os.SEEK_CUR)
        self._ReadFileFooter(self._file_object)

        self._file_object.seek(-4, os.SEEK_CUR)
        break

      first_guid_checked = True
      file_offset += 16
      remaining_file_size -= 16

      data_range_file_object = data_range.DataRange(
          self._file_object, data_offset=file_offset,
          data_size=remaining_file_size)

      yield self._ReadJumpListEntry(data_range_file_object)

      # We cannot trust the file size in the LNK data so we get the last offset
      # that was read instead. Because of DataRange the offset will be relative
      # to the start of the LNK data.
      data_size = data_range_file_object.get_offset()

      file_offset += data_size
      remaining_file_size -= data_size

      self._file_object.seek(file_offset, os.SEEK_SET)

  def ReadFileObject(self, file_object):
    """Reads a Custom Destinations Jump List file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadFileHeader(file_object)
