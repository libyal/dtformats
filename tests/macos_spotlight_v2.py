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

      structure = test_file._ReadFileHeader(f)
      print(structure.signature)
      print(structure.flags)
      print(structure.zero_gap)
      print(structure.unknown_bytes)
      print(structure.header_size)
      print(structure.block_0_size)
      print(structure.block_size)
      print(structure.property_block_location)
      print(structure.category_block_location)
      print(structure.unknown_block_location)
      print(structure.index_1_block_location)
      print(structure.index_2_block_location)
      print(structure.original_filename)

      test_file._ReadBlock0(f)

if __name__ == '__main__':
  unittest.main()
