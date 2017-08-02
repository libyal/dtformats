# -*- coding: utf-8 -*-
"""Tests for Safari Cookies (Cookies.binarycookies) files."""

from __future__ import unicode_literals

import unittest

from dtformats import safari_cookies

from tests import test_lib


class BinaryCookiesFileTest(test_lib.BaseTestCase):
  """Safari Cookies (Cookies.binarycookies) file tests."""

  # pylint: disable=protected-access

  def testDebugPrintFileHeader(self):
    """Tests the _DebugPrintFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = safari_cookies.BinaryCookiesFile(output_writer=output_writer)

    data_type_map = test_file._FILE_HEADER
    file_header = data_type_map.CreateStructureValues(
        number_of_pages=1,
        signature=b'cook')

    test_file._DebugPrintFileHeader(file_header)

  # TODO: add tests for _DebugPrintRecordHeader.
  # TODO: add tests for _ReadFileFooter.
  # TODO: add tests for _ReadFileHeader.
  # TODO: add tests for _ReadPage.
  # TODO: add tests for _ReadPages.
  # TODO: add tests for _ReadRecord.

  @test_lib.skipUnlessHasTestFile(['Cookies.binarycookies'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = safari_cookies.BinaryCookiesFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['Cookies.binarycookies'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
