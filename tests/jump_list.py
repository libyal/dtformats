# -*- coding: utf-8 -*-
"""Tests for Windows Jump List files:
* .automaticDestinations-ms
* .customDestinations-ms
"""

from __future__ import unicode_literals

import unittest

import pyolecf

from dtformats import jump_list

from tests import test_lib


class LNKFileEntryTest(test_lib.BaseTestCase):
  """Windows Shortcut (LNK) file entry tests."""

  def testOpenClose(self):
    """Tests the Open and Close functions."""
    lnk_file_entry = jump_list.LNKFileEntry('test')

    # TODO: implement.
    _ = lnk_file_entry

  # TODO: add tests for GetShellItems


class AutomaticDestinationsFileTest(test_lib.BaseTestCase):
  """Automatic Destinations Jump List file tests."""

  # pylint: disable=protected-access

  # TODO: add tests for _FormatIntegerAsPathSize.
  # TODO: add tests for _FormatString.

  @test_lib.skipUnlessHasTestFile([
      '1b4dd67f29cb1962.automaticDestinations-ms'])
  def testReadDestList(self):
    """Tests the _ReadDestList function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.AutomaticDestinationsFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        '1b4dd67f29cb1962.automaticDestinations-ms'])
    with open(test_file_path, 'rb') as file_object:
      olecf_file = pyolecf.file()
      olecf_file.open_file_object(file_object)

      try:
        test_file._ReadDestList(olecf_file)

      finally:
        olecf_file.close()

  # TODO: add tests for _ReadDestListEntry.
  # TODO: add tests for _ReadDestListHeader.
  # TODO: add tests for _ReadLNKFile.
  # TODO: add tests for _ReadLNKFiles.

  @test_lib.skipUnlessHasTestFile([
      '1b4dd67f29cb1962.automaticDestinations-ms'])
  def testReadFileObjectOnV1File(self):
    """Tests the ReadFileObject function on a format version 1 file."""
    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.AutomaticDestinationsFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        '1b4dd67f29cb1962.automaticDestinations-ms'])
    test_file.Open(test_file_path)

  @test_lib.skipUnlessHasTestFile([
      '9d1f905ce5044aee.automaticDestinations-ms'])
  def testReadFileObjectOnV3File(self):
    """Tests the ReadFileObject function on a format version 3 file."""
    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.AutomaticDestinationsFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        '9d1f905ce5044aee.automaticDestinations-ms'])
    test_file.Open(test_file_path)


class CustomDestinationsFileTest(test_lib.BaseTestCase):
  """Custom Destinations Jump List file tests."""

  # pylint: disable=protected-access

  # TODO: add tests for _DebugPrintFileFooter.
  # TODO: add tests for _DebugPrintFileHeader.
  # TODO: add tests for _ReadFileFooter.
  # TODO: add tests for _ReadFileHeader.
  # TODO: add tests for _ReadLNKFile.
  # TODO: add tests for _ReadLNKFiles.

  @test_lib.skipUnlessHasTestFile(['5afe4de1b92fc382.customDestinations-ms'])
  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.CustomDestinationsFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        '5afe4de1b92fc382.customDestinations-ms'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
