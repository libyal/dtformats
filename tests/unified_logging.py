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

  def testReadRangeDescriptors(self):
    """Test the _ReadRangeDescriptors function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    # Testing Version 1
    test_file_path = self._GetTestFilePath(['uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      ranges = list(test_file._ReadRangeDescriptors(file_object, 16, 1, 252))

    self.assertEqual(len(ranges), 252)
    self.assertEqual(ranges[64].range_offset, 1756712)
    self.assertEqual(ranges[64].range_size, 3834)

    # Testing version 2
    test_file_path = self._GetTestFilePath(['uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      ranges = list(test_file._ReadRangeDescriptors(file_object, 16, 2, 263))

    self.assertEqual(len(ranges), 263)
    self.assertEqual(ranges[10].range_offset, 64272)
    self.assertEqual(ranges[10].range_size, 39755)

  def testReadUUIDPath(self):
    """Tests the _ReadUUIDPath function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      uuid_path = test_file._ReadUUIDPath(file_object, 3202606)

    expected_uuid_path = (
        '/System/Library/Extensions/AppleBCMWLANFirmware_Hashstore.kext/'
        'AppleBCMWLANFirmware_Hashstore')
    self.assertEqual(uuid_path, expected_uuid_path)

  def testReadUUIDDescriptors(self):
    """Test the _ReadUUIDDescriptors function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    # Testing Version 1
    test_file_path = self._GetTestFilePath(['uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      uuids = list(test_file._ReadUUIDDescriptors(file_object, 4048, 1, 196))

    self.assertEqual(len(uuids), 196)
    self.assertEqual(uuids[42].text_offset, 9191424)
    self.assertEqual(uuids[42].text_size, 223732)
    expected_path = '/System/Library/Extensions/AppleH8ADBE0.kext/AppleH8ADBE0'
    self.assertEqual(uuids[42].path, expected_path)

    # Testing Version 2
    test_file_path = self._GetTestFilePath(['uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      uuids = list(test_file._ReadUUIDDescriptors(file_object, 6328, 2, 200))

    self.assertEqual(len(uuids), 200)
    self.assertEqual(uuids[197].text_offset, 26816512)
    self.assertEqual(uuids[197].text_size, 43736)
    expected_path = (
        '/System/Library/Extensions/AppleD2207PMU.kext/AppleD2207PMU')
    self.assertEqual(uuids[197].path, expected_path)

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(
        debug=True, output_writer=output_writer)

    # TODO: test of 8E21CAB1DCF936B49F85CF860E6F34EC currently failing.
    test_file_path = self._GetTestFilePath([
        'uuidtext', 'dsc', 'dsc-version1'])
        # 'uuidtext', 'dsc', '8E21CAB1DCF936B49F85CF860E6F34EC'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)
    test_file.Close()


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
    test_file.Close()


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
    test_file.Close()


if __name__ == '__main__':
  unittest.main()
