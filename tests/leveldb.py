# -*- coding: utf-8 -*-
"""Tests for LevelDB database files."""

import unittest

from dtformats import leveldb

from tests import test_lib


class LevelDBDatabaseTest(test_lib.BaseTestCase):
  """LevelDB database files tests."""

  # pylint: disable=protected-access

  def testReadVariableSizeInteger(self):
    """Tests the _ReadVariableSizeInteger function."""
    integer_value, bytes_read = leveldb._ReadVariableSizeInteger(b'\x01')
    self.assertEqual(integer_value, 1)
    self.assertEqual(bytes_read, 1)

    integer_value, bytes_read = leveldb._ReadVariableSizeInteger(b'\x96\x01')
    self.assertEqual(integer_value, 150)
    self.assertEqual(bytes_read, 2)


# TODO: add tests for LevelDBDatabaseLogFile
# TODO: add tests for LevelDBDatabaseTableFile


if __name__ == '__main__':
  unittest.main()
