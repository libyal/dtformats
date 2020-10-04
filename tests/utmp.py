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

  def testReadEntries(self):
    """Tests the _ReadEntries function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.LinuxLibc6UtmpFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadEntries(file_object)

  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.LinuxLibc6UtmpFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

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

  def testReadEntries(self):
    """Tests the _ReadEntries function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.MacOSXUtmpxFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['utmpx-macosx10.5'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadEntries(file_object)

  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.MacOSXUtmpxFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['utmpx-macosx10.5'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
