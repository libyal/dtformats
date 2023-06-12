# -*- coding: utf-8 -*-
"""Firefox cache version 1 files."""

import os

from dtformats import data_format
from dtformats import errors


class CacheMapFile(data_format.BinaryDataFile):
  """Firefox cache version 1 map file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('firefox_cache1.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'firefox_cache1.debug.yaml', custom_format_callbacks={
          'array_of_decimal': '_FormatArrayOfIntegersAsDecimals',
          'cache_location': '_FormatCacheLocation'})

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Firefox cache map file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(CacheMapFile, self).__init__(
        debug=debug, output_writer=output_writer)

  def _FormatCacheLocation(self, integer):
    """Formats a cache location.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a cache location.
    """
    block_number = integer & 0x00ffffff
    extra_blocks = (integer & 0x03000000) >> 24
    location_selector = (integer & 0x30000000) >> 28
    reserved = (integer & 0x4c000000) >> 26
    location_flag = (integer & 0x80000000) >> 31
    return (
        f'block number: {block_number:d}, extra blocks: {extra_blocks:d}, '
        f'location selector: {location_selector:d}, reserved: {reserved:02x}, '
        f'location flag: {location_flag:d}')

  def _ReadFileHeader(self, file_object):
    """Reads a file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('firefox_cache1_map_header')

    file_header, file_header_data_size = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'file header')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get(
          'firefox_cache1_map_header', None)
      self._DebugPrintStructureObject(file_header, debug_info)

    if file_header.major_format_version != 1:
      raise errors.ParseError((
          f'Unsupported major format version: '
          f'{file_header.major_format_version:d}'))

    if file_header.data_size != (self._file_size - file_header_data_size):
      raise errors.ParseError('Data size does not correspond with file size.')

  def _ReadRecord(self, file_object, file_offset):
    """Reads a record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data relative to the start of
          the file-like object.

    Raises:
      ParseError: if the record cannot be read.
    """
    data_type_map = self._GetDataTypeMap('firefox_cache1_map_record')

    record, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'record')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get(
          'firefox_cache1_map_record', None)
      self._DebugPrintStructureObject(record, debug_info)

  def ReadFileObject(self, file_object):
    """Reads a Firefox cache map file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadFileHeader(file_object)

    file_offset = file_object.tell()
    while file_offset < self._file_size:
      self._ReadRecord(file_object, file_offset)
      file_offset = file_object.tell()


class CacheBlockFile(data_format.BinaryDataFile):
  """Firefox cache version 1 block file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('firefox_cache1.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'firefox_cache1.debug.yaml', custom_format_callbacks={
          'cache_location': '_FormatCacheLocation',
          'posix_time': '_FormatIntegerAsPosixTime'})

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Firefox cache map file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(CacheBlockFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._block_size = None

  def _FormatCacheLocation(self, integer):
    """Formats a cache location.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a cache location.
    """
    block_number = integer & 0x00ffffff
    extra_blocks = (integer & 0x03000000) >> 24
    location_selector = (integer & 0x30000000) >> 28
    reserved = (integer & 0x4c000000) >> 26
    location_flag = (integer & 0x80000000) >> 31
    return (
        f'block number: {block_number:d}, extra blocks: {extra_blocks:d}, '
        f'location selector: {location_selector:d}, reserved: {reserved:02x}, '
        f'location flag: {location_flag:d}')

  def _ReadCacheEntry(self, file_object, file_offset):
    """Reads a cache entry.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data relative to the start of
          the file-like object.

    Raises:
      ParseError: if the cache entry cannot be read.
    """
    data_type_map = self._GetDataTypeMap('firefox_cache1_entry')

    try:
      cache_entry, cache_entry_data_size = self._ReadStructureFromFileObject(
          file_object, file_offset, data_type_map, 'cache_entry')
    except errors.ParseError:
      file_object.seek(file_offset + self._block_size, os.SEEK_SET)
      return

    if self._debug and cache_entry.major_format_version == 1:
      debug_info = self._DEBUG_INFORMATION.get('firefox_cache1_entry', None)
      self._DebugPrintStructureObject(cache_entry, debug_info)

    _, trailing_data_size = divmod(cache_entry_data_size, self._block_size)
    if trailing_data_size > 0:
      next_block_offset = self._block_size - trailing_data_size
      file_object.seek(next_block_offset, os.SEEK_CUR)

  def ReadFileObject(self, file_object):
    """Reads a Firefox cache block file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    filename = os.path.basename(self._path)
    if filename == '_CACHE_001_':
      self._block_size = 256
    elif filename == '_CACHE_002_':
      self._block_size = 1024
    elif filename == '_CACHE_003_':
      self._block_size = 4096
    else:
      raise errors.ParseError(f'Unsupported cache block filename: {filename:s}')

    file_offset = 0
    while file_offset < self._file_size:
      self._ReadCacheEntry(file_object, file_offset)
      file_offset = file_object.tell()
