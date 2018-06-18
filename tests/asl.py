# -*- coding: utf-8 -*-
"""Tests for Apple System Log (ASL) files."""

from __future__ import unicode_literals

import unittest

from dtformats import asl

from tests import test_lib


class AppleSystemLogFileTest(test_lib.BaseTestCase):
  """Apple System Log (.asl) file tests."""

  # pylint: disable=protected-access

  def testDebugPrintFileHeader(self):
    """Tests the _DebugPrintFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = asl.AppleSystemLogFile(output_writer=output_writer)

    data_type_map = test_file._GetDataTypeMap('asl_file_header')

    file_header = data_type_map.CreateStructureValues(
        cache_size=1,
        creation_time=2,
        first_log_entry_offset=3,
        format_version=4,
        last_log_entry_offset=5,
        signature=b'test1',
        unknown1=b'test2')

    test_file._DebugPrintFileHeader(file_header)

  def testDebugPrintRecord(self):
    """Tests the _DebugPrintRecord function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = asl.AppleSystemLogFile(output_writer=output_writer)

    data_type_map = test_file._GetDataTypeMap('asl_record')

    file_header = data_type_map.CreateStructureValues(
        alert_level=1,
        data_size=2,
        facility_string_offset=3,
        flags=4,
        group_identifier=5,
        hostname_string_offset=6,
        message_identifier=7,
        message_string_offset=8,
        next_record_offset=9,
        process_identifier=10,
        real_group_identifier=11,
        real_user_identifier=12,
        reference_process_identifier=12,
        sender_string_offset=14,
        user_identifier=15,
        written_time=16,
        written_time_nanoseconds=17,
        unknown1=18)

    test_file._DebugPrintRecord(file_header)

  def testDebugPrintRecordExtraField(self):
    """Tests the _DebugPrintRecordExtraField function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = asl.AppleSystemLogFile(output_writer=output_writer)

    data_type_map = test_file._GetDataTypeMap('asl_record_extra_field')

    file_header = data_type_map.CreateStructureValues(
        name_string_offset=1,
        value_string_offset=2)

    test_file._DebugPrintRecordExtraField(file_header)

  def testDebugPrintRecordString(self):
    """Tests the _DebugPrintRecordString function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = asl.AppleSystemLogFile(output_writer=output_writer)

    data_type_map = test_file._GetDataTypeMap('asl_record_string')

    file_header = data_type_map.CreateStructureValues(
        unknown1=1,
        string_size=2,
        string='test')

    test_file._DebugPrintRecordString(file_header)

  @test_lib.skipUnlessHasTestFile(['applesystemlog.asl'])
  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = asl.AppleSystemLogFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['applesystemlog.asl'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  # TODO: add test for _ReadRecord
  # TODO: add test for _ReadRecordExtraField
  # TODO: add test for _ReadRecordString

  @test_lib.skipUnlessHasTestFile(['applesystemlog.asl'])
  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = asl.AppleSystemLogFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['applesystemlog.asl'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
