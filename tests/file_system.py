# -*- coding: utf-8 -*-
"""Tests for the file system helper."""

import pathlib
import os
import unittest

from dtformats import file_system

from tests import test_lib


class NativeFileSystemHelperTest(test_lib.BaseTestCase):
  """Python native system helper tests."""

  def testCheckFileExistsByPath(self):
    """Tests the CheckFileExistsByPath function."""
    test_file_path = self._GetTestFilePath(['utmp-linux_libc6'])
    self._SkipIfPathNotExists(test_file_path)

    test_helper = file_system.NativeFileSystemHelper()

    result = test_helper.CheckFileExistsByPath(test_file_path)
    self.assertTrue(result)

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

    path_segments = os.path.split(test_file_path)

    path = test_helper.JoinPath(path_segments)
    self.assertEqual(path, test_file_path)

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

    path_segments = test_helper.SplitPath(test_file_path)
    self.assertEqual(path_segments, expected_path_segments)


if __name__ == '__main__':
  unittest.main()
