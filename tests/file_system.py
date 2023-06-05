# -*- coding: utf-8 -*-
"""Tests for the file system helper."""

import pathlib
import platform
import unittest

from dtformats import file_system

from tests import test_lib


class NativeFileSystemHelperTest(test_lib.BaseTestCase):
  """Python native system helper tests."""

  def testBasenamePath(self):
    """Tests the BasenamePath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = file_system.NativeFileSystemHelper()

    basename = test_helper.BasenamePath(test_file_path)
    self.assertEqual(basename, 'utmp-linux_libc6')

  def testCheckFileExistsByPath(self):
    """Tests the CheckFileExistsByPath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = file_system.NativeFileSystemHelper()

    result = test_helper.CheckFileExistsByPath(test_file_path)
    self.assertTrue(result)

  def testDirnamePath(self):
    """Tests the DirnamePath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = file_system.NativeFileSystemHelper()

    dirname = test_helper.DirnamePath(test_file_path)
    self.assertEqual(dirname, self._TEST_DATA_PATH)

  def testGetFileSizeByPath(self):
    """Tests the GetFileSizeByPath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = file_system.NativeFileSystemHelper()

    file_size = test_helper.GetFileSizeByPath(test_file_path)
    self.assertEqual(file_size, 5376)

  def testJoinPath(self):
    """Tests the JoinPath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = file_system.NativeFileSystemHelper()

    path_segments = list(pathlib.Path(test_file_path).parts)
    path_segments.pop(0)

    path = test_helper.JoinPath(path_segments)
    self.assertEqual(path, test_file_path)

  def testListDirectory(self):
    """Tests the ListDirectory function."""
    test_file_path = self._GetTestFilePath(['unified_logging'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = file_system.NativeFileSystemHelper()

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

    test_helper = file_system.NativeFileSystemHelper()

    file_object = test_helper.OpenFileByPath(test_file_path)
    self.assertIsNotNone(file_object)

    file_object.close()

  def testSplitPath(self):
    """Tests the SplitPath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = file_system.NativeFileSystemHelper()

    expected_path_segments = list(pathlib.Path(test_file_path).parts)
    expected_path_segments.pop(0)

    path_segments = test_helper.SplitPath(test_file_path)
    if platform.system() == 'Windows':
      path_segments.pop(0)

    self.assertEqual(path_segments, expected_path_segments)


if __name__ == '__main__':
  unittest.main()
