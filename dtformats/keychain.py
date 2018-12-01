# -*- coding: utf-8 -*-
"""MacOS keychain database files."""

from __future__ import unicode_literals

import collections

from dtfabric.runtime import data_maps as dtfabric_data_maps

from dtformats import data_format
from dtformats import errors


class KeychainDatabaseColumn(object):
  """MacOS keychain database column.

  Attributes:
    attribute_data_type (int): attribute (data) type.
    attribute_identifier (int): attribute identifier.
    attribute_name (str): attribute name.
  """

  def __init__(self):
    """Initializes a MacOS keychain database column."""
    super(KeychainDatabaseColumn, self).__init__()
    self.attribute_data_type = None
    self.attribute_identifier = None
    self.attribute_name = None


class KeychainDatabaseTable(object):
  """MacOS keychain database table.

  Attributes:
    columns (list[KeychainDatabaseColumn]): columns.
    records (list[dict[str, object]]): records.
    relation_identifier (int): relation identifier.
    relation_name (str): relation name.
  """

  def __init__(self):
    """Initializes a MacOS keychain database table."""
    super(KeychainDatabaseTable, self).__init__()
    self.columns = []
    self.records = []
    self.relation_identifier = None
    self.relation_name = None


class KeychainDatabaseFile(data_format.BinaryDataFile):
  """MacOS keychain database file."""

  _DEFINITION_FILE = 'keychain.yaml'

  _FILE_SIGNATURE = b'kych'

  _RECORD_TYPE_CSSM_DL_DB_SCHEMA_INFO = 0x00000000
  _RECORD_TYPE_CSSM_DL_DB_SCHEMA_INDEXES = 0x00000001
  _RECORD_TYPE_CSSM_DL_DB_SCHEMA_ATTRIBUTES = 0x00000002

  _TABLE_NAMES = {
      0x00000000: 'CSSM_DL_DB_SCHEMA_INFO',
      0x00000001: 'CSSM_DL_DB_SCHEMA_INDEXES',
      0x00000002: 'CSSM_DL_DB_SCHEMA_ATTRIBUTES',
      0x00000003: 'CSSM_DL_DB_SCHEMA_PARSING_MODULE',
      0x0000000a: 'CSSM_DL_DB_RECORD_ANY',
      0x0000000b: 'CSSM_DL_DB_RECORD_CERT',
      0x0000000c: 'CSSM_DL_DB_RECORD_CRL',
      0x0000000d: 'CSSM_DL_DB_RECORD_POLICY',
      0x0000000e: 'CSSM_DL_DB_RECORD_GENERIC',
      0x0000000f: 'CSSM_DL_DB_RECORD_PUBLIC_KEY',
      0x00000010: 'CSSM_DL_DB_RECORD_PRIVATE_KEY',
      0x00000011: 'CSSM_DL_DB_RECORD_SYMMETRIC_KEY',
      0x00000012: 'CSSM_DL_DB_RECORD_ALL_KEYS',
      0x80000000: 'CSSM_DL_DB_RECORD_GENERIC_PASSWORD',
      0x80000001: 'CSSM_DL_DB_RECORD_INTERNET_PASSWORD',
      0x80000002: 'CSSM_DL_DB_RECORD_APPLESHARE_PASSWORD',
      0x80000003: 'CSSM_DL_DB_RECORD_USER_TRUST',
      0x80000004: 'CSSM_DL_DB_RECORD_X509_CRL',
      0x80000005: 'CSSM_DL_DB_RECORD_UNLOCK_REFERRAL',
      0x80000006: 'CSSM_DL_DB_RECORD_EXTENDED_ATTRIBUTE',
      0x80001000: 'CSSM_DL_DB_RECORD_X509_CERTIFICATE',
      0x80008000: 'CSSM_DL_DB_RECORD_METADATA'}

  _ATTRIBUTE_DATA_TYPES = {
      0: 'CSSM_DB_ATTRIBUTE_FORMAT_STRING',
      1: 'CSSM_DB_ATTRIBUTE_FORMAT_SINT32',
      2: 'CSSM_DB_ATTRIBUTE_FORMAT_UINT32',
      3: 'CSSM_DB_ATTRIBUTE_FORMAT_BIG_NUM',
      4: 'CSSM_DB_ATTRIBUTE_FORMAT_REAL',
      5: 'CSSM_DB_ATTRIBUTE_FORMAT_TIME_DATE',
      6: 'CSSM_DB_ATTRIBUTE_FORMAT_BLOB',
      7: 'CSSM_DB_ATTRIBUTE_FORMAT_MULTI_UINT32',
      8: 'CSSM_DB_ATTRIBUTE_FORMAT_COMPLEX'}

  _ATTRIBUTE_DATA_READ_FUNCTIONS = {
      0: '_ReadAttributeValueString',
      1: '_ReadAttributeValueInteger',
      2: '_ReadAttributeValueInteger',
      5: '_ReadAttributeValueDateTime',
      6: '_ReadAttributeValueBinaryData'}

  _DEBUG_INFO_FILE_HEADER = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('major_format_version', 'Major format version',
       '_FormatIntegerAsDecimal'),
      ('minor_format_version', 'Minor format version',
       '_FormatIntegerAsDecimal'),
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('tables_array_offset', 'Tables array offset',
       '_FormatIntegerAsHexadecimal8'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8')]

  _DEBUG_INFO_RECORD_HEADER = [
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('record_index', 'Record index', '_FormatIntegerAsDecimal'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal8'),
      ('unknown3', 'Unknown3', '_FormatIntegerAsHexadecimal8'),
      ('key_data_size', 'Key data size', '_FormatIntegerAsDecimal'),
      ('unknown4', 'Unknown4', '_FormatIntegerAsHexadecimal8')]

  _DEBUG_INFO_TABLES_ARRAY = [
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('number_of_tables', 'Number of tables', '_FormatIntegerAsDecimal'),
      ('table_offsets', 'Table offsets', '_FormatTableOffsets')]

  _DEBUG_INFO_TABLE_HEADER = [
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('record_type', 'Record type', '_FormatIntegerAsRecordType'),
      ('number_of_records', 'Number of records', '_FormatIntegerAsDecimal'),
      ('record_array_offset', 'Record array offset',
       '_FormatIntegerAsHexadecimal8'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal8'),
      ('number_of_record_offsets', 'Number of record offsets',
       '_FormatIntegerAsDecimal'),
      ('record_offsets', 'Record offsets', '_FormatRecordOffsets')]

  _DEBUG_INFO_SCHEMA_INDEXES_RECORD_VALUES = [
      ('relation_identifier', 'Relation identifier',
       '_FormatIntegerAsHexadecimal8'),
      ('index_identifier', 'Index identifier', '_FormatIntegerAsHexadecimal8'),
      ('attribute_identifier', 'Attribute identifier',
       '_FormatIntegerAsHexadecimal8'),
      ('index_type', 'Index type', '_FormatIntegerAsHexadecimal8'),
      ('index_data_location', 'Index data location',
       '_FormatIntegerAsHexadecimal8')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a MacOS keychain database file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(KeychainDatabaseFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._tables = collections.OrderedDict()

  @property
  def tables(self):
    """list[KeychainDatabaseTable]: tables."""
    return self._tables.values()

  def _FormatRecordOffsets(self, array_of_integers):
    """Formats the record offsets.

    Args:
      array_of_integers (list[int]): array of integers.

    Returns:
      str: formatted record offsets.
    """
    lines = []
    for index, record_offset in enumerate(array_of_integers):
      description_string = 'Record offset: {0:d}'.format(index)
      value_string = self._FormatIntegerAsHexadecimal8(record_offset)
      line = self._FormatValue(description_string, value_string)
      lines.append(line)

    return ''.join(lines)

  def _FormatIntegerAsRecordValue(self, integer):
    """Formats an integer as a record value.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as record value.
    """
    if integer is None:
      return 'NULL'

    return self._FormatIntegerAsHexadecimal8(integer)

  def _FormatIntegerAsRecordType(self, integer):
    """Formats an integer as a record type.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as record type.
    """
    table_name = self._TABLE_NAMES.get(integer, 'UNKNOWN')
    return '0x{0:08x} ({1:s})'.format(integer, table_name)

  def _FormatStreamAsSignature(self, stream):
    """Formats a stream as a signature.

    Args:
      stream (bytes): stream.

    Returns:
      str: stream formatted as a signature.
    """
    return stream.decode('ascii')

  def _FormatTableOffsets(self, array_of_integers):
    """Formats the table offsets.

    Args:
      array_of_integers (list[int]): array of integers.

    Returns:
      str: formatted table offsets.
    """
    lines = []
    for index, table_offset in enumerate(array_of_integers):
      description_string = 'Table offset: {0:d}'.format(index)
      value_string = self._FormatIntegerAsHexadecimal8(table_offset)
      line = self._FormatValue(description_string, value_string)
      lines.append(line)

    return ''.join(lines)

  def _ReadAttributeValueBinaryData(
      self, attribute_values_data, record_offset, attribute_values_data_offset,
      attribute_value_offset, description):
    """Reads a binary data attribute value.

    Args:
      attribute_values_data (bytes): attribute values data.
      record_offset (int): offset of the record relative to the start of
          the file.
      attribute_values_data_offset (int): offset of the attribute values data
          relative to the start of the record.
      attribute_value_offset (int): offset of the attribute relative to
          the start of the record.
      description (str): description of the attribute value.

    Returns:
      bytes: binary data value or None if attribute value offset is not set.

    Raises:
      ParseError: if the attribute value cannot be read.
    """
    if attribute_value_offset == 0:
      return None

    data_type_map = self._GetDataTypeMap('keychain_blob')

    file_offset = (
        record_offset + attribute_values_data_offset + attribute_value_offset)

    attribute_value_offset -= attribute_values_data_offset + 1
    attribute_value_data = attribute_values_data[attribute_value_offset:]

    try:
      string_attribute_value = self._ReadStructureFromByteStream(
          attribute_value_data, file_offset, data_type_map, description)
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map binary data attribute value data at offset: 0x{0:08x} '
          'with error: {1!s}').format(file_offset, exception))

    return repr(string_attribute_value.blob)

  def _ReadAttributeValueDateTime(
      self, attribute_values_data, record_offset, attribute_values_data_offset,
      attribute_value_offset, description):
    """Reads a date time attribute value.

    Args:
      attribute_values_data (bytes): attribute values data.
      record_offset (int): offset of the record relative to the start of
          the file.
      attribute_values_data_offset (int): offset of the attribute values data
          relative to the start of the record.
      attribute_value_offset (int): offset of the attribute relative to
          the start of the record.
      description (str): description of the attribute value.

    Returns:
      str: date and time values.

    Raises:
      ParseError: if the attribute value cannot be read.
    """
    if attribute_value_offset == 0:
      return None

    data_type_map = self._GetDataTypeMap('keychain_date_time')

    file_offset = (
        record_offset + attribute_values_data_offset + attribute_value_offset)

    attribute_value_offset -= attribute_values_data_offset + 1
    attribute_value_data = attribute_values_data[attribute_value_offset:]

    try:
      date_time_attribute_value = self._ReadStructureFromByteStream(
          attribute_value_data, file_offset, data_type_map, description)
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map date time attribute value data at offset: 0x{0:08x} '
          'with error: {1!s}').format(file_offset, exception))

    return date_time_attribute_value.date_time.rstrip('\x00')

  def _ReadAttributeValueInteger(
      self, attribute_values_data, record_offset, attribute_values_data_offset,
      attribute_value_offset, description):
    """Reads an integer attribute value.

    Args:
      attribute_values_data (bytes): attribute values data.
      record_offset (int): offset of the record relative to the start of
          the file.
      attribute_values_data_offset (int): offset of the attribute values data
          relative to the start of the record.
      attribute_value_offset (int): offset of the attribute relative to
          the start of the record.
      description (str): description of the attribute value.

    Returns:
      int: integer value or None if attribute value offset is not set.

    Raises:
      ParseError: if the attribute value cannot be read.
    """
    if attribute_value_offset == 0:
      return None

    data_type_map = self._GetDataTypeMap('uint32be')

    file_offset = (
        record_offset + attribute_values_data_offset + attribute_value_offset)

    attribute_value_offset -= attribute_values_data_offset + 1
    attribute_value_data = attribute_values_data[attribute_value_offset:]

    try:
      return self._ReadStructureFromByteStream(
          attribute_value_data, file_offset, data_type_map, description)
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map integer attribute value data at offset: 0x{0:08x} '
          'with error: {1!s}').format(file_offset, exception))

  def _ReadAttributeValueString(
      self, attribute_values_data, record_offset, attribute_values_data_offset,
      attribute_value_offset, description):
    """Reads a string attribute value.

    Args:
      attribute_values_data (bytes): attribute values data.
      record_offset (int): offset of the record relative to the start of
          the file.
      attribute_values_data_offset (int): offset of the attribute values data
          relative to the start of the record.
      attribute_value_offset (int): offset of the attribute relative to
          the start of the record.
      description (str): description of the attribute value.

    Returns:
      str: string value or None if attribute value offset is not set.

    Raises:
      ParseError: if the attribute value cannot be read.
    """
    if attribute_value_offset == 0:
      return None

    data_type_map = self._GetDataTypeMap('keychain_string')

    file_offset = (
        record_offset + attribute_values_data_offset + attribute_value_offset)

    attribute_value_offset -= attribute_values_data_offset + 1
    attribute_value_data = attribute_values_data[attribute_value_offset:]

    try:
      string_attribute_value = self._ReadStructureFromByteStream(
          attribute_value_data, file_offset, data_type_map, description)
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map string attribute value data at offset: 0x{0:08x} '
          'with error: {1!s}').format(file_offset, exception))

    return string_attribute_value.string

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
      self._DebugPrintStructureObject(file_header, self._DEBUG_INFO_FILE_HEADER)

    if file_header.signature != self._FILE_SIGNATURE:
      raise errors.ParseError('Unsupported file signature.')

    return file_header

  def _ReadRecord(self, tables, file_object, record_offset, record_type):
    """Reads the record.

    Args:
      tables (dict[str, KeychainDatabaseTable]): tables per name.
      file_object (file): file-like object.
      record_offset (int): offset of the record relative to the start of
          the file.
      record_type (int): record type, which should correspond to a relation
          identifier of a table defined in the schema.

    Raises:
      ParseError: if the record cannot be read.
    """
    table = tables.get(record_type, None)
    if not table:
      raise errors.ParseError(
          'Missing table for relation identifier: 0x{0:08}'.format(record_type))

    record_header = self._ReadRecordHeader(file_object, record_offset)

    record = collections.OrderedDict()
    if table.columns:
      number_of_columns = len(table.columns)
      attribute_value_offsets = self._ReadRecordAttributeValueOffset(
          file_object, record_offset + 24, number_of_columns)

      file_offset = file_object.tell()
      record_data_offset = file_offset - record_offset
      record_data_size = record_header.data_size
      record_data = file_object.read(record_data_size - record_data_offset)

      if self._debug:
        if record_header.key_data_size > 0:
          self._DebugPrintData(
              'Key data', record_data[:record_header.key_data_size])

        self._DebugPrintData(
            'Attribute values data', record_data[record_header.key_data_size:])

        data_offsets = [
            offset - record_data_offset - 1
            for offset in sorted(attribute_value_offsets)
            if offset > record_data_offset]
        data_offsets.append(record_data_size - record_data_offset)
        data_offsets.pop(0)

      for index, column in enumerate(table.columns):
        if self._debug:
          if attribute_value_offsets[index] == 0:
            attribute_value_offset = 0
            attribute_value_end_offset = 0
          else:
            attribute_value_offset = (
                attribute_value_offsets[index] - record_data_offset - 1)
            attribute_value_end_offset = data_offsets[0]
            while attribute_value_end_offset <= attribute_value_offset:
              data_offsets.pop(0)
              attribute_value_end_offset = data_offsets[0]

          description = 'Attribute value: {0:d} ({1:s}) data'.format(
              index, column.attribute_name)
          self._DebugPrintData(description, record_data[
              attribute_value_offset:attribute_value_end_offset])

        attribute_data_read_function = self._ATTRIBUTE_DATA_READ_FUNCTIONS.get(
            column.attribute_data_type, None)
        if attribute_data_read_function:
          attribute_data_read_function = getattr(
              self, attribute_data_read_function, None)

        if not attribute_data_read_function:
          attribute_value = None
        else:
          attribute_value = attribute_data_read_function(
              record_data, record_offset, record_data_offset,
              attribute_value_offsets[index], column.attribute_name)

        record[column.attribute_name] = attribute_value

    table.records.append(record)

  def _ReadRecordAttributeValueOffset(
      self, file_object, file_offset, number_of_attribute_values):
    """Reads the record attribute value offsets.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the record attribute values offsets relative
          to the start of the file.
      number_of_attribute_values (int): number of attribute values.

    Returns:
      keychain_record_attribute_value_offsets: record attribute value offsets.

    Raises:
      ParseError: if the record attribute value offsets cannot be read.
    """
    offsets_data_size = number_of_attribute_values * 4

    offsets_data = file_object.read(offsets_data_size)

    if self._debug:
      self._DebugPrintData('Attribute value offsets data', offsets_data)

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'number_of_attribute_values': number_of_attribute_values})

    data_type_map = self._GetDataTypeMap(
        'keychain_record_attribute_value_offsets')

    try:
      attribute_value_offsets = self._ReadStructureFromByteStream(
          offsets_data, file_offset, data_type_map,
          'record attribute value offsets', context=context)
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map record attribute value offsets data at offset: '
          '0x{0:08x} with error: {1!s}').format(file_offset, exception))

    if self._debug:
      for index, attribute_value_offset in enumerate(attribute_value_offsets):
        description_string = 'Attribute value offset: {0:d}'.format(index)
        value_string = self._FormatIntegerAsHexadecimal8(attribute_value_offset)
        self._DebugPrintValue(description_string, value_string)

      self._DebugPrintText('\n')

    return attribute_value_offsets

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
      self._DebugPrintStructureObject(
          record_header, self._DEBUG_INFO_RECORD_HEADER)

    return record_header

  def _ReadRecordSchemaAttributes(self, tables, file_object, record_offset):
    """Reads a schema attributes (CSSM_DL_DB_SCHEMA_ATTRIBUTES) record.

    Args:
      tables (dict[str, KeychainDatabaseTable]): tables per name.
      file_object (file): file-like object.
      record_offset (int): offset of the record relative to the start of
          the file.

    Raises:
      ParseError: if the record cannot be read.
    """
    record_header = self._ReadRecordHeader(file_object, record_offset)

    attribute_value_offsets = self._ReadRecordAttributeValueOffset(
        file_object, record_offset + 24, 6)

    file_offset = file_object.tell()
    attribute_values_data_offset = file_offset - record_offset
    attribute_values_data_size = record_header.data_size - (
        file_offset - record_offset)
    attribute_values_data = file_object.read(attribute_values_data_size)

    if self._debug:
      self._DebugPrintData('Attribute values data', attribute_values_data)

    relation_identifier = self._ReadAttributeValueInteger(
        attribute_values_data, record_offset, attribute_values_data_offset,
        attribute_value_offsets[0], 'relation identifier')

    if self._debug:
      if relation_identifier is None:
        value_string = 'NULL'
      else:
        table_name = self._TABLE_NAMES.get(relation_identifier, 'UNKNOWN')
        value_string = '0x{0:08x} ({1:s})'.format(
            relation_identifier, table_name)
      self._DebugPrintValue('Relation identifier', value_string)

    attribute_identifier = self._ReadAttributeValueInteger(
        attribute_values_data, record_offset, attribute_values_data_offset,
        attribute_value_offsets[1], 'attribute identifier')

    if self._debug:
      value_string = self._FormatIntegerAsRecordValue(attribute_identifier)
      self._DebugPrintValue('Attribute identifier', value_string)

    attribute_name_data_type = self._ReadAttributeValueInteger(
        attribute_values_data, record_offset, attribute_values_data_offset,
        attribute_value_offsets[2], 'attribute name data type')

    if self._debug:
      if attribute_name_data_type is None:
        value_string = 'NULL'
      else:
        data_type_string = self._ATTRIBUTE_DATA_TYPES.get(
            attribute_name_data_type, 'UNKNOWN')
        value_string = '{0:d} ({1:s})'.format(
            attribute_name_data_type, data_type_string)
      self._DebugPrintValue('Attribute name data type', value_string)

    attribute_name = self._ReadAttributeValueString(
        attribute_values_data, record_offset, attribute_values_data_offset,
        attribute_value_offsets[3], 'attribute name')

    if self._debug:
      if attribute_name is None:
        value_string = 'NULL'
      else:
        value_string = attribute_name
      self._DebugPrintValue('Attribute name', value_string)

    # TODO: add support for AttributeNameID

    attribute_data_type = self._ReadAttributeValueInteger(
        attribute_values_data, record_offset, attribute_values_data_offset,
        attribute_value_offsets[5], 'attribute data type')

    if self._debug:
      if attribute_data_type is None:
        value_string = 'NULL'
      else:
        data_type_string = self._ATTRIBUTE_DATA_TYPES.get(
            attribute_data_type, 'UNKNOWN')
        value_string = '{0:d} ({1:s})'.format(
            attribute_data_type, data_type_string)
      self._DebugPrintValue('Attribute data type', value_string)

    if self._debug:
      self._DebugPrintText('\n')

    table = tables.get(relation_identifier, None)
    if not table:
      raise errors.ParseError(
          'Missing table for relation identifier: 0x{0:08}'.format(
              relation_identifier))

    # TODO: map attribute identifier to module specific names?
    if attribute_name is None and attribute_value_offsets[1] != 0:
      attribute_value_offset = attribute_value_offsets[1]
      attribute_value_offset -= attribute_values_data_offset + 1
      attribute_name = attribute_values_data[
          attribute_value_offset:attribute_value_offset + 4]
      attribute_name = attribute_name.decode('ascii')

    column = KeychainDatabaseColumn()
    column.attribute_data_type = attribute_data_type
    column.attribute_identifier = attribute_identifier
    column.attribute_name = attribute_name

    table.columns.append(column)

    table = tables.get(self._RECORD_TYPE_CSSM_DL_DB_SCHEMA_ATTRIBUTES, None)
    if not table:
      raise errors.ParseError('Missing CSSM_DL_DB_SCHEMA_ATTRIBUTES table.')

    record = collections.OrderedDict({
        'RelationID': relation_identifier,
        'AttributeID': attribute_identifier,
        'AttributeNameFormat': attribute_name_data_type,
        'AttributeName': attribute_name,
        'AttributeFormat': attribute_data_type})

    table.records.append(record)

  def _ReadRecordSchemaIndexes(self, tables, file_object, record_offset):
    """Reads a schema indexes (CSSM_DL_DB_SCHEMA_INDEXES) record.

    Args:
      tables (dict[str, KeychainDatabaseTable]): tables per name.
      file_object (file): file-like object.
      record_offset (int): offset of the record relative to the start of
          the file.

    Raises:
      ParseError: if the record cannot be read.
    """
    record_header = self._ReadRecordHeader(file_object, record_offset)

    attribute_value_offsets = self._ReadRecordAttributeValueOffset(
        file_object, record_offset + 24, 5)

    if attribute_value_offsets != (0x2d, 0x31, 0x35, 0x39, 0x3d):
      raise errors.ParseError('Unuspported record attribute value offsets')

    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('keychain_record_schema_indexes')

    record_values, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map,
        'schema indexes record values')

    if self._debug:
      self._DebugPrintStructureObject(
          record_values, self._DEBUG_INFO_SCHEMA_INDEXES_RECORD_VALUES)

    if self._debug:
      file_offset = file_object.tell()
      trailing_data_size = record_header.data_size - (
          file_offset - record_offset)

      if trailing_data_size == 0:
        self._DebugPrintText('\n')
      else:
        trailing_data = file_object.read(trailing_data_size)
        self._DebugPrintData('Record trailing data', trailing_data)

    if record_values.relation_identifier not in tables:
      raise errors.ParseError(
          'CSSM_DL_DB_SCHEMA_INDEXES defines relation identifier not defined '
          'in CSSM_DL_DB_SCHEMA_INFO.')

    table = tables.get(self._RECORD_TYPE_CSSM_DL_DB_SCHEMA_INDEXES, None)
    if not table:
      raise errors.ParseError('Missing CSSM_DL_DB_SCHEMA_INDEXES table.')

    record = collections.OrderedDict({
        'RelationID': record_values.relation_identifier,
        'IndexID': record_values.index_identifier,
        'AttributeID': record_values.attribute_identifier,
        'IndexType': record_values.index_type,
        'IndexedDataLocation': record_values.index_data_location})

    table.records.append(record)

  def _ReadRecordSchemaInformation(self, tables, file_object, record_offset):
    """Reads a schema information (CSSM_DL_DB_SCHEMA_INFO) record.

    Args:
      tables (dict[str, KeychainDatabaseTable]): tables per name.
      file_object (file): file-like object.
      record_offset (int): offset of the record relative to the start of
          the file.

    Raises:
      ParseError: if the record cannot be read.
    """
    record_header = self._ReadRecordHeader(file_object, record_offset)

    attribute_value_offsets = self._ReadRecordAttributeValueOffset(
        file_object, record_offset + 24, 2)

    if attribute_value_offsets != (0x21, 0x25):
      raise errors.ParseError('Unuspported record attribute value offsets')

    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('keychain_record_schema_information')

    record_values, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map,
        'schema information record values')

    relation_name = record_values.relation_name.decode('ascii')

    if self._debug:
      value_string = '0x{0:08x}'.format(record_values.relation_identifier)
      self._DebugPrintValue('Relation identifier', value_string)

      value_string = '{0:d}'.format(record_values.relation_name_size)
      self._DebugPrintValue('Relation name size', value_string)

      self._DebugPrintValue('Relation name', relation_name)

    if self._debug:
      file_offset = file_object.tell()
      trailing_data_size = record_header.data_size - (
          file_offset - record_offset)

      if trailing_data_size == 0:
        self._DebugPrintText('\n')
      else:
        trailing_data = file_object.read(trailing_data_size)
        self._DebugPrintData('Record trailing data', trailing_data)

    table = KeychainDatabaseTable()
    table.relation_identifier = record_values.relation_identifier
    table.relation_name = relation_name

    tables[table.relation_identifier] = table

    table = tables.get(self._RECORD_TYPE_CSSM_DL_DB_SCHEMA_INFO, None)
    if not table:
      raise errors.ParseError('Missing CSSM_DL_DB_SCHEMA_INFO table.')

    record = collections.OrderedDict({
        'RelationID': record_values.relation_identifier,
        'RelationName': relation_name})

    table.records.append(record)

  def _ReadTable(self, tables, file_object, table_offset):
    """Reads the table.

    Args:
      tables (dict[str, KeychainDatabaseTable]): tables per name.
      file_object (file): file-like object.
      table_offset (int): offset of the table relative to the start of
          the file.

    Raises:
      ParseError: if the table cannot be read.
    """
    table_header = self._ReadTableHeader(file_object, table_offset)

    for record_offset in table_header.record_offsets:
      if record_offset == 0:
        continue

      record_offset += table_offset

      if table_header.record_type == self._RECORD_TYPE_CSSM_DL_DB_SCHEMA_INFO:
        self._ReadRecordSchemaInformation(tables, file_object, record_offset)
      elif table_header.record_type == (
          self._RECORD_TYPE_CSSM_DL_DB_SCHEMA_INDEXES):
        self._ReadRecordSchemaIndexes(tables, file_object, record_offset)
      elif table_header.record_type == (
          self._RECORD_TYPE_CSSM_DL_DB_SCHEMA_ATTRIBUTES):
        self._ReadRecordSchemaAttributes(tables, file_object, record_offset)
      else:
        self._ReadRecord(
            tables, file_object, record_offset, table_header.record_type)

    if self._debug:
      file_offset = file_object.tell()
      trailing_data_size = table_header.data_size - (file_offset - table_offset)

      if trailing_data_size != 0:
        trailing_data = file_object.read(trailing_data_size)
        self._DebugPrintData('Table trailing data', trailing_data)

  def _ReadTableHeader(self, file_object, table_header_offset):
    """Reads the table header.

    Args:
      file_object (file): file-like object.
      table_header_offset (int): offset of the table header relative to
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
      self._DebugPrintStructureObject(
          table_header, self._DEBUG_INFO_TABLE_HEADER)

    return table_header

  def _ReadTablesArray(self, file_object, tables_array_offset):
    """Reads the tables array.

    Args:
      file_object (file): file-like object.
      tables_array_offset (int): offset of the tables array relative to
          the start of the file.

    Returns:
      dict[str, KeychainDatabaseTable]: tables per name.

    Raises:
      ParseError: if the tables array cannot be read.
    """
    # TODO: implement https://github.com/libyal/dtfabric/issues/12 and update
    # keychain_tables_array definition.

    data_type_map = self._GetDataTypeMap('keychain_tables_array')

    tables_array, _ = self._ReadStructureFromFileObject(
        file_object, tables_array_offset, data_type_map, 'tables array')

    if self._debug:
      self._DebugPrintStructureObject(
          tables_array, self._DEBUG_INFO_TABLES_ARRAY)

    tables = collections.OrderedDict()
    for table_offset in tables_array.table_offsets:
      self._ReadTable(tables, file_object, tables_array_offset + table_offset)

    return tables

  def ReadFileObject(self, file_object):
    """Reads a MacOS keychain database file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_header = self._ReadFileHeader(file_object)

    self._tables = self._ReadTablesArray(
        file_object, file_header.tables_array_offset)
