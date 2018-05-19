# -*- coding: utf-8 -*-
"""Tests for GZip files."""

# Note: do not rename file to gzip.py this can cause the exception:
# AttributeError: 'module' object has no attribute 'GzipFile'
# when using pip.

from __future__ import unicode_literals

import unittest

from dtformats import gzipfile

from tests import test_lib


class GZipFileTest(test_lib.BaseTestCase):
  """GZip file tests."""

  # pylint: disable=protected-access

  def testDebugPrintMemberHeader(self):
    """Tests the _DebugPrintMemberHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = gzipfile.GZipFile(output_writer=output_writer)

    data_type_map = test_file._DATA_TYPE_FABRIC.CreateDataTypeMap(
        'gzip_member_header')
    data_section = data_type_map.CreateStructureValues(
        compression_flags=0x00,
        compression_method=8,
        flags=0x08,
        modification_time=1343493847,
        operating_system=3,
        signature=0x8b1f)

    test_file._DebugPrintMemberHeader(data_section)

  @test_lib.skipUnlessHasTestFile(['syslog.gz'])
  def testReadMemberHeader(self):
    """Tests the _ReadMemberHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = gzipfile.GZipFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['syslog.gz'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadMemberHeader(file_object)

  @test_lib.skipUnlessHasTestFile(['syslog.gz'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    # TODO: add debug=True
    test_file = gzipfile.GZipFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['syslog.gz'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
