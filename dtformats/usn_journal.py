# -*- coding: utf-8 -*-
"""USN change journal records."""

from dtformats import data_format


class USNRecords(data_format.BinaryDataFile):
  """USN change journal records."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('usn_journal.yaml')

  _DEBUG_INFO_RECORD_V2 = [
      ('size', 'Size', '_FormatIntegerAsDecimal'),
      ('major_version', 'Major version', '_FormatIntegerAsDecimal'),
      ('minor_version', 'Manor version', '_FormatIntegerAsDecimal'),
      ('file_reference', 'File reference', '_FormatIntegerAsHexadecimal8'),
      ('parent_file_reference', 'Parent file reference',
       '_FormatIntegerAsHexadecimal8'),
      ('timestamp', 'Timestamp', '_FormatIntegerAsFiletime'),
      ('update_reason_flags', 'Update reason flags',
       '_FormatIntegerAsHexadecimal8'),
      ('update_reason_flags', 'Update reason flags',
       '_FormatIntegerAsHexadecimal8'),
      ('update_source_flags', 'Update source flags',
       '_FormatIntegerAsHexadecimal8'),
      ('security_descriptor_entry', 'Security descriptor entry',
       '_FormatIntegerAsDecimal'),
      ('file_attribute_flags', 'File attribute flags',
       '_FormatIntegerAsHexadecimal8'),
      ('name_size', 'Name size', '_FormatIntegerAsDecimal'),
      ('name_offset', 'Name offset', '_FormatIntegerAsDecimal'),
      ('name', 'Name', '_FormatString')]

  def _ReadRecordV2(self, file_object):
    """Reads a version 2 USN record.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the record cannot be read.
    """
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('usn_record_v2')

    usn_record, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'USN record (version 2)')

    if self._debug:
      self._DebugPrintStructureObject(usn_record, self._DEBUG_INFO_RECORD_V2)

  def ReadFileObject(self, file_object):
    """Reads a file-like object containing USN change journal records.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_offset = 0
    while file_offset < self._file_size:
      self._ReadRecordV2(file_object)

      file_offset = file_object.tell()
