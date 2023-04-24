# -*- coding: utf-8 -*-
"""Tests for Windows Jump List files:
* .automaticDestinations-ms
* .customDestinations-ms
"""

import unittest

import pyolecf

from dtformats import jump_list

from tests import test_lib


class JumpListEntryTest(test_lib.BaseTestCase):
  """Jump list entry tests."""

  def testOpenClose(self):
    """Tests the Open and Close functions."""
    lnk_file_entry = jump_list.JumpListEntry('test')

    # TODO: implement.
    _ = lnk_file_entry

  # TODO: add tests for GetShellItems


class AutomaticDestinationsFileTest(test_lib.BaseTestCase):
  """Automatic Destinations Jump List file tests."""

  # pylint: disable=protected-access

  # TODO: add tests for _FormatIntegerAsPathSize.
  # TODO: add tests for _FormatString.

  def testReadDestList(self):
    """Tests the _ReadDestList function."""
    test_file_path = self._GetTestFilePath([
        '1b4dd67f29cb1962.automaticDestinations-ms'])
    self._SkipIfPathNotExists(test_file_path)

    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.AutomaticDestinationsFile(output_writer=output_writer)

    with open(test_file_path, 'rb') as file_object:
      olecf_file = pyolecf.file()
      olecf_file.open_file_object(file_object)

      try:
        test_file._ReadDestList(olecf_file.root_item)

      finally:
        olecf_file.close()

  # TODO: add tests for _ReadDestListEntry.
  # TODO: add tests for _ReadDestListHeader.

  def testGetJumpListEntriesOnV1File(self):
    """Tests the GetJumpListEntries function on a format version 1 file."""
    test_file_path = self._GetTestFilePath([
        '1b4dd67f29cb1962.automaticDestinations-ms'])
    self._SkipIfPathNotExists(test_file_path)

    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.AutomaticDestinationsFile(output_writer=output_writer)
    test_file.Open(test_file_path)

    try:
      jump_list_entries = list(test_file.GetJumpListEntries())
    finally:
      test_file.Close()

    self.assertEqual(len(jump_list_entries), 11)

  def testGetJumpListEntriesOnV3File(self):
    """Tests the GetJumpListEntries function on a format version 3 file."""
    test_file_path = self._GetTestFilePath([
        '9d1f905ce5044aee.automaticDestinations-ms'])
    self._SkipIfPathNotExists(test_file_path)

    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.AutomaticDestinationsFile(output_writer=output_writer)
    test_file.Open(test_file_path)

    try:
      jump_list_entries = list(test_file.GetJumpListEntries())
    finally:
      test_file.Close()

    self.assertEqual(len(jump_list_entries), 2)


class CustomDestinationsFileTest(test_lib.BaseTestCase):
  """Custom Destinations Jump List file tests."""

  # pylint: disable=protected-access

  # TODO: add tests for _DebugPrintFileFooter.
  # TODO: add tests for _DebugPrintFileHeader.
  # TODO: add tests for _ReadFileFooter.
  # TODO: add tests for _ReadFileHeader.

  def testGetJumpListEntries(self):
    """Tests the GetJumpListEntries function."""
    test_file_path = self._GetTestFilePath([
        '5afe4de1b92fc382.customDestinations-ms'])
    self._SkipIfPathNotExists(test_file_path)

    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.CustomDestinationsFile(output_writer=output_writer)
    test_file.Open(test_file_path)

    try:
      jump_list_entries = list(test_file.GetJumpListEntries())
    finally:
      test_file.Close()

    self.assertEqual(len(jump_list_entries), 9)


if __name__ == '__main__':
  unittest.main()
