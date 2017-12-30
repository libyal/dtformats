# -*- coding: utf-8 -*-
"""Tests for Windows Task Scheduler job files."""

from __future__ import unicode_literals

import os
import unittest
import uuid

from dtformats import job

from tests import test_lib


class WindowsTaskSchedularJobFileTest(test_lib.BaseTestCase):
  """Windows Task Scheduler job file tests."""

  # pylint: disable=protected-access

  def testDebugPrintFixedLengthDataSection(self):
    """Tests the _DebugPrintFixedLengthDataSection function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = job.WindowsTaskSchedularJobFile(
        output_writer=output_writer)

    data_type_map = test_file._DATA_TYPE_FABRIC.CreateDataTypeMap(
        'system_time')
    system_time = data_type_map.CreateStructureValues(
        day_of_month=7,
        hours=17,
        milliseconds=135,
        minutes=41,
        month=5,
        seconds=25,
        weekday=0,
        year=2017)

    uuid_value = uuid.UUID('{97d57d7f-24e9-4de7-9306-b40d93442fbb}')
    data_type_map = test_file._FIXED_LENGTH_DATA_SECTION
    data_section = data_type_map.CreateStructureValues(
        application_name_offset=3,
        error_retry_count=5,
        error_retry_interval=6,
        exit_code=11,
        flags=13,
        format_version=2,
        idle_deadline=7,
        idle_wait=8,
        job_identifier=uuid_value,
        last_run_time=system_time,
        maximum_run_time=10,
        priority=9,
        product_version=1,
        status=12,
        triggers_offset=4)

    test_file._DebugPrintFixedLengthDataSection(data_section)

  def testDebugPrintTrigger(self):
    """Tests the _DebugPrintTrigger function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = job.WindowsTaskSchedularJobFile(
        output_writer=output_writer)

    data_type_map = test_file._DATA_TYPE_FABRIC.CreateDataTypeMap(
        'job_trigger_date')
    date = data_type_map.CreateStructureValues(
        day_of_month=9,
        month=5,
        year=2017)

    data_type_map = test_file._DATA_TYPE_FABRIC.CreateDataTypeMap(
        'job_trigger_time')
    time = data_type_map.CreateStructureValues(
        hours=8,
        minutes=1)

    data_type_map = test_file._DATA_TYPE_FABRIC.CreateDataTypeMap(
        'job_trigger')
    trigger = data_type_map.CreateStructureValues(
        duration=6,
        end_date=date,
        interval=7,
        reserved1=2,
        size=1,
        start_date=date,
        start_time=time,
        trigger_arg0=10,
        trigger_arg1=11,
        trigger_arg2=12,
        trigger_flags=8,
        trigger_padding=13,
        trigger_reserved2=14,
        trigger_reserved3=15,
        trigger_type=9)

    test_file._DebugPrintTrigger(trigger)

  # TODO: add tests for _DebugPrintVariableLengthDataSection.

  @test_lib.skipUnlessHasTestFile(['wintask.job'])
  def testReadFixedLengthDataSection(self):
    """Tests the _ReadFixedLengthDataSection function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = job.WindowsTaskSchedularJobFile(
        output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['wintask.job'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFixedLengthDataSection(file_object)

  @test_lib.skipUnlessHasTestFile(['wintask.job'])
  def testReadVariableLengthDataSection(self):
    """Tests the _ReadVariableLengthDataSection function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = job.WindowsTaskSchedularJobFile(
        output_writer=output_writer)
    test_file._file_size = 896

    test_file_path = self._GetTestFilePath(['wintask.job'])
    with open(test_file_path, 'rb') as file_object:
      file_object.seek(test_file._FIXED_LENGTH_DATA_SECTION_SIZE, os.SEEK_SET)

      test_file._ReadVariableLengthDataSection(file_object)

  @test_lib.skipUnlessHasTestFile(['wintask.job'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    # TODO: add debug=True
    test_file = job.WindowsTaskSchedularJobFile(
        output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['wintask.job'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
