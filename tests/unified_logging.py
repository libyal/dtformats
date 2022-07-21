# -*- coding: utf-8 -*-
"""Tests for Apple Unified Logging and Activity Tracing files."""

import unittest

from dtformats import unified_logging

from tests import test_lib


class DSCFileTest(test_lib.BaseTestCase):
  """Shared-Cache Strings (dsc) file tests."""

  # pylint: disable=protected-access

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_header = test_file._ReadFileHeader(file_object)

    self.assertEqual(file_header.signature, b'hcsd')
    self.assertEqual(file_header.major_format_version, 2)
    self.assertEqual(file_header.minor_format_version, 0)
    self.assertEqual(file_header.number_of_ranges, 263)
    self.assertEqual(file_header.number_of_uuids, 200)

  def testReadRanges(self):
    """Tests the _ReadRanges function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    file_offset = 9536

    with open(test_file_path, 'rb') as file_object:
      range_descriptors, _ = test_file._ReadRangeDescriptors(
          16, file_object, 1, 252)

    with open(test_file_path, 'rb') as file_object:
      ranges, _ = test_file._ReadRanges(
          file_offset, file_object, range_descriptors)

      self.assertEqual(len(ranges), 252)
      self.assertEqual(ranges[1], b'%06llu.%06llu %s.%c[%lu] %s\x00')
      self.assertEqual(
          ranges[143], b'AppleUSBTopCaseHIDDriver\x00ATC\x00handleStart\x00')
      self.assertEqual(ranges[217], b'BTDebugService\x00')

  def testReadRangeDescriptors(self):
    """Test the _ReadRangeDescriptors function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    # Testing Version 1
    test_file_path = self._GetTestFilePath([
        'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    file_offset = 16
    version = 1
    number_of_ranges = 252

    with open(test_file_path, 'rb') as file_object:
      range_descriptors, _ = test_file._ReadRangeDescriptors(
          file_offset, file_object, version, number_of_ranges)

    self.assertEqual(len(range_descriptors), 252)
    self.assertEqual(range_descriptors[64].range_offset, 792393)
    self.assertEqual(range_descriptors[64].range_size, 3834)

    # Testing version 2
    test_file_path = self._GetTestFilePath([
        'uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    file_offset = 16
    version = 2
    number_of_ranges = 263

    with open(test_file_path, 'rb') as file_object:
      range_descriptors, _ = test_file._ReadRangeDescriptors(
          file_offset, file_object, version, number_of_ranges)

    self.assertEqual(len(range_descriptors), 263)
    self.assertEqual(range_descriptors[10].range_offset, 64272)
    self.assertEqual(range_descriptors[10].range_size, 39755)

  def testReadUUIDPaths(self):
    """Tests the _ReadUUIDPaths function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    file_offset = 3202606
    number_of_uuids = 196

    with open(test_file_path, 'rb') as file_object:
      uuid_paths, _ = test_file._ReadUUIDPaths(
          file_offset, file_object, number_of_uuids)

    self.assertEqual(len(uuid_paths), number_of_uuids)
    self.assertEqual(
        uuid_paths[8], '/System/Library/Extensions/AppleAVEH8.kext/AppleAVEH8')
    self.assertEqual(
        uuid_paths[190], '/System/Library/Extensions/AGXG5P.kext/AGXG5P')

  def testReadUUIDDescriptors(self):
    """Test the _ReadUUIDDescriptors function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    # Testing Version 1
    test_file_path = self._GetTestFilePath([
        'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    file_offset = 4048
    version = 1
    number_of_uuids = 196

    with open(test_file_path, 'rb') as file_object:
      uuid_descriptors, _ = test_file._ReadUUIDDescriptors(
          file_offset, file_object, version, number_of_uuids)

    self.assertEqual(len(uuid_descriptors), 196)
    self.assertEqual(uuid_descriptors[42].text_offset, 9191424)
    self.assertEqual(uuid_descriptors[42].text_size, 223732)
    self.assertEqual(uuid_descriptors[42].path_offset, 3203048)

    # Testing Version 2
    test_file_path = self._GetTestFilePath([
        'uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    file_offset = 6328
    version = 2
    number_of_uuids = 200

    with open(test_file_path, 'rb') as file_object:
      uuid_descriptors, _ = test_file._ReadUUIDDescriptors(
          file_offset, file_object, version, number_of_uuids)

    self.assertEqual(len(uuid_descriptors), 200)
    self.assertEqual(uuid_descriptors[197].text_offset, 26816512)
    self.assertEqual(uuid_descriptors[197].text_size, 43736)
    self.assertEqual(uuid_descriptors[197].path_offset, 4143087)

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


class TraceV3FileTest(test_lib.BaseTestCase):
  """Apple Unified Logging and Activity Tracing (tracev3) file tests."""

  # pylint: disable=protected-access

  # TODO: add tests for _FormatArrayOfStrings
  # TODO: add tests for _FormatArrayOfUUIDS
  # TODO: add tests for _FormatStreamAsSignature

  def testReadChunkHeader(self):
    """Tests the _ReadChunkHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['0000000000000030.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadChunkHeader(file_object, 0)

  # TODO: add tests for _ReadCatalog
  # TODO: add tests for _ReadChunkSet

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['0000000000000030.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


class UUIDTextFileTest(test_lib.BaseTestCase):
  """Apple Unified Logging and Activity Tracing (uuidtext) file tests."""

  # pylint: disable=protected-access

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
