# -*- coding: utf-8 -*-
"""Tests for the dfVFS helpers."""

import pathlib
import os
import unittest

try:
  from dfvfs.lib import definitions as dfvfs_definitions
  from dfvfs.path import factory as path_spec_factory
except ImportError:
  dfvfs_definitions = None
  path_spec_factory = None

try:
  from dtformats import dfvfs_helpers
except ImportError:
  dfvfs_helpers = None

from tests import test_lib


@unittest.skipIf(dfvfs_helpers is None, 'missing dfVFS support')
class DFVFSFileSystemHelperTest(test_lib.BaseTestCase):
  """dfVFS file system helper tests."""

  def testBasenamePath(self):
    """Tests the BasenamePath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = dfvfs_helpers.DFVFSFileSystemHelper(None)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        dfvfs_definitions.TYPE_INDICATOR_OS, location=test_file_path)
    test_helper.OpenFileSystem(path_spec)

    basename = test_helper.BasenamePath(test_file_path)
    self.assertEqual(basename, 'utmp-linux_libc6')

  def testCheckFileExistsByPath(self):
    """Tests the CheckFileExistsByPath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = dfvfs_helpers.DFVFSFileSystemHelper(None)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        dfvfs_definitions.TYPE_INDICATOR_OS, location=test_file_path)
    test_helper.OpenFileSystem(path_spec)

    result = test_helper.CheckFileExistsByPath(test_file_path)
    self.assertTrue(result)

  def testDirnamePath(self):
    """Tests the DirnamePath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = dfvfs_helpers.DFVFSFileSystemHelper(None)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        dfvfs_definitions.TYPE_INDICATOR_OS, location=test_file_path)
    test_helper.OpenFileSystem(path_spec)

    dirname = test_helper.DirnamePath(test_file_path)
    self.assertEqual(dirname, self._TEST_DATA_PATH)

  def testGetFileSizeByPath(self):
    """Tests the GetFileSizeByPath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = dfvfs_helpers.DFVFSFileSystemHelper(None)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        dfvfs_definitions.TYPE_INDICATOR_OS, location=test_file_path)
    test_helper.OpenFileSystem(path_spec)

    file_size = test_helper.GetFileSizeByPath(test_file_path)
    self.assertEqual(file_size, 5376)

  def testJoinPath(self):
    """Tests the JoinPath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = dfvfs_helpers.DFVFSFileSystemHelper(None)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        dfvfs_definitions.TYPE_INDICATOR_OS, location=test_file_path)
    test_helper.OpenFileSystem(path_spec)

    path_segments = os.path.split(test_file_path)

    path = test_helper.JoinPath(path_segments)
    self.assertEqual(path, test_file_path)

  def testListDirectory(self):
    """Tests the ListDirectory function."""
    test_file_path = self._GetTestFilePath(['unified_logging'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = dfvfs_helpers.DFVFSFileSystemHelper(None)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        dfvfs_definitions.TYPE_INDICATOR_OS, location=test_file_path)
    test_helper.OpenFileSystem(path_spec)

    expected_directory_entries = [
        '0000000000000030.tracev3',
        '0000000000000f85.tracev3',
        'timesync',
        'uuidtext']

    directory_entries = sorted(test_helper.ListDirectory(test_file_path))
    self.assertEqual(directory_entries, expected_directory_entries)

  def testOpenFileByPath(self):
    """Tests the OpenFileByPath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = dfvfs_helpers.DFVFSFileSystemHelper(None)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        dfvfs_definitions.TYPE_INDICATOR_OS, location=test_file_path)
    test_helper.OpenFileSystem(path_spec)

    file_object = test_helper.OpenFileByPath(test_file_path)
    self.assertIsNotNone(file_object)

    file_object.close()

  def testSplitPath(self):
    """Tests the SplitPath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = dfvfs_helpers.DFVFSFileSystemHelper(None)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        dfvfs_definitions.TYPE_INDICATOR_OS, location=test_file_path)
    test_helper.OpenFileSystem(path_spec)

    expected_path_segments = list(pathlib.Path(test_file_path).parts)
    expected_path_segments.pop(0)

    path_segments = test_helper.SplitPath(test_file_path)
    self.assertEqual(path_segments, expected_path_segments)


# TODO: add test for SetDFVFSBackEnd
# TODO: add test for AddDFVFSCLIArguments
# TODO: add test for ParseDFVFSCLIArguments


if __name__ == '__main__':
  unittest.main()
