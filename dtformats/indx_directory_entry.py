# -*- coding: utf-8 -*-
"""INDX entries """

import os

from dtformats import data_format
from dtformats.errors import ParseError

class INDXRecord(data_format.BinaryDataFile):
  """ Class that represents an INDX record.

  Note: currently only supports $I30 index records
  """

  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile(
    'indx_directory_entry.yml')

  _DEBUG_INDX_ENTRY_HEADER = [
    ('signature', 'signature', ''),
    ('fixup_value_offset', 'fixup_value_offset', '_FormatIntegerAsDecimal'),
    ('num_fixup_values', 'num_fixup_values', '_FormatIntegerAsDecimal'),
    ('logfile_sequence_number', 'logfile_sequence_number',
     '_FormatIntegerAsDecimal'),
    ('virtual_cluster_number', 'virtual_cluster_number',
     '_FormatIntegerAsDecimal')]

  _DEBUG_INDX_NODE_HEADER = [
    ('index_values_offset', 'index_values_offset',
     '_FormatIntegerAsDecimal'),
    ('index_node_size', 'index_node_size', '_FormatIntegerAsDecimal'),
    ('allocated_index_node_size', 'allocated_index_node_size',
     '_FormatIntegerAsDecimal'),
    ('index_node_flags', 'index_node_flags', '_FormatIntegerAsDecimal')]

  _DEBUG_INDX_DIR_RECORD = [
      ('file_reference', 'file_reference', '_FormatIntegerAsDecimal'),
      ('index_value_size', 'index_value_size', '_FormatIntegerAsDecimal'),
      ('index_key_data_size', 'index_key_data_size', '_FormatIntegerAsDecimal'),
      ('index_value_flags', 'index_value_flags', '_FormatIntegerAsDecimal')]

  _DEBUG_FILE_NAME_ATTR = [
      ('parent_file_reference', 'parent_file_reference',
       '_FormatIntegerAsDecimal'),
      ('creation_time', 'creation_time', '_FormatIntegerAsDecimal'),
      ('modification_time', 'modification_time', '_FormatIntegerAsDecimal'),
      ('entry_modification_time', 'entry_modification_time',
       '_FormatIntegerAsDecimal'),
      ('access_time', 'access_time', '_FormatIntegerAsDecimal'),
      ('allocated_file_size', 'allocated_file_size', '_FormatIntegerAsDecimal'),
      ('file_size', 'file_size', '_FormatIntegerAsDecimal'),
      ('file_attribute_flags', 'file_attribute_flags',
       '_FormatIntegerAsDecimal'),
      ('extended_data', 'extended_data', '_FormatIntegerAsDecimal'),
      ('name_size', 'name_size', '_FormatIntegerAsDecimal'),
      ('name_space', 'name_space', '_FormatIntegerAsDecimal'),
      ('filename', 'filename', '_FormatString')]

  def PrintRecord(self, record):
    """
    Prints a human readable version of the INDX record
    to STDOUT.

    Args:
        record (index_dir_entry): An index_dir_entry structure.
    """
    if record is not None:
      if self._debug:
        self._DebugPrintStructureObject(
          record.entry_header, self._DEBUG_INDX_ENTRY_HEADER)
        self._DebugPrintStructureObject(
          record.node_header, self._DEBUG_INDX_NODE_HEADER)
        self._DebugPrintStructureObject(
          record, self._DEBUG_INDX_DIR_RECORD)
        self._DebugPrintStructureObject(
          record.index_key_data, self._DEBUG_FILE_NAME_ATTR)


  def _ParseIndexEntryHeader(self, file_object):
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('index_entry_header')

    indx_record, data_size = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'INDX Entry Header')
    return indx_record, data_size


  def _ParseIndexNodeHeader(self, file_object):
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('index_node_header')

    indx_record, data_size = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'INDX Node Header')
    return indx_record, data_size


  def _ParseIndexDirectoryEntry(self, file_object):
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('index_dir_entry')

    try:
      indx_record, data_size = self._ReadStructureFromFileObject(
          file_object, file_offset, data_type_map,
          '4KB block with possible INDX Directory Entry')
      return indx_record, data_size
    except ParseError as e:
      if self._debug:
        print(e)
      return None, None


  def ReadFileObject(self, file_object):
    """Reads a file-like object containing INDX records.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._file_object = file_object

  def ReadRecords(self):
    """
    Reads INDX records.

    Yields:
      index_dir_entry: An $I30 INDX record.

    Raises:
      ParseError: if a record cannot be read.
    """
    self._file_object.seek(0, os.SEEK_SET)
    file_offset = 0

    # INDX entries allocated in 4096-byte chunks
    block_size = 4096

    while file_offset < self._file_size:
      self._file_object.seek(file_offset, os.SEEK_SET)
      index_dir_entry, _ = self._ParseIndexDirectoryEntry(self._file_object)
      if index_dir_entry:
        yield index_dir_entry

      file_offset += block_size
