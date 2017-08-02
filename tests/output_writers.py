# -*- coding: utf-8 -*-
"""Tests for output writers."""

from __future__ import unicode_literals

import unittest

from dtformats import output_writers

from tests import test_lib


class StdoutWriterTest(test_lib.BaseTestCase):
  """Stdout output writer tests."""

  def testClose(self):
    """Tests the Close function."""
    test_writer = output_writers.StdoutWriter()

    test_writer.Close()

  def testOpen(self):
    """Tests the Open function."""
    test_writer = output_writers.StdoutWriter()

    test_writer.Open()

  def testWriteText(self):
    """Tests the WriteText function."""
    test_writer = output_writers.StdoutWriter()

    test_writer.WriteText('')


if __name__ == '__main__':
  unittest.main()
