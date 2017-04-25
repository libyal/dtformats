# -*- coding: utf-8 -*-
"""Tests for the UTMP files."""

import unittest

from dtformats import utmp

from tests import test_lib


class UTMPFileTest(test_lib.BaseTestCase):
  """UTMP file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile([u'utmp'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = utmp.UTMPFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'utmp'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
