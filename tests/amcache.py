# -*- coding: utf-8 -*-
"""Tests for Windows AMCache (AMCache.hve) files."""

from __future__ import unicode_literals

import unittest

from dtformats import amcache

from tests import test_lib


class WindowsAMCacheFileTest(test_lib.BaseTestCase):
  """Windows AMCache (AMCache.hve) file tests."""

  # pylint: disable=protected-access

  # TODO: add test for _ReadFileKey
  # TODO: add test for _ReadFileReferenceKey

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    test_file_path = self._GetTestFilePath(['Amcache.hve'])
    self._SkipIfPathNotExists(test_file_path)

    output_writer = test_lib.TestOutputWriter()
    test_file = amcache.WindowsAMCacheFile(
        debug=True, output_writer=output_writer)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
