# -*- coding: utf-8 -*-
"""Tests for Time zone information files (TZif)."""

import unittest

from dtformats import tzif

from tests import test_lib


class TimeZoneInformationFileTest(test_lib.BaseTestCase):
  """Time zone information file (TZif) tests."""

  # pylint: disable=protected-access

  def testDebugPrintFileHeader(self):
    """Tests the _DebugPrintFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = tzif.TimeZoneInformationFile(output_writer=output_writer)

    data_type_map = test_file._GetDataTypeMap('tzif_file_header')

    file_header = data_type_map.CreateStructureValues(
        format_version=0x32,
        number_of_leap_seconds=1,
        number_of_local_time_types=2,
        number_of_standard_time_indicators=3,
        number_of_transition_times=4,
        number_of_utc_time_indicators=5,
        signature=b'TZif',
        time_zone_abbreviation_strings_size=6,
        unknown1=(
            b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e'))

    test_file._DebugPrintFileHeader(file_header)

  # TODO: add tests for _DebugPrintTransitionTimeIndex
  # TODO: add tests for _DebugPrintTransitionTimes

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = tzif.TimeZoneInformationFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['localtime.tzif'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  # TODO: add tests for _ReadLeapSecondRecords
  # TODO: add tests for _ReadLocalTimeTypesTable
  # TODO: add tests for _ReadStandardTimeIndicators
  # TODO: add tests for _ReadTransitionTimeIndex
  # TODO: add tests for _ReadTimeZoneAbbreviationStrings
  # TODO: add tests for _ReadTimeZoneInformation32bit
  # TODO: add tests for _ReadTimeZoneInformation64bit
  # TODO: add tests for _ReadTransitionTimes32bit
  # TODO: add tests for _ReadTransitionTimes64bit
  # TODO: add tests for _ReadUTCTimeIndicators

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = tzif.TimeZoneInformationFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['localtime.tzif'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
