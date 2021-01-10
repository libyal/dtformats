# -*- coding: utf-8 -*-
"""Tests for Apple System Log (ASL) files."""

import unittest

from dtformats import asl

from tests import test_lib


class AppleSystemLogFileTest(test_lib.BaseTestCase):
  """Apple System Log (.asl) file tests."""

  # pylint: disable=protected-access

  def testFormatIntegerAsFlags(self):
    """Tests the _FormatIntegerAsFlags function."""
    test_file = asl.AppleSystemLogFile()

    formatted_flags = test_file._FormatIntegerAsFlags(1)
    self.assertEqual(formatted_flags, '0x0001')

  def testFormatStreamAsSignature(self):
    """Tests the _FormatStreamAsSignature function."""
    test_file = asl.AppleSystemLogFile()

    formatted_signature = test_file._FormatStreamAsSignature(
        b'ASL DB\x00\x00\x00\x00\x00\x00')
    self.assertEqual(
        formatted_signature, 'ASL DB\\x00\\x00\\x00\\x00\\x00\\x00')

  def testFormatString(self):
    """Tests the _FormatString function."""
    test_file = asl.AppleSystemLogFile()

    formatted_string = test_file._FormatString('string\x00')
    self.assertEqual(formatted_string, 'string')

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = asl.AppleSystemLogFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['applesystemlog.asl'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  # TODO: add test for _ReadRecord
  # TODO: add test for _ReadRecordExtraField
  # TODO: add test for _ReadRecordString

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = asl.AppleSystemLogFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['applesystemlog.asl'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
