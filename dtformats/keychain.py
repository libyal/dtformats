# -*- coding: utf-8 -*-
"""MacOS keychain database files."""

from __future__ import unicode_literals

from dtformats import data_format
from dtformats import errors


class KeychainDatabaseFile(data_format.BinaryDataFile):
  """MacOS keychain database file."""

  _DEFINITION_FILE = 'keychain.yaml'

  _FILE_SIGNATURE = b'kych'

  def __init__(self, debug=False, output_writer=None):
    """Initializes a MacOS keychain database file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(KeychainDatabaseFile, self).__init__(
        debug=debug, output_writer=output_writer)

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (keychain_file_header): file header.
    """
    value_string = file_header.signature.decode('ascii')
    self._DebugPrintValue('Signature', value_string)

    value_string = '{0:d}'.format(file_header.major_format_version)
    self._DebugPrintValue('Major format version', value_string)

    value_string = '{0:d}'.format(file_header.major_format_version)
    self._DebugPrintValue('Major format version', value_string)

    value_string = '{0:d}'.format(file_header.minor_format_version)
    self._DebugPrintValue('Minor format version', value_string)

    value_string = '{0:d}'.format(file_header.data_size)
    self._DebugPrintValue('Data size', value_string)

    value_string = '0x{0:08x}'.format(file_header.tables_array_offset)
    self._DebugPrintValue('Tables array offset', value_string)

    value_string = '0x{0:08x}'.format(file_header.unknown1)
    self._DebugPrintValue('Unknown1', value_string)

    self._DebugPrintText('\n')

  def _DebugPrintRecordHeader(self, record_header):
    """Prints record header debug information.

    Args:
      record_header (keychain_record_header): record header.
    """
    value_string = '{0:d}'.format(record_header.data_size)
    self._DebugPrintValue('Data size', value_string)

    # TODO: implement

    self._DebugPrintText('\n')

  def _DebugPrintTablesArray(self, tables_array):
    """Prints file tables array information.

    Args:
      tables_array (keychain_tables_array): tables array.
    """
    value_string = '{0:d}'.format(tables_array.data_size)
    self._DebugPrintValue('Data size', value_string)

    value_string = '{0:d}'.format(tables_array.number_of_tables)
    self._DebugPrintValue('Number of tables', value_string)

    for index, table_offset in enumerate(tables_array.table_offsets):
      description_string = 'Table offset: {0:d}'.format(index)
      value_string = '0x{0:08x}'.format(table_offset)
      self._DebugPrintValue(description_string, value_string)

    self._DebugPrintText('\n')

  def _DebugPrintTableHeader(self, table_header):
    """Prints table header debug information.

    Args:
      table_header (keychain_table_header): table header.
    """
    value_string = '{0:d}'.format(table_header.data_size)
    self._DebugPrintValue('Data size', value_string)

    value_string = '0x{0:08x}'.format(table_header.record_type)
    self._DebugPrintValue('Record type', value_string)

    value_string = '{0:d}'.format(table_header.number_of_records)
    self._DebugPrintValue('Number of records', value_string)

    value_string = '0x{0:08x}'.format(table_header.records_array_offset)
    self._DebugPrintValue('Records array offset', value_string)

    value_string = '0x{0:08x}'.format(table_header.index_offset)
    self._DebugPrintValue('Index offset', value_string)

    value_string = '0x{0:08x}'.format(table_header.unknown1)
    self._DebugPrintValue('Unknown1', value_string)

    value_string = '{0:d}'.format(table_header.number_of_record_offsets)
    self._DebugPrintValue('Number of record offsets', value_string)

    for index, record_offset in enumerate(table_header.record_offsets):
      description_string = 'Record offset: {0:d}'.format(index)
      value_string = '0x{0:08x}'.format(record_offset)
      self._DebugPrintValue(description_string, value_string)

    self._DebugPrintText('\n')

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Returns:
      keychain_file_header: file header.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('keychain_file_header')

    file_header, _ = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

    if file_header.signature != self._FILE_SIGNATURE:
      raise errors.ParseError('Unsupported file signature.')

    return file_header

  def _ReadRecord(self, file_object, record_offset):
    """Reads the record.

    Args:
      file_object (file): file-like object.
      record_offset (int): offset of the record relative to the start of
          the file.

    Raises:
      ParseError: if the record cannot be read.
    """
    record_header = self._ReadRecordHeader(file_object, record_offset)

    # TODO: implement read record values.
    _ = record_header

  def _ReadRecordHeader(self, file_object, record_header_offset):
    """Reads the record header.

    Args:
      file_object (file): file-like object.
      record_header_offset (int): offset of the record header relative to
          the start of the file.

    Returns:
      keychain_record_header: record header.

    Raises:
      ParseError: if the record header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('keychain_record_header')

    record_header, _ = self._ReadStructureFromFileObject(
        file_object, record_header_offset, data_type_map, 'record header')

    if self._debug:
      self._DebugPrintRecordHeader(record_header)

    return record_header

  def _ReadTablesArray(self, file_object, tables_array_offset):
    """Reads the tables array.

    Args:
      file_object (file): file-like object.
      tables_array_offset (int): offset of the tables array relative to
          the start of the file.

    Raises:
      ParseError: if the tables array cannot be read.
    """
    # TODO: implement https://github.com/libyal/dtfabric/issues/12 and update
    # keychain_tables_array definition.

    data_type_map = self._GetDataTypeMap('keychain_tables_array')

    tables_array, _ = self._ReadStructureFromFileObject(
        file_object, tables_array_offset, data_type_map, 'tables array')

    if self._debug:
      self._DebugPrintTablesArray(tables_array)

    for table_offset in tables_array.table_offsets:
      self._ReadTable(file_object, tables_array_offset + table_offset)

  def _ReadTable(self, file_object, table_offset):
    """Reads the table.

    Args:
      file_object (file): file-like object.
      table_offset (int): offset of the table relative to the start of
          the file.

    Raises:
      ParseError: if the table cannot be read.
    """
    table_header = self._ReadTableHeader(file_object, table_offset)

    record_offset = table_offset + table_header.records_array_offset

    for record_offset in table_header.record_offsets:
      self._ReadRecord(file_object, table_offset + record_offset)

  def _ReadTableHeader(self, file_object, table_header_offset):
    """Reads the table header.

    Args:
      file_object (file): file-like object.
      tables_header_offset (int): offset of the tables header relative to
          the start of the file.

    Returns:
      keychain_table_header: table header.

    Raises:
      ParseError: if the table header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('keychain_table_header')

    table_header, _ = self._ReadStructureFromFileObject(
        file_object, table_header_offset, data_type_map, 'table header')

    if self._debug:
      self._DebugPrintTableHeader(table_header)

    if table_header.number_of_records != table_header.number_of_record_offsets:
      raise errors.ParseError(
          'Number of records does not match number of record offsets.')

    return table_header

  def ReadFileObject(self, file_object):
    """Reads a MacOS keychain database file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_header = self._ReadFileHeader(file_object)

    self._ReadTablesArray(
        file_object, file_header.tables_array_offset)
