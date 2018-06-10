# -*- coding: utf-8 -*-
"""Windows Recycler INFO2 files."""

from __future__ import unicode_literals

from dtformats import data_format
from dtformats import errors


class RecyclerInfo2File(data_format.BinaryDataFile):
  """Windows Recycler INFO2 file.

  Attributes:
    deletion_time (int): FILETIME timestamp of the date and time the original
        file was deleted.
    original_filename (str): original name of the deleted file.
    original_size (int): original size of the deleted file.
  """

  _DEFINITION_FILE = 'recycler.yaml'

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Windows Recycler INFO2 file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(RecyclerInfo2File, self).__init__(
        debug=debug, output_writer=output_writer)
    self.deletion_time = None
    self.original_filename = None
    self.original_file_size = None

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

    self._DebugPrintValue('Original filename', file_entry.original_filename)

    self._DebugPrintText('\n')

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
    data_type_map = self._GetDataTypeMap('recycler_info2_file_entry')

    file_entry, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file entry')

    if self._debug:
      self._DebugPrintFileEntry(file_entry)

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

    if file_header.file_entry_size != 800:
      raise errors.ParseError('Unsupported file entry size: {0:d}'.format(
          file_header.file_entry_size))

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

      file_offset = file_object.tell()
