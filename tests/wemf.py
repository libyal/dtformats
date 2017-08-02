# -*- coding: utf-8 -*-
"""Tests for Windows (Enhanced) Metafile Format (WMF and EMF) files."""

from __future__ import unicode_literals

import unittest

from dtformats import wemf

from tests import test_lib


class EMFFileTest(test_lib.BaseTestCase):
  """Enhanced Metafile Format (EMF) file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile(['Memo.emf'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wemf.EMFFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['Memo.emf'])
    test_file.Open(test_file_path)


class WMFFileTest(test_lib.BaseTestCase):
  """Windows Metafile Format (WMF) file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile(['grid.wmf'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wemf.WMFFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['grid.wmf'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
