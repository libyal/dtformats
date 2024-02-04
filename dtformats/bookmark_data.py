# -*- coding: utf-8 -*-
"""Mac OS backgrounditems.btm bookmark data."""

from dtformats import data_format
from dtformats import errors


class MacOSBackgroundItemBookmarkData(data_format.BinaryDataFile):
  """Mac OS backgrounditems.btm bookmark data."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('bookmark_data.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'bookmark_data.debug.yaml', custom_format_callbacks={
          'array_of_decimals': '_FormatArrayOfIntegersAsDecimals',
          'array_of_tagged_values': '_FormatArrayOfTaggedValues',
          'signature': '_FormatStreamAsString'})

  def __init__(self, debug=False, output_writer=None):
    """Initializes Mac OS backgrounditems.btm bookmark data.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(MacOSBackgroundItemBookmarkData, self).__init__(
        debug=debug, output_writer=output_writer)

  def _FormatArrayOfTaggedValues(self, array):
    """Formats an array of tagged values.

    Args:
      array (list[bookmark_data_tagged_value]): array of tagged values.

    Returns:
      str: formatted array of tagged values.
    """
    value = '\n'.join([
        (f'\ttag: 0x{entry.value_tag:04x}, '
         f'data record offset: 0x{entry.value_data_record_offset:08x}, '
         f'unknown1: 0x{entry.unknown1:08x}')
        for entry in array])
    return f'{value:s}\n'

  def _ReadDataRecord(self, file_object, file_offset):
    """Reads a data record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data record relative to the start of the
          file.

    Returns:
      bookmark_data_record: data record.

    Raises:
      ParseError: if the data record cannot be read.
    """
    data_type_map = self._GetDataTypeMap('bookmark_data_record')

    data_record, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'data record')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('bookmark_data_record', None)
      self._DebugPrintStructureObject(data_record, debug_info)

    return data_record

  def _ReadHeader(self, file_object, file_offset):
    """Reads a header.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the header relative to the start of the file.

    Returns:
      bookmark_data_header: header.

    Raises:
      ParseError: if the header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('bookmark_data_header')

    header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'header')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('bookmark_data_header', None)
      self._DebugPrintStructureObject(header, debug_info)

    return header

  def _ReadIntegersArray(
      self, file_object, data_area_offset, data_record_offsets):
    """Reads an integers array.

    Args:
      file_object (file): file-like object.
      data_area_offset (int): offset of the data area relative to the start of
          the file.
      data_record_offsets (list[int]): offsets of the entry data records.

    Returns:
      list[str]: integers.
    """
    integers_array = []

    for data_record_offset in data_record_offsets:
      data_record = self._ReadDataRecord(
          file_object, data_area_offset + data_record_offset)

      integers_array.append(data_record.integer)

    return integers_array

  def _ReadStringsArray(
      self, file_object, data_area_offset, data_record_offsets):
    """Reads a strings array.

    Args:
      file_object (file): file-like object.
      data_area_offset (int): offset of the data area relative to the start of
          the file.
      data_record_offsets (list[int]): offsets of the entry data records.

    Returns:
      list[str]: strings.
    """
    strings_array = []

    for data_record_offset in data_record_offsets:
      data_record = self._ReadDataRecord(
          file_object, data_area_offset + data_record_offset)

      strings_array.append(data_record.string)

    return strings_array

  def _ReadTableOfContents(self, file_object, file_offset):
    """Reads a table of contents (TOC).

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the table of contents (TOC) relative to the
          start of the file.

    Returns:
      bookmark_data_toc: table of contents (TOC).

    Raises:
      ParseError: if the table of contents (TOC) cannot be read.
    """
    data_type_map = self._GetDataTypeMap('bookmark_data_toc')

    table_of_contents, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'table of contents (TOC)')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('bookmark_data_toc', None)
      self._DebugPrintStructureObject(table_of_contents, debug_info)

    if table_of_contents.next_toc_offset != 0:
      raise errors.ParseError('Unsupported next TOC offset')

    return table_of_contents

  def ReadFileObject(self, file_object):
    """Reads a Mac OS backgrounditems.btm bookmark data file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    header = self._ReadHeader(file_object, 0)

    if header.size != self._file_size:
      raise errors.ParseError('Unsupported bookmark data size')

    if header.data_area_offset != 48:
      raise errors.ParseError('Unsupported bookmark data area offset')

    data_type_map = self._GetDataTypeMap('uint32le')

    data_area_size, _ = self._ReadStructureFromFileObject(
        file_object, header.data_area_offset, data_type_map, 'data area size')

    if self._debug:
      value_string, _ = self._FormatIntegerAsDecimal(data_area_size)
      self._DebugPrintValue('Data area size', value_string)

      self._DebugPrintText('\n')

    table_of_contents = self._ReadTableOfContents(
        file_object, header.data_area_offset + data_area_size)

    for tagged_value in table_of_contents.tagged_values:
      if self._debug:
        value_string, _ = self._FormatIntegerAsHexadecimal4(
            tagged_value.value_tag)
        self._DebugPrintValue('Value tag', value_string)

      data_record_offset = (
          header.data_area_offset + tagged_value.value_data_record_offset)
      data_record = self._ReadDataRecord(file_object, data_record_offset)

      if data_record.data_type == 0x00000400:
        # TODO: change dtFabric to support setting float64be directly in struct
        data_type_map = self._GetDataTypeMap('float64be')
        cocoa_timestamp = self._ReadStructureFromByteStream(
            data_record.data, 0, data_type_map, 'Floating-point 64-bit')

        if self._debug:
          value_string, _ = self._FormatFloatingPoint(cocoa_timestamp)
          self._DebugPrintValue('Cocoa timestamp', value_string)

          self._DebugPrintText('\n')

      elif tagged_value.value_tag == 0x1004:
        strings_array = self._ReadStringsArray(
            file_object, header.data_area_offset, data_record.integers)

        if self._debug:
          value_string = '/'.join(strings_array)
          self._DebugPrintValue('Path', value_string)

          self._DebugPrintText('\n')

      elif tagged_value.value_tag == 0x1005:
        integers_array = self._ReadIntegersArray(
            file_object, header.data_area_offset, data_record.integers)

        if self._debug:
          value_string, _ = self._FormatArrayOfIntegersAsDecimals(
              integers_array)
          self._DebugPrintValue('Integers array', value_string)

          self._DebugPrintText('\n')

      elif tagged_value.value_tag in (0x1010, 0x2020):
        data_type_map = self._GetDataTypeMap('bookmark_data_property_flags')
        property_flags = self._ReadStructureFromByteStream(
            data_record.data, 0, data_type_map, 'Property flags')

        if self._debug:
          debug_info = self._DEBUG_INFORMATION.get(
              'bookmark_data_property_flags', None)
          self._DebugPrintStructureObject(property_flags, debug_info)
