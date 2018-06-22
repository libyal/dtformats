# -*- coding: utf-8 -*-
"""Tests for BSM event auditing files."""

from __future__ import unicode_literals

import unittest

from dtformats import bsm

from tests import test_lib


class BSMEventAuditingFileTest(test_lib.BaseTestCase):
  """BSM event auditing file tests."""

  # pylint: disable=protected-access

  @test_lib.skipUnlessHasTestFile(['openbsm.bsm'])
  def testReadToken(self):
    """Tests the _ReadToken function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = bsm.BSMEventAuditingFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['openbsm.bsm'])
    with open(test_file_path, 'rb') as file_object:
      test_file._ReadToken(file_object)

  @test_lib.skipUnlessHasTestFile(['openbsm.bsm'])
  def testReadFileObjectWithOpenBSM(self):
    """Tests the ReadFileObject function with an Open BSM file ."""
    output_writer = test_lib.TestOutputWriter()
    test_file = bsm.BSMEventAuditingFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['openbsm.bsm'])
    test_file.Open(test_file_path)

  @test_lib.skipUnlessHasTestFile(['apple.bsm'])
  def testReadFileObjectWithAppleBSM(self):
    """Tests the ReadFileObject function with an Apple BSM file."""
    output_writer = test_lib.TestOutputWriter()
    test_file = bsm.BSMEventAuditingFile(
        debug=True, output_writer=output_writer)

    test_file_path = self._GetTestFilePath(['apple.bsm'])
    test_file.Open(test_file_path)


if __name__ == '__main__':
  unittest.main()
