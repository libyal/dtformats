# -*- coding: utf-8 -*-
"""Tests for macOS Spotlight Database V2 files."""

from __future__ import unicode_literals

import io
import os
import unittest

from dtformats import errors
from dtformats import macos_spotlight_v2

from tests import test_lib

class MacOSSpotlightDatabaseV2FileTest(test_lib.BaseTestCase):
  """macOS Spotlight Database V2 file tests."""
  def testReadFileHeader(self):
    with open(self._GetTestFilePath(['store.db']), 'rb') as f:
      output_writer = test_lib.TestOutputWriter()
      test_file = macos_spotlight_v2.MacOSSpotlightDatabaseV2File(output_writer=output_writer)

      test_file.ReadFileObject(f)
      # print(len(test_file.categories))
      # print(len(test_file.properties))

if __name__ == '__main__':
  unittest.main()
