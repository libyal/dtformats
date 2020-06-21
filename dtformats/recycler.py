# -*- coding: utf-8 -*-
"""Windows Recycler INFO2 files."""

from __future__ import unicode_literals

from dtformats import data_format
from dtformats import errors


class RecyclerInfo2File(data_format.BinaryDataFile):
  """Windows Recycler INFO2 file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('recycler.yaml')

  _DEBUG_INFO_FILE_ENTRY = [
      ('original_filename', 'Original filename (ANSI)', '_FormatANSIString'),
      ('index', 'Index', '_FormatIntegerAsDecimal'),
      ('drive_number', 'Drive number', '_FormatIntegerAsDecimal'),
      ('deletion_time', 'Deletion time', '_FormatIntegerAsFiletime'),
      ('original_file_size', 'Original file size', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_FILE_HEADER = [
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8'),
      ('number_of_file_entries', 'Number of file entries',
       '_FormatIntegerAsDecimal'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal8'),
      ('file_entry_size', 'File entry size', '_FormatIntegerAsDecimal'),
      ('unknown3', 'Unknown3', '_FormatIntegerAsHexadecimal8')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Windows Recycler INFO2 file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(RecyclerInfo2File, self).__init__(
        debug=debug, output_writer=output_writer)
    self._codepage = 'cp1252'
    self._file_entry_data_size = 0

  def _FormatANSIString(self, string):
    """Formats an ANSI string.

    Args:
      string (str): string.

    Returns:
      str: formatted ANSI string.

    Raises:
      ParseError: if the string could not be decoded.
    """
    try:
      return string.decode(self._codepage)
    except UnicodeDecodeError as exception:
      raise errors.ParseError(
          'Unable to decode ANSI string with error: {0!s}.'.format(exception))

  def _ReadFileEntry(self, file_object):
    """Reads the file entry.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file entry cannot be read.
    """
    file_offset = file_object.tell()

    file_entry_data = self._ReadData(
        file_object, file_offset, self._file_entry_data_size, 'file entry')

    data_type_map = self._GetDataTypeMap('recycler_info2_file_entry')

    try:
      file_entry = self._ReadStructureFromByteStream(
          file_entry_data, file_offset, data_type_map, 'file entry')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map file entry data at offset: 0x{0:08x} with error: '
          '{1!s}').format(file_offset, exception))

    if self._debug:
      self._DebugPrintStructureObject(file_entry, self._DEBUG_INFO_FILE_ENTRY)

    if self._file_entry_data_size > 280:
      file_offset += 280

      data_type_map = self._GetDataTypeMap(
          'recycler_info2_file_entry_utf16le_string')

      try:
        original_filename = self._ReadStructureFromByteStream(
            file_entry_data[280:], file_offset, data_type_map, 'file entry')
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            'Unable to map file entry data at offset: 0x{0:08x} with error: '
            '{1!s}').format(file_offset, exception))

      if self._debug:
        self._DebugPrintValue('Original filename (Unicode)', original_filename)

    if self._debug:
      self._DebugPrintText('\n')

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('recycler_info2_file_header')

    file_header, _ = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'file header')

    if self._debug:
      self._DebugPrintStructureObject(file_header, self._DEBUG_INFO_FILE_HEADER)

    if file_header.file_entry_size not in (280, 800):
      raise errors.ParseError('Unsupported file entry size: {0:d}'.format(
          file_header.file_entry_size))

    self._file_entry_data_size = file_header.file_entry_size

  def ReadFileObject(self, file_object):
    """Reads a Windows Recycler INFO2 file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadFileHeader(file_object)

    file_offset = file_object.tell()

    while file_offset < self._file_size:
      self._ReadFileEntry(file_object)

      file_offset += self._file_entry_data_size
