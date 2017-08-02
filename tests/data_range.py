# -*- coding: utf-8 -*-
"""Tests for the data range file-like object."""

from __future__ import unicode_literals

import io
import os
import unittest

from dtformats import data_range

from tests import test_lib


class DataRangeTest(test_lib.BaseTestCase):
  """In-file data range file-like object tests."""

  _FILE_DATA = bytes(bytearray(range(128)))

  def testRead(self):
    """Tests the read function."""
    file_object = io.BytesIO(self._FILE_DATA)
    test_range = data_range.DataRange(
        file_object, data_offset=32, data_size=64)

    byte_stream = test_range.read(size=1)
    self.assertEqual(byte_stream, b'\x20')

    byte_stream = test_range.read()
    self.assertEqual(len(byte_stream), 63)

    byte_stream = test_range.read()
    self.assertEqual(byte_stream, b'')

    test_range.data_offset = -1

    with self.assertRaises(IOError):
      test_range.read()

    test_range.data_offset = 32

    test_range.data_size = -1

    with self.assertRaises(IOError):
      test_range.read()

    test_range.data_offset = 64

  def testSeek(self):
    """Tests the seek function."""
    file_object = io.BytesIO(self._FILE_DATA)
    test_range = data_range.DataRange(
        file_object, data_offset=32, data_size=64)

    test_range.seek(0, os.SEEK_SET)
    offset = test_range.get_offset()
    self.assertEqual(offset, 0)

    test_range.seek(0, os.SEEK_END)
    offset = test_range.get_offset()
    self.assertEqual(offset, 64)

    test_range.seek(-32, os.SEEK_CUR)
    offset = test_range.get_offset()
    self.assertEqual(offset, 32)

    test_range.seek(128, os.SEEK_SET)
    offset = test_range.get_offset()
    self.assertEqual(offset, 128)

    with self.assertRaises(IOError):
      test_range.seek(0, -1)

    with self.assertRaises(IOError):
      test_range.seek(-256, os.SEEK_CUR)

    test_range.data_size = -1

    with self.assertRaises(IOError):
      test_range.seek(0, os.SEEK_SET)

    test_range.data_offset = 64

  def testGetOffset(self):
    """Tests the get_offset function."""
    file_object = io.BytesIO(self._FILE_DATA)
    test_range = data_range.DataRange(
        file_object, data_offset=32, data_size=64)

    offset = test_range.get_offset()
    self.assertEqual(offset, 0)

  def testTell(self):
    """Tests the tell function."""
    file_object = io.BytesIO(self._FILE_DATA)
    test_range = data_range.DataRange(
        file_object, data_offset=32, data_size=64)

    offset = test_range.tell()
    self.assertEqual(offset, 0)

  def testGetSize(self):
    """Tests the get_size function."""
    file_object = io.BytesIO(self._FILE_DATA)
    test_range = data_range.DataRange(
        file_object, data_offset=32, data_size=64)

    size = test_range.get_size()
    self.assertEqual(size, 64)

  def testSeekable(self):
    """Tests the seekable function."""
    file_object = io.BytesIO(self._FILE_DATA)
    test_range = data_range.DataRange(
        file_object, data_offset=32, data_size=64)

    result = test_range.seekable()
    self.assertTrue(result)


if __name__ == '__main__':
  unittest.main()
