# -*- coding: utf-8 -*-
"""Tests for copy in and out (CPIO) archive format files."""

from __future__ import unicode_literals

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

  # pylint: disable=protected-access

  def testDebugPrintFileEntry(self):
    """Tests the _DebugPrintFileEntry function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)
    test_file.file_format = 'bin-little-endian'

    data_type_map = test_file._CPIO_BINARY_LITTLE_ENDIAN_FILE_ENTRY
    file_entry = data_type_map.CreateStructureValues(
        device_number=1,
        file_size=0,
        group_identifier=1001,
        inode_number=2,
        mode=0o777,
        modification_time=0,
        number_of_links=1,
        path_size=0,
        signature=0x71c7,
        special_device_number=0,
        user_identifier=1000)

    test_file._DebugPrintFileEntry(file_entry)

    test_file.file_format = 'newc'

    data_type_map = test_file._CPIO_NEW_ASCII_FILE_ENTRY
    file_entry = data_type_map.CreateStructureValues(
        checksum=0x12345678,
        device_major_number=3,
        device_minor_number=4,
        file_size=0,
        group_identifier=1001,
        inode_number=2,
        mode=0o777,
        modification_time=0,
        number_of_links=1,
        path_size=0,
        signature=b'070702',
        special_device_major_number=5,
        special_device_minor_number=5,
        user_identifier=1000)

    test_file._DebugPrintFileEntry(file_entry)

  @test_lib.skipUnlessHasTestFile(['cpio', 'syslog.bin.cpio'])
  def testReadFileEntryOnBinary(self):
    """Tests the _ReadFileEntry function on binary format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)
    test_file.file_format = 'bin-little-endian'

    test_file_path = self._GetTestFilePath(['cpio', 'syslog.bin.cpio'])
    with open(test_file_path, 'rb') as file_object:
      file_entry = test_file._ReadFileEntry(file_object, 0)

    self.assertEqual(file_entry.data_size, 1247)

  @test_lib.skipUnlessHasTestFile(['cpio', 'syslog.newc.cpio'])
  def testReadFileEntryOnNewASCII(self):
    """Tests the _ReadFileEntry function on new ASCII format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)
    test_file.file_format = 'newc'

    test_file_path = self._GetTestFilePath(['cpio', 'syslog.newc.cpio'])
    with open(test_file_path, 'rb') as file_object:
      file_entry = test_file._ReadFileEntry(file_object, 0)

    self.assertEqual(file_entry.data_size, 1247)

  @test_lib.skipUnlessHasTestFile(['cpio', 'syslog.crc.cpio'])
  def testReadFileEntryOnNewASCIIWithCRC(self):
    """Tests the _ReadFileEntry function on new ASCII with CRC format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)
    test_file.file_format = 'crc'

    test_file_path = self._GetTestFilePath(['cpio', 'syslog.crc.cpio'])
    with open(test_file_path, 'rb') as file_object:
      file_entry = test_file._ReadFileEntry(file_object, 0)

    self.assertEqual(file_entry.data_size, 1247)

  @test_lib.skipUnlessHasTestFile(['cpio', 'syslog.odc.cpio'])
  def testReadFileEntryOnPortableASCII(self):
    """Tests the _ReadFileEntry function on portable ASCII format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)
    test_file.file_format = 'odc'

    test_file_path = self._GetTestFilePath(['cpio', 'syslog.odc.cpio'])
    with open(test_file_path, 'rb') as file_object:
      file_entry = test_file._ReadFileEntry(file_object, 0)

    self.assertEqual(file_entry.data_size, 1247)

  @test_lib.skipUnlessHasTestFile(['cpio', 'syslog.bin.cpio'])
  def testReadFileEntriesOnBinary(self):
    """Tests the _ReadFileEntries function on binary format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)
    test_file.file_format = 'bin-little-endian'

    test_file_path = self._GetTestFilePath(['cpio', 'syslog.bin.cpio'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileEntries(file_object)

    self.assertEqual(len(test_file._file_entries), 1)

  @test_lib.skipUnlessHasTestFile(['cpio', 'syslog.bin.cpio'])
  def testFileEntryExistsByPathOnBinary(self):
    """Tests the FileEntryExistsByPath function on binary format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cpio', 'syslog.bin.cpio'])
    test_file.Open(test_file_path)

    result = test_file.FileEntryExistsByPath('syslog')
    self.assertTrue(result)

    result = test_file.FileEntryExistsByPath('bogus')
    self.assertFalse(result)

    test_file.Close()

  @test_lib.skipUnlessHasTestFile(['cpio', 'syslog.bin.cpio'])
  def testGetFileEntriesOnBinary(self):
    """Tests the GetFileEntries function on binary format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cpio', 'syslog.bin.cpio'])
    test_file.Open(test_file_path)

    file_entries = list(test_file.GetFileEntries())
    self.assertEqual(len(file_entries), 1)

    test_file.Close()

    file_entries = list(test_file.GetFileEntries())
    self.assertEqual(len(file_entries), 0)

  @test_lib.skipUnlessHasTestFile(['cpio', 'syslog.bin.cpio'])
  def testGetFileEntryByPathOnBinary(self):
    """Tests the GetFileEntryByPath function on binary format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cpio', 'syslog.bin.cpio'])
    test_file.Open(test_file_path)

    file_entry = test_file.GetFileEntryByPath('syslog')
    self.assertIsNotNone(file_entry)

    file_entry = test_file.GetFileEntryByPath('bogus')
    self.assertIsNone(file_entry)

    test_file.Close()

  @test_lib.skipUnlessHasTestFile(['cpio', 'syslog.bin.cpio'])
  def testReadFileObjectOnBinary(self):
    """Tests the ReadFileObject function on binary format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cpio', 'syslog.bin.cpio'])
    test_file.Open(test_file_path)

    self.assertEqual(test_file.file_format, 'bin-little-endian')

    test_file.Close()

  @test_lib.skipUnlessHasTestFile(['cpio', 'syslog.newc.cpio'])
  def testReadFileObjectOnNewASCII(self):
    """Tests the ReadFileObject function on new ASCII format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cpio', 'syslog.newc.cpio'])
    test_file.Open(test_file_path)

    self.assertEqual(test_file.file_format, 'newc')

    test_file.Close()

  @test_lib.skipUnlessHasTestFile(['cpio', 'syslog.crc.cpio'])
  def testReadFileObjectOnNewASCIIWithCRC(self):
    """Tests the ReadFileObject function on new ASCII with CRC format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cpio', 'syslog.crc.cpio'])
    test_file.Open(test_file_path)

    self.assertEqual(test_file.file_format, 'crc')

    test_file.Close()

  @test_lib.skipUnlessHasTestFile(['cpio', 'syslog.odc.cpio'])
  def testReadFileObjectOnPortableASCII(self):
    """Tests the ReadFileObject function on portable ASCII format."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cpio.CPIOArchiveFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cpio', 'syslog.odc.cpio'])
    test_file.Open(test_file_path)

    self.assertEqual(test_file.file_format, 'odc')

    test_file.Close()

  # TODO: add tests for ReadFileObject on random data.


if __name__ == '__main__':
  unittest.main()
