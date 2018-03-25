# -*- coding: utf-8 -*-
"""Chrome Cache files."""

from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
import os

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import fabric as dtfabric_fabric

from dtformats import data_format
from dtformats import errors
from dtformats import py2to3


def SuperFastHash(key):
  """Function to calculate the super fast hash.

  Args:
    key (bytes): key for which to calculate the hash.

  Returns:
    int: hash of the key.
  """
  if not key:
    return 0

  key_length = len(key)
  hash_value = key_length & 0xffffffff
  remainder = key_length & 0x00000003
  key_length -= remainder

  if isinstance(key[0], py2to3.STRING_TYPES):
    key = [ord(byte_value) for byte_value in key]

  for key_index in range(0, key_length, 4):
    hash_value = (
        (hash_value + key[key_index] + (key[key_index + 1] << 8)) & 0xffffffff)
    temp_value = key[key_index + 2] + (key[key_index + 3] << 8)

    temp_value = ((temp_value << 11) & 0xffffffff) ^ hash_value
    hash_value = ((hash_value << 16) & 0xffffffff) ^ temp_value

    hash_value = (hash_value + (hash_value >> 11)) & 0xffffffff

  key_index = key_length

  if remainder == 3:
    hash_value = (
        (hash_value + key[key_index] + (key[key_index + 1] << 8)) & 0xffffffff)
    hash_value ^= (hash_value << 16) & 0xffffffff
    hash_value ^= (key[key_index + 2] << 18) & 0xffffffff
    hash_value = (hash_value + (hash_value >> 11)) & 0xffffffff

  elif remainder == 2:
    hash_value = (
        (hash_value + key[key_index] + (key[key_index + 1] << 8)) & 0xffffffff)
    hash_value ^= (hash_value << 11) & 0xffffffff
    hash_value = (hash_value + (hash_value >> 17)) & 0xffffffff

  elif remainder == 1:
    hash_value = (hash_value + key[key_index]) & 0xffffffff
    hash_value ^= (hash_value << 10) & 0xffffffff
    hash_value = (hash_value + (hash_value >> 1)) & 0xffffffff

  # Force "avalanching" of final 127 bits.
  hash_value ^= (hash_value << 3) & 0xffffffff
  hash_value = (hash_value + (hash_value >> 5)) & 0xffffffff
  hash_value ^= (hash_value << 4) & 0xffffffff
  hash_value = (hash_value + (hash_value >> 17)) & 0xffffffff
  hash_value ^= (hash_value << 25) & 0xffffffff
  hash_value = (hash_value + (hash_value >> 6)) & 0xffffffff

  return hash_value


class CacheAddress(object):
  """Cache address.

  Attributes:
    block_number (int): block data file number.
    block_offset (int): offset within the block data file.
    block_size (int): block size.
    filename (str): name of the block data file.
    value (int): cache address.
  """
  FILE_TYPE_SEPARATE = 0
  FILE_TYPE_BLOCK_RANKINGS = 1
  FILE_TYPE_BLOCK_256 = 2
  FILE_TYPE_BLOCK_1024 = 3
  FILE_TYPE_BLOCK_4096 = 4

  _BLOCK_DATA_FILE_TYPES = (
      FILE_TYPE_BLOCK_RANKINGS,
      FILE_TYPE_BLOCK_256,
      FILE_TYPE_BLOCK_1024,
      FILE_TYPE_BLOCK_4096)

  _FILE_TYPE_DESCRIPTIONS = {
      FILE_TYPE_SEPARATE: 'Separate file',
      FILE_TYPE_BLOCK_RANKINGS: 'Rankings block file',
      FILE_TYPE_BLOCK_256: '256 byte block file',
      FILE_TYPE_BLOCK_1024: '1024 byte block file',
      FILE_TYPE_BLOCK_4096: '4096 byte block file'}

  _FILE_TYPE_BLOCK_SIZES = (0, 36, 256, 1024, 4096)

  def __init__(self, cache_address):
    """Initializes a cache address.

    Args:
      cache_address (int): cache address.
    """
    super(CacheAddress, self).__init__()
    self.block_number = None
    self.block_offset = None
    self.block_size = None
    self.filename = None
    self.is_initialized = False
    self.value = cache_address

    if cache_address & 0x80000000:
      self.is_initialized = True

    self.file_type = (cache_address & 0x70000000) >> 28
    if not cache_address == 0x00000000:
      if self.file_type == self.FILE_TYPE_SEPARATE:
        file_selector = cache_address & 0x0fffffff
        self.filename = 'f_{0:06x}'.format(file_selector)

      elif self.file_type in self._BLOCK_DATA_FILE_TYPES:
        file_selector = (cache_address & 0x00ff0000) >> 16
        self.filename = 'data_{0:d}'.format(file_selector)

        file_block_size = self._FILE_TYPE_BLOCK_SIZES[self.file_type]
        self.block_number = cache_address & 0x0000ffff
        self.block_size = (cache_address & 0x03000000) >> 24
        self.block_size *= file_block_size
        self.block_offset = 8192 + (self.block_number * file_block_size)

  def GetDebugString(self):
    """Retrieves a debug string of the cache address object.

    Return:
      str: debug string of the cache address object.
    """
    if self.value == 0x00000000:
      return '0x{0:08x} (uninitialized)'.format(self.value)

    file_type_description = self._FILE_TYPE_DESCRIPTIONS.get(
        self.file_type, 'Unknown')

    if self.file_type == 0:
      return (
          '0x{0:08x} (initialized: {1!s}, file type: {2:s}, '
          'filename: {3:s})').format(
              self.value, self.is_initialized, file_type_description,
              self.filename)

    # TODO: print reserved bits.
    return (
        '0x{0:08x} (initialized: {1!s}, file type: {2:s}, '
        'filename: {3:s}, block number: {4:d}, block offset: 0x{5:08x}, '
        'block size: {6:d})').format(
            self.value, self.is_initialized, file_type_description,
            self.filename, self.block_number, self.block_offset,
            self.block_size)


class CacheEntry(object):
  """Cache entry.

  Attributes:
    creation_time (int): creation time, in number of micro seconds since
        January 1, 1970, 00:00:00 UTC.
    hash (int): super fast hash of the key.
    key (byte): data of the key.
    next (int): cache address of the next cache entry.
    rankings_node (int): cache address of the rankings node.
  """

  def __init__(self):
    """Initializes a cache entry."""
    super(CacheEntry, self).__init__()
    self.creation_time = None
    self.hash = None
    self.key = None
    self.next = None
    self.rankings_node = None


class DataBlockFile(data_format.BinaryDataFile):
  """Chrome Cache data block file.

  Attributes:
    block_size (int): size of a data block.
    creation_time (int): date and time the file was created.
    format_version (str): format version.
    number_of_entries (int): number of entries.
  """

  _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
      os.path.dirname(__file__), 'chrome_cache.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  # TODO: update empty, hints, updating and user.

  _FILE_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'chrome_cache_data_file_header')

  _FILE_HEADER_SIZE = _FILE_HEADER.GetByteSize()

  _CACHE_ENTRY = _DATA_TYPE_FABRIC.CreateDataTypeMap('chrome_cache_entry')

  _CACHE_ENTRY_SIZE = _CACHE_ENTRY.GetByteSize()

  SIGNATURE = 0xc104cac3

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Chrome Cache data block file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(DataBlockFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self.block_size = None
    self.creation_time = None
    self.format_version = None
    self.number_of_entries = None

  def _DebugPrintAllocationBitmap(self, allocation_bitmap):
    """Prints allocation bitmap debug information.

    Args:
      allocation_bitmap (list[int]): allocation bitmap.
    """
    block_number = 0
    block_range_start = 0
    block_range_end = 0
    in_block_range = False

    for value_32bit in allocation_bitmap:
      for unused_bit in range(32):
        if value_32bit & 0x00000001:
          if not in_block_range:
            block_range_start = block_number
            block_range_end = block_number
            in_block_range = True

          block_range_end += 1

        elif in_block_range:
          in_block_range = False

          if self._debug:
            value_string = '{0:d} - {1:d} ({2:d})'.format(
                block_range_start, block_range_end,
                block_range_end - block_range_start)
            self._DebugPrintValue('Block range', value_string)

        value_32bit >>= 1
        block_number += 1

  def _DebugPrintCacheEntry(self, cache_entry):
    """Prints cache entry debug information.

    Args:
      cache_entry (chrome_cache_entry): cache entry.
    """
    value_string = '0x{0:08x}'.format(cache_entry.hash)
    self._DebugPrintValue('Hash', value_string)

    cache_address = CacheAddress(cache_entry.next_address)
    value_string = cache_address.GetDebugString()
    self._DebugPrintValue('Next address', value_string)

    cache_address = CacheAddress(cache_entry.rankings_node_address)
    value_string = cache_address.GetDebugString()
    self._DebugPrintValue('Rankings node address', value_string)

    value_string = '{0:d}'.format(cache_entry.reuse_count)
    self._DebugPrintValue('Reuse count', value_string)

    value_string = '{0:d}'.format(cache_entry.refetch_count)
    self._DebugPrintValue('Refetch count', value_string)

    value_string = '0x{0:08x}'.format(cache_entry.state)
    self._DebugPrintValue('State', value_string)

    date_string = (datetime.datetime(1601, 1, 1) +
                   datetime.timedelta(microseconds=cache_entry.creation_time))

    value_string = '{0!s} (0x{1:08x})'.format(
        date_string, cache_entry.creation_time)
    self._DebugPrintValue('Creation time', value_string)

    for value in cache_entry.data_stream_sizes:
      value_string = '{0:d}'.format(value)
      self._DebugPrintValue('Data stream size', value_string)

    for index, value in enumerate(cache_entry.data_stream_addresses):
      description = 'Data stream address: {0:d}'.format(index)
      cache_address = CacheAddress(value)
      value_string = cache_address.GetDebugString()
      self._DebugPrintValue(description, value_string)

    value_string = '0x{0:08x}'.format(cache_entry.flags)
    self._DebugPrintValue('Flags', value_string)

    value_string = '0x{0:08x}'.format(cache_entry.self_hash)
    self._DebugPrintValue('Self hash', value_string)

    self._DebugPrintValue('Key', cache_entry.key)

    self._DebugPrintText('\n')

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (chrome_cache_data_file_header): file header.
    """
    value_string = '0x{0:08x}'.format(file_header.signature)
    self._DebugPrintValue('Signature', value_string)

    value_string = '{0:d}'.format(file_header.minor_version)
    self._DebugPrintValue('Minor version', value_string)

    value_string = '{0:d}'.format(file_header.major_version)
    self._DebugPrintValue('Major version', value_string)

    value_string = '{0:d}'.format(file_header.file_number)
    self._DebugPrintValue('File number', value_string)

    value_string = '{0:d}'.format(file_header.next_file_number)
    self._DebugPrintValue('Next file number', value_string)

    value_string = '{0:d}'.format(file_header.block_size)
    self._DebugPrintValue('Block size', value_string)

    value_string = '{0:d}'.format(file_header.number_of_entries)
    self._DebugPrintValue('Number of entries', value_string)

    value_string = '{0:d}'.format(file_header.maximum_number_of_entries)
    self._DebugPrintValue('Maximum number of entries', value_string)

    value_string = '{0!s}'.format(file_header.empty)
    self._DebugPrintValue('Empty', value_string)

    value_string = '{0!s}'.format(file_header.hints)
    self._DebugPrintValue('Hints', value_string)

    value_string = '0x{0:08x}'.format(file_header.updating)
    self._DebugPrintValue('Updating', value_string)

    value_string = '{0!s}'.format(file_header.user)
    self._DebugPrintValue('User', value_string)

    self._DebugPrintAllocationBitmap(file_header.allocation_bitmap)

    self._DebugPrintText('\n')

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()
    file_header = self._ReadStructure(
        file_object, file_offset, self._FILE_HEADER_SIZE, self._FILE_HEADER,
        'data block file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

    if file_header.signature != self.SIGNATURE:
      raise errors.ParseError(
          'Unsupported data block file signature: 0x{0:08x}'.format(
              file_header.signature))

    self.format_version = '{0:d}.{1:d}'.format(
        file_header.major_version, file_header.minor_version)

    if self.format_version not in ('2.0', '2.1'):
      raise errors.ParseError(
          'Unsupported data block file version: {0:s}'.format(
              self.format_version))

    self.block_size = file_header.block_size
    self.number_of_entries = file_header.number_of_entries

  def ReadCacheEntry(self, block_offset):
    """Reads a cache entry.

    Args:
      block_offset (int): offset of the block that contains the cache entry.

    Raises:
      ParseError: if the cache entry cannot be read.
    """
    cache_entry = self._ReadStructure(
        self._file_object, block_offset, self._CACHE_ENTRY_SIZE,
        self._CACHE_ENTRY, 'data block cache entry')

    byte_string = bytes(cache_entry.key)
    cache_entry_key, _, _ = byte_string.partition(b'\x00')

    try:
      cache_entry_key = cache_entry_key.decode('ascii')
    except UnicodeDecodeError:
      logging.warning((
          'Unable to decode cache entry key at block offset: '
          '0x{0:08x}. Characters that cannot be decoded will be '
          'replaced with "?" or "\\ufffd".').format(block_offset))
      cache_entry_key = cache_entry_key.decode('ascii', errors='replace')

    cache_entry.key = cache_entry_key

    if self._debug:
      self._DebugPrintCacheEntry(cache_entry)

    # TODO: calculate and verify hash.

    cache_entry_object = CacheEntry()
    cache_entry_object.creation_time = cache_entry.creation_time
    cache_entry_object.hash = cache_entry.hash
    cache_entry_object.key = cache_entry.key
    cache_entry_object.next = CacheAddress(cache_entry.next_address)
    cache_entry_object.rankings_node = CacheAddress(
        cache_entry.rankings_node_address)

    return cache_entry_object

  def ReadFileObject(self, file_object):
    """Reads a Chrome Cache data block file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadFileHeader(file_object)

    self._file_object = file_object


class IndexFile(data_format.BinaryDataFile):
  """Chrome Cache index file.

  Attributes:
    creation_time (int): date and time the file was created.
    format_version (str): format version.
    index_table (dict[str, object]): index table.
  """

  _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
      os.path.dirname(__file__), 'chrome_cache.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _UINT32LE = _DATA_TYPE_FABRIC.CreateDataTypeMap('uint32le')

  _FILE_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'chrome_cache_index_file_header')

  _FILE_HEADER_SIZE = _FILE_HEADER.GetByteSize()

  _LRU_DATA = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'chrome_cache_index_file_lru_data')

  _LRU_DATA_SIZE = _LRU_DATA.GetByteSize()

  SIGNATURE = 0xc103cac3

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Chrome Cache index file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(IndexFile, self).__init__(debug=debug, output_writer=output_writer)
    self.creation_time = None
    self.format_version = None
    self.index_table = {}

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (chrome_cache_index_file_header): file header.
    """
    value_string = '0x{0:08x}'.format(file_header.signature)
    self._DebugPrintValue('Signature', value_string)

    value_string = '{0:d}'.format(file_header.major_version)
    self._DebugPrintValue('Major version', value_string)

    value_string = '{0:d}'.format(file_header.minor_version)
    self._DebugPrintValue('Minor version', value_string)

    value_string = '{0:d}'.format(file_header.number_of_entries)
    self._DebugPrintValue('Number of entries', value_string)

    value_string = '{0:d}'.format(file_header.stored_data_size)
    self._DebugPrintValue('Stored data size', value_string)

    value_string = 'f_{0:06x}'.format(file_header.last_created_file_number)
    self._DebugPrintValue('Last created file number', value_string)

    value_string = '0x{0:08x}'.format(file_header.unknown1)
    self._DebugPrintValue('Unknown1', value_string)

    value_string = '0x{0:08x}'.format(file_header.unknown2)
    self._DebugPrintValue('Unknown2', value_string)

    value_string = '{0:d}'.format(file_header.table_size)
    self._DebugPrintValue('Table size', value_string)

    value_string = '0x{0:08x}'.format(file_header.unknown3)
    self._DebugPrintValue('Unknown3', value_string)

    value_string = '0x{0:08x}'.format(file_header.unknown4)
    self._DebugPrintValue('Unknown4', value_string)

    date_string = (
        datetime.datetime(1601, 1, 1) +
        datetime.timedelta(microseconds=file_header.creation_time))

    value_string = '{0!s} (0x{1:08x})'.format(
        date_string, file_header.creation_time)
    self._DebugPrintValue('Creation time', value_string)

    self._DebugPrintText('\n')

  def _DebugPrintLRUData(self, lru_data):
    """Prints LRU data debug information.

    Args:
      lru_data (chrome_cache_index_file_lru_data): LRU data.
    """
    value_string = '0x{0:08x}'.format(lru_data.filled_flag)
    self._DebugPrintValue('Filled flag', value_string)

    for value in lru_data.sizes:
      value_string = '{0:d}'.format(value)
      self._DebugPrintValue('Size', value_string)

    for index, value in enumerate(lru_data.head_addresses):
      description = 'Head address: {0:d}'.format(index)
      cache_address = CacheAddress(value)
      value_string = cache_address.GetDebugString()
      self._DebugPrintValue(description, value_string)

    for index, value in enumerate(lru_data.tail_addresses):
      description = 'Tail address: {0:d}'.format(index)
      cache_address = CacheAddress(value)
      value_string = cache_address.GetDebugString()
      self._DebugPrintValue(description, value_string)

    cache_address = CacheAddress(lru_data.transaction_address)
    value_string = cache_address.GetDebugString()
    self._DebugPrintValue('Transaction address', value_string)

    value_string = '0x{0:08x}'.format(lru_data.operation)
    self._DebugPrintValue('Operation', value_string)

    value_string = '0x{0:08x}'.format(lru_data.operation_list)
    self._DebugPrintValue('Operation list', value_string)

    self._DebugPrintText('\n')

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()
    file_header = self._ReadStructure(
        file_object, file_offset, self._FILE_HEADER_SIZE, self._FILE_HEADER,
        'index file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

    if file_header.signature != self.SIGNATURE:
      raise errors.ParseError(
          'Unsupported index file signature: 0x{0:08x}'.format(
              file_header.signature))

    self.format_version = '{0:d}.{1:d}'.format(
        file_header.major_version, file_header.minor_version)

    if self.format_version not in ('2.0', '2.1'):
      raise errors.ParseError(
          'Unsupported index file version: {0:s}'.format(self.format_version))

    self.creation_time = file_header.creation_time

  def _ReadLRUData(self, file_object):
    """Reads the LRU data.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the LRU data cannot be read.
    """
    file_offset = file_object.tell()
    lru_data = self._ReadStructure(
        file_object, file_offset, self._LRU_DATA_SIZE, self._LRU_DATA,
        'index file LRU')

    if self._debug:
      self._DebugPrintLRUData(lru_data)

  def _ReadIndexTable(self, file_object):
    """Reads the index table.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the index table cannot be read.
    """
    cache_address_index = 0
    cache_address_data = file_object.read(4)

    while len(cache_address_data) == 4:
      try:
        value = self._UINT32LE.MapByteStream(cache_address_data)
      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError((
            'Unable to parse index table entry: {0:d} with error: '
            '{1:s}').format(cache_address_index, exception))

      if value:
        cache_address = CacheAddress(value)

        if self._debug:
          description = 'Cache address: {0:d}'.format(cache_address_index)
          value_string = cache_address.GetDebugString()
          self._DebugPrintValue(description, value_string)

        self.index_table[cache_address_index] = cache_address

      cache_address_index += 1
      cache_address_data = file_object.read(4)

    if self._debug:
      self._DebugPrintText('\n')

  def ReadFileObject(self, file_object):
    """Reads a Chrome Cache index file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadFileHeader(file_object)
    self._ReadLRUData(file_object)
    self._ReadIndexTable(file_object)


class ChromeCacheParser(object):
  """Chrome Cache parser."""

  _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
      os.path.dirname(__file__), 'chrome_cache.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _UINT32LE = _DATA_TYPE_FABRIC.CreateDataTypeMap('uint32le')

  _UINT32LE_SIZE = _UINT32LE.GetByteSize()

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Chrome Cache parser.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(ChromeCacheParser, self).__init__()
    self._debug = debug
    self._output_writer = output_writer

  def ParseDirectory(self, path):
    """Parses a Chrome Cache directory.

    Args:
      path (str): path of the directory.

    Raises:
      ParseError: if the directory cannot be read.
    """
    index_file_path = os.path.join(path, 'index')
    if not os.path.exists(index_file_path):
      raise errors.ParseError(
          'Missing index file: {0:s}'.format(index_file_path))

    index_file = IndexFile(debug=self._debug, output_writer=self._output_writer)
    index_file.Open(index_file_path)

    data_block_files = {}
    have_all_data_block_files = True
    for cache_address in iter(index_file.index_table.values()):
      if cache_address.filename not in data_block_files:
        data_block_file_path = os.path.join(path, cache_address.filename)

        if not os.path.exists(data_block_file_path):
          logging.error('Missing data block file: {0:s}'.format(
              data_block_file_path))
          have_all_data_block_files = False

        else:
          data_block_file = DataBlockFile(
              debug=self._debug, output_writer=self._output_writer)
          data_block_file.Open(data_block_file_path)

          data_block_files[cache_address.filename] = data_block_file

    if have_all_data_block_files:
      # TODO: read the cache entries from the data block files
      for cache_address in iter(index_file.index_table.values()):
        cache_address_chain_length = 0
        while cache_address.value != 0x00000000:
          if cache_address_chain_length >= 64:
            logging.error(
                'Maximum allowed cache address chain length reached.')
            break

          data_file = data_block_files.get(cache_address.filename, None)
          if not data_file:
            logging.warning(
                'Cache address: 0x{0:08x} missing filename.'.format(
                    cache_address.value))
            break

          # print('Cache address\t: {0:s}'.format(
          #     cache_address.GetDebugString()))
          cache_entry = data_file.ReadCacheEntry(cache_address.block_offset)

          try:
            cache_entry_key = cache_entry.key.decode('ascii')
          except UnicodeDecodeError:
            logging.warning((
                'Unable to decode cache entry key at cache address: '
                '0x{0:08x}. Characters that cannot be decoded will be '
                'replaced with "?" or "\\ufffd".').format(cache_address.value))
            cache_entry_key = cache_entry.key.decode(
                'ascii', errors='replace')

          # TODO: print('Url\t\t: {0:s}'.format(cache_entry_key))
          _ = cache_entry_key

          date_string = (datetime.datetime(1601, 1, 1) + datetime.timedelta(
              microseconds=cache_entry.creation_time))

          # print('Creation time\t: {0!s}'.format(date_string))

          # print('')

          print('{0!s}\t{1:s}'.format(date_string, cache_entry.key))

          cache_address = cache_entry.next
          cache_address_chain_length += 1

    for data_block_file in iter(data_block_files.values()):
      data_block_file.Close()

    index_file.Close()

    if not have_all_data_block_files:
      raise errors.ParseError('Missing data block files.')

  def ParseFile(self, path):
    """Parses a Chrome Cache file.

    Args:
      path (str): path of the file.

    Raises:
      ParseError: if the file cannot be read.
    """
    with open(path, 'rb') as file_object:
      signature_data = file_object.read(self._UINT32LE_SIZE)

      try:
        signature = self._UINT32LE.MapByteStream(signature_data)
      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError(
            'Unable to signature with error: {0!s}'.format(exception))

      if signature not in (DataBlockFile.SIGNATURE, IndexFile.SIGNATURE):
        raise errors.ParseError(
            'Unsupported signature: 0x{0:08x}'.format(signature))

      if signature == DataBlockFile.SIGNATURE:
        chrome_cache_file = DataBlockFile(
            debug=self._debug, output_writer=self._output_writer)

      elif signature == IndexFile.SIGNATURE:
        chrome_cache_file = IndexFile(
            debug=self._debug, output_writer=self._output_writer)

      chrome_cache_file.ReadFileObject(file_object)
      chrome_cache_file.Close()
