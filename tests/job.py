# -*- coding: utf-8 -*-
"""Tests for Windows Task Scheduler job files."""

import os
import unittest

from dtformats import job

from tests import test_lib


class WindowsTaskSchedularJobFileTest(test_lib.BaseTestCase):
  """Windows Task Scheduler job file tests."""

  # pylint: disable=protected-access

  # TODO: add test for _FormatDataStream
  # TODO: add test for _FormatDate
  # TODO: add test for _FormatIntegerAsIntervalInMilliseconds
  # TODO: add test for _FormatIntegerAsIntervalInMinutes
  # TODO: add test for _FormatIntegerAsProductVersion
  # TODO: add test for _FormatString
  # TODO: add test for _FormatSystemTime
  # TODO: add test for _FormatTime

  def testReadFixedLengthDataSection(self):
    """Tests the _ReadFixedLengthDataSection function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = job.WindowsTaskSchedularJobFile(
        output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['wintask.job'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFixedLengthDataSection(file_object)

  def testReadVariableLengthDataSection(self):
    """Tests the _ReadVariableLengthDataSection function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = job.WindowsTaskSchedularJobFile(
        output_writer=output_writer)
    test_file._file_size = 896

    test_file_path = self._GetTestFilePath(['wintask.job'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_object.seek(test_file._FIXED_LENGTH_DATA_SECTION_SIZE, os.SEEK_SET)

      test_file._ReadVariableLengthDataSection(file_object)

  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = job.WindowsTaskSchedularJobFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['wintask.job'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
