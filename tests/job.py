# -*- coding: utf-8 -*-
"""Tests for Windows Task Scheduler job files."""

import unittest
import uuid

from dtfabric import data_maps as dtfabric_data_maps

from dtformats import job

from tests import test_lib


class RestorePointChangeLogFileTest(test_lib.BaseTestCase):
  """Windows Task Scheduler job file tests."""

  # pylint: disable=protected-access

  def testDebugPrintFixedLengthDataSection(self):
    """Tests the _DebugPrintFixedLengthDataSection function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = job.WindowsTaskSchedularJobFile(
        output_writer=output_writer)

    data_type_map = test_file._DATA_TYPE_FABRIC.CreateDataTypeMap(
        u'system_time')
    system_time = data_type_map.CreateStructureValues(
        day_of_month=7,
        hours=17,
        milliseconds=135,
        minutes=41,
        month=5,
        seconds=25,
        weekday=0,
        year=2017)

    uuid_value = uuid.UUID(u'{97d57d7f-24e9-4de7-9306-b40d93442fbb}')
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

  # TODO: add tests for _DebugPrintTrigger.
  # TODO: add tests for _DebugPrintVariableLengthDataSection.
  # TODO: add tests for _ReadFixedLengthDataSection.
  # TODO: add tests for _ReadVariableLengthDataSection.

  @test_lib.skipUnlessHasTestFile([u'wintask.job'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = job.WindowsTaskSchedularJobFile(
        output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'wintask.job'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
