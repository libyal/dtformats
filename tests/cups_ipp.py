# -*- coding: utf-8 -*-
"""Tests for CUPS Internet Printing Protocol (IPP) files."""

from __future__ import unicode_literals

import unittest

from dtformats import cups_ipp

from tests import test_lib


class CupsIppFileTest(test_lib.BaseTestCase):
  """CUPS Internet Printing Protocol (IPP) file tests."""

  # pylint: disable=protected-access

  # TODO: test _DebugPrintAttribute function

  def testDebugPrintHeader(self):
    """Tests the _DebugPrintHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cups_ipp.CupsIppFile(output_writer=output_writer)

    data_type_map = test_file._HEADER
    header = data_type_map.CreateStructureValues(
        major_version=1,
        minor_version=2,
        operation_identifier=3,
        request_identifier=4)

    test_file._DebugPrintHeader(header)

  # TODO: test _DebugPrintTagValue function
  # TODO: test _ReadAttribute function
  # TODO: test _ReadAttributesGroup function
  # TODO: test _ReadDateTimeValue function

  @test_lib.skipUnlessHasTestFile(['cups_ipp_2.0'])
  def testReadHeader(self):
    """Tests the _ReadHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cups_ipp.CupsIppFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cups_ipp_2.0'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadHeader(file_object)

  @test_lib.skipUnlessHasTestFile(['cups_ipp_2.0'])
  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = cups_ipp.CupsIppFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cups_ipp_2.0'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
