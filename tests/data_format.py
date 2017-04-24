# -*- coding: utf-8 -*-
"""Tests for the binary data format and file."""

import os
import unittest

from dtformats import data_format

from tests import test_lib


class BinaryDataFormatTest(test_lib.BaseTestCase):
  """Binary data format tests."""

  def testDebugPrintData(self):
    """Tests the _DebugPrintData function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        output_writer=output_writer)

    data = b'\x00\x01\x02\x03\x04\x05\x06'
    test_format._DebugPrintData(u'Description', data)

    expected_output = [
        u'Description:\n',
        (u'0x00000000  00 01 02 03 04 05 06                              '
         u'.......\n')]
    self.assertEqual(output_writer.output, expected_output)

  def testDebugPrintValue(self):
    """Tests the _DebugPrintValue function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        output_writer=output_writer)

    test_format._DebugPrintValue(u'Description', u'Value')

    expected_output = [u'Description\t\t\t\t\t\t\t\t: Value\n']
    self.assertEqual(output_writer.output, expected_output)

  def testFormatDataInHexadecimal(self):
    """Tests the _FormatDataInHexadecimal function."""
    test_format = data_format.BinaryDataFormat()

    data = b'\x00\x01\x02\x03\x04\x05\x06'
    expected_formatted_data = (
        u'0x00000000  00 01 02 03 04 05 06                              '
        u'.......\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'
    expected_formatted_data = (
        u'0x00000000  00 01 02 03 04 05 06 07  08 09                    '
        u'..........\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = b'\x00\x01\x02\x03\x04\x05\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    expected_formatted_data = (
        u'0x00000000  00 01 02 03 04 05 07 08  09 0a 0b 0c 0d 0e 0f     '
        u'...............\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

  # TODO: add tests for _ReadStructure.


class BinaryDataFileTest(test_lib.BaseTestCase):
  """Binary data file tests."""

  # TODO: add tests for Open and Close.


if __name__ == '__main__':
  unittest.main()
