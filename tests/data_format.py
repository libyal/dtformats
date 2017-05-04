# -*- coding: utf-8 -*-
"""Tests for binary data format and file."""

import io
import unittest

from dtfabric import data_maps as dtfabric_data_maps
from dtfabric import errors as dtfabric_errors
from dtfabric import fabric as dtfabric_fabric

from dtformats import data_format
from dtformats import errors

from tests import test_lib


class ErrorBytesIO(io.BytesIO):
  """Bytes IO that errors."""

  # The following methods are part of the file-like object interface.

  def read(self, size=None):  # pylint: disable=unused-argument
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


class ErrorDataTypeMap(dtfabric_data_maps.DataTypeMap):
  """Data type map that errors."""

  def MapByteStream(self, byte_stream, **unused_kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      object: mapped value.

    Raises:
      dtfabric.MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    raise dtfabric_errors.MappingError(
        u'Unable to map byte stream for testing purposes.')


class BinaryDataFormatTest(test_lib.BaseTestCase):
  """Binary data format tests."""

  # pylint: disable=protected-access

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
         u'.......\n\n')]
    self.assertEqual(output_writer.output, expected_output)

  def testDebugPrintValue(self):
    """Tests the _DebugPrintValue function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        output_writer=output_writer)

    test_format._DebugPrintValue(u'Description', u'Value')

    expected_output = [u'Description\t\t\t\t\t\t\t\t: Value\n']
    self.assertEqual(output_writer.output, expected_output)

  def testDebugPrintText(self):
    """Tests the _DebugPrintText function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        output_writer=output_writer)

    test_format._DebugPrintText(u'Text')

    expected_output = [u'Text']
    self.assertEqual(output_writer.output, expected_output)

  def testFormatDataInHexadecimal(self):
    """Tests the _FormatDataInHexadecimal function."""
    test_format = data_format.BinaryDataFormat()

    data = b'\x00\x01\x02\x03\x04\x05\x06'
    expected_formatted_data = (
        u'0x00000000  00 01 02 03 04 05 06                              '
        u'.......\n'
        u'\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'
    expected_formatted_data = (
        u'0x00000000  00 01 02 03 04 05 06 07  08 09                    '
        u'..........\n'
        u'\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    expected_formatted_data = (
        u'0x00000000  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  '
        u'................\n'
        u'\n')
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
        u'................\n'
        u'\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

  def testReadData(self):
    """Tests the _ReadData function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        debug=True, output_writer=output_writer)

    file_object = io.BytesIO(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00')

    test_format._ReadData(file_object, 0, self._POINT3D_SIZE, u'point3d')

    # Test with missing file-like object.
    with self.assertRaises(ValueError):
      test_format._ReadData(None, 0, self._POINT3D_SIZE, u'point3d')

    # Test with file-like object with insufficient data.
    file_object = io.BytesIO(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00')

    with self.assertRaises(errors.ParseError):
      test_format._ReadData(file_object, 0, self._POINT3D_SIZE, u'point3d')

    # Test with file-like object that raises an IOError.
    file_object = ErrorBytesIO(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00')

    with self.assertRaises(errors.ParseError):
      test_format._ReadData(file_object, 0, self._POINT3D_SIZE, u'point3d')

  def testReadStructure(self):
    """Tests the _ReadStructure function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        debug=True, output_writer=output_writer)

    file_object = io.BytesIO(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00')

    test_format._ReadStructure(
        file_object, 0, self._POINT3D_SIZE, self._POINT3D, u'point3d')

  def testReadStructureFromByteStream(self):
    """Tests the _ReadStructureFromByteStream function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        debug=True, output_writer=output_writer)

    test_format._ReadStructureFromByteStream(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00', 0,
        self._POINT3D, u'point3d')

    # Test with missing byte stream.
    with self.assertRaises(ValueError):
      test_format._ReadStructureFromByteStream(
          None, 0, self._POINT3D, u'point3d')

    # Test with missing data map type.
    with self.assertRaises(ValueError):
      test_format._ReadStructureFromByteStream(
          b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00', 0, None,
          u'point3d')

    # Test with data type map that raises an dtfabric.MappingError.
    data_type_map = ErrorDataTypeMap(None)

    with self.assertRaises(errors.ParseError):
      test_format._ReadStructureFromByteStream(
          b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00', 0,
          data_type_map, u'point3d')


class BinaryDataFileTest(test_lib.BaseTestCase):
  """Binary data file tests."""

  @test_lib.skipUnlessHasTestFile([u'syslog.bin.cpio'])
  def testOpenClose(self):
    """Tests the Open and Close functions."""
    test_file = data_format.BinaryDataFile()

    test_file_path = self._GetTestFilePath([u'syslog.bin.cpio'])
    test_file.Open(test_file_path)

    with self.assertRaises(IOError):
      test_file.Open(test_file_path)

    test_file.Close()

    with self.assertRaises(IOError):
      test_file.Close()


if __name__ == '__main__':
  unittest.main()
