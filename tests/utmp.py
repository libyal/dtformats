# -*- coding: utf-8 -*-
"""Tests for utmp files."""

from __future__ import unicode_literals

import unittest

from dtformats import utmp

from tests import test_lib


class LinuxLibc6UtmpFileTest(test_lib.BaseTestCase):
  """Linux libc6 utmp file tests."""

  # pylint: disable=protected-access

  def testDebugPrintEntry(self):
    """Tests the _DebugPrintEntry function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.LinuxLibc6UtmpFile(output_writer=output_writer)

    data_type_map = test_file._GetDataTypeMap('linux_libc6_utmp_entry')

    entry = data_type_map.CreateStructureValues(
        ip_address=test_file._EMPTY_IP_ADDRESS,
        exit_status=5,
        hostname=b'host',
        microseconds=8,
        pid=2,
        session=6,
        terminal=b'vty',
        terminal_identifier=3,
        termination_status=4,
        timestamp=7,
        type=1,
        unknown1=b'unknown',
        username=b'user')

    test_file._DebugPrintEntry(entry)

  def testDecodeString(self):
    """Tests the _DecodeString function."""
    test_file = utmp.LinuxLibc6UtmpFile()

    string = test_file._DecodeString(b'test\x00')
    self.assertEqual(string, 'test')

  def testFormatPackedIPv4Address(self):
    """Tests the _FormatPackedIPv4Address function."""
    test_file = utmp.LinuxLibc6UtmpFile()

    ip_address = test_file._FormatPackedIPv4Address([0xc0, 0xa8, 0xcc, 0x62])
    self.assertEqual(ip_address, '192.168.204.98')

  def testFormatPackedIPv6Address(self):
    """Tests the _FormatPackedIPv6Address function."""
    test_file = utmp.LinuxLibc6UtmpFile()

    ip_address = test_file._FormatPackedIPv6Address([
        0x20, 0x01, 0x0d, 0xb8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00,
        0x00, 0x42, 0x83, 0x29])
    self.assertEqual(ip_address, '2001:0db8:0000:0000:0000:ff00:0042:8329')

  @test_lib.skipUnlessHasTestFile(['utmp-linux_libc6'])
  def testReadEntries(self):
    """Tests the _ReadEntries function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.LinuxLibc6UtmpFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadEntries(file_object)

  @test_lib.skipUnlessHasTestFile(['utmp-linux_libc6'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.LinuxLibc6UtmpFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    test_file.Open(test_file_path)


class MacOSXUtmpxFileTest(test_lib.BaseTestCase):
  """Mac OS X 10.5 utmpx file tests."""

  # pylint: disable=protected-access

  def testDebugPrintEntry(self):
    """Tests the _DebugPrintEntry function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.MacOSXUtmpxFile(output_writer=output_writer)

    data_type_map = test_file._GetDataTypeMap('macosx_utmpx_entry')

    entry = data_type_map.CreateStructureValues(
        hostname=b'host',
        microseconds=1,
        pid=2,
        terminal=b'vty',
        terminal_identifier=3,
        timestamp=4,
        type=5,
        unknown1=6,
        unknown2=b'unknown',
        username=b'user')

    test_file._DebugPrintEntry(entry)

  def testDecodeString(self):
    """Tests the _DecodeString function."""
    test_file = utmp.MacOSXUtmpxFile()

    string = test_file._DecodeString(b'test\x00')
    self.assertEqual(string, 'test')

  @test_lib.skipUnlessHasTestFile(['utmpx-macosx10.5'])
  def testReadEntries(self):
    """Tests the _ReadEntries function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.MacOSXUtmpxFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['utmpx-macosx10.5'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadEntries(file_object)

  @test_lib.skipUnlessHasTestFile(['utmpx-macosx10.5'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.MacOSXUtmpxFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['utmpx-macosx10.5'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
