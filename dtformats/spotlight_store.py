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


class AppleSpotlightStoreDatabaseFile(data_format.BinaryDataFile):
  """Apple Spotlight store database file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile(
      'spotlight_store.yaml')

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
      ('page_content_type', 'Page content type',
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

        metadata_type_index = property_value.table_index
        metadata_type = self._metadata_types.get(metadata_type_index, None)
        value_string = getattr(metadata_type, 'key_name', '')
        self._DebugPrintValue(
            'Key: {0:d}'.format(metadata_type_index), value_string)

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

  def _ReadPropertyPage(self, file_object, file_offset, property_table):
    """Reads a property page.

    Args:
      file_object (file): file-like object.
      file_offset (int): file offset.
      property_table (dict[int, object]): property table in which to store the
          property page values.

    Returns:
      spotlight_store_db_property_page_header: page header.

    Raises:
      ParseError: if the property page cannot be read.
    """
    data_type_map = self._GetDataTypeMap(
        'spotlight_store_db_property_page_header')

    page_header, page_header_size = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'property page header')

    if self._debug:
      self._DebugPrintStructureObject(
          page_header, self._DEBUG_INFO_PROPERTY_PAGE_HEADER)

    if self._debug:
      self._DebugPrintDecimalValue('Block number', int(file_offset / 0x1000))
      self._DebugPrintDecimalValue(
          'Page number', int(file_offset / page_header.page_size))

    page_data = file_object.read(page_header.page_size - page_header_size)

    file_offset += page_header_size

    next_block_number = 0
    if page_header.page_content_type in (
        0x00000011, 0x00000021, 0x00000041, 0x00000081):
      data_type_map = self._GetDataTypeMap(
          'spotlight_store_db_property_values_header')

      page_values_header = self._ReadStructureFromByteStream(
          page_data, file_offset, data_type_map, 'property values header')

      if self._debug:
        self._DebugPrintStructureObject(
            page_values_header, self._DEBUG_INFO_PROPERTY_VALUES_HEADER)

      next_block_number = page_values_header.next_block_number

    if page_header.page_content_type == 0x00000009:
      self._ReadRecordPageValues(page_header, page_data, property_table)

    elif page_header.page_content_type in (0x00000011, 0x00000021):
      self._ReadPropertyPageValues(page_header, page_data, property_table)

    elif page_header.page_content_type == 0x00000081:
      self._ReadIndexPageValues(page_header, page_data, property_table)

    elif self._debug:
      self._DebugPrintData('Page data', page_data)

    return page_header, next_block_number

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

    while file_offset < self._file_size:
      _, next_block_number = self._ReadPropertyPage(
          file_object, file_offset, property_table)

      if next_block_number == 0:
        break

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
    if page_header.page_content_type == 0x00000011:
      data_type_map = self._GetDataTypeMap(
          'spotlight_store_db_property_value11')

    elif page_header.page_content_type == 0x00000021:
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

        if page_header.page_content_type == 0x00000011:
          debug_info = self._DEBUG_INFO_PROPERTY_VALUE11
        elif page_header.page_content_type == 0x00000021:
          debug_info = self._DEBUG_INFO_PROPERTY_VALUE21

        self._DebugPrintStructureObject(property_value, debug_info)

      property_table[property_value.table_index] = property_value

      page_data_offset += context.byte_size
      page_value_index += 1

  def _ReadRecordPageValues(self, page_header, page_data, property_table):
    """Reads the record page values.

    Args:
      page_header (spotlight_store_db_property_page_header): page header.
      page_data (bytes): page data.
      property_table (dict[int, object]): property table in which to store the
          property page values.

    Raises:
      ParseError: if the property page values cannot be read.
    """
    data_type_map = self._GetDataTypeMap('spotlight_store_db_record')

    if page_header.uncompressed_page_size > 0:
      page_data = zlib.decompress(page_data)

    page_value_index = 0
    page_data_offset = 0
    page_data_size = len(page_data)

    while page_data_offset < page_data_size:
      context = dtfabric_data_maps.DataTypeMapContext()

      try:
        record = data_type_map.MapByteStream(
            page_data[page_data_offset:], context=context)
      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError((
            'Unable to map record at offset: 0x{0:08x} with error: '
            '{1!s}').format(page_data_offset, exception))

      if self._debug:
        self._DebugPrintText('Record at offset: 0x{0:08x}\n'.format(
            page_data_offset + 20))
        self._DebugPrintData(
            'Page value: {0:d} data'.format(page_value_index),
            page_data[page_data_offset:page_data_offset + record.data_size])

      page_value_offset = page_data_offset + context.byte_size

      identifier, bytes_read = self._ReadVariableSizeInteger(
          page_data[page_value_offset:])

      page_value_offset += bytes_read
      record_data_offset = bytes_read

      flags = page_data[page_value_offset]

      page_value_offset += 1
      record_data_offset += 1

      value_names = ['item_identifier', 'parent_identifier', 'updated_time']
      values, bytes_read = self._ReadVariableSizeIntegers(
          page_data[page_value_offset:], value_names)

      page_value_offset += bytes_read
      record_data_offset += bytes_read

      if self._debug:
        self._DebugPrintDecimalValue('Data size', record.data_size)
        self._DebugPrintDecimalValue('Identifier', identifier)

        value_string = self._FormatIntegerAsHexadecimal2(flags)
        self._DebugPrintValue('Flags', value_string)

        self._DebugPrintDecimalValue(
            'Item identifier', values.get('item_identifier'))
        self._DebugPrintDecimalValue(
            'Parent identifier', values.get('parent_identifier'))
        self._DebugPrintPosixTimeValue(
            'Updated time', values.get('updated_time'))
        self._DebugPrintText('\n')

      metadata_attribute_index = 0
      metadata_type_index = 0

      while record_data_offset < record.data_size:
        if self._debug:
          value_string = self._FormatIntegerAsHexadecimal8(
              record_data_offset + 4)
          self._DebugPrintValue('Record data offset', value_string)

        relative_metadata_type_index, bytes_read = (
            self._ReadVariableSizeInteger(page_data[page_value_offset:]))

        page_value_offset += bytes_read
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
        _, bytes_read = self._ReadMetadataAttributeValue(
            metadata_type, page_data[page_value_offset:])

        page_value_offset += bytes_read
        record_data_offset += bytes_read

        if self._debug:
          self._DebugPrintText('\n')

        metadata_attribute_index += 1

      page_data_offset += context.byte_size + record.data_size
      page_value_index += 1

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
      raise errors.ParseError((
          'Unable to parse array of string values with error: {0!s}').format(
              exception))

    if property_type & 0x02 == 0x00:
      value = array_of_values[0]
    else:
      value = array_of_values

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

  def _ReadMetadataAttributeValue(self, metadata_type, data):
    """Reads a metadata attribute value.

    Args:
      metadata_type (spotlight_store_db_property_value11): metadata type
          property value.
      data (bytes): data.

    Returns:
      tuple[object, int]: value and number of bytes read.
    """
    property_type = getattr(metadata_type, 'property_type', None)
    value_type = getattr(metadata_type, 'value_type', None)
    if value_type is None:
      return None, 0

    if self._debug:
      key_name = getattr(metadata_type, 'key_name', '')
      self._DebugPrintValue('Key name', key_name)

      value_string = self._FormatIntegerAsHexadecimal2(property_type or 0)
      self._DebugPrintValue('Property type', value_string)

      value_string = self._FormatIntegerAsHexadecimal2(value_type or 0)
      self._DebugPrintValue('Value type', value_string)

    if value_type in (0x00, 0x02, 0x06):
      value, bytes_read = self._ReadVariableSizeInteger(data)

    elif value_type == 0x07:
      value, bytes_read = self._ReadMetadataAttributeVariableSizeIntegerValue(
          property_type, data)

    elif value_type == 0x08:
      if property_type & 0x02 == 0x00:
        value, bytes_read = 1, 0
      else:
        value, bytes_read = self._ReadVariableSizeInteger(data)

      if self._debug and bytes_read != 0:
        self._DebugPrintDecimalValue('Binary data size', value)

      if self._debug:
        self._DebugPrintData(
            'Binary data', data[bytes_read:bytes_read + value])

      # TODO: handle as array of bytes?

      bytes_read += value

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
      value, bytes_read = self._ReadVariableSizeInteger(data)

      if self._debug:
        self._DebugPrintDecimalValue('Binary data size', value)
        self._DebugPrintData(
            'Binary data', data[bytes_read:bytes_read + value])

      # TODO: decode binary data

      bytes_read += value

    elif value_type == 0x0f:
      value, bytes_read = self._ReadVariableSizeInteger(data)

      if property_type & 0x03 == 0x03:
        metadata_localized_strings = self._metadata_localized_strings.get(
            value, None)
        value_list = getattr(metadata_localized_strings, 'values_list', [])

        value_string = '(null)'
        if value_list:
          value_string = value_list[0]
          if '\x16\x02' in value_string:
            value_string = value_string.split('\x16\x02')[0]

        if self._debug:
          description = 'Metadata localized strings: {0:d}'.format(value)
          self._DebugPrintValue(description, value_string)

        value = value_string

      elif property_type & 0x03 == 0x02:
        metadata_list = self._metadata_lists.get(value, None)
        value_list = getattr(metadata_list, 'values_list', [])

        if self._debug:
          description = 'Metadata list: {0:d}'.format(value)
          value_string = '{0!s}'.format(value_list)
          self._DebugPrintValue(description, value_string)

        value = value_list

      else:
        metadata_value = self._metadata_values.get(value, None)
        value_name = getattr(metadata_value, 'value_name', '(null)')

        if self._debug:
          description = 'Metadata value: {0:d}'.format(value)
          self._DebugPrintValue(description, value_name)

        value = value_name

    else:
      value, bytes_read = None, 0

    if self._debug:
      if value_type == 0x00:
        self._DebugPrintDecimalValue('Integer', value)
        value_string = '{0!s}'.format(bool(value))
        self._DebugPrintValue('Boolean', value_string)

      elif value_type in (0x02, 0x06):
        value_string = self._FormatIntegerAsHexadecimal8(value)
        self._DebugPrintValue('Integer', value_string)

      elif value_type == 0x07:
        if property_type & 0x02 == 0x00:
          self._DebugPrintDecimalValue('Integer', value)
        else:
          for array_index, array_value in enumerate(value):
            description = 'Integer: {0:d}'.format(array_index)
            self._DebugPrintDecimalValue(description, array_value)

      elif value_type == 0x08:
        pass

      elif value_type in (0x09, 0x0a):
        if property_type & 0x02 == 0x00:
          value_string = self._FormatFloatingPoint(value)
          self._DebugPrintValue('Floating-point', value_string)
        else:
          for array_index, array_value in enumerate(value):
            description = 'Floating-point: {0:d}'.format(array_index)
            value_string = self._FormatFloatingPoint(array_value)
            self._DebugPrintValue(description, value_string)

      elif value_type == 0x0b:
        if property_type & 0x02 == 0x00:
          self._DebugPrintValue('String', value)
        else:
          for array_index, array_value in enumerate(value):
            description = 'String: {0:d}'.format(array_index)
            self._DebugPrintValue(description, array_value)

      elif value_type == 0x0c:
        if property_type & 0x02 == 0x00:
          if value < 7500000000.0:
            self._DebugPrintCocoaTimeValue('Date and time', value)
          else:
            value_string = self._FormatFloatingPoint(value)
            self._DebugPrintValue('Floating-point', value_string)

        else:
          for array_index, array_value in enumerate(value):
            if array_value < 7500000000.0:
              description = 'Date and time: {0:d}'.format(array_index)
              self._DebugPrintCocoaTimeValue(description, array_value)
            else:
              description = 'Floating-point: {0:d}'.format(array_index)
              value_string = self._FormatFloatingPoint(array_value)
              self._DebugPrintValue(description, value_string)

    return value, bytes_read

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
      self._ReadPropertyPage(file_object, file_offset, {})
