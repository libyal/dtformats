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

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Windows Restore Point rp.log file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(RestorePointLogFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self.entries = []
    self.volume_path = None

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (rp_log_file_header): file header.
    """
    value_string = '0x{0:08x}'.format(file_header.event_type)
    self._DebugPrintValue('Event type', value_string)

    value_string = '0x{0:08x}'.format(file_header.restore_point_type)
    self._DebugPrintValue('Restore point type', value_string)

    value_string = '0x{0:08x}'.format(file_header.sequence_number)
    self._DebugPrintValue('Sequence number', value_string)

    self._DebugPrintValue('Description', file_header.description)

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()
    file_header = self._ReadStructureWithSizeHint(
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
