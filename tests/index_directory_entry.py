# -*- coding: utf-8 -*-
"""Tests for NTFS INDX directory entries."""

import unittest
import os

from dtformats import index_directory_entry

from tests import test_lib

 # pylint: disable=protected-access
class IndexRecordFileTest(test_lib.BaseTestCase):
  """NTFS $I30 index record tests."""

  expected_values = [
    {'entry_header_signature': b'INDX',
    'entry_header_fixup_value_offset': 40,
    'entry_header_num_fixup_values': 9,
    'entry_header_logfile_sequence_number': 1143279,
    'entry_header_virtual_cluster_number': 0,
    'node_header_index_values_offset': 40,
    'node_header_index_node_size': 3176,
    'node_header_allocated_index_node_size': 4072,
    'node_header_index_node_flags': 0,
    'file_reference' : 281474976710748,
    'index_value_size' : 88,
    'index_key_data_size' : 72,
    'index_value_flags' : 0,
    'index_key_data_parent_file_reference': 281474976710691,
    'index_key_data_creation_time': 130795153668593750,
    'index_key_data_modification_time': 130870367262995000,
    'index_key_data_entry_modification_time': 130849843578932500,
    'index_key_data_access_time': 130870367262995000,
    'index_key_data_allocated_file_size': 24576,
    'index_key_data_file_size': 24576,
    'index_key_data_file_attribute_flags': 38,
    'index_key_data_extended_data': 0,
    'index_key_data_name_size': 3,
    'index_key_data_name_space': 3,
    'index_key_data_filename': 'BCD',
    },
    {'entry_header_signature': b'INDX',
    'entry_header_fixup_value_offset': 40,
    'entry_header_num_fixup_values': 9,
    'entry_header_logfile_sequence_number': 1060954,
    'entry_header_virtual_cluster_number': 0,
    'node_header_index_values_offset': 40,
    'node_header_index_node_size': 784,
    'node_header_allocated_index_node_size': 4072,
    'node_header_index_node_flags': 0,
    'file_reference' : 281474976710687,
    'index_value_size' : 96,
    'index_key_data_size' : 76,
    'index_value_flags' : 0,
    'index_key_data_parent_file_reference': 281474976710685,
    'index_key_data_creation_time': 130795138741093750,
    'index_key_data_modification_time': 130795138741093750,
    'index_key_data_entry_modification_time': 130795138741093750,
    'index_key_data_access_time': 130795138741093750,
    'index_key_data_allocated_file_size': 0,
    'index_key_data_file_size': 0,
    'index_key_data_file_attribute_flags': 38,
    'index_key_data_extended_data': 0,
    'index_key_data_name_size': 5,
    'index_key_data_name_space': 0,
    'index_key_data_filename': '$Tops',
    }]

  def _GetTestStructure(self, path):
    """ Helper method to create an NTFSIndexI30Record
    object.

    Args:
        path (str): Path to a test file.

    Returns:
        NTFSIndexI30Record: An NTFS I30 index object.
    """
    test_file_path = self._GetTestFilePath(path)
    self._SkipIfPathNotExists(test_file_path)

    output_writer = test_lib.TestOutputWriter()
    test_file = index_directory_entry.NTFSIndexI30Record(
        debug=True, output_writer=output_writer)

    test_file.Open(test_file_path)
    return test_file

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    test_file = self._GetTestStructure('indx.records')
    self.assertIsNotNone(test_file)

  def testParseIndexEntryHeader(self):
    """Tests the _ParseIndexEntryHeader function. """
    test_file = self._GetTestStructure('indx.records')
    record, _ = test_file._ParseIndexEntryHeader(test_file._file_object)

    self.assertEqual(record.signature,
      self.expected_values[0].get('entry_header_signature'))
    self.assertEqual(record.fixup_value_offset,
      self.expected_values[0].get('entry_header_fixup_value_offset'))
    self.assertEqual(record.num_fixup_values,
      self.expected_values[0].get('entry_header_num_fixup_values'))
    self.assertEqual(record.logfile_sequence_number,
      self.expected_values[0].get('entry_header_logfile_sequence_number'))
    self.assertEqual(record.virtual_cluster_number,
      self.expected_values[0].get('entry_header_virtual_cluster_number'))

  def testParseIndexNodeHeader(self):
    """Tests the _ParseIndexNodeHeader function. """
    test_file = self._GetTestStructure('indx.records')
    test_file._file_object.seek(24, os.SEEK_SET)
    record, _ = test_file._ParseIndexNodeHeader(test_file._file_object)

    self.assertEqual(record.index_values_offset,
      self.expected_values[0].get('node_header_index_values_offset'))
    self.assertEqual(record.index_node_size,
      self.expected_values[0].get('node_header_index_node_size'))
    self.assertEqual(record.allocated_index_node_size,
      self.expected_values[0].get('node_header_allocated_index_node_size'))
    self.assertEqual(record.index_node_flags,
      self.expected_values[0].get('node_header_index_node_flags'))

  def testReadRecords(self):
    """
    Method to test class functionality.
    """
    test_file = self._GetTestStructure('indx.records')

    i = 0
    for r in test_file.ReadRecords():
      self.assertEqual(r.entry_header.signature,
        self.expected_values[i].get('entry_header_signature'))
      self.assertEqual(r.entry_header.fixup_value_offset,
        self.expected_values[i].get('entry_header_fixup_value_offset'))
      self.assertEqual(r.entry_header.num_fixup_values,
        self.expected_values[i].get('entry_header_num_fixup_values'))
      self.assertEqual(r.entry_header.logfile_sequence_number,
        self.expected_values[i].get('entry_header_logfile_sequence_number'))
      self.assertEqual(r.entry_header.virtual_cluster_number,
        self.expected_values[i].get('entry_header_virtual_cluster_number'))
      self.assertEqual(r.node_header.index_values_offset,
        self.expected_values[i].get('node_header_index_values_offset'))
      self.assertEqual(r.node_header.index_node_size,
        self.expected_values[i].get('node_header_index_node_size'))
      self.assertEqual(r.node_header.allocated_index_node_size,
        self.expected_values[i].get('node_header_allocated_index_node_size'))
      self.assertEqual(r.node_header.index_node_flags,
        self.expected_values[i].get('node_header_index_node_flags'))
      self.assertEqual(r.file_reference,
        self.expected_values[i].get('file_reference'))
      self.assertEqual(r.index_value_size,
        self.expected_values[i].get('index_value_size'))
      self.assertEqual(r.index_key_data_size,
        self.expected_values[i].get('index_key_data_size'))
      self.assertEqual(r.index_value_flags,
        self.expected_values[i].get('index_value_flags'))
      self.assertEqual(r.index_key_data.parent_file_reference,
        self.expected_values[i].get('index_key_data_parent_file_reference'))
      self.assertEqual(r.index_key_data.creation_time,
        self.expected_values[i].get('index_key_data_creation_time'))
      self.assertEqual(r.index_key_data.modification_time,
        self.expected_values[i].get('index_key_data_modification_time'))
      self.assertEqual(r.index_key_data.entry_modification_time,
        self.expected_values[i].get('index_key_data_entry_modification_time'))
      self.assertEqual(r.index_key_data.access_time,
        self.expected_values[i].get('index_key_data_access_time'))
      self.assertEqual(r.index_key_data.allocated_file_size,
        self.expected_values[i].get('index_key_data_allocated_file_size'))
      self.assertEqual(r.index_key_data.file_size,
        self.expected_values[i].get('index_key_data_file_size'))
      self.assertEqual(r.index_key_data.file_attribute_flags,
        self.expected_values[i].get('index_key_data_file_attribute_flags'))
      self.assertEqual(r.index_key_data.extended_data,
        self.expected_values[i].get('index_key_data_extended_data'))
      self.assertEqual(r.index_key_data.name_size,
        self.expected_values[i].get('index_key_data_name_size'))
      self.assertEqual(r.index_key_data.name_space,
        self.expected_values[i].get('index_key_data_name_space'))
      self.assertEqual(r.index_key_data.filename,
        self.expected_values[i].get('index_key_data_filename'))

      i += 1


if __name__ == '__main__':
  unittest.main()
