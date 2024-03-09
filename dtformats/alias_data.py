# -*- coding: utf-8 -*-
"""Mac OS com.apple.loginitems.plist Alias data."""

from dfdatetime import hfs_time as dfdatetime_hfs_time

from dtformats import data_format
from dtformats import errors


class MacOSLoginItemAliasData(data_format.BinaryDataFile):
  """Mac OS com.apple.loginitems.plist Alias data."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('alias_data.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'alias_data.debug.yaml', custom_format_callbacks={
          'array_of_decimals': '_FormatArrayOfIntegersAsDecimals',
          'hfs_time': '_FormatIntegerAsHFSTime',
          'hfs_time_64bit': '_FormatIntegerAsHFSTime64bit'})

  def __init__(self, debug=False, output_writer=None):
    """Initializes Mac OS com.apple.loginitems.plist Alias data.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(MacOSLoginItemAliasData, self).__init__(
        debug=debug, output_writer=output_writer)

  def _FormatIntegerAsHFSTime64bit(self, integer):
    """Formats an integer as a HFS date and time value.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a HFS date and time value.
    """
    if integer == 0:
      return 'Not set (0)'

    number_of_seconds, fraction_of_second = divmod(integer, 65536)

    date_time = dfdatetime_hfs_time.HFSTime(timestamp=number_of_seconds)
    date_time_string = date_time.CopyToDateTimeString()
    if not date_time_string:
      return f'0x{integer:08x}'

    return f'{date_time_string:s}.{fraction_of_second:03d} UTC'

  def _ReadRecordHeader(self, file_object, file_offset):
    """Reads a record header.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the record header relative to the start of
          the file.

    Returns:
      alias_data_record_header: record header.

    Raises:
      ParseError: if the record header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('alias_data_record_header')

    record_header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'record header')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('alias_data_record_header', None)
      self._DebugPrintStructureObject(record_header, debug_info)

    if record_header.application_information != b'\x00\x00\x00\x00':
      raise errors.ParseError('Unsupported application information')

    return record_header

  def _ReadRecordV2(self, file_object, file_offset):
    """Reads a version 2 record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the record data relative to the start of the
          file.

    Returns:
      alias_data_record_v2: record.

    Raises:
      ParseError: if the record cannot be read.
    """
    data_type_map = self._GetDataTypeMap('alias_data_record_v2')

    record, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'record data')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('alias_data_record_v2', None)
      self._DebugPrintStructureObject(record, debug_info)

    return record

  def _ReadRecordV3(self, file_object, file_offset):
    """Reads a version 3 record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the record data relative to the start of the
          file.

    Returns:
      alias_data_record_v3: record.

    Raises:
      ParseError: if the record cannot be read.
    """
    data_type_map = self._GetDataTypeMap('alias_data_record_v3')

    record, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'record data')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('alias_data_record_v3', None)
      self._DebugPrintStructureObject(record, debug_info)

    return record

  def _ReadTaggedValue(self, file_object, file_offset):
    """Reads a tagged value.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the tagged value relative to the start of the
          file.

    Returns:
      tuple[alias_data_tagged_value, int]: tagged value and the number of bytes
          read.

    Raises:
      ParseError: if the tagged value cannot be read.
    """
    data_type_map = self._GetDataTypeMap('alias_data_tagged_value')

    tagged_value, bytes_read = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'tagged value')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('alias_data_tagged_value', None)
      self._DebugPrintStructureObject(tagged_value, debug_info)

    return tagged_value, bytes_read

  def ReadFileObject(self, file_object):
    """Reads a Mac OS com.apple.loginitems.plist Alias data file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    record_header = self._ReadRecordHeader(file_object, 0)

    record_offset = 8

    if record_header.record_size != self._file_size:
      raise errors.ParseError('Unsupported alias data record size')

    if record_header.format_version == 2:
      _ = self._ReadRecordV2(file_object, record_offset)
      record_offset += 142

    elif record_header.format_version == 3:
      _ = self._ReadRecordV3(file_object, record_offset)
      record_offset += 50

    while record_offset < record_header.record_size:
      _, bytes_read = self._ReadTaggedValue(file_object, record_offset)

      record_offset += bytes_read
