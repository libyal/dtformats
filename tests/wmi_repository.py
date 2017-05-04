# -*- coding: utf-8 -*-
"""Tests for WMI Common Information Model (CIM) repository files."""

import unittest

from dtformats import wmi_repository

from tests import test_lib


class IndexBinaryTreeFileTest(test_lib.BaseTestCase):
  """Index binary-tree (Index.btr) file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile([u'cim', u'INDEX.BTR'])
  @test_lib.skipUnlessHasTestFile([u'cim', u'INDEX.MAP'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    test_file_path = self._GetTestFilePath([u'cim', u'INDEX.MAP'])
    mapping_file = wmi_repository.MappingFile(test_file_path)

    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.IndexBinaryTreeFile(
        mapping_file, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'cim', u'INDEX.BTR'])
    test_file.Open(test_file_path)


class MappingFileTest(test_lib.BaseTestCase):
  """Mappings (*.map) file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile([u'cim', u'INDEX.MAP'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.MappingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'cim', u'INDEX.MAP'])
    test_file.Open(test_file_path)


class ObjectsDataFileTest(test_lib.BaseTestCase):
  """Index binary-tree (Index.btr) file tests."""

  # TODO: add tests.

  @test_lib.skipUnlessHasTestFile([u'cim', u'OBJECTS.DATA'])
  @test_lib.skipUnlessHasTestFile([u'cim', u'OBJECTS.MAP'])
  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    test_file_path = self._GetTestFilePath([u'cim', u'OBJECTS.MAP'])
    mapping_file = wmi_repository.MappingFile(test_file_path)

    output_writer = test_lib.TestOutputWriter()
    test_file = wmi_repository.ObjectsDataFile(
        mapping_file, output_writer=output_writer)

    test_file_path = self._GetTestFilePath([u'cim', u'OBJECTS.DATA'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
