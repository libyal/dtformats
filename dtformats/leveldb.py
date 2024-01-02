# -*- coding: utf-8 -*-
"""LevelDB database files."""

from dtformats import data_format
from dtformats import errors


def _ReadVariableSizeInteger(data):
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


class LevelDBDatabaseLogFile(data_format.BinaryDataFile):
  """LevelDB write ahead log (.log) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('leveldb.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'leveldb.debug.yaml')

  # TODO: add custom formatter to print record type.

  _RECORD_TYPES = {
      1: 'FULL',
      2: 'FIRST',
      3: 'MIDDLE',
      4: 'LAST'}

  _VALUE_TAGS = {
      1: 'kComparator',
      2: 'kLogNumber',
      3: 'kNextFileNumber',
      4: 'kLastSequence',
      5: 'kCompactPointer',
      6: 'kDeletedFile',
      7: 'kNewFile',
      9: 'kPrevLogNumber'}

  def __init__(self, debug=False, file_system_helper=None, output_writer=None):
    """Initializes a LevelDB write ahead log file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      file_system_helper (Optional[FileSystemHelper]): file system helper.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(LevelDBDatabaseLogFile, self).__init__(
        debug=debug, file_system_helper=file_system_helper,
        output_writer=output_writer)

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

    data_offset = 0

    while data_offset < data_size:
      value_tag, bytes_read = _ReadVariableSizeInteger(data[data_offset:])
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

        key, bytes_read = self._ReadRecordValueKey(data[data_offset:], 'Key')

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

        smallest_record_key, bytes_read = self._ReadRecordValueKey(
            data[data_offset:], 'Smallest record key')
        data_offset += bytes_read

        largest_record_key, bytes_read = self._ReadRecordValueKey(
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
    integer_value, bytes_read = _ReadVariableSizeInteger(data)

    if self._debug:
      value_string, _ = self._FormatIntegerAsDecimal(integer_value)
      self._DebugPrintValue(description, value_string)

    return integer_value, bytes_read

  def _ReadRecordValueKey(self, data, description):
    """Reads a key record value.

    Args:
      data (bytes): value data.
      description (str): description of the value.

    Returns:
      tuple[bytes, int]: key value and number of bytes read.

    Raises:
      ParseError: if the value cannot be read.
    """
    data_size, bytes_read = _ReadVariableSizeInteger(data)

    key_data = data[bytes_read:bytes_read + data_size]

    if self._debug:
      value_string, _ = self._FormatIntegerAsDecimal(data_size)
      self._DebugPrintValue(f'{description:s} key size', value_string)

      self._DebugPrintData(f'{description:s} key', key_data)

    return key_data, bytes_read + data_size

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
    data_size, bytes_read = _ReadVariableSizeInteger(data)

    string_data = data[bytes_read:bytes_read + data_size]

    string_value = string_data.decode('utf-8')

    if self._debug:
      value_string, _ = self._FormatIntegerAsDecimal(data_size)
      self._DebugPrintValue(f'{description:s} string size', value_string)

      self._DebugPrintValue(f'{description:s} string', string_value)

    return string_value, bytes_read + data_size

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


class LevelDBDatabaseTableFile(data_format.BinaryDataFile):
  """LevelDB database sorted tables (.ldb) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('leveldb.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'leveldb.debug.yaml')

  def __init__(self, debug=False, file_system_helper=None, output_writer=None):
    """Initializes a LevelDB database stored tables file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      file_system_helper (Optional[FileSystemHelper]): file system helper.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(LevelDBDatabaseTableFile, self).__init__(
        debug=debug, file_system_helper=file_system_helper,
        output_writer=output_writer)

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

  def _ReadKeyPrefix(self, data):
    """Reads a key prefix.

    Args:
      data (bytes): data.

    Returns:
      tuple[tuple[int, int, int], int]: key prefix and number of bytes read.
    """
    byte_value = data[0]
    bytes_read = 1

    database_identifier = 0
    object_store_identifier = 0
    index_identifier = 0

    bit_shift = 0
    for _ in range((byte_value >> 5) + 1):
      database_identifier |= data[bytes_read] << bit_shift
      bytes_read += 1
      bit_shift += 8

    bit_shift = 0
    for _ in range(((byte_value & 0x1f) >> 2) + 1):
      object_store_identifier |= data[bytes_read] << bit_shift
      bytes_read += 1
      bit_shift += 8

    bit_shift = 0
    for _ in range((byte_value & 0x03) + 1):
      index_identifier |= data[bytes_read] << bit_shift
      bytes_read += 1
      bit_shift += 8

    key_prefix = (
        database_identifier, object_store_identifier, index_identifier)

    return key_prefix, bytes_read

  def _ReadFileFooter(self, file_object):
    """Reads the file footer.

    Args:
      file_object (file): file-like object.

    Returns:
      leveldb_ldb_footer: file footer.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    data_type_map = self._GetDataTypeMap('leveldb_ldb_footer')
    file_offset = self._file_size - 48

    file_footer, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file footer')

    file_footer.metaindex_block_offset, data_offset = (
        _ReadVariableSizeInteger(file_footer.data))

    file_footer.metaindex_block_size, bytes_read = (
        _ReadVariableSizeInteger(file_footer.data[data_offset:]))
    data_offset += bytes_read

    file_footer.index_block_offset, bytes_read = (
        _ReadVariableSizeInteger(file_footer.data[data_offset:]))
    data_offset += bytes_read

    file_footer.index_block_size, bytes_read = (
        _ReadVariableSizeInteger(file_footer.data[data_offset:]))
    data_offset += bytes_read

    if self._debug:
      file_footer.padding = file_footer.data[data_offset:]

      debug_info = self._DEBUG_INFORMATION.get('leveldb_ldb_footer', None)
      self._DebugPrintStructureObject(file_footer, debug_info)

    return file_footer

  def _ReadIndexBlock(self, file_object, file_footer):
    """Reads an index block.

    Args:
      file_object (file): file-like object.
      file_footer (leveldb_ldb_footer): file footer.

    Raises:
      ParseError: if the index block cannot be read.
    """
    data = self._ReadData(
        file_object, file_footer.index_block_offset,
        file_footer.index_block_size, 'index block')

    if self._debug:
      self._DebugPrintData('Index block data', data)

    data_offset = 0

    unknown1, bytes_read = _ReadVariableSizeInteger(data[data_offset:])
    data_offset += bytes_read

    unknown2, bytes_read = _ReadVariableSizeInteger(data[data_offset:])
    data_offset += bytes_read

    unknown3, bytes_read = _ReadVariableSizeInteger(data[data_offset:])
    data_offset += bytes_read

    if self._debug:
      value_string, _ = self._FormatIntegerAsHexadecimal8(unknown1)
      self._DebugPrintValue('Unknown1', value_string)

      value_string, _ = self._FormatIntegerAsHexadecimal8(unknown2)
      self._DebugPrintValue('Unknown2', value_string)

      value_string, _ = self._FormatIntegerAsHexadecimal8(unknown3)
      self._DebugPrintValue('Unknown3', value_string)

  def _ReadMetaindexBlock(self, file_object, file_footer):
    """Reads a metaindex block.

    Args:
      file_object (file): file-like object.
      file_footer (leveldb_ldb_footer): file footer.

    Raises:
      ParseError: if the metaindex block cannot be read.
    """
    data = self._ReadData(
        file_object, file_footer.metaindex_block_offset,
        file_footer.metaindex_block_size, 'metaindex block')

    if self._debug:
      self._DebugPrintData('Metaindex block data', data)

    data_offset = 0
    data_size = len(data)

    while data_offset < data_size:
      key_prefix, bytes_read = self._ReadKeyPrefix(data[data_offset:])
      data_offset += bytes_read

      metadata_type = int(data[data_offset])
      data_offset += 1

      if self._debug:
        self._DebugPrintKeyPrefix(key_prefix)

        value_string, _ = self._FormatIntegerAsDecimal(metadata_type)
        self._DebugPrintValue('Metadata type', value_string)

      if key_prefix != (0, 0, 0):
        raise errors.ParseError(f'Unsupported key prefix: {key_prefix!s}')

      if metadata_type not in (0, 1, 2, 3, 4, 5, 201):
        raise errors.ParseError(f'Unsupported metadata type: {metadata_type:d}')

      if self._debug:
        self._DebugPrintData('Metadata', data[data_offset:])

      break

  def ReadFileObject(self, file_object):
    """Reads a LevelDB database stored tables file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_footer = self._ReadFileFooter(file_object)

    self._ReadMetaindexBlock(file_object, file_footer)
    self._ReadIndexBlock(file_object, file_footer)
