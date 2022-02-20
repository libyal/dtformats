# -*- coding: utf-8 -*-
"""Tests for Windows Task Scheduler job files."""

import unittest

from dtformats import job

from tests import test_lib


class WindowsTaskSchedulerJobFileTest(test_lib.BaseTestCase):
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

  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = job.WindowsTaskSchedulerJobFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['wintask.job'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
