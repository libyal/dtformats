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

  # TODO: add tests for _DebugPrintPageBody

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

    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.IndexBinaryTreeFile(
        output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'INDEX.BTR'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)

    test_file.Close()


class MappingFileTest(test_lib.BaseTestCase):
  """Mappings (*.map) file tests."""

  # pylint: disable=protected-access

  # TODO: add tests _DebugPrintMappingTable
  # TODO: add tests _DebugPrintUnknownTable

  def testReadFileFooter(self):
    """Tests the _ReadFileFooter function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'INDEX.MAP'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_object.seek(-4, os.SEEK_END)

      test_file._ReadFileFooter(file_object, format_version=1)

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'INDEX.MAP'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadFileHeader(file_object)

  def testReadMappingTable(self):
    """Tests the _ReadMappingTable function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)
    test_file.format_version = 1

    test_file_path = self._GetTestFilePath(['cim', 'INDEX.MAP'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_object.seek(12, os.SEEK_SET)

      test_file._ReadMappingTable(file_object)

  def testReadUnknownTable(self):
    """Tests the _ReadUnknownTable function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'INDEX.MAP'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_object.seek(572, os.SEEK_SET)

      test_file._ReadUnknownTable(file_object)

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

    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.ObjectsDataFile(
        output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['cim', 'OBJECTS.DATA'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


# TODO: add tests for CIMRepository


if __name__ == '__main__':
  unittest.main()
