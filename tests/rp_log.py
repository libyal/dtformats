# -*- coding: utf-8 -*-
"""Tests for Windows Restore Point rp.log files."""

from __future__ import unicode_literals

import unittest

from dtformats import rp_log

from tests import test_lib


class RestorePointLogFileTest(test_lib.BaseTestCase):
  """Windows Restore Point rp.log file tests."""

  # pylint: disable=protected-access

  def testDebugPrintFileFooter(self):
    """Tests the _DebugPrintFileFooter function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = rp_log.RestorePointLogFile(output_writer=output_writer)

    data_type_map = test_file._GetDataTypeMap('rp_log_file_footer')

    file_footer = data_type_map.CreateStructureValues(
        creation_time=1)

    test_file._DebugPrintFileFooter(file_footer)

  def testDebugPrintFileHeader(self):
    """Tests the _DebugPrintFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = rp_log.RestorePointLogFile(output_writer=output_writer)

    data_type_map = test_file._GetDataTypeMap('rp_log_file_header')

    file_header = data_type_map.CreateStructureValues(
        description='Description'.encode('utf-16-le'),
        event_type=1,
        restore_point_type=2,
        sequence_number=3)

    test_file._DebugPrintFileHeader(file_header)

  @test_lib.skipUnlessHasTestFile(['rp.log'])
  def testReadFileFooter(self):
    """Tests the _ReadFileFooter function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = rp_log.RestorePointLogFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['rp.log'])
    with open(test_file_path, 'rb') as file_object:
      test_file._file_size = 536
      test_file._ReadFileFooter(file_object)

  @test_lib.skipUnlessHasTestFile(['rp.log'])
  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = rp_log.RestorePointLogFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['rp.log'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  @test_lib.skipUnlessHasTestFile(['rp.log'])
  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = rp_log.RestorePointLogFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['rp.log'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
