# -*- coding: utf-8 -*-
"""LevelDB database files."""

import abc

import snappy
import zstd

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import data_maps as dtfabric_data_maps

from dtformats import data_format
from dtformats import errors


class LevelDBDatabaseBlockHandle(object):
  """LevelDB block handle.

  Attributes:
    offset (int): block offset.
    size (int): block size.
  """

  def __init__(self, offset, size):
    """Initializes a LevelDB block handle.

    Args:
      offset (int): block offset.
      size (int): block size.
    """
    super(LevelDBDatabaseBlockHandle, self).__init__()
    self.offset = offset
    self.size = size


class LevelDBDatabaseTableEntry(object):
  """LevelDB table entry.

  Attributes:
    key (bytes): key.
    value (bytes): value.
  """

  def __init__(self, key, value):
    """Initializes a LevelDB table entry.

    Args:
      key (bytes): key.
      value (bytes): value.
    """
    super(LevelDBDatabaseTableEntry, self).__init__()
    self.key = key
    self.value = value


class LevelDBDatabaseFile(data_format.BinaryDataFile):
  """LevelDB file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('leveldb.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'leveldb.debug.yaml')

  # TODO: add custom formatter to print log record type.
  # TODO: add custom formatter to print compression type.

  _LOG_RECORD_TYPES = {
      1: 'FULL',
      2: 'FIRST',
      3: 'MIDDLE',
      4: 'LAST'}

  _VALUE_TYPES = {
      0: 'kTypeDeletion',
      1: 'kTypeValue'}

  def __init__(self, debug=False, file_system_helper=None, output_writer=None):
    """Initializes a LevelDB file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      file_system_helper (Optional[FileSystemHelper]): file system helper.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(LevelDBDatabaseFile, self).__init__(
        debug=debug, file_system_helper=file_system_helper,
        output_writer=output_writer)

  def _ReadVariableSizeInteger(self, data):
    """Reads a variable size integer.

    Args:
      data (bytes): data.

    Returns:
      tuple[int, int]: integer value and number of bytes read.
    """
    data_size = len(data)

    byte_value = data[0]
    bytes_read = 1
    bit_shift = 0

    integer_value = int(byte_value) & 0x7f

    while bytes_read < data_size and byte_value & 0x80:
      byte_value = data[bytes_read]
      bytes_read += 1
      bit_shift += 7

      integer_value |= (int(byte_value) & 0x7f) << bit_shift

      # TODO: check maximum size

    return integer_value, bytes_read

  @abc.abstractmethod
  def ReadFileObject(self, file_object):
    """Reads binary data from a file-like object.

    Args:
      file_object (file): file-like object.
    """


class LevelDBDatabaseLogFile(LevelDBDatabaseFile):
  """LevelDB write ahead log (.log) file."""

  def _ReadBlock(self, file_object, file_offset):
    """Reads a block.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the block relative to the start of the file.

    Returns:
      tuple[leveldb_log_block, int]: block and number of bytes read.

    Raises:
      ParseError: if the block cannot be read.
    """
    data_type_map = self._GetDataTypeMap('leveldb_log_block')

    block, bytes_read = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'block')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('leveldb_log_block', None)
      self._DebugPrintStructureObject(block, debug_info)

    # TODO: calculate and validate checksum

    return block, bytes_read

  def _ReadRecord(self, file_offset, data, data_size):
    """Reads a record.

    Args:
      file_offset (int): offset of the record relative to the start of the file.
      data (bytes): record data.
      data_size (int): record data size.

    Raises:
      ParseError: if the record cannot be read.
    """
    # pylint: disable=unused-variable

    if self._debug:
      value_string, _ = self._FormatIntegerAsDecimal(file_offset)
      self._DebugPrintValue('Offset', value_string)

    value_header, data_offset = self._ReadRecordValueHeader(file_offset, data)

    while data_offset < data_size:
      value_type = int(data[data_offset])
      data_offset += 1

      if self._debug:
        value_type_string = self._VALUE_TYPES.get(value_type, 'UNKNOWN')
        value_string, _ = self._FormatIntegerAsDecimal(value_type)
        self._DebugPrintValue(
            'Value type', f'{value_string:s} ({value_type_string:s})')

      if value_type not in (0, 1):
        raise errors.ParseError(f'Unsupported value type: {value_type:d}')

      key, bytes_read = self._ReadRecordValueSlice(data[data_offset:], 'Key')
      data_offset += bytes_read

      if value_type == 1:
        value, bytes_read = self._ReadRecordValueSlice(
            data[data_offset:], 'Value')
        data_offset += bytes_read

  def _ReadRecordValueHeader(self, file_offset, data):
    """Reads a value header.

    Args:
      file_offset (int): offset of the record relative to the start of the file.
      data (bytes): record data.

    Returns:
      tuple[leveldb_log_value_header, int]: value header and number of bytes
          read.

    Raises:
      ParseError: if the value header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('leveldb_log_value_header')

    value_header = self._ReadStructureFromByteStream(
        data, file_offset, data_type_map, 'Value header')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('leveldb_log_value_header', None)
      self._DebugPrintStructureObject(value_header, debug_info)

    return value_header, 12

  def _ReadRecordValueSlice(self, data, description):
    """Reads a slice record value.

    Args:
      data (bytes): value data.
      description (str): description of the value.

    Returns:
      tuple[bytes, int]: slice value and number of bytes read.

    Raises:
      ParseError: if the value cannot be read.
    """
    data_size, bytes_read = self._ReadVariableSizeInteger(data)

    value_data = data[bytes_read:bytes_read + data_size]

    if self._debug:
      value_string, _ = self._FormatIntegerAsDecimal(data_size)
      self._DebugPrintValue(f'{description:s} size', value_string)

      self._DebugPrintData(description, value_data)

    return value_data, bytes_read + data_size

  def ReadFileObject(self, file_object):
    """Reads a LevelDB write ahead log file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_offset = 0
    page_size = 32 * 1024
    record_data = b''
    record_offset = 0

    while file_offset < self._file_size:
      log_block, bytes_read = self._ReadBlock(file_object, file_offset)

      if log_block.record_type in (1, 2):
        record_data = log_block.record_data
        record_offset = file_offset

      elif log_block.record_type in (3, 4):
        record_data = b''.join([record_data, log_block.record_data])

      if log_block.record_type in (1, 4):
        self._ReadRecord(record_offset, record_data, len(record_data))

      file_offset += bytes_read
      page_size -= bytes_read

      if page_size <= 6:
        file_offset += page_size
        page_size = 32 * 1024


class LevelDBDatabaseDescriptorFile(LevelDBDatabaseLogFile):
  """LevelDB descriptor file."""

  _VALUE_TAGS = {
      1: 'kComparator',
      2: 'kLogNumber',
      3: 'kNextFileNumber',
      4: 'kLastSequence',
      5: 'kCompactPointer',
      6: 'kDeletedFile',
      7: 'kNewFile',
      9: 'kPrevLogNumber'}

  def _ReadRecord(self, file_offset, data, data_size):
    """Reads a record.

    Args:
      file_offset (int): offset of the record relative to the start of the file.
      data (bytes): record data.
      data_size (int): record data size.

    Raises:
      ParseError: if the record cannot be read.
    """
    # pylint: disable=unused-variable

    if self._debug:
      value_string, _ = self._FormatIntegerAsDecimal(file_offset)
      self._DebugPrintValue('Offset', value_string)

    data_offset = 0

    while data_offset < data_size:
      value_tag, bytes_read = self._ReadVariableSizeInteger(data[data_offset:])
      data_offset += bytes_read

      if self._debug:
        value_tag_string = self._VALUE_TAGS.get(value_tag, 'UNKNOWN')
        value_string, _ = self._FormatIntegerAsDecimal(value_tag)
        self._DebugPrintValue(
            'Value tag', f'{value_string:s} ({value_tag_string:s})')

      if value_tag not in (1, 2, 3, 4, 5, 6, 7, 9):
        raise errors.ParseError(f'Unsupported value tag: {value_tag:d}')

      if value_tag == 1:
        comparator_name, bytes_read = self._ReadRecordValueString(
            data[data_offset:], 'Name')

      elif value_tag == 2:
        log_number, bytes_read = self._ReadRecordValueInteger(
            data[data_offset:], 'Log number')

      elif value_tag == 3:
        next_file_number, bytes_read = self._ReadRecordValueInteger(
            data[data_offset:], 'Next file number')

      elif value_tag == 4:
        last_sequence_number, bytes_read = self._ReadRecordValueInteger(
            data[data_offset:], 'Last sequence number')

      elif value_tag == 5:
        level, bytes_read = self._ReadRecordValueInteger(
            data[data_offset:], 'Level')
        data_offset += bytes_read

        key, bytes_read = self._ReadRecordValueSlice(data[data_offset:], 'Key')

      elif value_tag == 6:
        level, bytes_read = self._ReadRecordValueInteger(
            data[data_offset:], 'Level')
        data_offset += bytes_read

        number_of_files, bytes_read = self._ReadRecordValueInteger(
            data[data_offset:], 'Number of files')

      elif value_tag == 7:
        level, bytes_read = self._ReadRecordValueInteger(
            data[data_offset:], 'Level')
        data_offset += bytes_read

        number_of_files, bytes_read = self._ReadRecordValueInteger(
            data[data_offset:], 'Number of files')
        data_offset += bytes_read

        number_of_files, bytes_read = self._ReadRecordValueInteger(
            data[data_offset:], 'File size')
        data_offset += bytes_read

        smallest_record_key, bytes_read = self._ReadRecordValueSlice(
            data[data_offset:], 'Smallest record key')
        data_offset += bytes_read

        largest_record_key, bytes_read = self._ReadRecordValueSlice(
            data[data_offset:], 'Largest record key')

      elif value_tag == 9:
        previous_log_number, bytes_read = self._ReadRecordValueInteger(
            data[data_offset:], 'Previous log number')

      data_offset += bytes_read

  def _ReadRecordValueInteger(self, data, description):
    """Reads an integer record value.

    Args:
      data (bytes): value data.
      description (str): description of the value.

    Returns:
      tuple[int, int]: integer value and number of bytes read.

    Raises:
      ParseError: if the value cannot be read.
    """
    integer_value, bytes_read = self._ReadVariableSizeInteger(data)

    if self._debug:
      value_string, _ = self._FormatIntegerAsDecimal(integer_value)
      self._DebugPrintValue(description, value_string)

    return integer_value, bytes_read

  def _ReadRecordValueString(self, data, description):
    """Reads a string record value.

    Args:
      data (bytes): value data.
      description (str): description of the value.

    Returns:
      tuple[str, int]: string value and number of bytes read.

    Raises:
      ParseError: if the value cannot be read.
    """
    data_size, bytes_read = self._ReadVariableSizeInteger(data)

    string_data = data[bytes_read:bytes_read + data_size]

    string_value = string_data.decode('utf-8')

    if self._debug:
      value_string, _ = self._FormatIntegerAsDecimal(data_size)
      self._DebugPrintValue(f'{description:s} string size', value_string)

      self._DebugPrintValue(f'{description:s} string', string_value)

    return string_value, bytes_read + data_size


class LevelDBDatabaseTableFile(LevelDBDatabaseFile):
  """LevelDB database sorted tables (.ldb) file."""

  def _DebugPrintKeyPrefix(self, key_prefix):
    """Prints key prefix information.

    Args:
      key_prefix (tuple[int, int, int]): key prefix.
    """
    value_string, _ = self._FormatIntegerAsDecimal(key_prefix[0])
    self._DebugPrintValue('Database identifier', value_string)

    value_string, _ = self._FormatIntegerAsDecimal(key_prefix[1])
    self._DebugPrintValue('Object store identifier', value_string)

    value_string, _ = self._FormatIntegerAsDecimal(key_prefix[2])
    self._DebugPrintValue('Index identifier', value_string)

  def _ReadBlock(self, file_object, file_offset, block_data_size):
    """Reads a block.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the block relative to the start of the file.
      block_data_size (int): size of the block data.

    Returns:
      bytes: block data.

    Raises:
      ParseError: if the block cannot be read.
    """
    block_data = self._ReadData(
        file_object, file_offset, block_data_size, 'block data')

    if self._debug:
      self._DebugPrintData('Block data', block_data)

    data_type_map = self._GetDataTypeMap('leveldb_table_block_trailer')
    file_offset += block_data_size

    block_trailer, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'block trailer')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get(
          'leveldb_table_block_trailer', None)
      self._DebugPrintStructureObject(block_trailer, debug_info)

    # TODO: calculate and validate checksum

    if block_trailer.compression_type not in (0, 1, 2):
      raise errors.ParseError(
          f'Unsupported compression type: {block_trailer.compression_type!s}')

    if block_trailer.compression_type == 1:
      block_data = snappy.decompress(block_data)

    elif block_trailer.compression_type == 2:
      block_data = zstd.decompress(block_data)

    return block_data

  def _ReadBlockHandle(self, data, description):
    """Reads a  block handle.

    Args:
      data (bytes): value data.
      description (str): description of the block handle.

    Returns:
      tuple[LevelDBDatabaseBlockHandle, int]: block handle and number of bytes
          read.

    Raises:
      ParseError: if the block handle cannot be read.
    """
    block_offset, data_offset = self._ReadVariableSizeInteger(data)

    block_size, bytes_read = self._ReadVariableSizeInteger(data[data_offset:])
    data_offset += bytes_read

    if self._debug:
      value_string, _ = self._FormatIntegerAsHexadecimal8(block_offset)
      self._DebugPrintValue(f'{description:s} block offset', value_string)

      value_string, _ = self._FormatIntegerAsDecimal(block_size)
      self._DebugPrintValue(f'{description:s} block size', value_string)

    block_handle = LevelDBDatabaseBlockHandle(block_offset, block_size)
    return block_handle, data_offset

  def _ReadDataBlock(self, file_object, file_offset, block_data_size):
    """Reads a data block.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the block containing the data relative to
         the start of the file.
      block_data_size (int): size of the block data.

    Raises:
      ParseError: if the index cannot be read.
    """
    # pylint: disable=unused-variable

    table_entries = list(self._ReadTable(
        file_object, file_offset, block_data_size, 'Data'))

  def _ReadFileFooter(self, file_object):
    """Reads the file footer.

    Args:
      file_object (file): file-like object.

    Returns:
      leveldb_table_footer: file footer.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    data_type_map = self._GetDataTypeMap('leveldb_table_footer')
    file_offset = self._file_size - 48

    file_footer, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file footer')

    block_handle, data_offset = self._ReadBlockHandle(
        file_footer.data, 'Metaindex')

    file_footer.metaindex_block_offset = block_handle.offset
    file_footer.metaindex_block_size = block_handle.size

    block_handle, bytes_read = self._ReadBlockHandle(
        file_footer.data[data_offset:], 'Index')
    data_offset += bytes_read

    file_footer.index_block_offset = block_handle.offset
    file_footer.index_block_size = block_handle.size

    if self._debug:
      file_footer.padding = file_footer.data[data_offset:]

      debug_info = self._DEBUG_INFORMATION.get('leveldb_table_footer', None)
      self._DebugPrintStructureObject(file_footer, debug_info)

    return file_footer

  def _ReadIndexBlock(self, file_object, file_offset, block_data_size):
    """Reads the index block.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the block containing the index block
         relative to the start of the file.
      block_data_size (int): size of the block data.

    Raises:
      ParseError: if the index cannot be read.
    """
    table_entries = list(self._ReadTable(
        file_object, file_offset, block_data_size, 'Index'))

    for table_entry in table_entries:
      block_handle, _ = self._ReadBlockHandle(table_entry.value, 'Data')

      self._ReadDataBlock(file_object, block_handle.offset, block_handle.size)

  def _ReadMetaindexBlock(self, file_object, file_footer):
    """Reads a metaindex block.

    Args:
      file_object (file): file-like object.
      file_footer (leveldb_table_footer): file footer.

    Raises:
      ParseError: if the metaindex block cannot be read.
    """
    data = self._ReadData(
        file_object, file_footer.metaindex_block_offset,
        file_footer.metaindex_block_size, 'metaindex block')

    if self._debug:
      self._DebugPrintData('Metaindex block data', data)

  def _ReadTable(self, file_object, file_offset, block_data_size, description):
    """Reads a table.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the block containing the tabel relative to
         the start of the file.
      block_data_size (int): size of the block data.
      description (str): description of the table.

    Yields:
      LevelDBDatabaseTableEntry: table entry.

    Raises:
      ParseError: if the table cannot be read.
    """
    table_data = self._ReadBlock(file_object, file_offset, block_data_size)
    table_data_size = len(table_data)

    if self._debug:
      self._DebugPrintData(f'{description:s} table data', table_data)

    data_type_map = self._GetDataTypeMap('uint32le')
    table_data_end_offset = table_data_size - 4

    number_of_restart_values = self._ReadStructureFromByteStream(
         table_data[-4:], table_data_end_offset, data_type_map,
         'number of restart values')

    if self._debug:
      value_string, _ = self._FormatIntegerAsDecimal(number_of_restart_values)
      self._DebugPrintValue('Number of restart values', value_string)

    data_type_map = self._GetDataTypeMap('array_of_uint32le')
    table_data_end_offset -= 4 * number_of_restart_values

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'number_of_elements': number_of_restart_values})

    try:
      restart_values = data_type_map.MapByteStream(
          table_data[table_data_end_offset:], context=context)

    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          f'Unable to parse array of 32-bit restart values with error: '
          f'{exception!s}'))

    if self._debug:
      value_string, _ = self._FormatArrayOfIntegersAsDecimals(restart_values)
      self._DebugPrintValue('Restart values', value_string)

    data_offset = 0
    entry_index = 0
    shared_key_data = b''

    while data_offset < table_data_end_offset:
      entry_offset = data_offset

      if self._debug:
        value_string, _ = self._FormatIntegerAsDecimal(entry_offset)
        self._DebugPrintValue('Offset', value_string)

      shared_key_data_size, bytes_read = self._ReadVariableSizeInteger(
          table_data[data_offset:])
      data_offset += bytes_read

      non_shared_key_data_size, bytes_read = self._ReadVariableSizeInteger(
          table_data[data_offset:])
      data_offset += bytes_read

      value_data_size, bytes_read = self._ReadVariableSizeInteger(
          table_data[data_offset:])
      data_offset += bytes_read

      if self._debug:
        value_string, _ = self._FormatIntegerAsDecimal(shared_key_data_size)
        self._DebugPrintValue(
            f'Entry: {entry_index:d} shared key data size', value_string)

        value_string, _ = self._FormatIntegerAsDecimal(non_shared_key_data_size)
        self._DebugPrintValue(
            f'Entry: {entry_index:d} non-shared key data size', value_string)

        value_string, _ = self._FormatIntegerAsDecimal(value_data_size)
        self._DebugPrintValue(
            f'Entry: {entry_index:d} value data size', value_string)

      key_data_size = non_shared_key_data_size

      key_data_end_offset = data_offset + key_data_size
      key_data = table_data[data_offset:key_data_end_offset]

      if self._debug:
        self._DebugPrintData(f'Entry: {entry_index:d} key data', key_data)

      if shared_key_data_size > 0:
        key_data = b''.join([shared_key_data[:shared_key_data_size], key_data])
        key_data_size += shared_key_data_size

        if self._debug:
          self._DebugPrintData(f'Entry: {entry_index:d} key data', key_data)

      shared_key_data = key_data

      if key_data_size < 8:
        raise errors.ParseError(f'Unsupported key data size: {key_data_size:d}')

      data_type_map = self._GetDataTypeMap('uint64le')

      internal_key_suffix = self._ReadStructureFromByteStream(
           key_data[-8:], key_data_end_offset - 8, data_type_map,
           'internal key suffix')

      if self._debug:
        self._DebugPrintValue('Key', key_data[:-8])

        value_type = internal_key_suffix & 0xff
        value_type_string = self._VALUE_TYPES.get(value_type, 'UNKNOWN')
        value_string, _ = self._FormatIntegerAsDecimal(value_type)
        self._DebugPrintValue(
            'Value type', f'{value_string:s} ({value_type_string:s})')

        value_string, _ = self._FormatIntegerAsDecimal(internal_key_suffix >> 8)
        self._DebugPrintValue('Sequence number', value_string)

      data_offset = key_data_end_offset

      value_data_end_offset = data_offset + value_data_size
      value_data = table_data[data_offset:value_data_end_offset]

      if self._debug:
        self._DebugPrintData(f'Entry: {entry_index:d} value data', value_data)

      data_offset = value_data_end_offset

      yield LevelDBDatabaseTableEntry(key_data, value_data)

      entry_index += 1

  def ReadFileObject(self, file_object):
    """Reads a LevelDB database stored tables file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_footer = self._ReadFileFooter(file_object)

    self._ReadMetaindexBlock(file_object, file_footer)
    self._ReadIndexBlock(
        file_object, file_footer.index_block_offset,
        file_footer.index_block_size)
