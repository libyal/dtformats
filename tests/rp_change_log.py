# -*- coding: utf-8 -*-
"""Tests for Windows Restore Point change.log files."""

import unittest

from dtformats import rp_change_log

from tests import test_lib


class RestorePointChangeLogFileTest(test_lib.BaseTestCase):
  """Windows Restore Point change.log file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile([u'change.log.1'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = rp_change_log.RestorePointChangeLogFile(
        output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'change.log.1'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
