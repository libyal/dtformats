# -*- coding: utf-8 -*-
"""Tests for BSM event auditing files."""

import unittest

from dtformats import bsm
from dtformats import errors

from tests import test_lib


class BSMEventAuditingFileTest(test_lib.BaseTestCase):
  """BSM event auditing file tests."""

  # pylint: disable=protected-access

  def testFormatArrayOfIntegersAsIPAddress(self):
    """Tests the _FormatArrayOfIntegersAsIPAddress function."""
    test_file = bsm.BSMEventAuditingFile()

    ip_address = [127, 0, 0, 1]
    formatted_ip_address = test_file._FormatArrayOfIntegersAsIPAddress(
        ip_address)
    self.assertEqual(formatted_ip_address, '127.0.0.1')

    ip_address = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    formatted_ip_address = test_file._FormatArrayOfIntegersAsIPAddress(
        ip_address)
    self.assertEqual(
        formatted_ip_address, '0000:0000:0000:0000:0000:0000:0000:0001')

    ip_address = []
    formatted_ip_address = test_file._FormatArrayOfIntegersAsIPAddress(
        ip_address)
    self.assertIsNone(formatted_ip_address)

  def testFormatIntegerAsEventType(self):
    """Tests the _FormatIntegerAsEventType function."""
    test_file = bsm.BSMEventAuditingFile()

    formatted_event_type = test_file._FormatIntegerAsEventType(1)
    self.assertEqual(formatted_event_type, '0x0001 (exit(2))')

  def testFormatIntegerAsNetType(self):
    """Tests the _FormatIntegerAsNetType function."""
    test_file = bsm.BSMEventAuditingFile()

    formatted_net_type = test_file._FormatIntegerAsNetType(4)
    self.assertEqual(formatted_net_type, '4')

    with self.assertRaises(errors.ParseError):
      test_file._FormatIntegerAsNetType(0)

  def testFormatString(self):
    """Tests the _FormatString function."""
    test_file = bsm.BSMEventAuditingFile()

    formatted_string = test_file._FormatString('string\x00')
    self.assertEqual(formatted_string, 'string')

  def testReadRecord(self):
    """Tests the _ReadRecord function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = bsm.BSMEventAuditingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['openbsm.bsm'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadRecord(file_object, 0)

  def testReadToken(self):
    """Tests the _ReadToken function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = bsm.BSMEventAuditingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['openbsm.bsm'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      token_type, token_data = test_file._ReadToken(file_object, 0)

      self.assertEqual(token_type, 20)
      self.assertIsNotNone(token_data)

  def testReadFileObjectWithOpenBSM(self):
    """Tests the ReadFileObject function with an Open BSM file ."""
    output_writer = test_lib.TestOutputWriter()
    test_file = bsm.BSMEventAuditingFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['openbsm.bsm'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)

  def testReadFileObjectWithAppleBSM(self):
    """Tests the ReadFileObject function with an Apple BSM file."""
    output_writer = test_lib.TestOutputWriter()
    test_file = bsm.BSMEventAuditingFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['apple.bsm'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
