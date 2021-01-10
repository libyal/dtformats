# -*- coding: utf-8 -*-
"""Systemd journal files."""

from dtformats import data_format
from dtformats import errors


class SystemdJournalFile(data_format.BinaryDataFile):
  """Systemd journal file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('systemd.yaml')

  _OBJECT_COMPRESSED_XZ = 1
  _OBJECT_COMPRESSED_LZ4 = 2

  _OBJECT_FLAGS = {
      1: 'OBJECT_COMPRESSED_XZ',
      2: 'OBJECT_COMPRESSED_LZ4'}

  _OBJECT_TYPE_UNUSED = 0
  _OBJECT_TYPE_DATA = 1
  _OBJECT_TYPE_FIELD = 2
  _OBJECT_TYPE_ENTRY = 3
  _OBJECT_TYPE_DATA_HASH_TABLE = 4
  _OBJECT_TYPE_FIELD_HASH_TABLE = 5
  _OBJECT_TYPE_ENTRY_ARRAY = 6
  _OBJECT_TYPE_TAG = 7

  _OBJECT_TYPES = {
      0: 'OBJECT_UNUSED',
      1: 'OBJECT_DATA',
      2: 'OBJECT_FIELD',
      3: 'OBJECT_ENTRY',
      4: 'OBJECT_DATA_HASH_TABLE',
      5: 'OBJECT_FIELD_HASH_TABLE',
      6: 'OBJECT_ENTRY_ARRAY',
      7: 'OBJECT_TAG'}

  _SUPPORTED_FILE_HEADER_SIZES = frozenset([208, 224, 240])

  _SUPPORTED_OBJECT_TYPES = frozenset([
      _OBJECT_TYPE_UNUSED,
      _OBJECT_TYPE_DATA,
      _OBJECT_TYPE_FIELD,
      _OBJECT_TYPE_ENTRY,
      _OBJECT_TYPE_DATA_HASH_TABLE,
      _OBJECT_TYPE_FIELD_HASH_TABLE,
      _OBJECT_TYPE_ENTRY_ARRAY,
      _OBJECT_TYPE_TAG])

  _DEBUG_INFO_DATA_OBJECT_VALUES = [
      ('hash', 'Hash', '_FormatIntegerAsHexadecimal8'),
      ('next_hash_offset', 'Next hash offset', '_FormatIntegerAsHexadecimal8'),
      ('next_field_offset', 'Next field offset',
       '_FormatIntegerAsHexadecimal8'),
      ('entry_offset', 'Entry offset', '_FormatIntegerAsHexadecimal8'),
      ('entry_array_offset', 'Entry array offset',
       '_FormatIntegerAsHexadecimal8'),
      ('number_of_entries', 'Number of entries', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_ENTRY_ARRAY_OBJECT_VALUES = [
      ('next_entry_array_offset', 'Next entry array offset',
       '_FormatIntegerAsHexadecimal8'),
      ('entry_object_offsets', 'Entry object offsets',
       '_FormatEntryObjectOffsets')]

  _DEBUG_INFO_ENTRY_OBJECT_VALUES = [
      ('sequence_number', 'Sequence number', '_FormatIntegerAsDecimal'),
      ('real_time', 'Real time', '_FormatIntegerAsPosixTimeInMicroseconds'),
      ('monotonic', 'Monotonic', '_FormatIntegerAsHexadecimal8'),
      ('boot_identifier', 'Boot identifier', '_FormatDataInHexadecimal'),
      ('xor_hash', 'XOR hash', '_FormatIntegerAsHexadecimal8'),
      ('entry_items', 'Entry items', '_FormatEntryItems')]

  _DEBUG_INFO_FILE_HEADER = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('compatible_flags', 'Compatible flags', '_FormatIntegerAsHexadecimal8'),
      ('incompatible_flags', 'Incompatible flags',
       '_FormatIntegerAsHexadecimal8'),
      ('state', 'State', '_FormatIntegerAsHexadecimal2'),
      ('reserved1', 'Reserved', '_FormatDataInHexadecimal'),
      ('file_identifier', 'File identifier', '_FormatDataInHexadecimal'),
      ('machine_identifier', 'Machine identifier', '_FormatDataInHexadecimal'),
      ('boot_identifier', 'Boot identifier', '_FormatDataInHexadecimal'),
      ('sequence_number_identifier', 'Sequence number identifier',
       '_FormatDataInHexadecimal'),
      ('header_size', 'Header size', '_FormatIntegerAsDecimal'),
      ('arena_size', 'Arena size', '_FormatIntegerAsDecimal'),
      ('data_hash_table_offset', 'Data hash table offset',
       '_FormatIntegerAsHexadecimal8'),
      ('data_hash_table_size', 'Data hash table size',
       '_FormatIntegerAsDecimal'),
      ('field_hash_table_offset', 'Field hash table offset',
       '_FormatIntegerAsHexadecimal8'),
      ('field_hash_table_size', 'Field hash table size',
       '_FormatIntegerAsDecimal'),
      ('tail_object_offset', 'Tail object offset',
       '_FormatIntegerAsHexadecimal8'),
      ('number_of_objects', 'Number of objects', '_FormatIntegerAsDecimal'),
      ('number_of_entry_objects', 'Number of entry objects',
       '_FormatIntegerAsDecimal'),
      ('tail_entry_sequence_number', 'Tail entry sequence number',
       '_FormatIntegerAsHexadecimal8'),
      ('head_entry_sequence_number', 'Head entry sequence number',
       '_FormatIntegerAsHexadecimal8'),
      ('entry_array_offset', 'Entry array offset',
       '_FormatIntegerAsHexadecimal8'),
      ('head_entry_real_time', 'Head entry real time',
       '_FormatIntegerAsPosixTimeInMicroseconds'),
      ('tail_entry_real_time', 'Tail entry real time',
       '_FormatIntegerAsPosixTimeInMicroseconds'),
      ('tail_entry_monotonic', 'Tail entry monotonic',
       '_FormatIntegerAsHexadecimal8')]

  _DEBUG_INFO_OBJECT_HEADER = [
      ('object_type', 'Object type', '_FormatIntegerAsObjectType'),
      ('object_flags', 'Object flags', '_FormatIntegerAsObjectFlags'),
      ('reserved1', 'Reserved', '_FormatDataInHexadecimal'),
      ('data_size', 'Data size', '_FormatIntegerAsDecimal')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a systemd journal file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(SystemdJournalFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._format_version = None

  def _FormatEntryItems(self, entry_items):
    """Formats the entry items.

    Args:
      entry_items (list[systemd_journal_entry_item]): array of entry items.

    Returns:
      str: formatted entry items.
    """
    lines = []
    for index, entry_item in enumerate(entry_items):
      description_string = '    Entry item: {0:d} object offset'.format(index)
      value_string = self._FormatIntegerAsHexadecimal8(entry_item.object_offset)
      line = self._FormatValue(description_string, value_string)
      lines.append(line)

      description_string = '    Entry item: {0:d} hash'.format(index)
      value_string = self._FormatIntegerAsHexadecimal8(entry_item.hash)
      line = self._FormatValue(description_string, value_string)
      lines.append(line)

    return ''.join(lines)

  def _FormatEntryObjectOffsets(self, array_of_integers):
    """Formats the entry object offsets.

    Args:
      array_of_integers (list[int]): array of integers.

    Returns:
      str: array of integers formatted as entry object offsets.
    """
    lines = []
    for index, entry_object_offset in enumerate(array_of_integers):
      description_string = '    Entry object offset: {0:d}'.format(index)
      value_string = self._FormatIntegerAsHexadecimal8(entry_object_offset)
      line = self._FormatValue(description_string, value_string)
      lines.append(line)

    return ''.join(lines)

  def _FormatIntegerAsObjectFlags(self, integer):
    """Formats an integer as object flags .

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as object flags.
    """
    if integer == 0:
      return self._FormatIntegerAsHexadecimal2(integer)

    return '0x{0:02x} ({1:s})'.format(
        integer, self._OBJECT_FLAGS.get(integer, 'UNKNOWN'))

  def _FormatIntegerAsObjectType(self, integer):
    """Formats an integer as an object type .

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as an object type.
    """
    return '{0:d} ({1:s})'.format(
        integer, self._OBJECT_TYPES.get(integer, 'UNKNOWN'))

  def _FormatStreamAsSignature(self, stream):
    """Formats a stream as a signature.

    Args:
      stream (bytes): stream.

    Returns:
      str: stream formatted as a signature.
    """
    return stream.decode('ascii')

  def _ReadDataObject(self, file_object, file_offset):
    """Reads a data object.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data object relative to the start
          of the file-like object.

    Returns:
      systemd_journal_data_object: data object.

    Raises:
      ParseError: if the data object cannot be read.
    """
    data_type_map = self._GetDataTypeMap('systemd_journal_data_object')

    data_object, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'data object')

    if self._debug:
      self._DebugPrintStructureObject(
          data_object, self._DEBUG_INFO_OBJECT_HEADER)

    if data_object.object_type != self._OBJECT_TYPE_DATA:
      raise errors.ParseError('Unsupported object type: {0:d}.'.format(
          data_object.object_type))

    if data_object.object_flags not in (
        0, self._OBJECT_COMPRESSED_XZ, self._OBJECT_COMPRESSED_LZ4):
      raise errors.ParseError('Unsupported object flags: 0x{0:02x}.'.format(
          data_object.object_flags))

    if self._debug:
      self._DebugPrintStructureObject(
          data_object, self._DEBUG_INFO_DATA_OBJECT_VALUES)

    return data_object

  def _ReadEntryArrayObject(self, file_object, file_offset):
    """Reads an entry array object.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the entry array object relative to the start
          of the file-like object.

    Returns:
      systemd_journal_entry_array_object: entry array object.

    Raises:
      ParseError: if the entry array object cannot be read.
    """
    data_type_map = self._GetDataTypeMap('systemd_journal_entry_array_object')

    entry_array_object, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'entry array object')

    if self._debug:
      self._DebugPrintStructureObject(
          entry_array_object, self._DEBUG_INFO_OBJECT_HEADER)

    if entry_array_object.object_type != self._OBJECT_TYPE_ENTRY_ARRAY:
      raise errors.ParseError('Unsupported object type: {0:d}.'.format(
          entry_array_object.object_type))

    if entry_array_object.object_flags != 0:
      raise errors.ParseError('Unsupported object flags: 0x{0:02x}.'.format(
          entry_array_object.object_flags))

    if self._debug:
      self._DebugPrintStructureObject(
          entry_array_object, self._DEBUG_INFO_ENTRY_ARRAY_OBJECT_VALUES)

    return entry_array_object

  def _ReadEntryObject(self, file_object, file_offset):
    """Reads an entry object.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the entry object relative to the start
          of the file-like object.

    Returns:
      systemd_journal_entry_object: entry object.

    Raises:
      ParseError: if the entry object cannot be read.
    """
    data_type_map = self._GetDataTypeMap('systemd_journal_entry_object')

    entry_object, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'entry object')

    if self._debug:
      self._DebugPrintStructureObject(
          entry_object, self._DEBUG_INFO_OBJECT_HEADER)

    if entry_object.object_type != self._OBJECT_TYPE_ENTRY:
      raise errors.ParseError('Unsupported object type: {0:d}.'.format(
          entry_object.object_type))

    if entry_object.object_flags != 0:
      raise errors.ParseError('Unsupported object flags: 0x{0:02x}.'.format(
          entry_object.object_flags))

    if self._debug:
      self._DebugPrintStructureObject(
          entry_object, self._DEBUG_INFO_ENTRY_OBJECT_VALUES)

    return entry_object

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Returns:
      systemd_journal_file_header: file header.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('systemd_journal_file_header')

    file_header, _ = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'file header')

    if self._debug:
      self._DebugPrintStructureObject(file_header, self._DEBUG_INFO_FILE_HEADER)

    if file_header.header_size not in self._SUPPORTED_FILE_HEADER_SIZES:
      raise errors.ParseError('Unsupported file header size: {0:d}.'.format(
          file_header.header_size))

    if file_header.header_size == 224:
      self._format_version = 187
    elif file_header.header_size == 240:
      self._format_version = 189

    return file_header

  def _ReadObjectHeader(self, file_object, file_offset):
    """Reads an object header.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the object header relative to the start of
          the file-like object.

    Returns:
      systemd_journal_object_header: object header.

    Raises:
      ParseError: if the object header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('systemd_journal_object_header')

    object_header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'object header')

    if self._debug:
      self._DebugPrintStructureObject(
          object_header, self._DEBUG_INFO_OBJECT_HEADER)

    return object_header

  def ReadFileObject(self, file_object):
    """Reads a Windows Task Scheduler job file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_header = self._ReadFileHeader(file_object)

    entry_array_object = self._ReadEntryArrayObject(
        file_object, file_header.entry_array_offset)

    entry_object_offsets = list(entry_array_object.entry_object_offsets)
    while entry_array_object.next_entry_array_offset != 0:
      entry_array_object = self._ReadEntryArrayObject(
          file_object, entry_array_object.next_entry_array_offset)
      entry_object_offsets.extend(entry_array_object.entry_object_offsets)

    for entry_object_offset in entry_object_offsets:
      if entry_object_offset == 0:
        continue

      entry_object = self._ReadEntryObject(file_object, entry_object_offset)

      for entry_item in entry_object.entry_items:
        self._ReadDataObject(file_object, entry_item.object_offset)
