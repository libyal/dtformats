# -*- coding: utf-8 -*-
"""Windows Restore Point rp.log files."""

from __future__ import unicode_literals

import os

from dtfabric.runtime import fabric as dtfabric_fabric

from dtformats import data_format


class RestorePointLogFile(data_format.BinaryDataFile):
  """Windows Restore Point rp.log file."""

  _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
      os.path.dirname(__file__), 'rp_log.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _FILE_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'rp_log_file_header')

  _FILE_FOOTER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'rp_log_file_footer')

  _FILE_FOOTER_SIZE = _FILE_FOOTER.GetByteSize()

  # TODO: implement an item based lookup.
  _EVENT_TYPES = {
      0x00000064: 'BEGIN_SYSTEM_CHANGE',
      0x00000065: 'END_SYSTEM_CHANGE',
      0x00000066: 'BEGIN_NESTED_SYSTEM_CHANGE',
      0x00000067: 'END_NESTED_SYSTEM_CHANGE',
  }

  # TODO: implement an item based lookup.
  _RESTORE_POINT_TYPES = {
      0x00000000: 'APPLICATION_INSTALL',
      0x00000001: 'APPLICATION_UNINSTALL',
      0x0000000a: 'DEVICE_DRIVER_INSTALL',
      0x0000000c: 'MODIFY_SETTINGS',
      0x0000000d: 'CANCELLED_OPERATION',
  }

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Windows Restore Point rp.log file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(RestorePointLogFile, self).__init__(
        debug=debug, output_writer=output_writer)

  def _DebugPrintFileFooter(self, file_footer):
    """Prints file footer debug information.

    Args:
      file_footer (rp_log_file_footer): file footer.
    """
    self._DebugPrintFiletimeValue('Creation time', file_footer.creation_time)

    self._DebugPrintText('\n')

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (rp_log_file_header): file header.
    """
    event_type_string = self._EVENT_TYPES.get(
        file_header.event_type, 'UNKNOWN')
    value_string = '0x{0:08x} ({1:s})'.format(
        file_header.event_type, event_type_string)
    self._DebugPrintValue('Event type', value_string)

    restore_point_type_string = self._RESTORE_POINT_TYPES.get(
        file_header.restore_point_type, 'UNKNOWN')
    value_string = '0x{0:08x} ({1:s})'.format(
        file_header.restore_point_type, restore_point_type_string)
    self._DebugPrintValue('Restore point type', value_string)

    value_string = '0x{0:08x}'.format(file_header.sequence_number)
    self._DebugPrintValue('Sequence number', value_string)

    self._DebugPrintValue('Description', file_header.description)

    self._DebugPrintText('\n')

  def _ReadFileFooter(self, file_object):
    """Reads the file footer.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    file_offset = self._file_size - 8
    file_footer = self._ReadStructure(
        file_object, file_offset, self._FILE_FOOTER_SIZE, self._FILE_FOOTER,
        'file footer')

    if self._debug:
      self._DebugPrintFileFooter(file_footer)

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()
    file_header, _ = self._ReadStructureWithSizeHint(
        file_object, file_offset, self._FILE_HEADER, 'file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

  def ReadFileObject(self, file_object):
    """Reads a Windows Restore Point rp.log file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadFileHeader(file_object)

    data_size = (self._file_size - 8) - file_object.tell()
    data = file_object.read(data_size)
    self._DebugPrintData('Unknown1', data)

    self._ReadFileFooter(file_object)
