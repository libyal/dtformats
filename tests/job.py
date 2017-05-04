# -*- coding: utf-8 -*-
"""Tests for Windows Task Scheduler job files."""

import unittest

from dtformats import job

from tests import test_lib


class RestorePointChangeLogFileTest(test_lib.BaseTestCase):
  """Windows Task Scheduler job file tests."""

  # TODO: add tests.

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
