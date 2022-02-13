# -*- coding: utf-8 -*-
"""Windows Defender scan DetectionHistory files."""

from dtformats import data_format


class WindowsDefenderScanDetectionHistoryFile(data_format.BinaryDataFile):
  """Windows Defender scan DetectionHistory file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile(
      'detection_history.yaml')

  _DEBUG_INFO_VALUE = [
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('data_type', 'Data type', '_FormatIntegerAsHexadecimal8'),
      ('data', 'Data', '_FormatDataInHexadecimal'),
      ('value_filetime', 'Value FILETIME', '_FormatIntegerAsFiletime'),
      ('value_guid', 'Value GUID', '_FormatUUIDAsString'),
      ('value_integer', 'Value integer', '_FormatIntegerAsDecimal'),
      ('value_string', 'Value string', '_FormatString'),
      ('alignment_padding', 'Alignment padding', '_FormatDataInHexadecimal')]

  def _ReadValue(self, file_object, file_offset):
    """Reads the value.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the value relative to the start of the file.

    Returns:
      detection_history_value: value.

    Raises:
      IOError: if the value cannot be read.
    """
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
    file_offset = 0
    while file_offset < self._file_size:
      self._ReadValue(file_object, file_offset)
      file_offset = file_object.tell()
