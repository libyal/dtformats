# -*- coding: utf-8 -*-
"""Tests for WMI Common Information Model (CIM) repository files."""

import os
import unittest

from dtformats import wmi_repository

from tests import test_lib


# TODO: add tests for IndexBinaryTreePage
# TODO: add tests for ObjectRecord
# TODO: add tests for ObjectsDataPage


class IndexBinaryTreeFileTest(test_lib.BaseTestCase):
  """Index binary-tree (Index.btr) file tests."""

  # pylint: disable=protected-access

  # TODO: add tests for _DebugPrintKeyOffsets
  # TODO: add tests for _DebugPrintPageBody
  # TODO: add tests for _DebugPrintPageHeader

  def testDebugPrintPageNumber(self):
    """Tests the _DebugPrintPageNumber function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)

    test_file._DebugPrintPageNumber('Page number', 0x00000001)

    test_file._DebugPrintPageNumber(
        'Page number', 0xffffffff, unavailable_page_numbers=set([0xffffffff]))

  # TODO: add tests for _GetPage
  # TODO: add tests for _ReadPage
  # TODO: add tests for _ReadPageKeyData
  # TODO: add tests for _ReadPageValueData
  # TODO: add tests for _ReadSubPages
  # TODO: add tests for GetFirstMappedPage
  # TODO: add tests for GetMappedPage
  # TODO: add tests for GetRootPage

  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    test_file_path = self._GetTestFilePath(['cim', 'INDEX.MAP'])
    self._SkipIfPathNotExists(test_file_path)

    mapping_file = wmi_repository.MappingFile(test_file_path)

    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.IndexBinaryTreeFile(
        mapping_file, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'INDEX.BTR'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)

    test_file.Close()


class MappingFileTest(test_lib.BaseTestCase):
  """Mappings (*.map) file tests."""

  # pylint: disable=protected-access

  def testDebugPrintPageNumber(self):
    """Tests the _DebugPrintPageNumber function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)

    test_file._DebugPrintPageNumber('Page number', 0x00000001)

    test_file._DebugPrintPageNumber(
        'Page number', 0xffffffff, unavailable_page_numbers=set([0xffffffff]))

  # TODO: add tests _DebugPrintPageNumbersTable

  def testReadFileFooter(self):
    """Tests the _ReadFileFooter function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'INDEX.MAP'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_offset = -1 * test_file._FILE_FOOTER_SIZE
      file_object.seek(file_offset, os.SEEK_END)

      test_file._ReadFileFooter(file_object)

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'INDEX.MAP'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  def testReadMappings(self):
    """Tests the _ReadMappings function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'INDEX.MAP'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_offset = test_file._FILE_HEADER_SIZE
      file_object.seek(file_offset, os.SEEK_SET)

      test_file._ReadMappings(file_object)

  def testReadPageNumbersTable(self):
    """Tests the _ReadPageNumbersTable function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'INDEX.MAP'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_offset = test_file._FILE_HEADER_SIZE
      test_file._ReadPageNumbersTable(file_object, file_offset, 'mappings')

  def testReadUnknownEntries(self):
    """Tests the _ReadUnknownEntries function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'INDEX.MAP'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_object.seek(572, os.SEEK_SET)

      test_file._ReadUnknownEntries(file_object)

  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'INDEX.MAP'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)

    test_file.Close()


class ObjectsDataFileTest(test_lib.BaseTestCase):
  """Index binary-tree (Index.btr) file tests."""

  # TODO: add tests _GetKeyValues
  # TODO: add tests _GetPage
  # TODO: add tests _ReadPage
  # TODO: add tests GetMappedPage
  # TODO: add tests GetObjectRecordByKey

  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    test_file_path = self._GetTestFilePath(['cim', 'OBJECTS.MAP'])
    self._SkipIfPathNotExists(test_file_path)

    mapping_file = wmi_repository.MappingFile(test_file_path)

    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.ObjectsDataFile(
        mapping_file, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'OBJECTS.DATA'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


# TODO: add tests for CIMRepository


if __name__ == '__main__':
  unittest.main()
