# -*- coding: utf-8 -*-
"""Tests for Windows Jump List files:
* .automaticDestinations-ms
* .customDestinations-ms
"""

from __future__ import unicode_literals

import unittest
import uuid

from dtformats import jump_list

from tests import test_lib


# TODO: add tests for FromFiletime.
# TODO: add tests for LNKFileEntry.


class AutomaticDestinationsFileTest(test_lib.BaseTestCase):
  """Automatic Destinations Jump List file tests."""

  # pylint: disable=protected-access

  def testDebugPrintDestListEntry(self):
    """Tests the _DebugPrintDestListEntry function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.AutomaticDestinationsFile(output_writer=output_writer)
    test_file._format_version = 3

    uuid_value = uuid.UUID('{97d57d7f-24e9-4de7-9306-b40d93442fbb}')
    data_type_map = test_file._DEST_LIST_ENTRY_V3
    dest_list_entry = data_type_map.CreateStructureValues(
        unknown1=1,
        droid_volume_identifier=uuid_value,
        droid_file_identifier=uuid_value,
        birth_droid_volume_identifier=uuid_value,
        birth_droid_file_identifier=uuid_value,
        hostname='myhost',
        entry_number=2,
        unknown2=3,
        unknown3=4.0,
        last_modification_time=5,
        pin_status=6,
        unknown4=7,
        unknown5=8,
        unknown6=9,
        path_size=6,
        path='mypath',
        unknown7=10)

    test_file._DebugPrintDestListEntry(dest_list_entry)

  def testDebugPrintDestListHeader(self):
    """Tests the _DebugPrintDestListHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.AutomaticDestinationsFile(output_writer=output_writer)
    test_file._format_version = 3

    data_type_map = test_file._DEST_LIST_HEADER
    dest_list_header = data_type_map.CreateStructureValues(
        format_version=1,
        last_entry_number=5,
        last_revision_number=7,
        number_of_entries=2,
        number_of_pinned_entries=3,
        unknown1=4.0,
        unknown2=6,
        unknown3=8)

    test_file._DebugPrintDestListHeader(dest_list_header)

  # TODO: add tests for _ReadDestList.
  # TODO: add tests for _ReadDestListEntry.
  # TODO: add tests for _ReadDestListHeader.
  # TODO: add tests for _ReadLNKFile.
  # TODO: add tests for _ReadLNKFiles.

  @test_lib.skipUnlessHasTestFile([
      '1b4dd67f29cb1962.automaticDestinations-ms'])
  def testReadFileObjectOnV1File(self):
    """Tests the ReadFileObject on a format version 1 file."""
    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.AutomaticDestinationsFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        '1b4dd67f29cb1962.automaticDestinations-ms'])
    test_file.Open(test_file_path)

  @test_lib.skipUnlessHasTestFile([
      '9d1f905ce5044aee.automaticDestinations-ms'])
  def testReadFileObjectOnV3File(self):
    """Tests the ReadFileObject on a format version 3 file."""
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
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = jump_list.CustomDestinationsFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        '5afe4de1b92fc382.customDestinations-ms'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
