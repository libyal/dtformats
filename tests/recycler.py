# -*- coding: utf-8 -*-
"""Tests for Windows Recycler INFO2 files."""

from __future__ import unicode_literals

import unittest

from dtformats import recycler

from tests import test_lib


class RecyclerInfo2FileTest(test_lib.BaseTestCase):
  """Windows Recycler INFO2 file tests."""

  # pylint: disable=protected-access

  # TODO: add test for _FormatANSIString
  # TODO: add test for _ReadFileEntry

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = recycler.RecyclerInfo2File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['INFO2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  def testReadFileObjectFormatVersion1(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = recycler.RecyclerInfo2File(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['INFO2'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
