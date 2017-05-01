# -*- coding: utf-8 -*-
"""Tests for the Windows Jump List files:
* .automaticDestinations-ms
* .customDestinations-ms
"""

import unittest

from dtformats import jump_list

from tests import test_lib


class AutomaticDestinationsFileTest(test_lib.BaseTestCase):
  """Automatic Destinations Jump List file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile([
      u'1b4dd67f29cb1962.automaticDestinations-ms'])
  def testReadFileObjectOnV1File(self):
    """Tests the ReadFileObject on a format version 1 file."""
    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.AutomaticDestinationsFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        u'1b4dd67f29cb1962.automaticDestinations-ms'])
    test_file.Open(test_file_path)

  @test_lib.skipUnlessHasTestFile([
      u'9d1f905ce5044aee.automaticDestinations-ms'])
  def testReadFileObjectOnV3File(self):
    """Tests the ReadFileObject on a format version 3 file."""
    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.AutomaticDestinationsFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        u'9d1f905ce5044aee.automaticDestinations-ms'])
    test_file.Open(test_file_path)


class CustomDestinationsFileTest(test_lib.BaseTestCase):
  """Custom Destinations Jump List file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile([u'5afe4de1b92fc382.customDestinations-ms'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.CustomDestinationsFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        u'5afe4de1b92fc382.customDestinations-ms'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
