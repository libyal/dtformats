# -*- coding: utf-8 -*-
"""Tests for the binary data format and file."""

import io
import os
import unittest

from dtfabric import fabric as dtfabric_fabric

from dtformats import data_format
from dtformats import errors

from tests import test_lib


class ErrorBytesIO(io.BytesIO):
  """Bytes IO that errors."""

  def read(self, size=None):
    """Reads bytes.

    Args:
      size (Optional[int]): number of bytes to read, where None represents
          all remaining bytes.

    Returns:
      bytes: bytes read.

    Raises:
      IOError: for testing.
    """
    raise IOError(u'Unable to read for testing purposes.')


class BinaryDataFormatTest(test_lib.BaseTestCase):
  """Binary data format tests."""

  _DATA_TYPE_FABRIC_DEFINITION = b'\n'.join([
      b'name: uint32',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 4',
      b'  units: bytes',
      b'---',
      b'name: point3d',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: x',
      b'  data_type: uint32',
      b'- name: y',
      b'  data_type: uint32',
      b'- name: z',
      b'  data_type: uint32'])

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _POINT3D = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'point3d')

  _POINT3D_SIZE = _POINT3D.GetByteSize()

  def testDebugPrintData(self):
    """Tests the _DebugPrintData function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        output_writer=output_writer)

    data = b'\x00\x01\x02\x03\x04\x05\x06'
    test_format._DebugPrintData(u'Description', data)

    expected_output = [
        u'Description:\n',
        (u'0x00000000  00 01 02 03 04 05 06                              '
         u'.......\n')]
    self.assertEqual(output_writer.output, expected_output)

  def testDebugPrintValue(self):
    """Tests the _DebugPrintValue function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        output_writer=output_writer)

    test_format._DebugPrintValue(u'Description', u'Value')

    expected_output = [u'Description\t\t\t\t\t\t\t\t: Value\n']
    self.assertEqual(output_writer.output, expected_output)

  def testFormatDataInHexadecimal(self):
    """Tests the _FormatDataInHexadecimal function."""
    test_format = data_format.BinaryDataFormat()

    data = b'\x00\x01\x02\x03\x04\x05\x06'
    expected_formatted_data = (
        u'0x00000000  00 01 02 03 04 05 06                              '
        u'.......\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'
    expected_formatted_data = (
        u'0x00000000  00 01 02 03 04 05 06 07  08 09                    '
        u'..........\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    expected_formatted_data = (
        u'0x00000000  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  '
        u'................\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = (
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f')
    expected_formatted_data = (
        u'0x00000000  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  '
        u'................\n'
        u'...\n'
        u'0x00000020  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  '
        u'................\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

  def testReadStructure(self):
    """Tests the _ReadStructure function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        output_writer=output_writer)

    file_object = io.BytesIO(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00')

    test_format._ReadStructure(
        file_object, 0, self._POINT3D_SIZE, self._POINT3D, u'point3d')

    # Test missing file-like object.
    with self.assertRaises(ValueError):
      test_format._ReadStructure(
          None, 0, self._POINT3D_SIZE, self._POINT3D, u'point3d')

    # Test missing data map type.
    with self.assertRaises(ValueError):
      test_format._ReadStructure(
          file_object, 0, self._POINT3D_SIZE, None, u'point3d')

    # Test file-like object with insufficient data.
    file_object = io.BytesIO(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00')

    with self.assertRaises(errors.ParseError):
      test_format._ReadStructure(
          file_object, 0, self._POINT3D_SIZE, self._POINT3D, u'point3d')

    # Test file-like object that raises an IOError on read.
    file_object = ErrorBytesIO(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00')

    with self.assertRaises(errors.ParseError):
      test_format._ReadStructure(
          file_object, 0, self._POINT3D_SIZE, self._POINT3D, u'point3d')

    # TODO: improve test coverage.


class BinaryDataFileTest(test_lib.BaseTestCase):
  """Binary data file tests."""

  # TODO: add tests for Open and Close.


if __name__ == '__main__':
  unittest.main()
