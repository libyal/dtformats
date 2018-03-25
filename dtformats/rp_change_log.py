# -*- coding: utf-8 -*-
"""Windows Restore Point change.log files."""

from __future__ import unicode_literals

import os

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import data_maps as dtfabric_data_maps
from dtfabric.runtime import fabric as dtfabric_fabric

from dtformats import data_format
from dtformats import errors


class ChangeLogEntry(object):
  """Windows Restore Point change log entry.

  Attributes:
    entry_type (int): entry type.
    entry_flags (int): entry flags.
    file_attribute_flags (int): file attribute flags.
    process_name (str): process name.
    sequence_number (int): sequence number.
  """

  def __init__(self):
    """Initializes a change log entry."""
    super(ChangeLogEntry, self).__init__()
    self.entry_type = None
    self.entry_flags = None
    self.file_attribute_flags = None
    self.process_name = None
    self.sequence_number = None


class RestorePointChangeLogFile(data_format.BinaryDataFile):
  """Windows Restore Point change.log file."""

  _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
      os.path.dirname(__file__), 'rp_change_log.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  # TODO: refactor rp_change_log_volume_path_record in more generic
  # string record

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _FILE_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'rp_change_log_file_header')

  _FILE_HEADER_SIZE = _FILE_HEADER.GetByteSize()

  _RECORD_SIGNATURE = 0xabcdef12

  _RECORD_TYPE = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'rp_change_log_record_type')

  _RECORD_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'rp_change_log_record_header')

  _RECORD_HEADER_SIZE = _RECORD_HEADER.GetByteSize()

  _CHANGE_LOG_ENTRY = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'rp_change_log_entry')

  _CHANGE_LOG_ENTRY_SIZE = _CHANGE_LOG_ENTRY.GetByteSize()

  _CHANGE_LOG_ENTRY2 = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'rp_change_log_entry2')

  _VOLUME_PATH_RECORD = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'rp_change_log_volume_path_record')

  _LOG_ENTRY_FLAGS = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'rp_change_log_entry_flags')

  _LOG_ENTRY_TYPES = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'rp_change_log_entry_types')

  _UINT32LE = _DATA_TYPE_FABRIC.CreateDataTypeMap('uint32le')

  _UTF16LE_STRING = _DATA_TYPE_FABRIC.CreateDataTypeMap('utf16le_string')

  # TODO: implement an item based lookup.
  LOG_ENTRY_FLAGS = {
      0x00000001: 'CHANGE_LOG_ENTRYFLAGS_TEMPPATH',
      0x00000002: 'CHANGE_LOG_ENTRYFLAGS_SECONDPATH',
      0x00000004: 'CHANGE_LOG_ENTRYFLAGS_ACLINFO',
      0x00000008: 'CHANGE_LOG_ENTRYFLAGS_DEBUGINFO',
      0x00000010: 'CHANGE_LOG_ENTRYFLAGS_SHORTNAME',
  }

  # TODO: implement an item based lookup.
  LOG_ENTRY_TYPES = {
      0x00000001: 'CHANGE_LOG_ENTRYTYPES_STREAMCHANGE',
      0x00000002: 'CHANGE_LOG_ENTRYTYPES_ACLCHANGE',
      0x00000004: 'CHANGE_LOG_ENTRYTYPES_ATTRCHANGE',
      0x00000008: 'CHANGE_LOG_ENTRYTYPES_STREAMOVERWRITE',
      0x00000010: 'CHANGE_LOG_ENTRYTYPES_FILEDELETE',
      0x00000020: 'CHANGE_LOG_ENTRYTYPES_FILECREATE',
      0x00000040: 'CHANGE_LOG_ENTRYTYPES_FILERENAME',
      0x00000080: 'CHANGE_LOG_ENTRYTYPES_DIRCREATE',
      0x00000100: 'CHANGE_LOG_ENTRYTYPES_DIRRENAME',
      0x00000200: 'CHANGE_LOG_ENTRYTYPES_DIRDELETE',
      0x00000400: 'CHANGE_LOG_ENTRYTYPES_MOUNTCREATE',
      0x00000800: 'CHANGE_LOG_ENTRYTYPES_MOUNTDELETE',
      0x00001000: 'CHANGE_LOG_ENTRYTYPES_VOLUMEERROR',
      0x00002000: 'CHANGE_LOG_ENTRYTYPES_STREAMCREATE',
      0x00010000: 'CHANGE_LOG_ENTRYTYPES_NOOPTIMIZE',
      0x00020000: 'CHANGE_LOG_ENTRYTYPES_ISDIR',
      0x00040000: 'CHANGE_LOG_ENTRYTYPES_ISNOTDIR',
      0x00080000: 'CHANGE_LOG_ENTRYTYPES_SIMULATEDELETE',
      0x00100000: 'CHANGE_LOG_ENTRYTYPES_INPRECREATE',
      0x00200000: 'CHANGE_LOG_ENTRYTYPES_OPENBYID',
  }

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Windows Restore Point change.log file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(RestorePointChangeLogFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self.entries = []
    self.volume_path = None

  def _DebugPrintChangeLogEntryRecord(self, change_log_entry_record):
    """Prints change log entry record debug information.

    Args:
      change_log_entry_record (rp_change_log_entry): change log entry record.
    """
    self._DebugPrintRecordHeader(change_log_entry_record)

    value_string = '0x{0:08x}'.format(change_log_entry_record.signature)
    self._DebugPrintValue('Signature', value_string)

    # TODO: implement an item based lookup.
    value_string = '0x{0:08x}'.format(change_log_entry_record.entry_type)
    self._DebugPrintValue('Entry type', value_string)

    for flag, description in self.LOG_ENTRY_TYPES.items():
      if change_log_entry_record.entry_type & flag:
        text = '\t{0:s}\n'.format(description)
        self._DebugPrintText(text)

    self._DebugPrintText('\n')

    # TODO: implement an item based lookup.
    value_string = '0x{0:08x}'.format(change_log_entry_record.entry_flags)
    self._DebugPrintValue('Entry flags', value_string)

    for flag, description in self.LOG_ENTRY_FLAGS.items():
      if change_log_entry_record.entry_flags & flag:
        text = '\t{0:s}\n'.format(description)
        self._DebugPrintText(text)

    self._DebugPrintText('\n')

    value_string = '0x{0:08x}'.format(
        change_log_entry_record.file_attribute_flags)
    self._DebugPrintValue('File attribute flags', value_string)

    # TODO: print flags.

    value_string = '{0:d}'.format(change_log_entry_record.sequence_number)
    self._DebugPrintValue('Sequence number', value_string)

    value_string = '{0:d}'.format(change_log_entry_record.process_name_size)
    self._DebugPrintValue('Process name size', value_string)

    value_string = '0x{0:08x}'.format(change_log_entry_record.unknown2)
    self._DebugPrintValue('Unknown2', value_string)

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (rp_change_log_file_header): file header.
    """
    self._DebugPrintRecordHeader(file_header)

    value_string = '0x{0:08x}'.format(file_header.signature)
    self._DebugPrintValue('Signature', value_string)

    value_string = '{0:d}'.format(file_header.format_version)
    self._DebugPrintValue('Format version', value_string)

  def _DebugPrintRecordHeader(self, record_header):
    """Prints record header debug information.

    Args:
      record_header (rp_change_log_record_header): record header.
    """
    value_string = '{0:d}'.format(record_header.record_size)
    self._DebugPrintValue('Record size', value_string)

    record_type_string = self._RECORD_TYPE.GetName(record_header.record_type)
    value_string = '{0:d} ({1:s})'.format(
        record_header.record_type, record_type_string or 'UNKNOWN')
    self._DebugPrintValue('Record type', value_string)

  def _ReadChangeLogEntries(self, file_object):
    """Reads the change log entries.

    Args:
      file_object (file): file-like object.
    """
    self.entries = []

    file_offset = file_object.tell()
    while file_offset < self._file_size:
      change_log_entry = self._ReadChangeLogEntry(file_object)
      file_offset = file_object.tell()

      self.entries.append(change_log_entry)

  def _ReadChangeLogEntry(self, file_object):
    """Reads a change log entry.

    Args:
      file_object (file): file-like object.

    Returns:
      ChangeLogEntry: a change log entry.

    Raises:
      ParseError: if the change log entry cannot be read.
    """
    file_offset = file_object.tell()
    change_log_entry_record = self._ReadStructure(
        file_object, file_offset, self._CHANGE_LOG_ENTRY_SIZE,
        self._CHANGE_LOG_ENTRY, 'change log entry record')

    if self._debug:
      self._DebugPrintChangeLogEntryRecord(change_log_entry_record)

    if change_log_entry_record.record_type != 1:
      raise errors.ParseError('Unsupported record type: {0:d}'.format(
          change_log_entry_record.record_type))

    signature = change_log_entry_record.signature
    if signature != self._RECORD_SIGNATURE:
      raise errors.ParseError('Unsupported change.log file signature')

    # TODO: refactor to use size hints
    record_size = (
        change_log_entry_record.record_size - self._CHANGE_LOG_ENTRY_SIZE)
    record_data = file_object.read(record_size)
    file_offset += self._CHANGE_LOG_ENTRY_SIZE

    if self._debug:
      self._DebugPrintData('Record data', record_data)

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'rp_change_log_entry': change_log_entry_record})

    try:
      change_log_entry_record2 = self._CHANGE_LOG_ENTRY2.MapByteStream(
          record_data, context=context)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError(
          'Unable to parse change log entry record with error: {0!s}'.format(
              exception))

    if self._debug:
      self._DebugPrintValue(
          'Process name', change_log_entry_record2.process_name[:-1])

      self._DebugPrintText('\n')

    change_log_entry = ChangeLogEntry()
    change_log_entry.entry_type = change_log_entry_record.entry_type
    change_log_entry.entry_flags = change_log_entry_record.entry_flags
    change_log_entry.file_attribute_flags = (
        change_log_entry_record.file_attribute_flags)
    change_log_entry.sequence_number = change_log_entry_record.sequence_number
    change_log_entry.process_name = change_log_entry_record2.process_name[:-1]

    sub_record_data_offset = context.byte_size
    sub_record_data_size = record_size - 4
    if self._debug:
      value_string = '{0:d}'.format(sub_record_data_offset)
      self._DebugPrintValue('Sub record data offset', value_string)

      value_string = '{0:d}'.format(
          sub_record_data_size - sub_record_data_offset)
      self._DebugPrintValue('Sub record data size', value_string)

      if sub_record_data_offset < sub_record_data_size:
        self._DebugPrintText('\n')

    while sub_record_data_offset < sub_record_data_size:
      read_size = self._ReadRecord(record_data, sub_record_data_offset)
      if read_size == 0:
        break
      sub_record_data_offset += read_size

    try:
      copy_of_record_size = self._UINT32LE.MapByteStream(record_data[-4:])
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError(
          'Unable to parse copy of record size with error: {0!s}'.format(
              exception))

    if change_log_entry_record.record_size != copy_of_record_size:
      raise errors.ParseError('Record size mismatch ({0:d} != {1:d})'.format(
          change_log_entry_record.record_size, copy_of_record_size))

    if self._debug:
      value_string = '{0:d}'.format(copy_of_record_size)
      self._DebugPrintValue('Copy of record size', value_string)

      self._DebugPrintText('\n')

    return change_log_entry

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()
    file_header = self._ReadStructure(
        file_object, file_offset, self._FILE_HEADER_SIZE, self._FILE_HEADER,
        'file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

    if file_header.signature != self._RECORD_SIGNATURE:
      raise errors.ParseError('Unsupported change.log file signature')

    if file_header.record_type != 0:
      raise errors.ParseError(
          'Unsupported record type: {0:d}'.format(file_header.record_type))

    if file_header.format_version != 2:
      raise errors.ParseError(
          'Unsupported change.log format version: {0:d}'.format(
              file_header.format_version))

    record_size = file_header.record_size - self._FILE_HEADER_SIZE
    record_data = file_object.read(record_size)
    file_offset += self._FILE_HEADER_SIZE

    if self._debug:
      self._DebugPrintData('Record data', record_data)

    self._ReadVolumePath(record_data[:-4])

    try:
      copy_of_record_size = self._UINT32LE.MapByteStream(record_data[-4:])
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError(
          'Unable to parse copy of record size with error: {0!s}'.format(
              exception))

    if self._debug:
      value_string = '{0:d}'.format(copy_of_record_size)
      self._DebugPrintValue('Copy of record size', value_string)

      self._DebugPrintText('\n')

    if file_header.record_size != copy_of_record_size:
      raise errors.ParseError('Record size mismatch ({0:d} != {1:d})'.format(
          file_header.record_size, copy_of_record_size))

  def _ReadRecord(self, record_data, record_data_offset):
    """Reads a record.

    Args:
      record_data (bytes): record data.
      record_data_offset (int): record data offset.

    Returns:
      int: record data size.

    Raises:
      ParseError: if the record cannot be read.
    """
    try:
      record_header = self._RECORD_HEADER.MapByteStream(
          record_data[record_data_offset:])
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError(
          'Unable to parse record header with error: {0!s}'.format(
              exception))

    if self._debug:
      self._DebugPrintData('Record data', record_data[
          record_data_offset:record_data_offset + record_header.record_size])

    if self._debug:
      self._DebugPrintRecordHeader(record_header)

    record_data_offset += self._RECORD_HEADER_SIZE

    value_string = ''
    if record_header.record_type in (4, 5, 9):
      try:
        value_string = self._UTF16LE_STRING.MapByteStream(
            record_data[record_data_offset:])
      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError(
            'Unable to parse UTF-16 string with error: {0!s}'.format(
                exception))

    # TODO: add support for other record types.
    # TODO: store record values in runtime objects.

    if self._debug:
      description = None
      if record_header.record_type == 4:
        description = 'Secondary path'
      elif record_header.record_type == 5:
        description = 'Backup filename'
      elif record_header.record_type == 9:
        description = 'Short filename'

      if description:
        self._DebugPrintValue(description, value_string)

      self._DebugPrintText('\n')

    return record_header.record_size

  def _ReadVolumePath(self, record_data):
    """Reads the volume path.

    Args:
      record_data (bytes): record data.

    Raises:
      ParseError: if the volume path cannot be read.
    """
    try:
      volume_path_record = self._VOLUME_PATH_RECORD.MapByteStream(record_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError(
          'Unable to parse volume path record with error: {0!s}'.format(
              exception))

    if self._debug:
      self._DebugPrintRecordHeader(volume_path_record)

      self._DebugPrintValue('Volume path', volume_path_record.volume_path[:-1])

      self._DebugPrintText('\n')

    if volume_path_record.record_type != 2:
      raise errors.ParseError('Unsupported record type: {0:d}'.format(
          volume_path_record.record_type))

  def ReadFileObject(self, file_object):
    """Reads a Windows Restore Point change.log file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadFileHeader(file_object)
    self._ReadChangeLogEntries(file_object)
