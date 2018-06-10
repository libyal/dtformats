# -*- coding: utf-8 -*-
"""Tests for Windows Recycler INFO2 files."""

from __future__ import unicode_literals

import unittest

from dtformats import recycler

from tests import test_lib


class RecyclerInfo2FileTest(test_lib.BaseTestCase):
  """Windows Recycler INFO2 file tests."""

  # pylint: disable=protected-access

  # TODO: add test for _DebugPrintFileEntry

  def testDebugPrintFileHeader(self):
    """Tests the _DebugPrintFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = recycler.RecyclerInfo2File(output_writer=output_writer)

    data_type_map = test_file._GetDataTypeMap(
        'recycler_info2_file_header')

    file_header = data_type_map.CreateStructureValues(
        file_entry_size=0,
        number_of_file_entries=1,
        unknown1=2,
        unknown2=3,
        unknown3=4)

    test_file._DebugPrintFileHeader(file_header)

  # TODO: add test for _ReadFileEntry

  @test_lib.skipUnlessHasTestFile(['INFO2'])
  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = recycler.RecyclerInfo2File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['INFO2'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  @test_lib.skipUnlessHasTestFile(['INFO2'])
  def testReadFileObjectFormatVersion1(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = recycler.RecyclerInfo2File(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['INFO2'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
