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
        'uuidtext', 'dsc', '8E21CAB1DCF936B49F85CF860E6F34EC'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'uuidtext', 'dsc', '8E21CAB1DCF936B49F85CF860E6F34EC'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


class TimesyncFileTest(test_lib.BaseTestCase):
  """Tests for the timesync files."""

  # pylint: disable=protected-access

  def testReadFileRecord(self):
    """Tests the _ReadRecord method."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TimesyncFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'timesync', '0000000000000002.timesync'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      # Boot record
      record, _ = test_file._ReadRecord(file_object, 0)

      self.assertEqual(record.signature, b'\xb0\xbb')
      self.assertEqual(record.size, 48)
      self.assertEqual(record.timebase_numerator, 125)
      self.assertEqual(record.timebase_denominator, 3)
      self.assertEqual(record.timestamp, 1541730321839294000)
      self.assertEqual(record.time_zone_offset, 480)
      self.assertEqual(record.daylight_saving_flag, 0)

      # sync record
      record, _ = test_file._ReadRecord(file_object, 48)

      self.assertEqual(record.signature, b'\x54\x73\x20\x00')
      self.assertEqual(record.kernel_time, 494027973)
      self.assertEqual(record.timestamp, 1541730337313716000)
      self.assertEqual(record.time_zone_offset, 480)
      self.assertEqual(record.daylight_saving_flag, 0)

  def testReadFileObject(self):
    """Tests the ReadFileObject method."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TimesyncFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'timesync', '0000000000000002.timesync'])
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
