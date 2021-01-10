# -*- coding: utf-8 -*-
"""CUPS Internet Printing Protocol (IPP) files."""

import os

from dfdatetime import rfc2579_date_time as dfdatetime_rfc2579_date_time

from dtformats import data_format
from dtformats import errors


class CupsIppFile(data_format.BinaryDataFile):
  """CUPS Internet Printing Protocol (IPP) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('cups_ipp.yaml')

  _DELIMITER_TAG_OPERATION_ATTRIBUTES = 0x01
  _DELIMITER_TAG_JOB_ATTRIBUTES = 0x02
  _DELIMITER_TAG_END_OF_ATTRIBUTES = 0x03
  _DELIMITER_TAG_PRINTER_ATTRIBUTES = 0x04
  _DELIMITER_TAG_UNSUPPORTED_ATTRIBUTES = 0x05

  _DELIMITER_TAGS = frozenset([
      _DELIMITER_TAG_OPERATION_ATTRIBUTES,
      _DELIMITER_TAG_JOB_ATTRIBUTES,
      _DELIMITER_TAG_PRINTER_ATTRIBUTES,
      _DELIMITER_TAG_UNSUPPORTED_ATTRIBUTES])

  _TAG_VALUE_INTEGER = 0x21
  _TAG_VALUE_BOOLEAN = 0x22
  _TAG_VALUE_ENUM = 0x23

  _TAG_VALUE_DATE_TIME = 0x31
  _TAG_VALUE_RESOLUTION = 0x32

  _TAG_VALUE_TEXT_WITHOUT_LANGUAGE = 0x41
  _TAG_VALUE_NAME_WITHOUT_LANGUAGE = 0x42

  _TAG_VALUE_KEYWORD = 0x44
  _TAG_VALUE_URI = 0x45
  _TAG_VALUE_URI_SCHEME = 0x46
  _TAG_VALUE_CHARSET = 0x47
  _TAG_VALUE_NATURAL_LANGUAGE = 0x48
  _TAG_VALUE_MEDIA_TYPE = 0x49

  _ASCII_STRING_VALUES = frozenset([
      _TAG_VALUE_KEYWORD,
      _TAG_VALUE_URI,
      _TAG_VALUE_URI_SCHEME,
      _TAG_VALUE_CHARSET,
      _TAG_VALUE_NATURAL_LANGUAGE,
      _TAG_VALUE_MEDIA_TYPE])

  _INTEGER_TAG_VALUES = frozenset([
      _TAG_VALUE_INTEGER, _TAG_VALUE_ENUM])

  _STRING_WITHOUT_LANGUAGE_VALUES = frozenset([
      _TAG_VALUE_TEXT_WITHOUT_LANGUAGE,
      _TAG_VALUE_NAME_WITHOUT_LANGUAGE])

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

  _DEBUG_INFO_ATTRIBUTE = [
      ('tag_value', 'Tag value', '_FormatIntegerAsTagValue'),
      ('name_size', 'Name size', '_FormatIntegerAsDecimal'),
      ('name', 'Name', None),
      ('value_data_size', 'Value data size', '_FormatIntegerAsDecimal'),
      ('value_data', 'Value data', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_HEADER = [
      ('major_version', 'Major version', '_FormatIntegerAsDecimal'),
      ('minor_version', 'Minor version', '_FormatIntegerAsDecimal'),
      ('operation_identifier', 'Operation identifier',
       '_FormatIntegerAsHexadecimal4'),
      ('request_identifier', 'Request identifier',
       '_FormatIntegerAsHexadecimal8')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a CUPS Internet Printing Protocol (IPP) file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(CupsIppFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._last_charset_attribute = 'ascii'

  def _FormatIntegerAsTagValue(self, integer):
    """Formats an integer as a tag value.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a tag value.
    """
    return '0x{0:02x} ({1:s})'.format(
        integer, self._TAG_VALUE_STRINGS.get(integer, 'UNKNOWN'))

  def _ReadAttribute(self, file_object):
    """Reads an attribute.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the attribute cannot be read.
    """
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('cups_ipp_attribute')

    attribute, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'attribute')

    if self._debug:
      self._DebugPrintStructureObject(attribute, self._DEBUG_INFO_ATTRIBUTE)

    value = None
    if attribute.tag_value in self._INTEGER_TAG_VALUES:
      # TODO: correct file offset to point to the start of value_data.
      value = self._ReadIntegerValue(attribute.value_data, file_offset)

      if self._debug:
        value_string = '{0:d}'.format(value)
        self._DebugPrintValue('Value', value_string)

    elif attribute.tag_value == self._TAG_VALUE_BOOLEAN:
      value = self._ReadBooleanValue(attribute.value_data)

      if self._debug:
        value_string = '{0!s}'.format(value)
        self._DebugPrintValue('Value', value_string)

    elif attribute.tag_value == self._TAG_VALUE_DATE_TIME:
      # TODO: correct file offset to point to the start of value_data.
      value = self._ReadDateTimeValue(attribute.value_data, file_offset)

      if self._debug:
        self._DebugPrintValue('Value', value.CopyToDateTimeString())

    elif attribute.tag_value == self._TAG_VALUE_RESOLUTION:
      # TODO: add support for resolution
      pass

    elif attribute.tag_value in self._STRING_WITHOUT_LANGUAGE_VALUES:
      value = attribute.value_data.decode(self._last_charset_attribute)

      if self._debug:
        self._DebugPrintValue('Value', value)

    elif attribute.tag_value in self._ASCII_STRING_VALUES:
      value = attribute.value_data.decode('ascii')

      if self._debug:
        self._DebugPrintValue('Value', value)

      if attribute.tag_value == self._TAG_VALUE_CHARSET:
        self._last_charset_attribute = value

    if self._debug:
      self._DebugPrintText('\n')

  def _ReadAttributesGroup(self, file_object):
    """Reads an attributes group.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the attributes group cannot be read.
    """
    data_type_map = self._GetDataTypeMap('int8')
    tag_value = 0

    while tag_value != self._DELIMITER_TAG_END_OF_ATTRIBUTES:
      file_offset = file_object.tell()

      tag_value, _ = self._ReadStructureFromFileObject(
          file_object, file_offset, data_type_map, 'tag value')

      if tag_value >= 0x10:
        file_object.seek(file_offset, os.SEEK_SET)

        self._ReadAttribute(file_object)

      elif (tag_value != self._DELIMITER_TAG_END_OF_ATTRIBUTES and
            tag_value not in self._DELIMITER_TAGS):
        raise errors.ParseError((
            'Unsupported attributes groups start tag value: '
            '0x{0:02x}.').format(tag_value))

  def _ReadBooleanValue(self, byte_stream):
    """Reads a boolean value.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      bool: boolean value.

    Raises:
      ParseError: when the boolean value cannot be read.
    """
    if byte_stream == b'\x00':
      return False

    if byte_stream == b'\x01':
      return True

    raise errors.ParseError('Unsupported boolean value.')

  def _ReadDateTimeValue(self, byte_stream, file_offset):
    """Reads a RFC2579 date-time value.

    Args:
      byte_stream (bytes): byte stream.
      file_offset (int): offset of the attribute data relative to the start of
          the file-like object.

    Returns:
      dfdatetime.RFC2579DateTime: RFC2579 date-time stored in the value.

    Raises:
      ParseError: when the datetime value cannot be read.
    """
    data_type_map = self._GetDataTypeMap('cups_ipp_datetime_value')

    try:
      value = self._ReadStructureFromByteStream(
          byte_stream, file_offset, data_type_map, 'date-time value')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          'Unable to parse datetime value with error: {0!s}'.format(exception))

    rfc2579_date_time_tuple = (
        value.year, value.month, value.day,
        value.hours, value.minutes, value.seconds, value.deciseconds,
        value.direction_from_utc, value.hours_from_utc, value.minutes_from_utc)
    return dfdatetime_rfc2579_date_time.RFC2579DateTime(
        rfc2579_date_time_tuple=rfc2579_date_time_tuple)

  def _ReadIntegerValue(self, byte_stream, file_offset):
    """Reads an integer value.

    Args:
      byte_stream (bytes): byte stream.
      file_offset (int): offset of the attribute data relative to the start of
          the file-like object.

    Returns:
      int: integer value.

    Raises:
      ParseError: when the integer value cannot be read.
    """
    data_type_map = self._GetDataTypeMap('int32be')

    try:
      return self._ReadStructureFromByteStream(
          byte_stream, file_offset, data_type_map, 'integer value')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          'Unable to parse integer value with error: {0!s}'.format(exception))

  def _ReadHeader(self, file_object):
    """Reads the header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('cups_ipp_header')

    file_offset = file_object.tell()
    header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'header')

    if self._debug:
      self._DebugPrintStructureObject(header, self._DEBUG_INFO_HEADER)

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
