# -*- coding: utf-8 -*-
"""Apple Spotlight store database files."""

from __future__ import unicode_literals

import zlib

from dfdatetime import cocoa_time as dfdatetime_cocoa_time
from dfdatetime import posix_time as dfdatetime_posix_time
from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import data_maps as dtfabric_data_maps

from dtformats import data_format
from dtformats import errors


class SpotlightStoreMetadataAttribute(object):
  """Metadata attribute.

  Attributes:
    key (str): key or name of the metadata attribute.
    property_type (int): metadata attribute property type.
    value (object): metadata attribute value.
    value_type (int): metadata attribute value type.
  """

  def __init__(self):
    """Initializes a metadata attribute."""
    super(SpotlightStoreMetadataAttribute, self).__init__()
    self.key = None
    self.property_type = None
    self.value = None
    self.value_type = None


class SpotlightStoreMetadataItem(object):
  """Metadata item.

  Attributes:
    attributes (dict[str, MetadataAttribute]): metadata attributes.
    identifier (int): file (system) entry identifier.
    item_identifier (int): item identifier.
    last_update_time (int): last update time.
    parent_identifier (int): parent file (system) entry identifier.
  """

  def __init__(self):
    """Initializes a record."""
    super(SpotlightStoreMetadataItem, self).__init__()
    self.attributes = {}
    self.identifier = 0
    self.item_identifier = 0
    self.last_update_time = 0
    self.parent_identifier = 0


class SpotlightStoreRecordDescriptor(object):
  """Record descriptor.

  Attributes:
    identifier (int): record identifier.
    item_identifier (int): item identifier.
    last_update_time (int): record last update time.
    page_offset (int): offset of the page containing the record, relative to
        the start of the file.
    page_value_offset (int): offset of the page value containing the record,
        relative to the start of the page.
    parent_identifier (int): parent identifier.
  """

  def __init__(self, page_offset, page_value_offset):
    """Initializes a record descriptor.

    Args:
      page_offset (int): offset of the page containing the record, relative to
          the start of the file.
      page_value_offset (int): offset of the page value containing the record,
          relative to the start of the page.
    """
    super(SpotlightStoreRecordDescriptor, self).__init__()
    self.identifier = 0
    self.item_identifier = 0
    self.last_update_time = 0
    self.page_offset = page_offset
    self.page_value_offset = page_value_offset
    self.parent_identifier = 0


class SpotlightStoreRecordHeader(object):
  """Record header.

  Attributes:
    data_size (int): size of the record data.
    flags (int): record flags.
    identifier (int): record identifier.
    item_identifier (int): item identifier.
    last_update_time (int): record last update time.
    parent_identifier (int): parent identifier.
  """

  def __init__(self):
    """Initializes a record header."""
    super(SpotlightStoreRecordHeader, self).__init__()
    self.data_size = 0
    self.flags = 0
    self.identifier = 0
    self.item_identifier = 0
    self.last_update_time = 0
    self.parent_identifier = 0


class AppleSpotlightStoreDatabaseFile(data_format.BinaryDataFile):
  """Apple Spotlight store database file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile(
      'spotlight_storedb.yaml')

  _DEBUG_INFO_FILE_HEADER = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('flags', 'Flags', '_FormatIntegerAsHexadecimal8'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal8'),
      ('unknown3', 'Unknown3', '_FormatIntegerAsHexadecimal8'),
      ('unknown4', 'Unknown4', '_FormatIntegerAsHexadecimal8'),
      ('unknown5', 'Unknown5', '_FormatIntegerAsHexadecimal8'),
      ('unknown6', 'Unknown6', '_FormatIntegerAsHexadecimal8'),
      ('unknown7', 'Unknown7', '_FormatIntegerAsHexadecimal8'),
      ('map_offset', 'Map offset', '_FormatIntegerAsHexadecimal8'),
      ('map_size', 'Map size', '_FormatIntegerAsDecimal'),
      ('page_size', 'Page size', '_FormatIntegerAsDecimal'),
      ('metadata_types_block_number', 'Metadata types block number',
       '_FormatIntegerAsDecimal'),
      ('metadata_values_block_number', 'Metadata values block number',
       '_FormatIntegerAsDecimal'),
      ('unknown_values41_block_number', 'Unknown valuex 0x41 block number',
       '_FormatIntegerAsDecimal'),
      ('metadata_lists_block_number', 'Metadata lists block number',
       '_FormatIntegerAsDecimal'),
      ('metadata_localized_strings_block_number',
       'Metadata localized strings block number', '_FormatIntegerAsDecimal'),
      ('unknown8', 'Unknown8', '_FormatDataInHexadecimal'),
      ('path', 'Path', '_FormatString')]

  _DEBUG_INFO_MAP_PAGE_HEADER = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('page_size', 'Page size', '_FormatIntegerAsDecimal'),
      ('number_of_map_values', 'Number of map values',
       '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal8')]

  _DEBUG_INFO_MAP_VALUE = [
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8'),
      ('block_number', 'Block number', '_FormatIntegerAsDecimal'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal8')]

  _DEBUG_INFO_PROPERTY_PAGE_HEADER = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('page_size', 'Page size', '_FormatIntegerAsDecimal'),
      ('used_page_size', 'Used page size', '_FormatIntegerAsDecimal'),
      ('property_table_type', 'Property table type',
       '_FormatIntegerAsHexadecimal8'),
      ('uncompressed_page_size', 'Uncompressed page size',
       '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_PROPERTY_VALUES_HEADER = [
      ('next_block_number', 'Next block number', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8')]

  _DEBUG_INFO_PROPERTY_VALUE11 = [
      ('table_index', 'Table index', '_FormatIntegerAsDecimal'),
      ('value_type', 'Value type', '_FormatIntegerAsHexadecimal2'),
      ('property_type', 'Property type', '_FormatIntegerAsHexadecimal2'),
      ('key_name', 'Key name', '_FormatString')]

  _DEBUG_INFO_PROPERTY_VALUE21 = [
      ('table_index', 'Table index', '_FormatIntegerAsDecimal'),
      ('value_name', 'Value name', '_FormatString')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a binary data file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(AppleSpotlightStoreDatabaseFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._map_values = []
    self._metadata_lists = {}
    self._metadata_localized_strings = {}
    self._metadata_types = {}
    self._metadata_values = {}
    self._record_descriptors = {}
    self._record_pages_cache = {}

  @property
  def number_of_metadata_items(self):
    """int: number of metadata items in the database."""
    return len(self._record_descriptors)

  def _DebugPrintCocoaTimeValue(self, description, value):
    """Prints a Cocoa timestamp value for debugging.

    Args:
      description (str): description.
      value (object): value.
    """
    if value == 0:
      date_time_string = 'Not set (0)'
    else:
      date_time = dfdatetime_cocoa_time.CocoaTime(timestamp=value)
      date_time_string = date_time.CopyToDateTimeString()
      if date_time_string:
        date_time_string = '{0:s} UTC'.format(date_time_string)
      else:
        date_time_string = '0x{0:08x}'.format(value)

    self._DebugPrintValue(description, date_time_string)

  def _DebugPrintMetadataAttribute(self, metadata_attribute):
    """Prints a metadata attribute for debugging.

    Args:
      metadata_attribute (MetadataAttribute): metadata attribute.
    """
    if metadata_attribute.key == 'kMDStoreAccumulatedSizes':
      self._DebugPrintData('Data', metadata_attribute.value)

    elif metadata_attribute.value_type == 0x00:
      self._DebugPrintDecimalValue('Integer', metadata_attribute.value)
      value_string = '{0!s}'.format(bool(metadata_attribute.value))
      self._DebugPrintValue('Boolean', value_string)

    elif metadata_attribute.value_type in (0x02, 0x06):
      value_string = self._FormatIntegerAsHexadecimal8(metadata_attribute.value)
      self._DebugPrintValue('Integer', value_string)

    elif metadata_attribute.value_type == 0x07:
      if metadata_attribute.property_type & 0x02 == 0x00:
        self._DebugPrintDecimalValue('Integer', metadata_attribute.value)
      else:
        for array_index, array_value in enumerate(metadata_attribute.value):
          description = 'Integer: {0:d}'.format(array_index)
          self._DebugPrintDecimalValue(description, array_value)

    elif metadata_attribute.value_type == 0x08:
      if metadata_attribute.property_type & 0x02 == 0x00:
        self._DebugPrintDecimalValue('Byte', metadata_attribute.value)
      else:
        for array_index, array_value in enumerate(metadata_attribute.value):
          description = 'Byte: {0:d}'.format(array_index)
          self._DebugPrintDecimalValue(description, array_value)

    elif metadata_attribute.value_type in (0x09, 0x0a):
      if metadata_attribute.property_type & 0x02 == 0x00:
        value_string = self._FormatFloatingPoint(metadata_attribute.value)
        self._DebugPrintValue('Floating-point', value_string)
      else:
        for array_index, array_value in enumerate(metadata_attribute.value):
          description = 'Floating-point: {0:d}'.format(array_index)
          value_string = self._FormatFloatingPoint(array_value)
          self._DebugPrintValue(description, value_string)

    elif metadata_attribute.value_type == 0x0b:
      if metadata_attribute.property_type & 0x03 != 0x02:
        self._DebugPrintValue('String', metadata_attribute.value)
      else:
        for array_index, array_value in enumerate(metadata_attribute.value):
          description = 'String: {0:d}'.format(array_index)
          self._DebugPrintValue(description, array_value)

    elif metadata_attribute.value_type == 0x0c:
      if metadata_attribute.property_type & 0x02 == 0x00:
        if metadata_attribute.value < 7500000000.0:
          self._DebugPrintCocoaTimeValue(
              'Date and time', metadata_attribute.value)
        else:
          value_string = self._FormatFloatingPoint(metadata_attribute.value)
          self._DebugPrintValue('Floating-point', value_string)

      else:
        for array_index, array_value in enumerate(metadata_attribute.value):
          if array_value < 7500000000.0:
            description = 'Date and time: {0:d}'.format(array_index)
            self._DebugPrintCocoaTimeValue(description, array_value)
          else:
            description = 'Floating-point: {0:d}'.format(array_index)
            value_string = self._FormatFloatingPoint(array_value)
            self._DebugPrintValue(description, value_string)

    elif metadata_attribute.value_type == 0x0e:
      self._DebugPrintData('Binary data', metadata_attribute.value)

    elif metadata_attribute.value_type == 0x0f:
      if metadata_attribute.property_type & 0x03 == 0x03:
        self._DebugPrintValue('Localized string', metadata_attribute.value)

      elif metadata_attribute.property_type & 0x03 == 0x02:
        self._DebugPrintValue('Values list', metadata_attribute.value)

      else:
        self._DebugPrintValue('Value', metadata_attribute.value)

    self._DebugPrintText('\n')

  def _DebugPrintPosixTimeValue(self, description, value):
    """Prints a POSIX timestamp value for debugging.

    Args:
      description (str): description.
      value (object): value.
    """
    if value == 0:
      date_time_string = 'Not set (0)'
    else:
      date_time = dfdatetime_posix_time.PosixTimeInMicroseconds(timestamp=value)
      date_time_string = date_time.CopyToDateTimeString()
      if date_time_string:
        date_time_string = '{0:s} UTC'.format(date_time_string)
      else:
        date_time_string = '0x{0:08x}'.format(value)

    self._DebugPrintValue(description, date_time_string)

  def _FormatStreamAsSignature(self, stream):
    """Formats a stream as a signature.

    Args:
      stream (bytes): stream.

    Returns:
      str: stream formatted as a signature.
    """
    return stream.decode('ascii').replace('\x00', '\\x00')

  def _GetMetadataItemByIdentifier(self, file_object, identifier):
    """Retrieves a specific metadata item.

    Args:
      file_object (file): file-like object.
      identifier (int): file (system) entry identifier of the metadata item.

    Returns:
      SpotlightStoreMetadataItem: metadata item matching the identifier or None
          if no such item.
    """
    record_descriptor = self._record_descriptors.get(identifier, None)
    if not record_descriptor:
      return None

    if self._debug:
      self._DebugPrintText((
          'Retrieving record: {0:d} in page: 0x{1:08x} at offset: '
          '0x{2:04x}\n').format(
              identifier, record_descriptor.page_offset,
              record_descriptor.page_value_offset))
      self._DebugPrintText('\n')

    page_data = self._record_pages_cache.get(
        record_descriptor.page_offset, None)
    if not page_data:
      _, page_data = self._ReadRecordPage(
          file_object, record_descriptor.page_offset)

      # TODO: remove page from cache if full.
      self._record_pages_cache[record_descriptor.page_offset] = page_data

    return self._ReadRecord(page_data, record_descriptor.page_value_offset)

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Returns:
      spotlight_store_db_file_header: file header.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('spotlight_store_db_file_header')

    file_header, file_header_size = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'file header')

    if self._debug:
      self._DebugPrintStructureObject(file_header, self._DEBUG_INFO_FILE_HEADER)

    if self._debug:
      trailing_data = file_object.read(
          file_header.map_offset - file_header_size)
      self._DebugPrintData('Trailing data', trailing_data)

    return file_header

  def _ReadIndexPageValues(self, page_header, page_data, property_table):
    """Reads the index page values.

    Args:
      page_header (spotlight_store_db_property_page_header): page header.
      page_data (bytes): page data.
      property_table (dict[int, object]): property table in which to store the
          property page values.

    Raises:
      ParseError: if the property page values cannot be read.
    """
    data_type_map = self._GetDataTypeMap('spotlight_store_db_property_value81')
    index_values_data_type_map = self._GetDataTypeMap(
        'spotlight_store_db_index_values')

    page_data_offset = 12
    page_data_size = page_header.used_page_size - 20
    page_value_index = 0

    while page_data_offset < page_data_size:
      try:
        property_value = data_type_map.MapByteStream(
            page_data[page_data_offset:])
      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError((
            'Unable to map property value data at offset: 0x{0:08x} with '
            'error: {1!s}').format(page_data_offset, exception))

      page_value_size = 4

      index_size, bytes_read = self._ReadVariableSizeInteger(
          page_data[page_data_offset + page_value_size:])

      _, padding_size = divmod(index_size, 4)

      page_value_size += bytes_read + padding_size
      index_size -= padding_size

      context = dtfabric_data_maps.DataTypeMapContext(values={
          'index_size': index_size})

      try:
        index_values = index_values_data_type_map.MapByteStream(
            page_data[page_data_offset + page_value_size:], context=context)

      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError((
            'Unable to parse index data at offset: 0x{0:08x} with error: '
            '{1:s}').format(page_data_offset + page_value_size, exception))

      page_value_size += index_size

      if self._debug:
        self._DebugPrintData(
            'Page value: {0:d} data'.format(page_value_index),
            page_data[page_data_offset:page_data_offset + page_value_size])

      values_list = []
      for metadata_value_index in index_values:
        metadata_value = self._metadata_values.get(metadata_value_index, None)
        value_string = getattr(metadata_value, 'value_name', '')
        values_list.append(value_string)

      setattr(property_value, 'values_list', values_list)

      if self._debug:
        self._DebugPrintDecimalValue('Table index', property_value.table_index)
        self._DebugPrintDecimalValue('Index size', index_size)

        value_string = self._FormatArrayOfIntegersAsDecimals(index_values)
        self._DebugPrintValue('Index values', value_string)
        self._DebugPrintText('\n')

        for metadata_value_index in index_values:
          metadata_value = self._metadata_values.get(metadata_value_index, None)
          value_string = getattr(metadata_value, 'value_name', '')
          self._DebugPrintValue(
              'Value: {0:d}'.format(metadata_value_index), value_string)

        self._DebugPrintText('\n')

      property_table[property_value.table_index] = property_value

      page_data_offset += page_value_size
      page_value_index += 1

  def _ReadMapPage(self, file_object, file_offset):
    """Reads a map page.

    Args:
      file_object (file): file-like object.
      file_offset (int): file offset.

    Returns:
      spotlight_store_db_map_page_header: page header.

    Raises:
      ParseError: if the map page cannot be read.
    """
    data_type_map = self._GetDataTypeMap('spotlight_store_db_map_page_header')

    page_header, page_header_size = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'map page header')

    if self._debug:
      self._DebugPrintStructureObject(
          page_header, self._DEBUG_INFO_MAP_PAGE_HEADER)

    file_offset += page_header_size

    self._ReadMapPageValues(page_header, file_object, file_offset)

    if self._debug:
      page_data = file_object.read(page_header.page_size - page_header_size)
      self._DebugPrintData('Page data', page_data)

    return page_header

  def _ReadMapPages(self, file_object, map_offset, map_size):
    """Reads the map pages.

    Args:
      file_object (file): file-like object.
      map_offset (int): map offset.
      map_size (int): map size.

    Raises:
      ParseError: if the map pages cannot be read.
    """
    map_end_offset = map_offset + map_size

    while map_offset < map_end_offset:
      page_header = self._ReadMapPage(file_object, map_offset)

      map_offset += page_header.page_size

  def _ReadMapPageValues(self, page_header, file_object, file_offset):
    """Reads the map page values.

    Args:
      page_header (spotlight_store_db_map_page_header): page header.
      file_object (file): file-like object.
      file_offset (int): file offset.

    Raises:
      ParseError: if the map page values cannot be read.
    """
    data_type_map = self._GetDataTypeMap('spotlight_store_db_map_page_value')

    for _ in range(page_header.number_of_map_values):
      map_value, map_value_size = self._ReadStructureFromFileObject(
          file_object, file_offset, data_type_map, 'map page value')

      if self._debug:
        self._DebugPrintStructureObject(map_value, self._DEBUG_INFO_MAP_VALUE)

      self._map_values.append(map_value)

      file_offset += map_value_size

  def _ReadMetadataAttribute(self, metadata_type, data):
    """Reads a metadata attribute.

    Args:
      metadata_type (spotlight_store_db_property_value11): metadata type
          property value.
      data (bytes): data.

    Returns:
      tuple[SpotlightStoreMetadataAttribute, int]: metadata attribute and
          number of bytes read.
    """
    value_type = getattr(metadata_type, 'value_type', None)
    if value_type is None:
      return None, 0

    key_name = getattr(metadata_type, 'key_name', None)
    property_type = getattr(metadata_type, 'property_type', None)

    if self._debug:
      self._DebugPrintValue('Key name', key_name or '')

      value_string = self._FormatIntegerAsHexadecimal2(property_type or 0)
      self._DebugPrintValue('Property type', value_string)

      value_string = self._FormatIntegerAsHexadecimal2(value_type or 0)
      self._DebugPrintValue('Value type', value_string)

    if key_name == 'kMDStoreAccumulatedSizes':
      bytes_read = 4 * 16
      value = data[:bytes_read]

    elif value_type in (0x00, 0x02, 0x06):
      value, bytes_read = self._ReadVariableSizeInteger(data)

    elif value_type == 0x07:
      value, bytes_read = self._ReadMetadataAttributeVariableSizeIntegerValue(
          property_type, data)

    elif value_type == 0x08:
      value, bytes_read = self._ReadMetadataAttributeByteValue(
          property_type, data)

    elif value_type == 0x09:
      value, bytes_read = self._ReadMetadataAttributeFloat32Value(
          property_type, data)

    elif value_type in (0x0a, 0x0c):
      value, bytes_read = self._ReadMetadataAttributeFloat64Value(
          property_type, data)

    elif value_type == 0x0b:
      value, bytes_read = self._ReadMetadataAttributeStringValue(
          property_type, data)

    elif value_type == 0x0e:
      data_size, bytes_read = self._ReadVariableSizeInteger(data)

      if self._debug:
        self._DebugPrintDecimalValue('Data size', data_size)

      value = data[bytes_read:bytes_read + data_size]
      bytes_read += data_size

      # TODO: decode binary data e.g. UUID

    elif value_type == 0x0f:
      value, bytes_read = self._ReadMetadataAttributeReferenceValue(
          property_type, data)

    else:
      # TODO: value type 0x01, 0x03, 0x04, 0x05, 0x0d
      value, bytes_read = None, 0

    metadata_attribute = SpotlightStoreMetadataAttribute()
    metadata_attribute.key = getattr(metadata_type, 'key_name', None)
    metadata_attribute.property_type = property_type
    metadata_attribute.value = value
    metadata_attribute.value_type = value_type

    if self._debug:
      self._DebugPrintMetadataAttribute(metadata_attribute)

    return metadata_attribute, bytes_read

  def _ReadMetadataAttributeByteValue(self, property_type, data):
    """Reads a metadata attribute byte value.

    Args:
      property_type (int): metadata attribute property type.
      data (bytes): data.

    Returns:
      tuple[object, int]: value and number of bytes read.

    Raises:
      ParseError: if the metadata attribute byte value cannot be read.
    """
    if property_type & 0x02 == 0x00:
      data_size, bytes_read = 1, 0
    else:
      data_size, bytes_read = self._ReadVariableSizeInteger(data)

    if self._debug and bytes_read != 0:
      self._DebugPrintDecimalValue('Data size', data_size)

    data_type_map = self._GetDataTypeMap('array_of_byte')

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'elements_data_size': data_size})

    try:
      array_of_values = data_type_map.MapByteStream(
          data[bytes_read:bytes_read + data_size], context=context)

    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError(
          'Unable to parse array of byte values with error: {0!s}'.format(
              exception))

    if bytes_read == 0:
      value = array_of_values[0]
    else:
      value = array_of_values

    bytes_read += data_size

    return value, bytes_read

  def _ReadMetadataAttributeFloat32Value(self, property_type, data):
    """Reads a metadata attribute 32-bit floating-point value.

    Args:
      property_type (int): metadata attribute property type.
      data (bytes): data.

    Returns:
      tuple[object, int]: value and number of bytes read.

    Raises:
      ParseError: if the metadata attribute 32-bit floating-point value cannot
          be read.
    """
    if property_type & 0x02 == 0x00:
      data_size, bytes_read = 4, 0
    else:
      data_size, bytes_read = self._ReadVariableSizeInteger(data)

    if self._debug and bytes_read != 0:
      self._DebugPrintDecimalValue('Data size', data_size)

    data_type_map = self._GetDataTypeMap('array_of_float32')

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'elements_data_size': data_size})

    try:
      array_of_values = data_type_map.MapByteStream(
          data[bytes_read:bytes_read + data_size], context=context)

    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          'Unable to parse array of 32-bit floating-point values with error: '
          '{0!s}').format(exception))

    if bytes_read == 0:
      value = array_of_values[0]
    else:
      value = array_of_values

    bytes_read += data_size

    return value, bytes_read

  def _ReadMetadataAttributeFloat64Value(self, property_type, data):
    """Reads a metadata attribute 64-bit floating-point value.

    Args:
      property_type (int): metadata attribute property type.
      data (bytes): data.

    Returns:
      tuple[object, int]: value and number of bytes read.

    Raises:
      ParseError: if the metadata attribute 64-bit floating-point value cannot
          be read.
    """
    if property_type & 0x02 == 0x00:
      data_size, bytes_read = 8, 0
    else:
      data_size, bytes_read = self._ReadVariableSizeInteger(data)

    if self._debug and bytes_read != 0:
      self._DebugPrintDecimalValue('Data size', data_size)

    data_type_map = self._GetDataTypeMap('array_of_float64')

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'elements_data_size': data_size})

    try:
      array_of_values = data_type_map.MapByteStream(
          data[bytes_read:bytes_read + data_size], context=context)

    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          'Unable to parse array of 64-bit floating-point values with error: '
          '{0!s}').format(exception))

    if bytes_read == 0:
      value = array_of_values[0]
    else:
      value = array_of_values

    bytes_read += data_size

    return value, bytes_read

  def _ReadMetadataAttributeReferenceValue(self, property_type, data):
    """Reads a metadata attribute reference value.

    Args:
      property_type (int): metadata attribute property type.
      data (bytes): data.

    Returns:
      tuple[object, int]: value and number of bytes read.

    Raises:
      ParseError: if the metadata attribute reference value cannot be read.
    """
    table_index, bytes_read = self._ReadVariableSizeInteger(data)

    if property_type & 0x03 == 0x03:
      if self._debug:
        self._DebugPrintDecimalValue(
            'Localized strings table index', table_index)

      metadata_localized_strings = self._metadata_localized_strings.get(
          table_index, None)
      value_list = getattr(metadata_localized_strings, 'values_list', [])

      value = '(null)'
      if value_list:
        value = value_list[0]
        if '\x16\x02' in value:
          value = value.split('\x16\x02')[0]

    elif property_type & 0x03 == 0x02:
      if self._debug:
        self._DebugPrintDecimalValue('Values list table index', table_index)

      metadata_list = self._metadata_lists.get(table_index, None)
      value = getattr(metadata_list, 'values_list', [])

    else:
      if self._debug:
        self._DebugPrintDecimalValue('Values table index', table_index)

      metadata_value = self._metadata_values.get(table_index, None)
      value = getattr(metadata_value, 'value_name', '(null)')

    return value, bytes_read

  def _ReadMetadataAttributeStringValue(self, property_type, data):
    """Reads a metadata attribute string value.

    Args:
      property_type (int): metadata attribute property type.
      data (bytes): data.

    Returns:
      tuple[object, int]: value and number of bytes read.

    Raises:
      ParseError: if the metadata attribute string value cannot be read.
    """
    data_size, bytes_read = self._ReadVariableSizeInteger(data)

    if self._debug:
      self._DebugPrintDecimalValue('Data size', data_size)
      self._DebugPrintData('Data', data[bytes_read:bytes_read + data_size])

    data_type_map = self._GetDataTypeMap('array_of_cstring')

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'elements_data_size': data_size})

    try:
      array_of_values = data_type_map.MapByteStream(
          data[bytes_read:bytes_read + data_size], context=context)

    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError(
          'Unable to parse array of string values with error: {0!s}'.format(
              exception))

    if property_type & 0x03 == 0x03:
      value = array_of_values[0]
      if '\x16\x02' in value:
        value = value.split('\x16\x02')[0]
    elif property_type & 0x03 == 0x02:
      value = array_of_values
    else:
      value = array_of_values[0]

    bytes_read += data_size

    return value, bytes_read

  def _ReadMetadataAttributeVariableSizeIntegerValue(self, property_type, data):
    """Reads a metadata attribute variable size integer value.

    Args:
      property_type (int): metadata attribute property type.
      data (bytes): data.

    Returns:
      tuple[object, int]: value and number of bytes read.
    """
    if property_type & 0x02 == 0x00:
      return self._ReadVariableSizeInteger(data)

    data_size, bytes_read = self._ReadVariableSizeInteger(data)
    if self._debug:
      self._DebugPrintDecimalValue('Data size', data_size)

    array_of_values = []

    data_offset = 0
    while data_offset < data_size:
      integer_value, integer_value_size = self._ReadVariableSizeInteger(
          data[data_offset:data_size])

      data_offset += integer_value_size

      array_of_values.append(integer_value)

    bytes_read += data_size

    return array_of_values, bytes_read

  def _ReadPropertyPage(self, file_object, file_offset, property_table):
    """Reads a property page.

    Args:
      file_object (file): file-like object.
      file_offset (int): file offset.
      property_table (dict[int, object]): property table in which to store the
          property page values.

    Returns:
      tuple[spotlight_store_db_property_page_header, int]: page header and next
          property page block number.

    Raises:
      ParseError: if the property page cannot be read.
    """
    page_header, bytes_read = self._ReadPropertyPageHeader(
        file_object, file_offset)

    if page_header.property_table_type not in (
        0x00000011, 0x00000021, 0x00000041, 0x00000081):
      raise errors.ParseError(
          'Unsupported property table type: 0x{0:08x}'.format(
              page_header.property_table_type))

    page_data = file_object.read(page_header.page_size - bytes_read)

    data_type_map = self._GetDataTypeMap(
        'spotlight_store_db_property_values_header')

    file_offset += bytes_read

    page_values_header = self._ReadStructureFromByteStream(
        page_data, file_offset, data_type_map, 'property values header')

    if self._debug:
      self._DebugPrintStructureObject(
          page_values_header, self._DEBUG_INFO_PROPERTY_VALUES_HEADER)

    if page_header.property_table_type in (0x00000011, 0x00000021):
      self._ReadPropertyPageValues(page_header, page_data, property_table)

    elif page_header.property_table_type == 0x00000081:
      self._ReadIndexPageValues(page_header, page_data, property_table)

    elif self._debug:
      self._DebugPrintData('Page data', page_data)

    return page_header, page_values_header.next_block_number

  def _ReadPropertyPageHeader(self, file_object, file_offset):
    """Reads a property page header.

    Args:
      file_object (file): file-like object.
      file_offset (int): file offset.

    Returns:
      tuple[spotlight_store_db_property_page_header, int]: page header and next
          property page block number.

    Raises:
      ParseError: if the property page header cannot be read.
    """
    data_type_map = self._GetDataTypeMap(
        'spotlight_store_db_property_page_header')

    page_header, bytes_read = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'property page header')

    if self._debug:
      block_number = int(file_offset / 0x1000)
      self._DebugPrintDecimalValue('Block number', block_number)

      page_number = int(file_offset / page_header.page_size)
      self._DebugPrintDecimalValue('Page number', page_number)

      self._DebugPrintText('\n')

      self._DebugPrintStructureObject(
          page_header, self._DEBUG_INFO_PROPERTY_PAGE_HEADER)

    return page_header, bytes_read

  def _ReadPropertyPages(self, file_object, block_number, property_table):
    """Reads the property pages.

    Args:
      file_object (file): file-like object.
      block_number (int): block number.
      property_table (dict[int, object]): property table in which to store the
          property page values.

    Raises:
      ParseError: if the property pages cannot be read.
    """
    file_offset = block_number * 0x1000
    while file_offset != 0:
      _, next_block_number = self._ReadPropertyPage(
          file_object, file_offset, property_table)

      file_offset = next_block_number * 0x1000

  def _ReadPropertyPageValues(self, page_header, page_data, property_table):
    """Reads the property page values.

    Args:
      page_header (spotlight_store_db_property_page_header): page header.
      page_data (bytes): page data.
      property_table (dict[int, object]): property table in which to store the
          property page values.

    Raises:
      ParseError: if the property page values cannot be read.
    """
    if page_header.property_table_type == 0x00000011:
      data_type_map = self._GetDataTypeMap(
          'spotlight_store_db_property_value11')

    elif page_header.property_table_type == 0x00000021:
      data_type_map = self._GetDataTypeMap(
          'spotlight_store_db_property_value21')

    page_data_offset = 12
    page_data_size = page_header.used_page_size - 20
    page_value_index = 0

    while page_data_offset < page_data_size:
      context = dtfabric_data_maps.DataTypeMapContext()

      try:
        property_value = data_type_map.MapByteStream(
            page_data[page_data_offset:], context=context)
      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError((
            'Unable to map property value data at offset: 0x{0:08x} with '
            'error: {1!s}').format(page_data_offset, exception))

      if self._debug:
        self._DebugPrintData(
            'Page value: {0:d} data'.format(page_value_index),
            page_data[page_data_offset:page_data_offset + context.byte_size])

        if page_header.property_table_type == 0x00000011:
          debug_info = self._DEBUG_INFO_PROPERTY_VALUE11
        elif page_header.property_table_type == 0x00000021:
          debug_info = self._DEBUG_INFO_PROPERTY_VALUE21

        self._DebugPrintStructureObject(property_value, debug_info)

      property_table[property_value.table_index] = property_value

      page_data_offset += context.byte_size
      page_value_index += 1

  def _ReadRecord(self, page_data, page_value_offset):
    """Reads a record.

    Args:
      page_data (bytes): page data.
      page_value_offset (int): offset of the page value relative to the start
          of the page data.

    Returns:
      SpotlightStoreMetadataItem: metadata item.

    Raises:
      ParseError: if the record cannot be read.
    """
    if self._debug:
      value_string = self._FormatIntegerAsHexadecimal8(
          page_value_offset)
      self._DebugPrintValue('Record data offset', value_string)

    page_data_offset = page_value_offset - 20
    record_header, bytes_read = self._ReadRecordHeader(
        page_data[page_data_offset:], page_data_offset)

    page_data_offset += bytes_read
    record_data_offset = bytes_read

    metadata_item = SpotlightStoreMetadataItem()
    metadata_item.identifier = record_header.identifier
    metadata_item.item_identifier = record_header.item_identifier
    metadata_item.last_update_time = record_header.last_update_time
    metadata_item.parent_identifier = record_header.parent_identifier

    metadata_attribute_index = 0
    metadata_type_index = 0

    while record_data_offset < record_header.data_size:
      relative_metadata_type_index, bytes_read = (
          self._ReadVariableSizeInteger(page_data[page_data_offset:]))

      page_data_offset += bytes_read
      record_data_offset += bytes_read

      metadata_type_index += relative_metadata_type_index

      if self._debug:
        description = 'Relative metadata attribute: {0:d} type index'.format(
            metadata_attribute_index)
        self._DebugPrintDecimalValue(
            description, relative_metadata_type_index)

        description = 'Metadata attribute: {0:d} type index'.format(
            metadata_attribute_index)
        self._DebugPrintDecimalValue(description, metadata_type_index)

      metadata_type = self._metadata_types.get(metadata_type_index, None)
      metadata_attribute, bytes_read = self._ReadMetadataAttribute(
          metadata_type, page_data[page_data_offset:])

      page_data_offset += bytes_read
      record_data_offset += bytes_read

      metadata_item.attributes[metadata_attribute.key] = metadata_attribute
      metadata_attribute_index += 1

    return metadata_item

  def _ReadRecordHeader(self, data, page_data_offset):
    """Reads a record header.

    Args:
      data (bytes): data.
      page_data_offset (int): offset of the page value relative to the start
          of the page data.

    Returns:
      tuple[SpotlightStoreRecordHeader, int]: record header and number of bytes
          read.

    Raises:
      ParseError: if the record page cannot be read.
    """
    data_type_map = self._GetDataTypeMap('spotlight_store_db_record')

    context = dtfabric_data_maps.DataTypeMapContext()

    try:
      record = data_type_map.MapByteStream(data, context=context)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          'Unable to map record at offset: 0x{0:08x} with error: '
          '{1!s}').format(page_data_offset, exception))

    data_offset = context.byte_size

    identifier, bytes_read = self._ReadVariableSizeInteger(data[data_offset:])

    data_offset += bytes_read

    flags = data[data_offset]

    data_offset += 1

    value_names = ['item_identifier', 'parent_identifier', 'last_update_time']
    values, bytes_read = self._ReadVariableSizeIntegers(
        data[data_offset:], value_names)

    data_offset += bytes_read

    if self._debug:
      self._DebugPrintDecimalValue('Record data size', record.data_size)

    record_header = SpotlightStoreRecordHeader()
    record_header.data_size = record.data_size
    record_header.identifier = identifier
    record_header.flags = flags
    record_header.item_identifier = values.get('item_identifier')
    record_header.parent_identifier = values.get('parent_identifier')
    record_header.last_update_time = values.get('last_update_time')

    return record_header, data_offset

  def _ReadRecordPage(self, file_object, file_offset):
    """Reads a record page.

    Args:
      file_object (file): file-like object.
      file_offset (int): file offset.

    Returns:
      tuple[spotlight_store_db_property_page_header, bytes]: page header and
          page data.

    Raises:
      ParseError: if the property page cannot be read.
    """
    page_header, bytes_read = self._ReadPropertyPageHeader(
        file_object, file_offset)

    if page_header.property_table_type != 0x00000009:
      raise errors.ParseError(
          'Unsupported property table type: 0x{0:08x}'.format(
              page_header.property_table_type))

    page_data = file_object.read(page_header.page_size - bytes_read)

    if page_header.uncompressed_page_size > 0:
      # TODO: add support for other compression types.
      if page_data[0] != 0x78:
        raise errors.ParseError('Unsupported compression type')

      page_data = zlib.decompress(page_data)

    return page_header, page_data

  def _ReadRecordPageValues(self, page_data, page_offset):
    """Reads the record page values.

    Args:
      page_data (bytes): page data.
      page_offset (int): file offset of the page.

    Raises:
      ParseError: if the property page values cannot be read.
    """
    page_data_offset = 0
    page_data_size = len(page_data)

    while page_data_offset < page_data_size:
      if self._debug:
        value_string = self._FormatIntegerAsHexadecimal8(
            page_data_offset + 20)
        self._DebugPrintValue('Record data offset', value_string)

      record_header, _ = self._ReadRecordHeader(
          page_data[page_data_offset:], page_data_offset)

      if self._debug:
        record_data = page_data[
            page_data_offset + 4:page_data_offset + record_header.data_size]
        self._DebugPrintData('Record data', record_data)

      if self._debug:
        if record_header.identifier <= 1:
          description = 'Identifier'
        else:
          description = 'File system identifier'
        self._DebugPrintDecimalValue(description, record_header.identifier)

        value_string = self._FormatIntegerAsHexadecimal2(record_header.flags)
        self._DebugPrintValue('Flags', value_string)

        value_string = self._FormatIntegerAsHexadecimal2(
            record_header.item_identifier)
        self._DebugPrintValue('Item identifier', value_string)

        if record_header.parent_identifier <= 1:
          description = 'Parent identifier'
        else:
          description = 'Parent file system identifier'
        self._DebugPrintDecimalValue(
            description, record_header.parent_identifier)

        self._DebugPrintPosixTimeValue(
            'Last update time', record_header.last_update_time)
        self._DebugPrintText('\n')

      record_descriptor = SpotlightStoreRecordDescriptor(
          page_offset, page_data_offset + 20)
      record_descriptor.last_update_time = record_header.last_update_time
      record_descriptor.identifier = record_header.identifier
      record_descriptor.item_identifier = record_header.item_identifier
      record_descriptor.parent_identifier = record_header.parent_identifier

      self._record_descriptors[record_header.identifier] = record_descriptor

      page_data_offset += 4 + record_header.data_size

  def _ReadVariableSizeInteger(self, data):
    """Reads a variable size integer.

    Args:
      data (bytes): data.

    Returns:
      tuple[int, int]: integer value and number of bytes read.
    """
    byte_value = data[0]
    bytes_read = 1

    number_of_additional_bytes = 0
    for bitmask in (0x80, 0xc0, 0xe0, 0xf0, 0xf8, 0xfc, 0xfe, 0xff):
      if byte_value & bitmask != bitmask:
        break
      number_of_additional_bytes += 1

    if number_of_additional_bytes > 4:
      byte_value = 0
    elif number_of_additional_bytes > 0:
      byte_value &= bitmask ^ 0xff

    integer_value = int(byte_value)
    while number_of_additional_bytes > 0:
      integer_value <<= 8

      integer_value += int(data[bytes_read])
      bytes_read += 1

      number_of_additional_bytes -= 1

    return integer_value, bytes_read

  def _ReadVariableSizeIntegers(self, data, names):
    """Reads variable size integers.

    Args:
      data (bytes): data.
      names (list[str]): names to identify the integer values.

    Returns:
      tuple[dict[str, int], int]: integer values per name and number of bytes
          read.
    """
    values = {}

    data_offset = 0
    for name in names:
      integer_value, bytes_read = self._ReadVariableSizeInteger(
          data[data_offset:])

      data_offset += bytes_read

      values[name] = integer_value

    return values, data_offset

  def GetMetadataItemByIdentifier(self, identifier):
    """Retrieves a specific metadata item.

    Args:
      identifier (int): file (system) entry identifier of the metadata item.

    Returns:
      SpotlightStoreMetadataItem: metadata item matching the identifier or None
          if no such item.
    """
    return self._GetMetadataItemByIdentifier(self._file_object, identifier)

  def ReadFileObject(self, file_object):
    """Reads an Apple Spotlight database file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_header = self._ReadFileHeader(file_object)

    self._ReadMapPages(
        file_object, file_header.map_offset, file_header.map_size)

    self._ReadPropertyPages(
        file_object, file_header.metadata_types_block_number,
        self._metadata_types)

    self._ReadPropertyPages(
        file_object, file_header.metadata_values_block_number,
        self._metadata_values)

    self._ReadPropertyPages(
        file_object, file_header.unknown_values41_block_number, {})

    self._ReadPropertyPages(
        file_object, file_header.metadata_lists_block_number,
        self._metadata_lists)

    self._ReadPropertyPages(
        file_object, file_header.metadata_localized_strings_block_number,
        self._metadata_localized_strings)

    for map_value in self._map_values:
      file_offset = map_value.block_number * 0x1000
      _, page_data = self._ReadRecordPage(file_object, file_offset)

      # TODO: remove page from cache if full.
      self._record_pages_cache[file_offset] = page_data

      self._ReadRecordPageValues(page_data, file_offset)

    if self._debug:
      for record_identifier in sorted(self._record_descriptors.keys()):
        metadata_item = self._GetMetadataItemByIdentifier(
            file_object, record_identifier)
      # TODO: do something with metadata_item or remove.
      _ = metadata_item
