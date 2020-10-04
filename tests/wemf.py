# -*- coding: utf-8 -*-
"""Tests for Windows (Enhanced) Metafile Format (WMF and EMF) files."""

from __future__ import unicode_literals

import unittest

from dtformats import wemf

from tests import test_lib


class EMFFileTest(test_lib.BaseTestCase):
  """Enhanced Metafile Format (EMF) file tests."""

  # pylint: disable=protected-access

  def testDebugPrintFileHeader(self):
    """Tests the _DebugPrintFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wemf.EMFFile(output_writer=output_writer)

    data_type_map = test_file._FILE_HEADER
    file_header = data_type_map.CreateStructureValues(
        description_string_offset=0,
        description_string_size=1,
        file_size=2,
        format_version=3,
        number_of_handles=4,
        number_of_records=5,
        record_size=6,
        record_type=7,
        signature=8,
        unknown1=9)

    test_file._DebugPrintFileHeader(file_header)

  def testDebugPrintRecordHeader(self):
    """Tests the _DebugPrintRecordHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wemf.EMFFile(output_writer=output_writer)

    data_type_map = test_file._RECORD_HEADER
    record_header = data_type_map.CreateStructureValues(
        record_size=0,
        record_type=1)

    test_file._DebugPrintRecordHeader(record_header)

  # TODO: add tests for _ReadFileHeader
  # TODO: add tests for _ReadRecord
  # TODO: add tests for _ReadRecordData

  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wemf.EMFFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['Memo.emf'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


class WMFFileTest(test_lib.BaseTestCase):
  """Windows Metafile Format (WMF) file tests."""

  # pylint: disable=protected-access

  def testDebugPrintHeader(self):
    """Tests the _DebugPrintHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wemf.WMFFile(output_writer=output_writer)

    data_type_map = test_file._HEADER
    file_header = data_type_map.CreateStructureValues(
        file_size_lower=0,
        file_size_upper=1,
        file_type=2,
        format_version=3,
        largest_record_size=4,
        maximum_number_of_objects=5,
        number_of_records=6,
        record_size=7)

    test_file._DebugPrintHeader(file_header)

  # TODO: add tests for _DebugPrintPlaceable

  def testDebugPrintRecordHeader(self):
    """Tests the _DebugPrintRecordHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wemf.WMFFile(output_writer=output_writer)

    data_type_map = test_file._RECORD_HEADER
    record_header = data_type_map.CreateStructureValues(
        record_size=0,
        record_type=1)

    test_file._DebugPrintRecordHeader(record_header)

  # TODO: add tests for _ReadHeader
  # TODO: add tests for _ReadPlaceable
  # TODO: add tests for _ReadRecord
  # TODO: add tests for _ReadRecordData

  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wemf.WMFFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['grid.wmf'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
