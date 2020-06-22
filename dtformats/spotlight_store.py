# -*- coding: utf-8 -*-
"""Apple Spotlight store database files."""

from __future__ import unicode_literals

import zlib

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
      ('metadata_keys_block_number', 'Metadata keys block number',
       '_FormatIntegerAsDecimal'),
      ('metadata_values_block_number', 'Metadata values block number',
       '_FormatIntegerAsDecimal'),
      ('attribute_table_block_number3', 'Attribute table block number 3',
       '_FormatIntegerAsDecimal'),
      ('attribute_table_block_number4', 'Attribute table block number 4',
       '_FormatIntegerAsDecimal'),
      ('attribute_table_block_number5', 'Attribute table block number 5',
       '_FormatIntegerAsDecimal'),
      ('unknown8', 'Unknown8', '_FormatDataInHexadecimal'),
      ('path', 'Path', '_FormatString')]

  _DEBUG_INFO_MAP_PAGE_HEADER = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('page_size', 'Page size', '_FormatIntegerAsDecimal'),
      ('number_of_map_values', 'Number of map values',
       '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8'),
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
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal4'),
      ('key_name', 'Key name', '_FormatString')]

  _DEBUG_INFO_PROPERTY_VALUE21 = [
      ('table_index', 'Table index', '_FormatIntegerAsDecimal'),
      ('value_name', 'Value name', '_FormatString')]

  _VARIABLE_INTEGER_ADDITIONAL_BYTES = {
      0x80: 1,
      0xc0: 2,
      0xe0: 3,
      0xf0: 4,
      0xf8: 5,
      0xfc: 6,
      0xfe: 7,
      0xff: 8}

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

  def _ReadIndexPageValues(self, page_header, page_data):
    """Reads the index page values.

    Args:
      page_header (spotlight_store_db_property_page_header): page header.
      page_data (bytes): page data.

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

      index_size, byte_size = self._ReadVariableSizeInteger(
          page_data[page_data_offset + page_value_size:])

      page_value_size += byte_size

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

      if self._debug:
        self._DebugPrintDecimalValue('Table index', property_value.table_index)
        self._DebugPrintDecimalValue('Index size', index_size)

        value_string = self._FormatArrayOfIntegersAsDecimals(index_values)
        self._DebugPrintValue('Index values', value_string)
        self._DebugPrintText('\n')

      page_data_offset += page_value_size

      page_value_index += 1

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
      data_type_map = self._GetDataTypeMap('spotlight_store_db_map_page_header')

      page_header, page_header_size = self._ReadStructureFromFileObject(
          file_object, map_offset, data_type_map, 'map page header')

      if self._debug:
        self._DebugPrintStructureObject(
            page_header, self._DEBUG_INFO_MAP_PAGE_HEADER)

      if self._debug:
        page_data = file_object.read(page_header.page_size - page_header_size)
        self._DebugPrintData('Page data', page_data)

      map_offset += page_header.page_size

  def _ReadPropertyPage(self, file_object, file_offset):
    """Reads a property page.

    Args:
      file_object (file): file-like object.
      file_offset (int): file offset.

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
      self._DebugPrintDecimalValue(
          'Page number', int(file_offset / page_header.page_size))

    page_data = file_object.read(page_header.page_size - page_header_size)
    if page_header.uncompressed_page_size > 0:
      page_data = zlib.decompress(page_data[:-page_header_size])

    file_offset += page_header_size

    data_type_map = self._GetDataTypeMap(
        'spotlight_store_db_property_values_header')

    page_values_header = self._ReadStructureFromByteStream(
        page_data, file_offset, data_type_map, 'property values header')

    if self._debug:
      self._DebugPrintStructureObject(
          page_values_header, self._DEBUG_INFO_PROPERTY_VALUES_HEADER)

    if page_header.page_content_type in (0x00000011, 0x00000021):
      self._ReadPropertyPageValues(page_header, page_data)
    elif page_header.page_content_type == 0x00000081:
      self._ReadIndexPageValues(page_header, page_data)
    elif self._debug:
      self._DebugPrintData('Page data', page_data[12:])

    return page_header, page_values_header.next_block_number

  def _ReadPropertyPages(self, file_object, block_number):
    """Reads the property pages.

    Args:
      file_object (file): file-like object.
      block_number (int): block number.

    Raises:
      ParseError: if the property pages cannot be read.
    """
    file_offset = block_number * 0x1000

    while file_offset < self._file_size:
      _, next_block_number = self._ReadPropertyPage(file_object, file_offset)

      if next_block_number == 0:
        break

      file_offset = next_block_number * 0x1000

  def _ReadPropertyPageValues(self, page_header, page_data):
    """Reads the property page values.

    Args:
      page_header (spotlight_store_db_property_page_header): page header.
      page_data (bytes): page data.

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

      page_data_offset += context.byte_size
      page_value_index += 1

  def _ReadVariableSizeInteger(self, page_data):
    """Reads a variable size integer.

    Args:
      page_data (bytes): page data.

    Returns:
      tuple[int, int]: integer value and number of bytes read.
    """
    byte_value = page_data[0]
    bytes_read = 1

    upper_nibble = byte_value & 0xf0
    if upper_nibble == 0xf0:
      number_of_additional_bytes = (
          self._VARIABLE_INTEGER_ADDITIONAL_BYTES.get(byte_value, 4))
    else:
      number_of_additional_bytes = (
          self._VARIABLE_INTEGER_ADDITIONAL_BYTES.get(upper_nibble, 0))

    if number_of_additional_bytes > 4:
      byte_value = 0
    elif number_of_additional_bytes > 0:
      byte_value &= 0x0f

    integer_value = int(byte_value)
    while number_of_additional_bytes > 0:
      integer_value <<= 8

      integer_value += int(page_data[bytes_read])
      bytes_read += 1

      number_of_additional_bytes -= 1

    if self._debug:
      self._DebugPrintData('Variable integer data', page_data[:bytes_read])
      self._DebugPrintDecimalValue('Integer value', integer_value)

    return integer_value, bytes_read

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
        file_object, file_header.metadata_keys_block_number)

    self._ReadPropertyPages(
        file_object, file_header.metadata_values_block_number)

    self._ReadPropertyPages(
        file_object, file_header.attribute_table_block_number3)

    self._ReadPropertyPages(
        file_object, file_header.attribute_table_block_number4)

    self._ReadPropertyPages(
        file_object, file_header.attribute_table_block_number5)
