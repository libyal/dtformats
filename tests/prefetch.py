# -*- coding: utf-8 -*-
"""Tests for prefetch functions."""

from __future__ import unicode_literals

import unittest

from dtformats import prefetch

from tests import test_lib


class PrefetchTest(test_lib.BaseTestCase):
  """Prefetch function tests."""

  def testCalculatePrefetchHashXP(self):
    """Tests the CalculatePrefetchHashXP function."""
    # Path from Windows XP CMD.EXE-087B4001.pf
    path = '\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\CMD.EXE'

    hash_value = prefetch.CalculatePrefetchHashXP(path)
    self.assertEqual(hash_value, 0x087b4001)

  def testCalculatePrefetchHashVista(self):
    """Tests the CalculatePrefetchHashVista function."""
    # Path from Windows Vista NETCFG.EXE-F61A0ADB.pf
    path = '\\DEVICE\\HARDDISKVOLUME2\\WINDOWS\\SYSTEM32\\NETCFG.EXE'

    hash_value = prefetch.CalculatePrefetchHashVista(path)
    self.assertEqual(hash_value, 0xf61a0adb)

    # Path from Windows 10 NOTEPAD.EXE-D8414F97.pf
    path = '\\VOLUME{01d08edc0cbccaad-3e0d2d25}\\WINDOWS\\SYSTEM32\\NOTEPAD.EXE'
    path = '\\DEVICE\\HARDDISKVOLUME2\\WINDOWS\\SYSTEM32\\NOTEPAD.EXE'
    hash_value = prefetch.CalculatePrefetchHashVista(path)
    self.assertEqual(hash_value, 0xd8414f97)

  def testCalculatePrefetchHash2008(self):
    """Tests the CalculatePrefetchHash2008 function."""
    # Path from Windows 7 NETCFG.EXE-F61A0ADB.pf
    path = '\\DEVICE\\HARDDISKVOLUME2\\WINDOWS\\SYSTEM32\\NETCFG.EXE'

    hash_value = prefetch.CalculatePrefetchHash2008(path)
    self.assertEqual(hash_value, 0xf61a0adb)

    # Path from Windows 8.1 NGEN.EXE-AE594A6B.pf
    path = (
        '\\DEVICE\\HARDDISKVOLUME2\\WINDOWS\\MICROSOFT.NET\\FRAMEWORK64'
        '\\V4.0.30319\\NGEN.EXE')

    hash_value = prefetch.CalculatePrefetchHash2008(path)
    self.assertEqual(hash_value, 0xae594a6b)


if __name__ == '__main__':
  unittest.main()
