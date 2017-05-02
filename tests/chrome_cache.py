# -*- coding: utf-8 -*-
"""Tests for the Chrome Cache files."""

import unittest

from dtformats import chrome_cache

from tests import test_lib


class IndexFileTest(test_lib.BaseTestCase):
  """Chrome Cache index file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile([u'chrome_cache', u'index'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = chrome_cache.IndexFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'chrome_cache', u'index'])
    test_file.Open(test_file_path)


class DataBlockFileTest(test_lib.BaseTestCase):
  """Chrome Cache data block file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile([u'chrome_cache', u'data_0'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = chrome_cache.DataBlockFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'chrome_cache', u'data_0'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
