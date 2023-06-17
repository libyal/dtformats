# -*- coding: utf-8 -*-
"""Systemd journal files."""

from dtformats import data_format
from dtformats import errors


class SystemdJournalFile(data_format.BinaryDataFile):
  """Systemd journal file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('systemd.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'systemd.debug.yaml', custom_format_callbacks={
          'entry_items': '_FormatEntryItems',
          'entry_object_offsets': '_FormatEntryObjectOffsets',
          'object_flags': '_FormatIntegerAsObjectFlags',
          'object_type': '_FormatIntegerAsObjectType',
          'posix_time': '_FormatIntegerAsPosixTimeInMicroseconds',
          'signature': '_FormatStreamAsSignature'})

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
      value_string = self._FormatIntegerAsHexadecimal8(entry_item.object_offset)
      line = self._FormatValue(
          f'    Entry item: {index:d} object offset', value_string)
      lines.append(line)

      value_string = self._FormatIntegerAsHexadecimal8(entry_item.hash)
      line = self._FormatValue(
          f'    Entry item: {index:d} hash', value_string)
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
      value_string = self._FormatIntegerAsHexadecimal8(entry_object_offset)
      line = self._FormatValue(
          f'    Entry object offset: {index:d}', value_string)
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

    object_flags = self._OBJECT_FLAGS.get(integer, 'UNKNOWN')
    return f'0x{integer:02x} ({object_flags:s})'

  def _FormatIntegerAsObjectType(self, integer):
    """Formats an integer as an object type .

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as an object type.
    """
    object_types = self._OBJECT_TYPES.get(integer, 'UNKNOWN')
    return f'{integer:d} ({object_types:s})'

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
      debug_info = self._DEBUG_INFORMATION.get(
          'systemd_journal_object_header', None)
      self._DebugPrintStructureObject(data_object, debug_info)

    if data_object.object_type != self._OBJECT_TYPE_DATA:
      raise errors.ParseError(
          f'Unsupported object type: {data_object.object_type:d}.')

    if data_object.object_flags not in (
        0, self._OBJECT_COMPRESSED_XZ, self._OBJECT_COMPRESSED_LZ4):
      raise errors.ParseError(
          f'Unsupported object flags: 0x{data_object.object_flags:02x}.')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get(
          'systemd_journal_data_object_values', None)
      self._DebugPrintStructureObject(data_object, debug_info)

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
      debug_info = self._DEBUG_INFORMATION.get(
          'systemd_journal_object_header', None)
      self._DebugPrintStructureObject(entry_array_object, debug_info)

    if entry_array_object.object_type != self._OBJECT_TYPE_ENTRY_ARRAY:
      raise errors.ParseError(
          f'Unsupported object type: {entry_array_object.object_type:d}.')

    if entry_array_object.object_flags != 0:
      raise errors.ParseError(
          f'Unsupported object flags: 0x{entry_array_object.object_flags:02x}.')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get(
          'systemd_journal_entry_array_object_values', None)
      self._DebugPrintStructureObject(entry_array_object, debug_info)

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
      debug_info = self._DEBUG_INFORMATION.get(
          'systemd_journal_object_header', None)
      self._DebugPrintStructureObject(entry_object, debug_info)

    if entry_object.object_type != self._OBJECT_TYPE_ENTRY:
      raise errors.ParseError(
          f'Unsupported object type: {entry_object.object_type:d}.')

    if entry_object.object_flags != 0:
      raise errors.ParseError(
          f'Unsupported object flags: 0x{entry_object.object_flags:02x}.')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get(
          'systemd_journal_entry_object_values', None)
      self._DebugPrintStructureObject(entry_object, debug_info)

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
      debug_info = self._DEBUG_INFORMATION.get(
          'systemd_journal_file_header', None)
      self._DebugPrintStructureObject(file_header, debug_info)

    if file_header.header_size not in self._SUPPORTED_FILE_HEADER_SIZES:
      raise errors.ParseError(
          f'Unsupported file header size: {file_header.header_size:d}.')

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
      debug_info = self._DEBUG_INFORMATION.get(
          'systemd_journal_object_header', None)
      self._DebugPrintStructureObject(object_header, debug_info)

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
