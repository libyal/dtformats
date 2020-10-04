# -*- coding: utf-8 -*-
"""Tests for Windows Recycle.Bin metadata ($I) files."""

from __future__ import unicode_literals

import unittest

from dtformats import recycle_bin

from tests import test_lib


class RecycleBinMetadataFileTest(test_lib.BaseTestCase):
  """Windows Recycle.Bin metadata ($I) file tests."""

  # pylint: disable=protected-access

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = recycle_bin.RecycleBinMetadataFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['$II3DF3L.zip'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_header = test_file._ReadFileHeader(file_object)

    self.assertEqual(file_header.format_version, 1)
    self.assertEqual(file_header.original_file_size, 724919)
    self.assertEqual(file_header.deletion_time, 129760589986330000)

  def testReadOriginalFilename(self):
    """Tests the _ReadOriginalFilename function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = recycle_bin.RecycleBinMetadataFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['$II3DF3L.zip'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_header = test_file._ReadFileHeader(file_object)
      original_filename = test_file._ReadOriginalFilename(
          file_object, file_header.format_version)

    expected_original_filename = (
        'C:\\Users\\bogus\\Documents\\RandomResearch\\Archives.zip')
    self.assertEqual(original_filename, expected_original_filename)

  def testReadFileObjectFormatVersion1(self):
    """Tests the ReadFileObject function on a format version 1 file."""
    output_writer = test_lib.TestOutputWriter()
    test_file = recycle_bin.RecycleBinMetadataFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['$II3DF3L.zip'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)

  def testReadFileObjectFormatVersion2(self):
    """Tests the ReadFileObject function on a format version 2 file."""
    output_writer = test_lib.TestOutputWriter()
    test_file = recycle_bin.RecycleBinMetadataFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['$I103S5F.jpg'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
