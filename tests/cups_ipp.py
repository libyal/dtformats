# -*- coding: utf-8 -*-
"""Tests for CUPS Internet Printing Protocol (IPP) files."""

import unittest

from dtformats import cups_ipp

from tests import test_lib


class CupsIppFileTest(test_lib.BaseTestCase):
  """CUPS Internet Printing Protocol (IPP) file tests."""

  # pylint: disable=protected-access

  _DATE_TIME_VALUE_DATA = bytes(bytearray([
      0x07, 0xe6, 0x07, 0x07, 0x00, 0x12, 0x1a, 0x00, 0x2b, 0x00, 0x00]))

  # TODO: test _FormatIntegerAsTagValue function

  # TODO: test _ReadAttribute function
  # TODO: test _ReadAttributesGroup function
  # TODO: test _ReadBooleanValue function

  def testReadDateTimeValue(self):
    """Tests the _ReadDateTimeValue function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cups_ipp.CupsIppFile(output_writer=output_writer)

    date_time = test_file._ReadDateTimeValue(self._DATE_TIME_VALUE_DATA, 0)

    self.assertIsNotNone(date_time)
    iso8601_string = date_time.CopyToDateTimeStringISO8601()

    self.assertEqual(iso8601_string, '2022-07-07T00:18:26.0+00:00')

  # TODO: test _ReadIntegerValue function

  def testReadHeader(self):
    """Tests the _ReadHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cups_ipp.CupsIppFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cups_ipp_2.0'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadHeader(file_object)

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cups_ipp.CupsIppFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cups_ipp_2.0'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
