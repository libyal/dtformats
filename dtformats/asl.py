# -*- coding: utf-8 -*-
"""Apple System Log (ASL) files."""

from dtformats import data_format
from dtformats import errors


class AppleSystemLogFile(data_format.BinaryDataFile):
  """Apple System Log (.asl) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('asl.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'asl.debug.yaml', custom_format_callbacks={
          'posix_time': '_FormatIntegerAsPosixTime',
          'record_flags': '_FormatRecordFlags',
          'signature': '_FormatStreamAsString'})

  # Most significant bit of a 64-bit string offset.
  _STRING_OFFSET_MSB = 1 << 63

  def _FormatRecordFlags(self, integer):
    """Formats record flags.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as record flags.
    """
    return f'0x{integer:04x}'

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Returns:
      asl_file_header: file header.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('asl_file_header')

    file_header, _ = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'file header')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('asl_file_header', None)
      self._DebugPrintStructureObject(file_header, debug_info)

    return file_header

  def _ReadRecord(self, file_object, file_offset):
    """Reads a record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the record relative to the start of the file.

    Returns:
      int: next record offset.

    Raises:
      ParseError: if the record cannot be read.
    """
    record_strings_data_offset = file_object.tell()
    record_strings_data_size = file_offset - record_strings_data_offset

    record_strings_data = self._ReadData(
        file_object, record_strings_data_offset, record_strings_data_size,
        'record strings data')

    if self._debug:
      self._DebugPrintData('Record strings data', record_strings_data)

    data_type_map = self._GetDataTypeMap('asl_record')

    record, record_data_size = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'record')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('asl_record', None)
      self._DebugPrintStructureObject(record, debug_info)

    hostname = self._ReadRecordString(
        file_object, record.hostname_string_offset)

    sender = self._ReadRecordString(
        file_object, record.sender_string_offset)

    facility = self._ReadRecordString(
        file_object, record.facility_string_offset)

    message = self._ReadRecordString(
        file_object, record.message_string_offset)

    file_offset += record_data_size
    additional_data_size = record.data_size + 6 - record_data_size

    if additional_data_size % 8 != 0:
      raise errors.ParseError('Invalid record additional data size.')

    additional_data = self._ReadData(
        file_object, file_offset, additional_data_size,
        'record additional data')

    if self._debug:
      self._DebugPrintData('Record additional data', additional_data)

    extra_fields = {}
    for additional_data_offset in range(0, additional_data_size - 8, 16):
      record_extra_field = self._ReadRecordExtraField(
          additional_data[additional_data_offset:], file_offset)

      file_offset += 16

      name = self._ReadRecordString(
          file_object, record_extra_field.name_string_offset)

      value = self._ReadRecordString(
          file_object, record_extra_field.value_string_offset)

      if name is not None:
        extra_fields[name] = value

    if self._debug:
      self._DebugPrintValue('Hostname', hostname)
      self._DebugPrintValue('Sender', sender)
      self._DebugPrintValue('Facility', facility)
      self._DebugPrintValue('Message', message)

      for name, value in extra_fields.items():
        self._DebugPrintValue(name, value)

      self._DebugPrintText('\n')

    # TODO: implement print previous record offset

    return record.next_record_offset

  def _ReadRecordExtraField(self, byte_stream, file_offset):
    """Reads a record extra field.

    Args:
      byte_stream (bytes): byte stream.
      file_offset (int): offset of the record extra field relative to
          the start of the file.

    Returns:
      asl_record_extra_field: record extra field.

    Raises:
      ParseError: if the record extra field cannot be read.
    """
    data_type_map = self._GetDataTypeMap('asl_record_extra_field')

    try:
      record_extra_field = self._ReadStructureFromByteStream(
          byte_stream, file_offset, data_type_map, 'record extra field')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          f'Unable to parse record extra field at offset: 0x{file_offset:08x} '
          f'with error: {exception!s}'))

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('asl_record_extra_field', None)
      self._DebugPrintStructureObject(record_extra_field, debug_info)

    return record_extra_field

  def _ReadRecordString(self, file_object, string_offset):
    """Reads a record string.

    Args:
      file_object (file): file-like object.
      string_offset (int): offset of the string relative to the start of
          the file.

    Returns:
      str: record string or None if string offset is 0.

    Raises:
      ParseError: if the record string cannot be read.
    """
    if string_offset == 0:
      return None

    if string_offset & self._STRING_OFFSET_MSB:
      flag_value = string_offset >> 60
      if self._debug:
        self._DebugPrintValue('Inline string flag', f'0x{flag_value:01x}')

      if flag_value != 8:
        raise errors.ParseError('Invalid inline record string flag.')

      string_size = (string_offset >> 56) & 0x0f
      if string_size >= 8:
        raise errors.ParseError('Invalid inline record string size.')

      string_data = bytes(bytearray([
          string_offset >> (8 * byte_index) & 0xff
          for byte_index in range(6, -1, -1)]))

      try:
        string = string_data[:string_size].decode('utf-8')
      except UnicodeDecodeError as exception:
        raise errors.ParseError(
            f'Unable to decode inline record string with error: {exception!s}.')

      if self._debug:
        self._DebugPrintDecimalValue('Inline string size', string_size)

        self._DebugPrintValue('Inline string', string)

        self._DebugPrintText('\n')

      return string

    data_type_map = self._GetDataTypeMap('asl_record_string')

    try:
      record_string, _ = self._ReadStructureFromFileObject(
          file_object, string_offset, data_type_map, 'record string')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          f'Unable to parse record string at offset: 0x{string_offset:08x} '
          f'with error: {exception!s}'))

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('asl_record_string', None)
      self._DebugPrintStructureObject(record_string, debug_info)

    return record_string.string.rstrip('\x00')

  def ReadFileObject(self, file_object):
    """Reads an Apple System Log file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_header = self._ReadFileHeader(file_object)

    if file_header.first_log_entry_offset > 0:
      file_offset = file_header.first_log_entry_offset
      while file_offset < self._file_size:
        file_offset = self._ReadRecord(file_object, file_offset)
        if file_offset == 0:
          break
