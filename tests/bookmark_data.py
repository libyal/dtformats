# -*- coding: utf-8 -*-
"""Tests for Mac OS backgrounditems.btm bookmark data."""

import unittest

from dtformats import bookmark_data

from tests import test_lib


class MacOSBackgroundItemBookmarkDataTest(test_lib.BaseTestCase):
  """Mac OS backgrounditems.btm bookmark data tests."""

  # pylint: disable=protected-access

  # TODO: add test for _ReadHeader

  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = bookmark_data.MacOSBackgroundItemBookmarkData(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'backgrounditems.btm.bookmark_data'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
