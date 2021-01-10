# -*- coding: utf-8 -*-
"""Tests for Apple Spotlight store database files."""

import unittest

from dtformats import spotlight_storedb

from tests import test_lib


class AppleSpotlightStoreDatabaseFileTest(test_lib.BaseTestCase):
  """Apple Spotlight store database file tests."""

  # pylint: disable=protected-access

  # TODO: add test for _FormatStreamAsSignature
  # TODO: add test for _ReadFileHeader
  # TODO: add test for _ReadMapPages
  # TODO: add test for _ReadPropertyPage
  # TODO: add test for _ReadPropertyPages
  # TODO: add test for _ReadPropertyPageValues

  def testReadVariableSizeInteger(self):
    """Tests the _ReadVariableSizeInteger function."""
    test_file = spotlight_storedb.AppleSpotlightStoreDatabaseFile()

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(b'\x24')
    self.assertEqual(integer_value, 36)
    self.assertEqual(bytes_read, 1)

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(b'\x80\x24')
    self.assertEqual(integer_value, 36)
    self.assertEqual(bytes_read, 2)

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(
        b'\xc0\x00\x24')
    self.assertEqual(integer_value, 36)
    self.assertEqual(bytes_read, 3)

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(
        b'\xe0\x00\x00\x24')
    self.assertEqual(integer_value, 36)
    self.assertEqual(bytes_read, 4)

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(
        b'\xf0\x00\x00\x00\x24')
    self.assertEqual(integer_value, 36)
    self.assertEqual(bytes_read, 5)

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(
        b'\xf1\x02\x03\x04\x05')
    self.assertEqual(integer_value, 4328719365)
    self.assertEqual(bytes_read, 5)

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(
        b'\xf8\x00\x00\x00\x00\x24')
    self.assertEqual(integer_value, 36)
    self.assertEqual(bytes_read, 6)

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(
        b'\xfc\x00\x00\x00\x00\x00\x24')
    self.assertEqual(integer_value, 36)
    self.assertEqual(bytes_read, 7)

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(
        b'\xfe\x00\x00\x00\x00\x00\x00\x24')
    self.assertEqual(integer_value, 36)
    self.assertEqual(bytes_read, 8)

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(
        b'\xff\x00\x00\x00\x00\x00\x00\x00\x24')
    self.assertEqual(integer_value, 36)
    self.assertEqual(bytes_read, 9)

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(
        b'\xff\x01\x02\x03\x04\x05\x06\x07\x08')
    self.assertEqual(integer_value, 72623859790382856)
    self.assertEqual(bytes_read, 9)

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    test_file_path = self._GetTestFilePath(['store.db'])
    self._SkipIfPathNotExists(test_file_path)

    output_writer = test_lib.TestOutputWriter()
    test_file = spotlight_storedb.AppleSpotlightStoreDatabaseFile(
        debug=False, output_writer=output_writer)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
