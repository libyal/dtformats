# -*- coding: utf-8 -*-
"""Tests for UTMP files."""

from __future__ import unicode_literals

import unittest

from dtformats import utmp

from tests import test_lib


class UTMPFileTest(test_lib.BaseTestCase):
  """UTMP file tests."""

  # pylint: disable=protected-access

  def testDebugPrintEntry(self):
    """Tests the _DebugPrintEntry function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.UTMPFile(output_writer=output_writer)

    data_type_map = test_file._UTMP_ENTRY
    entry = data_type_map.CreateStructureValues(
        address_a=9,
        address_b=10,
        address_c=11,
        address_d=12,
        exit=5,
        hostname=b'host',
        micro_seconds=8,
        pid=2,
        session=6,
        terminal=b'vty',
        terminal_identifier=3,
        termination=4,
        timestamp=7,
        type=1,
        unknown1=b'unknown',
        username=b'user')

    test_file._DebugPrintEntry(entry)

  @test_lib.skipUnlessHasTestFile(['utmp'])
  def testReadEntries(self):
    """Tests the _ReadEntries function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.UTMPFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['utmp'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadEntries(file_object)

  @test_lib.skipUnlessHasTestFile(['utmp'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.UTMPFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['utmp'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
