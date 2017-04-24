# -*- coding: utf-8 -*-
"""Tests for the copy in and out (CPIO) archive format files."""

import io
import os
import unittest

from dtformats import cpio

from tests import test_lib


class DataRangeTest(test_lib.BaseTestCase):
  """In-file data range file-like object tests."""

  _FILE_DATA = bytes(bytearray(range(128)))

  def testSetRange(self):
    """Tests the SetRange function."""
    file_object = io.BytesIO(self._FILE_DATA)
    data_range = cpio.DataRange(file_object)

    data_range.SetRange(32, 64)

    with self.assertRaises(ValueError):
      data_range.SetRange(-1, 64)

    with self.assertRaises(ValueError):
      data_range.SetRange(0, -1)

  def testRead(self):
    """Tests the read function."""
    file_object = io.BytesIO(self._FILE_DATA)
    data_range = cpio.DataRange(file_object)
    data_range.SetRange(32, 64)

    byte_stream = data_range.read(size=1)
    self.assertEqual(byte_stream, b'\x20')

    byte_stream = data_range.read()
    self.assertEqual(len(byte_stream), 63)

    byte_stream = data_range.read()
    self.assertEqual(byte_stream, b'')

  def testSeek(self):
    """Tests the seek function."""
    file_object = io.BytesIO(self._FILE_DATA)
    data_range = cpio.DataRange(file_object)
    data_range.SetRange(32, 64)

    data_range.seek(0, os.SEEK_SET)
    offset = data_range.get_offset()
    self.assertEqual(offset, 0)

    data_range.seek(0, os.SEEK_END)
    offset = data_range.get_offset()
    self.assertEqual(offset, 64)

    data_range.seek(-32, os.SEEK_CUR)
    offset = data_range.get_offset()
    self.assertEqual(offset, 32)

    data_range.seek(128, os.SEEK_SET)
    offset = data_range.get_offset()
    self.assertEqual(offset, 128)

    with self.assertRaises(IOError):
      data_range.seek(0, -1)

    with self.assertRaises(IOError):
      data_range.seek(-256, os.SEEK_CUR)

  def testGetOffset(self):
    """Tests the get_offset function."""
    file_object = io.BytesIO(self._FILE_DATA)
    data_range = cpio.DataRange(file_object)
    data_range.SetRange(32, 64)

    offset = data_range.get_offset()
    self.assertEqual(offset, 0)

  def testTell(self):
    """Tests the tesll function."""
    file_object = io.BytesIO(self._FILE_DATA)
    data_range = cpio.DataRange(file_object)
    data_range.SetRange(32, 64)

    offset = data_range.tell()
    self.assertEqual(offset, 0)

  def testGetSize(self):
    """Tests the get_size function."""
    file_object = io.BytesIO(self._FILE_DATA)
    data_range = cpio.DataRange(file_object)
    data_range.SetRange(32, 64)

    size = data_range.get_size()
    self.assertEqual(size, 64)

  def testSeekable(self):
    """Tests the seekable function."""
    file_object = io.BytesIO(self._FILE_DATA)
    data_range = cpio.DataRange(file_object)

    result = data_range.seekable()
    self.assertTrue(result)


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
