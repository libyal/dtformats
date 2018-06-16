# -*- coding: utf-8 -*-
"""Tests for Apple System Log (ASL) files."""

from __future__ import unicode_literals

import unittest

from dtformats import asl

from tests import test_lib


class AppleSystemLogFileTest(test_lib.BaseTestCase):
  """Apple System Log (.asl) file tests."""

  # pylint: disable=protected-access

  def testDebugPrintFileHeader(self):
    """Tests the _DebugPrintFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = asl.AppleSystemLogFile(output_writer=output_writer)

    data_type_map = test_file._GetDataTypeMap('asl_file_header')

    file_header = data_type_map.CreateStructureValues(
        cache_size=1,
        creation_time=2,
        first_log_entry_offset=3,
        format_version=4,
        last_log_entry_offset=5,
        signature=b'test1',
        unknown1=b'test2')

    test_file._DebugPrintFileHeader(file_header)

  @test_lib.skipUnlessHasTestFile(['applesystemlog.asl'])
  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = asl.AppleSystemLogFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['applesystemlog.asl'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  @test_lib.skipUnlessHasTestFile(['applesystemlog.asl'])
  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = asl.AppleSystemLogFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['applesystemlog.asl'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
