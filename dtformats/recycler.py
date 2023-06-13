# -*- coding: utf-8 -*-
"""Windows Recycler INFO2 files."""

from dtformats import data_format
from dtformats import errors


class RecyclerInfo2File(data_format.BinaryDataFile):
  """Windows Recycler INFO2 file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('recycler.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'recycler.debug.yaml', custom_format_callbacks={
          'ansi_string': '_FormatANSIString',
          'filetime': '_FormatIntegerAsFiletime'})

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
          f'Unable to decode ANSI string with error: {exception!s}.')

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
          f'Unable to map file entry data at offset: 0x{file_offset:08x} with '
          f'error: {exception!s}'))

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get(
          'recycler_info2_file_entry', None)
      self._DebugPrintStructureObject(file_entry, debug_info)

    if self._file_entry_data_size > 280:
      file_offset += 280

      data_type_map = self._GetDataTypeMap(
          'recycler_info2_file_entry_utf16le_string')

      try:
        original_filename = self._ReadStructureFromByteStream(
            file_entry_data[280:], file_offset, data_type_map, 'file entry')
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            f'Unable to map file entry data at offset: 0x{file_offset:08x} '
            f'with error: {exception!s}'))

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
      debug_info = self._DEBUG_INFORMATION.get(
          'recycler_info2_file_entry', None)
      self._DebugPrintStructureObject(file_header, debug_info)

    if file_header.file_entry_size not in (280, 800):
      raise errors.ParseError(
          f'Unsupported file entry size: {file_header.file_entry_size:d}')

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
