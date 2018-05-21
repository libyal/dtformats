# -*- coding: utf-8 -*-
"""CUPS Internet Printing Protocol (IPP) files."""

from __future__ import unicode_literals

import os

from dtfabric.runtime import fabric as dtfabric_fabric

from dtformats import data_format
from dtformats import errors


class CupsIppFile(data_format.BinaryDataFile):
  """CUPS Internet Printing Protocol (IPP) file."""

  _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
      os.path.dirname(__file__), 'cups_ipp.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap('cups_ipp_header')

  _HEADER_SIZE = _HEADER.GetByteSize()

  _TAG_VALUE = _DATA_TYPE_FABRIC.CreateDataTypeMap('int8')
  _TAG_VALUE_SIZE = _TAG_VALUE.GetByteSize()

  _ATTRIBUTE = _DATA_TYPE_FABRIC.CreateDataTypeMap('cups_ipp_attribute')

  # TODO: add descriptive names.
  _DELIMITER_TAGS = (0x01, 0x02, 0x04, 0x05)

  _TAG_VALUE_STRINGS = {
      0x01: 'operation-attributes-tag',
      0x02: 'job-attributes-tag',
      0x03: 'end-of-attributes-tag',
      0x04: 'printer-attributes-tag',
      0x05: 'unsupported-attributes-tag',

      0x0f: 'chunking-end-of-attributes-tag',

      0x13: 'no-value',

      0x21: 'integer',
      0x22: 'boolean',
      0x23: 'enum',

      0x30: 'octetString',
      0x31: 'dateTime',
      0x32: 'resolution',
      0x33: 'rangeOfInteger',

      0x35: 'textWithLanguage',
      0x36: 'nameWithLanguage',

      0x41: 'textWithoutLanguage',
      0x42: 'nameWithoutLanguage',

      0x44: 'keyword',
      0x45: 'uri',
      0x46: 'uriScheme',
      0x47: 'charset',
      0x48: 'naturalLanguage',
      0x49: 'mimeMediaType',
  }

  def __init__(self, debug=False, output_writer=None):
    """Initializes a CUPS Internet Printing Protocol (IPP) file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(CupsIppFile, self).__init__(
        debug=debug, output_writer=output_writer)

  def _DebugPrintAttribute(self, attribute):
    """Prints attribute debug information.

    Args:
      attribute (cups_ipp_attribute): attribute.
    """
    self._DebugPrintTagValue(attribute.tag_value)

    value_string = '{0:d}'.format(attribute.name_size)
    self._DebugPrintValue('Name size', value_string)

    self._DebugPrintValue('Name', attribute.name)

    value_string = '{0:d}'.format(attribute.value_data_size)
    self._DebugPrintValue('Value data size', value_string)

    self._DebugPrintData('Value data', attribute.value_data)

    self._DebugPrintText('\n')

  def _DebugPrintHeader(self, header):
    """Prints header debug information.

    Args:
      header (cups_ipp_header): header.
    """
    value_string = '{0:d}.{1:d}'.format(
        header.major_version, header.minor_version)
    self._DebugPrintValue('Format version', value_string)

    value_string = '0x{0:04x}'.format(header.operation_identifier)
    self._DebugPrintValue('Operation identifier', value_string)

    value_string = '0x{0:08x}'.format(header.request_identifier)
    self._DebugPrintValue('Request identifier', value_string)

    self._DebugPrintText('\n')

  def _DebugPrintTagValue(self, tag_value):
    """Prints tag value debug information.

    Args:
      tag_value (int8): tag value.
    """
    value_string = '0x{0:02x} ({1:s})'.format(
        tag_value, self._TAG_VALUE_STRINGS.get(tag_value, 'UNKNOWN'))
    self._DebugPrintValue('Tag value', value_string)

    self._DebugPrintText('\n')

  def _ReadAttribute(self, file_object):
    """Reads an attribute.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the attributes group cannot be read.
    """
    file_offset = file_object.tell()

    attribute, _ = self._ReadStructureWithSizeHint(
        file_object, file_offset, self._ATTRIBUTE, 'attribute')

    if self._debug:
      self._DebugPrintAttribute(attribute)

  def _ReadAttributesGroup(self, file_object):
    """Reads an attributes group.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the attributes group cannot be read.
    """
    tag_value = 0

    while tag_value != 0x03:
      file_offset = file_object.tell()
      tag_value = self._ReadStructure(
          file_object, file_offset, self._TAG_VALUE_SIZE, self._TAG_VALUE,
          'tag value')

      if tag_value < 0x10:
        if self._debug:
          self._DebugPrintTagValue(tag_value)

        if tag_value != 0x03 and tag_value not in self._DELIMITER_TAGS:
          raise errors.ParseError((
              'Unsupported attributes groups start tag value: '
              '0x{0:02x}.').format(tag_value))

      else:
        file_object.seek(file_offset, os.SEEK_SET)

        self._ReadAttribute(file_object)

  def _ReadHeader(self, file_object):
    """Reads the header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the header cannot be read.
    """
    file_offset = file_object.tell()
    header = self._ReadStructure(
        file_object, file_offset, self._HEADER_SIZE, self._HEADER, 'header')

    if self._debug:
      self._DebugPrintHeader(header)

  def ReadFileObject(self, file_object):
    """Reads a CUPS Internet Printing Protocol (IPP) file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadHeader(file_object)
    self._ReadAttributesGroup(file_object)

    # TODO: read data.
