# -*- coding: utf-8 -*-
"""Chrome Cache files."""

import datetime
import logging

from dtfabric import errors as dtfabric_errors

from dtformats import data_format
from dtformats import errors
from dtformats import file_system


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

  if isinstance(key[0], str):
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
        self.filename = f'f_{file_selector:06x}'

      elif self.file_type in self._BLOCK_DATA_FILE_TYPES:
        file_selector = (cache_address & 0x00ff0000) >> 16
        self.filename = f'data_{file_selector:d}'

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
      return f'0x{self.value:08x} (uninitialized)'

    file_type_description = self._FILE_TYPE_DESCRIPTIONS.get(
        self.file_type, 'Unknown')

    if self.file_type == 0:
      return (
          f'0x{self.value:08x} (initialized: {self.is_initialized!s}, '
          f'file type: {file_type_description:s}, filename: {self.filename:s})')

    # TODO: print reserved bits.
    return (
        f'0x{self.value:08x} (initialized: {self.is_initialized!s}, '
        f'file type: {file_type_description:s}, filename: {self.filename:s}, '
        f'block number: {self.block_number:d}, block offset: '
        f'0x{self.block_offset:08x}, block size: {self.block_size:d})')


class CacheEntry(object):
  """Cache entry.

  Attributes:
    creation_time (int): creation time, in number of microseconds since
        since January 1, 1601, 00:00:00 UTC.
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
    format_version (str): format version.
    number_of_entries (int): number of entries.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('chrome_cache.yaml')

  # TODO: update empty, hints, updating and user.

  SIGNATURE = 0xc104cac3

  _DEBUG_INFO_FILE_HEADER = [
      ('signature', 'Signature', '_FormatIntegerAsHexadecimal8'),
      ('minor_version', 'Minor version', '_FormatIntegerAsDecimal'),
      ('major_version', 'Major version', '_FormatIntegerAsDecimal'),
      ('file_number', 'File number', '_FormatIntegerAsDecimal'),
      ('next_file_number', 'Next file number', '_FormatIntegerAsDecimal'),
      ('block_size', 'Block size', '_FormatIntegerAsDecimal'),
      ('number_of_entries', 'Number of entries', '_FormatIntegerAsDecimal'),
      ('maximum_number_of_entries', 'Maximum number of entries',
       '_FormatIntegerAsDecimal'),
      ('number_of_entries', 'Number of entries', '_FormatIntegerAsDecimal'),
      ('empty', 'Empty', '_FormatArrayOfIntegersAsDecimals'),
      ('hints', 'Hints', '_FormatArrayOfIntegersAsDecimals'),
      ('updating', 'Updating', '_FormatIntegerAsHexadecimal8'),
      ('user', 'User', '_FormatArrayOfIntegersAsDecimals')]

  _DEBUG_INFO_CACHE_ENTRY = [
      ('hash', 'Hash', '_FormatIntegerAsHexadecimal8'),
      ('next_address', 'Next address', '_FormatIntegerAsCacheAddress'),
      ('rankings_node_address', 'Rankings node address',
       '_FormatIntegerAsCacheAddress'),
      ('reuse_count', 'Reuse count', '_FormatIntegerAsDecimal'),
      ('refetch_count', 'Refetch count', '_FormatIntegerAsDecimal'),
      ('state', 'State', '_FormatIntegerAsHexadecimal8'),
      ('creation_time', 'Creation time', '_FormatIntegerAsTimestamp')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Chrome Cache data block file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(DataBlockFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self.block_size = None
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
            block_range_size = block_range_end - block_range_start
            self._DebugPrintValue('Block range', (
                f'{block_range_start:d} - {block_range_end:d} '
                f'({block_range_size:d})'))

        value_32bit >>= 1
        block_number += 1

  def _DebugPrintCacheEntryDataStreamSizes(self, array_of_integers):
    """Prints cache entry data stream sizes debug information.

    Args:
      array_of_integers (list[int]): array of integers.
    """
    for index, value in enumerate(array_of_integers):
      self._DebugPrintValue(f'Data stream size: {index:d}', f'{value:d}')

  def _DebugPrintCacheEntryDataStreamAddresses(self, array_of_integers):
    """Prints cache entry data stream addresses debug information.

    Args:
      array_of_integers (list[int]): array of integers.
    """
    for index, value in enumerate(array_of_integers):
      cache_address = CacheAddress(value)
      value_string = cache_address.GetDebugString()
      self._DebugPrintValue(f'Data stream address: {index:d}', value_string)

  def _DebugPrintCacheEntry(self, cache_entry):
    """Prints cache entry debug information.

    Args:
      cache_entry (chrome_cache_entry): cache entry.
    """
    self._DebugPrintStructureObject(cache_entry, self._DEBUG_INFO_CACHE_ENTRY)

    self._DebugPrintCacheEntryDataStreamSizes(cache_entry.data_stream_sizes)

    self._DebugPrintCacheEntryDataStreamAddresses(
        cache_entry.data_stream_addresses)

    self._DebugPrintValue('Flags', f'0x{cache_entry.flags:08x}')

    self._DebugPrintValue('Self hash', f'0x{cache_entry.self_hash:08x}')

    self._DebugPrintValue('Key', cache_entry.key)

    self._DebugPrintText('\n')

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (chrome_cache_data_block_file_header): file header.
    """
    self._DebugPrintStructureObject(file_header, self._DEBUG_INFO_FILE_HEADER)

    self._DebugPrintAllocationBitmap(file_header.allocation_bitmap)

    self._DebugPrintText('\n')

  def _FormatIntegerAsCacheAddress(self, integer):
    """Formats an integer as a cache address.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a cache address.
    """
    cache_address = CacheAddress(integer)
    return cache_address.GetDebugString()

  def _FormatIntegerAsTimestamp(self, integer):
    """Formats an integer as a Chrome timestamp.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a Chrome timestamp.
    """
    date_string = (datetime.datetime(1601, 1, 1) +
                   datetime.timedelta(microseconds=integer))
    return f'{date_string!s} (0x{integer:08x})'

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('chrome_cache_data_block_file_header')

    file_header, _ = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'data block file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

    self.format_version = (
        f'{file_header.major_version:d}.{file_header.minor_version:d}')

    if self.format_version not in ('2.0', '2.1'):
      raise errors.ParseError(
          f'Unsupported data block file version: {self.format_version:s}')

    self.block_size = file_header.block_size
    self.number_of_entries = file_header.number_of_entries

  def ReadCacheEntry(self, block_offset):
    """Reads a cache entry.

    Args:
      block_offset (int): offset of the block that contains the cache entry.

    Returns:
      CacheEntry: a cache entry.

    Raises:
      ParseError: if the cache entry cannot be read.
    """
    data_type_map = self._GetDataTypeMap('chrome_cache_entry')

    cache_entry, _ = self._ReadStructureFromFileObject(
        self._file_object, block_offset, data_type_map,
        'data block cache entry')

    byte_string = bytes(cache_entry.key)
    cache_entry_key, _, _ = byte_string.partition(b'\x00')

    try:
      cache_entry_key = cache_entry_key.decode('ascii')
    except UnicodeDecodeError:
      logging.warning((
          f'Unable to decode cache entry key at block offset: '
          f'0x{block_offset:08x}. Characters that cannot be decoded will be '
          f'replaced with "?" or "\\ufffd".'))
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


class IndexFile(data_format.BinaryDataFile):
  """Chrome Cache index file.

  Attributes:
    creation_time (int): date and time the file was created.
    format_version (str): format version.
    index_table (dict[str, object]): index table.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('chrome_cache.yaml')

  _DEBUG_INFO_FILE_HEADER = [
      ('signature', 'Signature', '_FormatIntegerAsHexadecimal8'),
      ('minor_version', 'Minor version', '_FormatIntegerAsDecimal'),
      ('major_version', 'Major version', '_FormatIntegerAsDecimal'),
      ('number_of_entries', 'Number of entries', '_FormatIntegerAsDecimal'),
      ('stored_data_size', 'Stored data size', '_FormatIntegerAsDecimal'),
      ('last_created_file_number', 'Last created file number',
       '_FormatIntegerAsDataStreamFilename'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal8'),
      ('table_size', 'Table size', '_FormatIntegerAsDecimal'),
      ('unknown3', 'Unknown3', '_FormatIntegerAsHexadecimal8'),
      ('unknown4', 'Unknown4', '_FormatIntegerAsHexadecimal8'),
      ('creation_time', 'Creation time', '_FormatIntegerAsTimestamp')]

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

  def _DebugPrintLRUData(self, lru_data):
    """Prints LRU data debug information.

    Args:
      lru_data (chrome_cache_index_file_lru_data): LRU data.
    """
    self._DebugPrintValue('Filled flag', f'0x{lru_data.filled_flag:08x}')

    for value in lru_data.sizes:
      self._DebugPrintValue('Size', f'{value:d}')

    for index, value in enumerate(lru_data.head_addresses):
      cache_address = CacheAddress(value)
      value_string = cache_address.GetDebugString()
      self._DebugPrintValue(f'Head address: {index:d}', value_string)

    for index, value in enumerate(lru_data.tail_addresses):
      cache_address = CacheAddress(value)
      value_string = cache_address.GetDebugString()
      self._DebugPrintValue(f'Tail address: {index:d}', value_string)

    cache_address = CacheAddress(lru_data.transaction_address)
    value_string = cache_address.GetDebugString()
    self._DebugPrintValue('Transaction address', value_string)

    self._DebugPrintValue('Operation', f'0x{lru_data.operation:08x}')

    self._DebugPrintValue('Operation list', f'0x{lru_data.operation_list:08x}')

    self._DebugPrintText('\n')

  def _FormatIntegerAsDataStreamFilename(self, integer):
    """Formats an integer as a data stream filename.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a data stream filename.
    """
    return f'{integer:d} (f_{integer:06x})'

  def _FormatIntegerAsTimestamp(self, integer):
    """Formats an integer as a Chrome timestamp.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a Chrome timestamp.
    """
    date_string = (datetime.datetime(1601, 1, 1) +
                   datetime.timedelta(microseconds=integer))
    return f'{date_string!s} (0x{integer:08x})'

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('chrome_cache_index_file_header')

    file_header, _ = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'index file header')

    if self._debug:
      self._DebugPrintStructureObject(file_header, self._DEBUG_INFO_FILE_HEADER)

    self.format_version = (
        f'{file_header.major_version:d}.{file_header.minor_version:d}')

    if self.format_version not in ('2.0', '2.1'):
      raise errors.ParseError(
          f'Unsupported index file version: {self.format_version:s}')

    self.creation_time = file_header.creation_time

  def _ReadLRUData(self, file_object):
    """Reads the LRU data.

    Args:
      file_object (file): file-like object.
    """
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('chrome_cache_index_file_lru_data')

    lru_data, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'index file LRU')

    if self._debug:
      self._DebugPrintLRUData(lru_data)

  def _ReadIndexTable(self, file_object):
    """Reads the index table.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the index table cannot be read.
    """
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('uint32le')

    cache_address_index = 0
    cache_address_data = file_object.read(4)

    while len(cache_address_data) == 4:
      try:
        value = self._ReadStructureFromByteStream(
            cache_address_data, file_offset, data_type_map, 'cache address')
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            f'Unable to parse index table entry: {cache_address_index:d} with '
            f'error: {exception!s}'))

      if value:
        cache_address = CacheAddress(value)

        if self._debug:
          value_string = cache_address.GetDebugString()
          self._DebugPrintValue(
              f'Cache address: {cache_address_index:d}', value_string)

        self.index_table[cache_address_index] = cache_address

      file_offset = file_object.tell()
      cache_address_data = file_object.read(4)

      cache_address_index += 1

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

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('chrome_cache.yaml')

  _UINT32LE = _FABRIC.CreateDataTypeMap('uint32le')

  def __init__(self, debug=False, file_system_helper=None, output_writer=None):
    """Initializes a Chrome Cache parser.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      file_system_helper (Optional[FileSystemHelper]): file system helper.
      output_writer (Optional[OutputWriter]): output writer.
    """
    if not file_system_helper:
      file_system_helper = file_system.NativeFileSystemHelper()

    super(ChromeCacheParser, self).__init__()
    self._debug = debug
    self._file_system_helper = file_system_helper
    self._output_writer = output_writer

  def ParseDirectory(self, path):
    """Parses a Chrome Cache directory.

    Args:
      path (str): path of the directory.

    Raises:
      ParseError: if the directory cannot be read.
    """
    index_file_path = self._file_system_helper.JoinPath(path, 'index')
    if not self._file_system_helper.CheckFileExistsByPath(index_file_path):
      raise errors.ParseError(
          f'Missing index file: {index_file_path:s}')

    index_file = IndexFile(debug=self._debug, output_writer=self._output_writer)
    index_file.Open(index_file_path)

    data_block_files = {}
    have_all_data_block_files = True
    for cache_address in index_file.index_table.values():
      if cache_address.filename not in data_block_files:
        data_block_file_path = self._file_system_helper.JoinPath(
            path, cache_address.filename)

        if not self._file_system_helper.CheckFileExistsByPath(
            data_block_file_path):
          logging.error(f'Missing data block file: {data_block_file_path:s}')
          have_all_data_block_files = False

        else:
          data_block_file = DataBlockFile(
              debug=self._debug, output_writer=self._output_writer)
          data_block_file.Open(data_block_file_path)

          data_block_files[cache_address.filename] = data_block_file

    if have_all_data_block_files:
      # TODO: read the cache entries from the data block files
      for cache_address in index_file.index_table.values():
        cache_address_chain_length = 0
        while cache_address.value != 0x00000000:
          if cache_address_chain_length >= 64:
            logging.error(
                'Maximum allowed cache address chain length reached.')
            break

          data_file = data_block_files.get(cache_address.filename, None)
          if not data_file:
            logging.warning(
                f'Cache address: 0x{cache_address.value:08x} missing filename.')
            break

          # cache_address_string = cache_address.GetDebugString()
          # print(f'Cache address\t: {cache_address_string:s}')
          cache_entry = data_file.ReadCacheEntry(cache_address.block_offset)

          try:
            cache_entry_key = cache_entry.key.decode('ascii')
          except UnicodeDecodeError:
            logging.warning((
                f'Unable to decode cache entry key at cache address: '
                f'0x{cache_address.value:08x}. Characters that cannot be '
                f'decoded will be replaced with "?" or "\\ufffd".'))
            cache_entry_key = cache_entry.key.decode(
                'ascii', errors='replace')

          # TODO: print(f'Url\t\t: {cache_entry_key:s}')
          _ = cache_entry_key

          date_string = (datetime.datetime(1601, 1, 1) + datetime.timedelta(
              microseconds=cache_entry.creation_time))

          # print(f'Creation time\t: {date_string!s}')

          # print('')

          print(f'{date_string!s}\t{cache_entry.key:s}')

          cache_address = cache_entry.next
          cache_address_chain_length += 1

    for data_block_file in data_block_files.values():
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
      signature_data = file_object.read(4)

      try:
        signature = self._UINT32LE.MapByteStream(signature_data)
      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError(
            f'Unable to signature with error: {exception!s}')

      if signature not in (DataBlockFile.SIGNATURE, IndexFile.SIGNATURE):
        raise errors.ParseError(
            f'Unsupported signature: 0x{signature:08x}')

      if signature == DataBlockFile.SIGNATURE:
        chrome_cache_file = DataBlockFile(
            debug=self._debug, output_writer=self._output_writer)

      elif signature == IndexFile.SIGNATURE:
        chrome_cache_file = IndexFile(
            debug=self._debug, output_writer=self._output_writer)

      chrome_cache_file.ReadFileObject(file_object)
