# -*- coding: utf-8 -*-
"""Tests for LevelDB database files."""

import unittest

from dtformats import leveldb

from tests import test_lib


class LevelDBDatabaseStoredTablesFileTest(test_lib.BaseTestCase):
  """LevelDB database stored tables file ([0-9]{6}.ldb) tests."""

  # pylint: disable=protected-access

  def testReadVariableSizeInteger(self):
    """Tests the _ReadVariableSizeInteger function."""
    test_file = leveldb.LevelDBDatabaseStoredTablesFile()

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(b'\x01')
    self.assertEqual(integer_value, 1)
    self.assertEqual(bytes_read, 1)

    integer_value, bytes_read = test_file._ReadVariableSizeInteger(b'\x96\x01')
    self.assertEqual(integer_value, 150)
    self.assertEqual(bytes_read, 2)

  # TODO: add tests for _ReadFileFooter
  # TODO: add tests for ReadFileObject


if __name__ == '__main__':
  unittest.main()
