# -*- coding: utf-8 -*-
"""Tests for the Safari Cookies (Cookies.binarycookies) files."""

import unittest

from dtformats import safari_cookies

from tests import test_lib


class BinaryCookiesFileTest(test_lib.BaseTestCase):
  """Safari Cookies (Cookies.binarycookies) file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile([u'Cookies.binarycookies'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = safari_cookies.BinaryCookiesFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'Cookies.binarycookies'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
