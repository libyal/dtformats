# -*- coding: utf-8 -*-
"""Tests for Mac OS com.apple.loginitems.plist Alias value data."""

import unittest

from dtformats import alias_data

from tests import test_lib


class MacOSLoginItemAliasDataTest(test_lib.BaseTestCase):
  """Mac OS com.apple.loginitems.plist Alias value data tests."""

  # pylint: disable=protected-access

  # TODO: add test for _FormatIntegerAsHFSTime64bit
  # TODO: add test for _ReadRecordHeader
  # TODO: add test for _ReadRecordV3
  # TODO: add test for _ReadTaggedValue

  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = alias_data.MacOSLoginItemAliasData(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'com.apple.loginitems.plist.alias_data'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
