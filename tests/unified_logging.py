# -*- coding: utf-8 -*-
"""Tests for Apple Unified Logging and Activity Tracing files."""

from __future__ import unicode_literals

import unittest

from dtformats import unified_logging

from tests import test_lib


class DSCFileTest(test_lib.BaseTestCase):
  """Shared-Cache Strings (dsc) file tests."""

  # pylint: disable=protected-access

  @test_lib.skipUnlessHasTestFile([
      'uuidtext', 'dsc', '8E21CAB1DCF936B49F85CF860E6F34EC'])
  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'uuidtext', 'dsc', '8E21CAB1DCF936B49F85CF860E6F34EC'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  @test_lib.skipUnlessHasTestFile([
      'uuidtext', 'dsc', '8E21CAB1DCF936B49F85CF860E6F34EC'])
  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'uuidtext', 'dsc', '8E21CAB1DCF936B49F85CF860E6F34EC'])
    test_file.Open(test_file_path)


class TraceV3FileTest(test_lib.BaseTestCase):
  """Apple Unified Logging and Activity Tracing (tracev3) file tests."""

  # pylint: disable=protected-access

  # TODO: add tests for _FormatArrayOfStrings
  # TODO: add tests for _FormatArrayOfUUIDS
  # TODO: add tests for _FormatStreamAsSignature

  @test_lib.skipUnlessHasTestFile(['0000000000000030.tracev3'])
  def testReadChunkHeader(self):
    """Tests the _ReadChunkHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['0000000000000030.tracev3'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadChunkHeader(file_object, 0)

  # TODO: add tests for _ReadCatalog
  # TODO: add tests for _ReadChunkSet

  @test_lib.skipUnlessHasTestFile(['0000000000000030.tracev3'])
  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['0000000000000030.tracev3'])
    test_file.Open(test_file_path)


class UUIDTextFileTest(test_lib.BaseTestCase):
  """Apple Unified Logging and Activity Tracing (uuidtext) file tests."""

  # pylint: disable=protected-access

  @test_lib.skipUnlessHasTestFile([
      'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  @test_lib.skipUnlessHasTestFile([
      'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
