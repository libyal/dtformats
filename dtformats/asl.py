# -*- coding: utf-8 -*-
"""Apple System Log (ASL) files."""

from __future__ import unicode_literals

from dtformats import data_format


class AppleSystemLogFile(data_format.BinaryDataFile):
  """Apple System Log (.asl) file."""

  _DEFINITION_FILE = 'asl.yaml'

  def _DebugPrintHeader(self, header):
    """Prints header debug information.

    Args:
      header (asl_header): header.
    """
    self._DebugPrintValue('Signature', header.signature)

    value_string = '{0:d}'.format(header.format_version)
    self._DebugPrintValue('Format version', value_string)

    value_string = '0x{0:08x}'.format(header.first_log_entry_offset)
    self._DebugPrintValue('First log entry offset', value_string)

    value_string = '{0:d}'.format(header.creation_time)
    self._DebugPrintValue('Creation time', value_string)

    value_string = '{0:d}'.format(header.cache_size)
    self._DebugPrintValue('Cache size', value_string)

    value_string = '0x{0:08x}'.format(header.last_log_entry_offset)
    self._DebugPrintValue('Last log entry offset', value_string)

    self._DebugPrintData('Unknown1', header.unknown1)

    self._DebugPrintText('\n')

  def _DebugPrintRecord(self, record):
    """Prints record debug information.

    Args:
      record (asl_record): record.
    """
    value_string = '0x{0:04x}'.format(record.unknown1)
    self._DebugPrintValue('Unknown1', value_string)

    value_string = '{0:d}'.format(record.record_data_size)
    self._DebugPrintValue('Record data size', value_string)

    value_string = '0x{0:08x}'.format(record.next_record_offset)
    self._DebugPrintValue('Next record offset', value_string)

    value_string = '0x{0:08x}'.format(record.message_identifier)
    self._DebugPrintValue('Message identifier', value_string)

    value_string = '{0:d}'.format(record.written_time)
    self._DebugPrintValue('Written time', value_string)

    value_string = '{0:d}'.format(record.written_time_nanoseconds)
    self._DebugPrintValue('Written time nanoseconds', value_string)

    value_string = '{0:d}'.format(record.alert_level)
    self._DebugPrintValue('Alert level', value_string)

    value_string = '0x{0:04x}'.format(record.flags)
    self._DebugPrintValue('Flags', value_string)

    value_string = '{0:d}'.format(record.process_identifier)
    self._DebugPrintValue('Process identifier (PID)', value_string)

    value_string = '{0:d}'.format(record.user_identifier)
    self._DebugPrintValue('User identifier (UID)', value_string)

    value_string = '{0:d}'.format(record.group_identifier)
    self._DebugPrintValue('Group identifier (GID)', value_string)

    value_string = '{0:d}'.format(record.real_user_identifier)
    self._DebugPrintValue('Real user identifier (UID)', value_string)

    value_string = '{0:d}'.format(record.real_group_identifier)
    self._DebugPrintValue('Real group identifier (GID)', value_string)

    value_string = '{0:d}'.format(record.reference_process_identifier)
    self._DebugPrintValue('Reference process identifier (PID)', value_string)

    value_string = '0x{0:08x}'.format(record.hostname_string_offset)
    self._DebugPrintValue('Hostname string offset', value_string)

    value_string = '0x{0:08x}'.format(record.sender_string_offset)
    self._DebugPrintValue('Sender string offset', value_string)

    value_string = '0x{0:08x}'.format(record.facility_string_offset)
    self._DebugPrintValue('Facility string offset', value_string)

    value_string = '0x{0:08x}'.format(record.message_string_offset)
    self._DebugPrintValue('Message string offset', value_string)

    self._DebugPrintText('\n')

  def _ReadHeader(self, file_object):
    """Reads the header.

    Args:
      file_object (file): file-like object.

    Returns:
      asl_header: header.
    """
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('asl_header')

    header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'header')

    if self._debug:
      self._DebugPrintHeader(header)

    return header

  def _ReadRecord(self, file_object, file_offset):
    """Reads the record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the record relative to the start of the file.

    Returns:
      asl_record: record.
    """
    data_type_map = self._GetDataTypeMap('asl_record')

    record, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'record')

    if self._debug:
      self._DebugPrintRecord(record)

    data = file_object.read(record.record_data_size - 100)

    if self._debug:
      self._DebugPrintData('Record data', data)

    return record

  def ReadFileObject(self, file_object):
    """Reads an Apple System Log file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    header = self._ReadHeader(file_object)
    file_offset = header.first_log_entry_offset

    while file_offset < self._file_size:
      record = self._ReadRecord(file_object, file_offset)

      file_offset = record.next_record_offset
