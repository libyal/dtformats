# -*- coding: utf-8 -*-
"""Tests for Windows Restore Point change.log files."""

from __future__ import unicode_literals

import unittest

from dtformats import rp_change_log

from tests import test_lib


class ChangeLogEntryTest(test_lib.BaseTestCase):
  """Windows Restore Point change log entry tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    change_log_entry = rp_change_log.ChangeLogEntry()
    self.assertIsNotNone(change_log_entry)


class RestorePointChangeLogFileTest(test_lib.BaseTestCase):
  """Windows Restore Point change.log file tests."""

  # pylint: disable=protected-access

  def testDebugPrintChangeLogEntryRecord(self):
    """Tests the _DebugPrintChangeLogEntryRecord function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = rp_change_log.RestorePointChangeLogFile(
        output_writer=output_writer)

    data_type_map = test_file._CHANGE_LOG_ENTRY
    change_log_entry_record = data_type_map.CreateStructureValues(
        entry_flags=1,
        entry_type=2,
        file_attribute_flags=3,
        process_name_size=4,
        record_size=5,
        record_type=6,
        sequence_number=7,
        signature=8,
        unknown1=9,
        unknown2=10)

    test_file._DebugPrintChangeLogEntryRecord(change_log_entry_record)

  def testDebugPrintFileHeader(self):
    """Tests the _DebugPrintFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = rp_change_log.RestorePointChangeLogFile(
        output_writer=output_writer)

    data_type_map = test_file._FILE_HEADER
    file_header = data_type_map.CreateStructureValues(
        format_version=1,
        record_size=2,
        record_type=3,
        signature=4)

    test_file._DebugPrintFileHeader(file_header)

  def testDebugPrintRecordHeader(self):
    """Tests the _DebugPrintRecordHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = rp_change_log.RestorePointChangeLogFile(
        output_writer=output_writer)

    data_type_map = test_file._RECORD_HEADER
    record_header = data_type_map.CreateStructureValues(
        record_size=1,
        record_type=2)

    test_file._DebugPrintRecordHeader(record_header)

  # TODO: add tests for _ReadChangeLogEntries.
  # TODO: add tests for _ReadChangeLogEntry.
  # TODO: add tests for _ReadFileHeader.
  # TODO: add tests for _ReadRecord.
  # TODO: add tests for _ReadVolumePath.

  @test_lib.skipUnlessHasTestFile(['change.log.1'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = rp_change_log.RestorePointChangeLogFile(
        output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['change.log.1'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
