# -*- coding: utf-8 -*-
"""Tests for MacOS keychain database files."""

import unittest

from dtformats import keychain

from tests import test_lib


class KeychainDatabaseFileTest(test_lib.BaseTestCase):
  """MacOS keychain database file tests."""

  # pylint: disable=protected-access

  # TODO: add test for tables property

  # TODO: add test for _DebugPrintTablesArray
  # TODO: add test for _DebugPrintTableHeader

  # TODO: add test for _FormatStreamAsSignature

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = keychain.KeychainDatabaseFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['login.keychain'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  # TODO: add test for _ReadRecord
  # TODO: add test for _ReadRecordHeader
  # TODO: add test for _ReadTablesArray
  # TODO: add test for _ReadTable
  # TODO: add test for _ReadTableHeader

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = keychain.KeychainDatabaseFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['login.keychain'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
