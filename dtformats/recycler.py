# -*- coding: utf-8 -*-
"""Windows Recycler INFO2 files."""

from __future__ import unicode_literals

from dtformats import data_format
from dtformats import errors


class RecyclerInfo2File(data_format.BinaryDataFile):
  """Windows Recycler INFO2 file."""

  _DEFINITION_FILE = 'recycler.yaml'

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Windows Recycler INFO2 file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(RecyclerInfo2File, self).__init__(
        debug=debug, output_writer=output_writer)
    self._file_entry_size = 0

  def _DebugPrintFileEntry(self, file_entry):
    """Prints file entry debug information.

    Args:
      file_entry (rp_log_file_entry): file entry.
    """
    # TODO: debug print ANSI original filename.

    value_string = '{0:d}'.format(file_entry.index)
    self._DebugPrintValue('Index', value_string)

    value_string = '{0:d}'.format(file_entry.drive_number)
    self._DebugPrintValue('Drive number', value_string)

    self._DebugPrintFiletimeValue('Deletion time', file_entry.deletion_time)

    value_string = '{0:d}'.format(file_entry.original_file_size)
    self._DebugPrintValue('Original file size', value_string)

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (rp_log_file_header): file header.
    """
    value_string = '0x{0:08x}'.format(file_header.unknown1)
    self._DebugPrintValue('Unknown1', value_string)

    value_string = '{0:d}'.format(file_header.number_of_file_entries)
    self._DebugPrintValue('Number of file entries', value_string)

    value_string = '0x{0:08x}'.format(file_header.unknown2)
    self._DebugPrintValue('Unknown2', value_string)

    value_string = '{0:d}'.format(file_header.file_entry_size)
    self._DebugPrintValue('File entry size', value_string)

    value_string = '0x{0:08x}'.format(file_header.unknown3)
    self._DebugPrintValue('Unknown3', value_string)

    self._DebugPrintText('\n')

  def _ReadFileEntry(self, file_object):
    """Reads the file entry.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file entry cannot be read.
    """
    file_offset = file_object.tell()

    file_entry_data = self._ReadData(
        file_object, file_offset, self._file_entry_size, 'file entry')

    data_type_map = self._GetDataTypeMap('recycler_info2_file_entry')

    try:
      file_entry = self._ReadStructureFromByteStream(
          file_entry_data, file_offset, data_type_map, 'file entry')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map file entry data at offset: 0x{0:08x} with error: '
          '{1!s}').format(file_offset, exception))

    if self._debug:
      self._DebugPrintFileEntry(file_entry)

    if self._file_entry_size > 280:
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
        self._DebugPrintValue('Original filename', original_filename)

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
      self._DebugPrintFileHeader(file_header)

    if file_header.file_entry_size not in (280, 800):
      raise errors.ParseError('Unsupported file entry size: {0:d}'.format(
          file_header.file_entry_size))

    self._file_entry_size = file_header.file_entry_size

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

      file_offset += self._file_entry_size
