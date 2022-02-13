# -*- coding: utf-8 -*-
"""Windows Defender scan DetectionHistory files."""

from dtformats import data_format


class WindowsDefenderScanDetectionHistoryFile(data_format.BinaryDataFile):
  """Windows Defender scan DetectionHistory file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile(
      'detection_history.yaml')

  _DEBUG_INFO_HEADER = [
      ('unknown1', 'Unknown 1', '_FormatIntegerAsHexadecimal8'),
      ('unknown2', 'Unknown 2', '_FormatIntegerAsHexadecimal8'),
      ('unknown3', 'Unknown 3', '_FormatIntegerAsHexadecimal8')]

  _DEBUG_INFO_VALUE = [
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('data_type', 'Data type', '_FormatIntegerAsHexadecimal8'),
      ('data', 'Data', '_FormatDataInHexadecimal'),
      ('alignment_padding', 'Alignment padding', '_FormatDataInHexadecimal')]

  def _ReadHeader(self, file_object):
    """Reads the header.

    Args:
      file_object (file): file-like object.

    Returns:
      detection_history_header: header.

    Raises:
      IOError: if the header cannot be read.
    """
    file_offset = file_object.tell()

    data_type_map = self._GetDataTypeMap('detection_history_header')

    header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'header')

    if self._debug:
      self._DebugPrintStructureObject(header, self._DEBUG_INFO_HEADER)

    return header

  def _ReadValue(self, file_object):
    """Reads the value.

    Args:
      file_object (file): file-like object.

    Returns:
      detection_history_value: value.

    Raises:
      IOError: if the value cannot be read.
    """
    file_offset = file_object.tell()

    data_type_map = self._GetDataTypeMap('detection_history_value')

    value, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'value')

    if self._debug:
      self._DebugPrintStructureObject(value, self._DEBUG_INFO_VALUE)

    return value

  def ReadFileObject(self, file_object):
    """Reads a Windows Defender scan DetectionHistory file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadHeader(file_object)

    file_offset = file_object.tell()
    while file_offset < self._file_size:
      self._ReadValue(file_object)
      file_offset = file_object.tell()
