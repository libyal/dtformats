# -*- coding: utf-8 -*-
"""Tests for the copy in and out (CPIO) archive format files."""

import os
import unittest

from dtformats import cpio

from tests import test_lib


class DataRangeTest(test_lib.BaseTestCase):
  """In-file data range file-like object tests."""

  # TODO: add tests.


class CPIOArchiveFileEntryTest(test_lib.BaseTestCase):
  """CPIO archive file entry tests."""

  # TODO: add tests.


class CPIOArchiveFileTest(test_lib.BaseTestCase):
  """CPIO archive file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile([u'syslog.bin.cpio'])
  def testReadFileObjectOnBinary(self):
    """Tests the ReadFileObject function on binary format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'syslog.bin.cpio'])
    test_file.Open(test_file_path)

    self.assertEqual(test_file.file_format, u'bin-little-endian')

  @test_lib.skipUnlessHasTestFile([u'syslog.newc.cpio'])
  def testReadFileObjectOnNewASCII(self):
    """Tests the ReadFileObject function on new ASCII format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'syslog.newc.cpio'])
    test_file.Open(test_file_path)

    self.assertEqual(test_file.file_format, u'newc')

  @test_lib.skipUnlessHasTestFile([u'syslog.crc.cpio'])
  def testReadFileObjectOnNewASCIIWithCRC(self):
    """Tests the ReadFileObject function on new ASCII with CRC format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'syslog.crc.cpio'])
    test_file.Open(test_file_path)

    self.assertEqual(test_file.file_format, u'crc')

  @test_lib.skipUnlessHasTestFile([u'syslog.odc.cpio'])
  def testReadFileObjectOnPortableASCII(self):
    """Tests the ReadFileObject function on portable ASCII format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'syslog.odc.cpio'])
    test_file.Open(test_file_path)

    self.assertEqual(test_file.file_format, u'odc')


if __name__ == '__main__':
  unittest.main()
