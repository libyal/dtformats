# -*- coding: utf-8 -*-
"""Tests for MacOS fseventsd files."""

import unittest

import pygzipf

from dtformats import fseventsd

from tests import test_lib


class FseventsFileTest(test_lib.BaseTestCase):
  """MacOS fseventsd file tests."""

  # pylint: disable=protected-access

  def testReadDLSPageHeaderV1(self):
    """Tests the _ReadDLSPageHeader function on format version 1."""
    output_writer = test_lib.TestOutputWriter()
    test_file = fseventsd.FseventsFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['fsevents-0000000002d89b58'])
    self._SkipIfPathNotExists(test_file_path)

    gzipf_file = pygzipf.file()
    gzipf_file.open(test_file_path)

    try:
      test_file._ReadDLSPageHeader(gzipf_file, 0)
    finally:
      gzipf_file.close()

  def testReadDLSPageHeaderV2(self):
    """Tests the _ReadDLSPageHeader function on format version 2."""
    output_writer = test_lib.TestOutputWriter()
    test_file = fseventsd.FseventsFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['fsevents-00000000001a0b79'])
    self._SkipIfPathNotExists(test_file_path)

    gzipf_file = pygzipf.file()
    gzipf_file.open(test_file_path)

    try:
      test_file._ReadDLSPageHeader(gzipf_file, 0)
    finally:
      gzipf_file.close()

  def testReadFileObjectV1(self):
    """Tests the ReadFileObject function on format version 1."""
    output_writer = test_lib.TestOutputWriter()
    test_file = fseventsd.FseventsFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['fsevents-0000000002d89b58'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)
    test_file.Close()

  def testReadFileObjectV2(self):
    """Tests the ReadFileObject function on format version 2."""
    output_writer = test_lib.TestOutputWriter()
    test_file = fseventsd.FseventsFile(debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['fsevents-00000000001a0b79'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)
    test_file.Close()


if __name__ == '__main__':
  unittest.main()
