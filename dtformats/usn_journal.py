# -*- coding: utf-8 -*-
"""USN change journal records."""

import os

from dtformats import data_format


class USNRecords(data_format.BinaryDataFile):
  """USN change journal records."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('usn_journal.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'usn_journal.debug.yaml', custom_format_callbacks={
          'filetime': '_FormatIntegerAsFiletime'})

  _EMPTY_USN_RECORD_HEADER = bytes([0] * 60)

  def _ReadRecordV2(self, file_object):
    """Reads a version 2 USN record.

    Args:
      file_object (file): file-like object.

    Returns:
      tuple[usn_record_v2, int]: USN record and number of bytes read.

    Raises:
      ParseError: if the record cannot be read.
    """
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('usn_record_v2')

    usn_record, data_size = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'USN record (version 2)')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('usn_record_v2', None)
      self._DebugPrintStructureObject(usn_record, debug_info)

    return usn_record, data_size

  def ReadFileObject(self, file_object):
    """Reads a file-like object containing USN change journal records.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._file_object = file_object

  def ReadRecords(self):
    """Reads USN change journal records.

    Yields:
      usn_record_v2: USN record.

    Raises:
      ParseError: if a record cannot be read.
    """
    self._file_object.seek(0, os.SEEK_SET)

    file_offset = 0
    while file_offset < self._file_size:
      block_size = min(4096, self._file_size)

      while block_size > 60:
        usn_record_header = self._file_object.read(60)
        if usn_record_header == self._EMPTY_USN_RECORD_HEADER:
          break

        self._file_object.seek(-60, os.SEEK_CUR)
        usn_record, data_size = self._ReadRecordV2(self._file_object)
        yield usn_record

        file_offset += data_size
        block_size -= data_size

      file_offset += block_size
