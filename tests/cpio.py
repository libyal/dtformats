# -*- coding: utf-8 -*-
"""Tests for copy in and out (CPIO) archive format files."""

import io
import unittest

from dtformats import cpio

from tests import test_lib


class CPIOArchiveFileEntryTest(test_lib.BaseTestCase):
  """CPIO archive file entry tests."""

  _FILE_DATA = bytes(bytearray(range(128)))

  def testInitialize(self):
    """Tests the __init__ function."""
    file_object = io.BytesIO(self._FILE_DATA)
    file_entry = cpio.CPIOArchiveFileEntry(
        file_object, data_offset=32, data_size=64)

    self.assertIsNotNone(file_entry)


class CPIOArchiveFileTest(test_lib.BaseTestCase):
  """CPIO archive file tests."""

  # TODO: add tests for _DebugPrintFileEntry.
  # TODO: add tests for _ReadFileEntry.
  # TODO: add tests for _ReadFileEntries.
  # TODO: add tests for Close.
  # TODO: add tests for GetFileEntries.
  # TODO: add tests for GetFileEntryByPath.
  # TODO: add tests for ReadFileObject on random data.

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
