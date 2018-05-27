# -*- coding: utf-8 -*-
"""Windows Recycle.Bin metadata ($I) files."""

from __future__ import unicode_literals

import os

from dtfabric.runtime import fabric as dtfabric_fabric

from dtformats import data_format
from dtformats import errors


class RecycleBinMetadataFile(data_format.BinaryDataFile):
  """Windows Recycle.Bin metadata ($I) file.

  Attributes:
    deletion_time (int): FILETIME timestamp of the date and time the original
        file was deleted.
    format_version (int): format version of the metadata file.
    original_filename (str): original name of the deleted file.
    original_size (int): original size of the deleted file.
  """

  _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
      os.path.dirname(__file__), 'recycle_bin.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _FILE_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'recycle_bin_metadata_file_header')

  _FILE_HEADER_SIZE = _FILE_HEADER.GetByteSize()

  _UTF16LE_STRING = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'utf16le_string')

  _UTF16LE_STRING_WITH_SIZE = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'utf16le_string_with_size')

  _SUPPORTED_FORMAT_VERSION = (1, 2)

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Windows Restore Point rp.log file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(RecycleBinMetadataFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self.deletion_time = None
    self.format_version = None
    self.original_filename = None
    self.original_file_size = None

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (rp_log_file_header): file header.
    """
    value_string = '{0:d}'.format(file_header.format_version)
    self._DebugPrintValue('Format version', value_string)

    value_string = '{0:d}'.format(file_header.original_file_size)
    self._DebugPrintValue('Original file size', value_string)

    self._DebugPrintFiletimeValue('Deletion time', file_header.deletion_time)

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Returns:
      recycle_bin_metadata_file_header: file header.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()
    file_header = self._ReadStructure(
        file_object, file_offset, self._FILE_HEADER_SIZE, self._FILE_HEADER,
        'file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

    if file_header.format_version not in self._SUPPORTED_FORMAT_VERSION:
      raise errors.ParseError('Unsupported format version: {0:d}'.format(
          file_header.format_version))

    return file_header

  def _ReadOriginalFilename(self, file_object, format_version):
    """Reads the original filename.

    Args:
      file_object (file): file-like object.
      format_version (int): format version.

    Returns:
      str: filename or None on error.

    Raises:
      ParseError: if the original filename cannot be read.
    """
    file_offset = file_object.tell()

    if format_version == 1:
      data_map = self._UTF16LE_STRING
      data_map_description = 'UTF-16 little-endian string'
    else:
      data_map = self._UTF16LE_STRING_WITH_SIZE
      data_map_description = 'UTF-16 little-endian string with size'

    try:
      original_filename, _ = self._ReadStructureWithSizeHint(
          file_object, file_offset, data_map, data_map_description)
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          'Unable to parse original filename with error: {0!s}'.format(
              exception))

    if format_version == 1:
      return original_filename.rstrip('\x00')

    return original_filename.string.rstrip('\x00')

  def ReadFileObject(self, file_object):
    """Reads a Windows Restore Point rp.log file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_header = self._ReadFileHeader(file_object)

    self.format_version = file_header.format_version
    self.deletion_time = file_header.deletion_time
    self.original_file_size = file_header.original_file_size

    self.original_filename = self._ReadOriginalFilename(
        file_object, file_header.format_version)

    if self._debug:
      self._DebugPrintValue('Original filename', self.original_filename)

      self._DebugPrintText('\n')
