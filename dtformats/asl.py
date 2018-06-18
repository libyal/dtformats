# -*- coding: utf-8 -*-
"""Apple System Log (ASL) files."""

from __future__ import unicode_literals

from dtformats import data_format
from dtformats import errors


class AppleSystemLogFile(data_format.BinaryDataFile):
  """Apple System Log (.asl) file."""

  _DEFINITION_FILE = 'asl.yaml'

  _FILE_SIGNATURE = b'ASL DB\x00\x00\x00\x00\x00\x00'

  # Most significant bit of a 64-bit string offset.
  _STRING_OFFSET_MSB = 1 << 63

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (asl_file_header): file header.
    """
    value_string = file_header.signature.replace(b'\x00', b'\\x00')
    self._DebugPrintValue('Signature', value_string)

    self._DebugPrintDecimalValue('Format version', file_header.format_version)

    value_string = '0x{0:08x}'.format(file_header.first_log_entry_offset)
    self._DebugPrintValue('First log entry offset', value_string)

    self._DebugPrintPosixTimeValue('Creation time', file_header.creation_time)

    self._DebugPrintDecimalValue('Cache size', file_header.cache_size)

    value_string = '0x{0:08x}'.format(file_header.last_log_entry_offset)
    self._DebugPrintValue('Last log entry offset', value_string)

    self._DebugPrintData('Unknown1', file_header.unknown1)

    self._DebugPrintText('\n')

  def _DebugPrintRecord(self, record):
    """Prints record debug information.

    Args:
      record (asl_record): record.
    """
    value_string = '0x{0:04x}'.format(record.unknown1)
    self._DebugPrintValue('Unknown1', value_string)

    self._DebugPrintDecimalValue('Data size', record.data_size)

    value_string = '0x{0:08x}'.format(record.next_record_offset)
    self._DebugPrintValue('Next record offset', value_string)

    value_string = '0x{0:08x}'.format(record.message_identifier)
    self._DebugPrintValue('Message identifier', value_string)

    value_string = '{0:d}'.format(record.written_time)
    self._DebugPrintValue('Written time', value_string)

    value_string = '{0:d}'.format(record.written_time_nanoseconds)
    self._DebugPrintValue('Written time nanoseconds', value_string)

    self._DebugPrintDecimalValue('Alert level', record.alert_level)

    value_string = '0x{0:04x}'.format(record.flags)
    self._DebugPrintValue('Flags', value_string)

    self._DebugPrintDecimalValue(
        'Process identifier (PID)', record.process_identifier)

    self._DebugPrintDecimalValue(
        'User identifier (UID)', record.user_identifier)

    self._DebugPrintDecimalValue(
        'Group identifier (GID)', record.group_identifier)

    self._DebugPrintDecimalValue(
        'Real user identifier (UID)', record.real_user_identifier)

    self._DebugPrintDecimalValue(
        'Real group identifier (GID)', record.real_group_identifier)

    self._DebugPrintDecimalValue(
        'Reference process identifier (PID)',
        record.reference_process_identifier)

    value_string = '0x{0:08x}'.format(record.hostname_string_offset)
    self._DebugPrintValue('Hostname string offset', value_string)

    value_string = '0x{0:08x}'.format(record.sender_string_offset)
    self._DebugPrintValue('Sender string offset', value_string)

    value_string = '0x{0:08x}'.format(record.facility_string_offset)
    self._DebugPrintValue('Facility string offset', value_string)

    value_string = '0x{0:08x}'.format(record.message_string_offset)
    self._DebugPrintValue('Message string offset', value_string)

    self._DebugPrintText('\n')

  def _DebugPrintRecordExtraField(self, record_extra_field):
    """Prints record extra field debug information.

    Args:
      record_extra_field (asl_record_extra_field): record extra field.
    """
    value_string = '0x{0:08x}'.format(record_extra_field.name_string_offset)
    self._DebugPrintValue('Name string offset', value_string)

    value_string = '0x{0:08x}'.format(record_extra_field.value_string_offset)
    self._DebugPrintValue('Value string offset', value_string)

    self._DebugPrintText('\n')

  def _DebugPrintRecordString(self, record_string):
    """Prints record string debug information.

    Args:
      record_string (asl_record_string): record string.
    """
    value_string = '0x{0:04x}'.format(record_string.unknown1)
    self._DebugPrintValue('Unknown1', value_string)

    self._DebugPrintDecimalValue('String size', record_string.string_size)

    self._DebugPrintValue('String', record_string.string.rstrip('\x00'))

    self._DebugPrintText('\n')

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Returns:
      asl_file_header: file header.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('asl_file_header')

    file_header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

    if file_header.signature != self._FILE_SIGNATURE:
      raise errors.ParseError('Invalid file signature.')

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
      self._DebugPrintRecord(record)

    hostname = self._ReadRecordString(
        record_strings_data, record_strings_data_offset,
        record.hostname_string_offset)

    sender = self._ReadRecordString(
        record_strings_data, record_strings_data_offset,
        record.sender_string_offset)

    facility = self._ReadRecordString(
        record_strings_data, record_strings_data_offset,
        record.facility_string_offset)

    message = self._ReadRecordString(
        record_strings_data, record_strings_data_offset,
        record.message_string_offset)

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
          record_strings_data, record_strings_data_offset,
          record_extra_field.name_string_offset)

      value = self._ReadRecordString(
          record_strings_data, record_strings_data_offset,
          record_extra_field.value_string_offset)

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
          'Unable to parse record extra field at offset: 0x{0:08x} with error: '
          '{1!s}').format(file_offset, exception))

    if self._debug:
      self._DebugPrintRecordExtraField(record_extra_field)

    return record_extra_field

  def _ReadRecordString(
      self, record_strings_data, record_strings_data_offset, string_offset):
    """Reads a record string.

    Args:
      record_strings_data (bytes): record strings data.
      record_strings_data_offset (int): offset of the record strings data
          relative to the start of the file.
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
      if self._debug:
        value_string = '0x{0:01x}'.format(string_offset >> 60)
        self._DebugPrintValue('Inline string flag', value_string)

      if (string_offset >> 60) != 8:
        raise errors.ParseError('Invalid inline record string flag.')

      string_size = (string_offset >> 56) & 0x0f
      if string_size >= 8:
        raise errors.ParseError('Invalid inline record string size.')

      string_data = bytes(bytearray([
          string_offset >> (8 * byte_index) & 0xff
          for byte_index in range(6, 0, -1)]))

      try:
        string = string_data[:string_size].decode('utf-8')
      except UnicodeDecodeError as exception:
        raise errors.ParseError(
            'Unable to decode inline record string with error: {0!s}.'.format(
                exception))

      if self._debug:
        self._DebugPrintDecimalValue('Inline string size', string_size)

        self._DebugPrintValue('Inline string', string)

        self._DebugPrintText('\n')

      return string

    data_offset = string_offset - record_strings_data_offset
    data_type_map = self._GetDataTypeMap('asl_record_string')

    try:
      record_string = self._ReadStructureFromByteStream(
          record_strings_data[data_offset:], string_offset, data_type_map,
          'record string')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to parse record string at offset: 0x{0:08x} with error: '
          '{1!s}').format(string_offset, exception))

    if self._debug:
      self._DebugPrintRecordString(record_string)

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
