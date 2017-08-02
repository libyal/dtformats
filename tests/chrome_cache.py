# -*- coding: utf-8 -*-
"""Tests for Chrome Cache files."""

from __future__ import unicode_literals

import unittest

from dtformats import chrome_cache

from tests import test_lib


class SuperFastHashTest(test_lib.BaseTestCase):
  """Chrome Cache super fast hash tests."""

  def testSuperFastHash(self):
    """Tests the SuperFastHash function."""
    hash_value = chrome_cache.SuperFastHash(b'')
    self.assertEqual(hash_value, 0)

    hash_value = chrome_cache.SuperFastHash(b'Some random data')
    self.assertEqual(hash_value, 1868336631)


class CacheAddressTest(test_lib.BaseTestCase):
  """Chrome Cache address tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    cache_address = chrome_cache.CacheAddress(0x00000000)
    self.assertEqual(cache_address.block_number, None)
    self.assertEqual(cache_address.block_offset, None)
    self.assertEqual(cache_address.block_size, None)
    self.assertEqual(cache_address.filename, None)
    self.assertFalse(cache_address.is_initialized)
    self.assertEqual(cache_address.value, 0x00000000)

    cache_address = chrome_cache.CacheAddress(0x80000000)
    self.assertEqual(cache_address.block_number, None)
    self.assertEqual(cache_address.block_offset, None)
    self.assertEqual(cache_address.block_size, None)
    self.assertEqual(cache_address.filename, 'f_000000')
    self.assertTrue(cache_address.is_initialized)
    self.assertEqual(cache_address.value, 0x80000000)

    cache_address = chrome_cache.CacheAddress(0x10001234)
    self.assertEqual(cache_address.block_number, 4660)
    self.assertEqual(cache_address.block_offset, 0x0002af50)
    self.assertEqual(cache_address.block_size, 0)
    self.assertEqual(cache_address.filename, 'data_0')
    self.assertFalse(cache_address.is_initialized)
    self.assertEqual(cache_address.value, 0x10001234)

  def testGetDebugString(self):
    """Tests the GetDebugString function."""
    cache_address = chrome_cache.CacheAddress(0x00000000)
    debug_string = cache_address.GetDebugString()
    expected_debug_string = '0x00000000 (uninitialized)'
    self.assertEqual(debug_string, expected_debug_string)

    cache_address = chrome_cache.CacheAddress(0x80000000)
    debug_string = cache_address.GetDebugString()
    expected_debug_string = (
        '0x80000000 (initialized: True, file type: Separate file, '
        'filename: f_000000)')
    self.assertEqual(debug_string, expected_debug_string)

    cache_address = chrome_cache.CacheAddress(0x10001234)
    debug_string = cache_address.GetDebugString()
    expected_debug_string = (
        '0x10001234 (initialized: False, file type: Rankings block file, '
        'filename: data_0, block number: 4660, block offset: 0x0002af50, '
        'block size: 0)')
    self.assertEqual(debug_string, expected_debug_string)


class CacheEntryTest(test_lib.BaseTestCase):
  """Chrome Cache entry tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    cache_entry = chrome_cache.CacheEntry()
    self.assertIsNotNone(cache_entry)


class DataBlockFileTest(test_lib.BaseTestCase):
  """Chrome Cache data block file tests."""

  # pylint: disable=protected-access

  # TODO: add tests for _DebugPrintAllocationBitmap.
  # TODO: add tests for _DebugPrintCacheEntry.
  # TODO: add tests for _DebugPrintFileHeader.
  # TODO: add tests for _ReadFileHeader.
  # TODO: add tests for ReadCacheEntry.

  @test_lib.skipUnlessHasTestFile(['chrome_cache', 'data_0'])
  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = chrome_cache.DataBlockFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['chrome_cache', 'data_0'])
    test_file.Open(test_file_path)


class IndexFileTest(test_lib.BaseTestCase):
  """Chrome Cache index file tests."""

  # pylint: disable=protected-access

  # TODO: add tests for _DebugPrintFileHeader.
  # TODO: add tests for _DebugPrintLRUData.
  # TODO: add tests for _ReadFileHeader.
  # TODO: add tests for _ReadLRUData.
  # TODO: add tests for _ReadIndexTable.

  @test_lib.skipUnlessHasTestFile(['chrome_cache', 'index'])
  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = chrome_cache.IndexFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['chrome_cache', 'index'])
    test_file.Open(test_file_path)


class ChromeCacheParserTest(test_lib.BaseTestCase):
  """Chrome Cache parser tests."""

  # TODO: add tests for ParseDirectory.
  # TODO: add tests for ParseFile.


if __name__ == '__main__':
  unittest.main()
