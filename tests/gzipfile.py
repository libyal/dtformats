# -*- coding: utf-8 -*-
"""Tests for GZip files."""

# Note: do not rename file to gzip.py this can cause the exception:
# AttributeError: 'module' object has no attribute 'GzipFile'
# when using pip.

from __future__ import unicode_literals

import unittest

from dtformats import gzipfile

from tests import test_lib


class GZipFileTest(test_lib.BaseTestCase):
  """GZip file tests."""

  # pylint: disable=protected-access

  # TODO: test _ReadCompressedData function
  # TODO: test _ReadMemberCompressedData function
  # TODO: test _ReadMemberFooter function

  def testReadMemberHeader(self):
    """Tests the _ReadMemberHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = gzipfile.GZipFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['syslog.gz'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      test_file._ReadMemberHeader(file_object)

  def testReadFileObject(self):
    """Tests the ReadFileObject."""
    output_writer = test_lib.TestOutputWriter()
    # TODO: add debug=True
    test_file = gzipfile.GZipFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['syslog.gz'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
