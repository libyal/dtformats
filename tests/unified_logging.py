# -*- coding: utf-8 -*-
"""Tests for Apple Unified Logging and Activity Tracing files."""

import collections
import io
import os
import unittest
import uuid

import lz4.block

from dtformats import errors
from dtformats import unified_logging

from tests import test_lib


class FormatStringOperatorTest(test_lib.BaseTestCase):
  """Format string operator tests."""

  def testGetPythonFormatString(self):
    """Tests the GetPythonFormatString function."""
    format_string_operator = unified_logging.FormatStringOperator(specifier='a')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:f}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='A')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:f}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='c')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:c}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='C')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:c}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='d')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:d}')

    format_string_operator = unified_logging.FormatStringOperator(
        flags='-', specifier='d', width='5')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:<5d}')

    format_string_operator = unified_logging.FormatStringOperator(
        precision='.3', specifier='d', width='3')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:03d}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='D')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:d}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='e')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:e}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='E')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:E}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='f')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:f}')

    format_string_operator = unified_logging.FormatStringOperator(
        precision='.', specifier='f')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:.0f}')

    format_string_operator = unified_logging.FormatStringOperator(
        precision='.2', specifier='f')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:.2f}')

    format_string_operator = unified_logging.FormatStringOperator(
        precision='.*', specifier='f')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:f}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='F')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:F}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='g')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:g}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='G')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:G}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='i')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:d}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='o')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:o}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='O')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:o}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='p')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '0x{0:x}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='P')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:s}')

    format_string_operator = unified_logging.FormatStringOperator(
        precision='.16', specifier='P')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:s}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='s')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:s}')

    format_string_operator = unified_logging.FormatStringOperator(
        specifier='s', width='6')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:>6s}')

    format_string_operator = unified_logging.FormatStringOperator(
        flags='-', specifier='s', width='6')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:<6s}')

    format_string_operator = unified_logging.FormatStringOperator(
        specifier='s', width='6')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:>6s}')

    format_string_operator = unified_logging.FormatStringOperator(
        precision='.', specifier='s')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:s}')

    format_string_operator = unified_logging.FormatStringOperator(
        precision='.0', specifier='s')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:s}')

    format_string_operator = unified_logging.FormatStringOperator(
        precision='.16', specifier='s')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:.16s}')

    format_string_operator = unified_logging.FormatStringOperator(
        precision='.*', specifier='s')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:s}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='S')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:s}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='u')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:d}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='U')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:d}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='x')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:x}')

    format_string_operator = unified_logging.FormatStringOperator(
        flags='#', specifier='x')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:#x}')

    format_string_operator = unified_logging.FormatStringOperator(
        flags='0', specifier='x', width='2')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:02x}')

    format_string_operator = unified_logging.FormatStringOperator(
        precision='.2', specifier='x', width='2')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:2x}')

    format_string_operator = unified_logging.FormatStringOperator(specifier='X')

    format_string = format_string_operator.GetPythonFormatString()
    self.assertEqual(format_string, '{0:X}')


class StringFormatterTest(test_lib.BaseTestCase):
  """String formatter tests."""

  # pylint: disable=protected-access

  def testParseFormatString(self):
    """Tests the ParseFormatString function."""
    test_formatter = unified_logging.StringFormatter()

    test_formatter.ParseFormatString(None)
    self.assertEqual(test_formatter._decoders, [])
    self.assertIsNone(test_formatter._format_string)
    self.assertEqual(len(test_formatter._operators), 0)

    test_formatter.ParseFormatString('text')
    self.assertEqual(test_formatter._decoders, [])
    self.assertEqual(test_formatter._format_string, 'text')
    self.assertEqual(len(test_formatter._operators), 0)

    test_formatter.ParseFormatString('{text}')
    self.assertEqual(test_formatter._decoders, [])
    self.assertEqual(test_formatter._format_string, '{text}')
    self.assertEqual(len(test_formatter._operators), 0)

    test_formatter.ParseFormatString('%%')
    self.assertEqual(test_formatter._decoders, [])
    self.assertEqual(test_formatter._format_string, '%')
    self.assertEqual(len(test_formatter._operators), 0)

    test_formatter.ParseFormatString('%c')
    self.assertEqual(test_formatter._decoders, [['internal:u']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%d')
    self.assertEqual(test_formatter._decoders, [['internal:i']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%3.3d')
    self.assertEqual(test_formatter._decoders, [['internal:i']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('{text: %d}')
    self.assertEqual(test_formatter._decoders, [['internal:i']])
    self.assertEqual(test_formatter._format_string, '{{text: {0:s}}}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString((
        '%{public,signpost.telemetry:number1,'
        'name=SOSSignpostNameSOSCCEnsurePeerRegistration}d'))
    self.assertEqual(test_formatter._decoders, [['signpost.telemetry:number1']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%D')
    self.assertEqual(test_formatter._decoders, [['internal:i']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%i')
    self.assertEqual(test_formatter._decoders, [['internal:i']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%o')
    self.assertEqual(test_formatter._decoders, [['internal:u']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%O')
    self.assertEqual(test_formatter._decoders, [['internal:u']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%p')
    self.assertEqual(test_formatter._decoders, [['internal:u']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%u')
    self.assertEqual(test_formatter._decoders, [['internal:u']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString(
        '%{signpost.description:attribute,public}llu')
    self.assertEqual(test_formatter._decoders, [
        ['signpost.description:attribute']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%U')
    self.assertEqual(test_formatter._decoders, [['internal:u']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%x')
    self.assertEqual(test_formatter._decoders, [['internal:u']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%#llx')
    self.assertEqual(test_formatter._decoders, [['internal:u']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('0x%lx')
    self.assertEqual(test_formatter._decoders, [['internal:u']])
    self.assertEqual(test_formatter._format_string, '0x{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('0x%2.2x')
    self.assertEqual(test_formatter._decoders, [['internal:u']])
    self.assertEqual(test_formatter._format_string, '0x{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('0x%02x')
    self.assertEqual(test_formatter._decoders, [['internal:u']])
    self.assertEqual(test_formatter._format_string, '0x{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%X')
    self.assertEqual(test_formatter._decoders, [['internal:u']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%e')
    self.assertEqual(test_formatter._decoders, [['internal:f']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%E')
    self.assertEqual(test_formatter._decoders, [['internal:f']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%f')
    self.assertEqual(test_formatter._decoders, [['internal:f']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%.f')
    self.assertEqual(test_formatter._decoders, [['internal:f']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%{signpost.telemetry:number2,public}.2f')
    self.assertEqual(test_formatter._decoders, [['signpost.telemetry:number2']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%F')
    self.assertEqual(test_formatter._decoders, [['internal:f']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%g')
    self.assertEqual(test_formatter._decoders, [['internal:f']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%G')
    self.assertEqual(test_formatter._decoders, [['internal:f']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%s')
    self.assertEqual(test_formatter._decoders, [['internal:s']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%-6s')
    self.assertEqual(test_formatter._decoders, [['internal:s']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%.*s')
    self.assertEqual(test_formatter._decoders, [['internal:s']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%{public}s')
    self.assertEqual(test_formatter._decoders, [['internal:s']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%{public}@')
    self.assertEqual(test_formatter._decoders, [['internal:s']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%@')
    self.assertEqual(test_formatter._decoders, [['internal:s']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%m')
    self.assertEqual(test_formatter._decoders, [['internal:m']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%.16P')
    self.assertEqual(test_formatter._decoders, [['internal:s']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%{public,uuid_t}.16P')
    self.assertEqual(test_formatter._decoders, [['uuid_t']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%32s:%-5d')
    self.assertEqual(test_formatter._decoders, [['internal:s'], ['internal:i']])
    self.assertEqual(test_formatter._format_string, '{0:s}:{1:s}')
    self.assertEqual(len(test_formatter._operators), 2)

    format_string = test_formatter._operators[0].GetPythonFormatString()
    self.assertEqual(format_string, '{0:>32s}')

    format_string = test_formatter._operators[1].GetPythonFormatString()
    self.assertEqual(format_string, '{0:<5d}')

    test_formatter.ParseFormatString('"msg%{public}.0s"')
    self.assertEqual(test_formatter._decoders, [['internal:s']])
    self.assertEqual(test_formatter._format_string, '"msg{0:s}"')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString('%{public, location:escape_only}s')
    self.assertEqual(test_formatter._decoders, [['location:escape_only']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString(
        '%{private, mask.hash, mdnsresponder:ip_addr}.20P')
    self.assertEqual(test_formatter._decoders, [[
        'mask.hash', 'mdnsresponder:ip_addr']])
    self.assertEqual(test_formatter._format_string, '{0:s}')
    self.assertEqual(len(test_formatter._operators), 1)

    test_formatter.ParseFormatString((
        'Transform Manager cache hits: %d / %ld (%.2f%%). Size = %zu entries '
        '(events), %zu transforms, %zu bytes'))
    self.assertEqual(test_formatter._decoders, [
        ['internal:i'], ['internal:i'], ['internal:f'], ['internal:u'],
        ['internal:u'], ['internal:u']])
    self.assertEqual(test_formatter._format_string, (
        'Transform Manager cache hits: {0:s} / {1:s} ({2:s}%). Size = {3:s} '
        'entries (events), {4:s} transforms, {5:s} bytes'))
    self.assertEqual(len(test_formatter._operators), 6)

    test_formatter.ParseFormatString((
        '#%08x [%s] resolveDNSRecords -> public addresses: [%ld]%{private}@, '
        'favored servers: [%ld]%@, validityInterval %.f'))
    self.assertEqual(test_formatter._decoders, [
        ['internal:u'], ['internal:s'], ['internal:i'], ['internal:s'],
        ['internal:i'], ['internal:s'], ['internal:f']])
    self.assertEqual(test_formatter._format_string, (
        '#{0:s} [{1:s}] resolveDNSRecords -> public addresses: [{2:s}]{3:s}, '
        'favored servers: [{4:s}]{5:s}, validityInterval {6:s}'))
    self.assertEqual(len(test_formatter._operators), 7)


class BooleanFormatStringDecoderTest(test_lib.BaseTestCase):
  """Boolean value format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.BooleanFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'\x01\x00\x00\x00')
    self.assertEqual(formatted_value, 'true')

    formatted_value = test_decoder.FormatValue(b'\x00\x00\x00\x00')
    self.assertEqual(formatted_value, 'false')


class DateTimeInSecondsFormatStringDecoderTest(test_lib.BaseTestCase):
  """Date and time value in seconds format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.DateTimeInSecondsFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'\x78\x9b\x69\x64')
    self.assertEqual(formatted_value, '2023-05-21 04:18:00')


class ErrorCodeFormatStringDecoderTest(test_lib.BaseTestCase):
  """Error code format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.ErrorCodeFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'\x16\x00\x00\x00')
    self.assertEqual(formatted_value, 'Invalid argument')


class ExtendedErrorCodeFormatStringDecoderTest(test_lib.BaseTestCase):
  """Extended error code format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.ExtendedErrorCodeFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'\x02\x00\x00\x00')
    self.assertEqual(formatted_value, '[2: No such file or directory]')


class FileModeFormatStringDecoderTest(test_lib.BaseTestCase):
  """File mode format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.FileModeFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'\xc0\x01\x00\x00')
    self.assertEqual(formatted_value, '-rwx------')


class FloatingPointFormatStringDecoderTest(test_lib.BaseTestCase):
  """Floating-point format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.FloatingPointFormatStringDecoder()

    format_string_operator = unified_logging.FormatStringOperator(specifier='f')

    formatted_value = test_decoder.FormatValue(
        b'\xa4\x70\x45\x41', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '12.340000')

    formatted_value = test_decoder.FormatValue(
        b'\xec\x51\xb8\x1e\x45\x1a\xb3\x40',
        format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '4890.270000')


class IPv4FormatStringDecoderTest(test_lib.BaseTestCase):
  """IPv4 value format string decoder tests."""

  _VALUE_DATA = bytes(bytearray([0xc0, 0xa8, 0xcc, 0x62]))

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.IPv4FormatStringDecoder()

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA)
    self.assertEqual(formatted_value, '192.168.204.98')


class IPv6FormatStringDecoderTest(test_lib.BaseTestCase):
  """IPv6 value format string decoder tests."""

  _VALUE_DATA = bytes(bytearray([
      0x20, 0x01, 0x0d, 0xb8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00,
      0x00, 0x42, 0x83, 0x29]))

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.IPv6FormatStringDecoder()

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA)
    self.assertEqual(formatted_value, '2001:0db8:0000:0000:0000:ff00:0042:8329')


class LocationClientAuthorizationStatusFormatStringDecoder(
    test_lib.BaseTestCase):
  """Location client authorization status format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = (
        unified_logging.LocationClientAuthorizationStatusFormatStringDecoder())

    formatted_value = test_decoder.FormatValue(b'\x02\x00\x00\x00')
    self.assertEqual(formatted_value, '"Denied"')


class LocationClientManagerStateFormatStringDecoderTest(test_lib.BaseTestCase):
  """Location client manager state value format string decoder tests."""

  _VALUE_DATA = bytes(bytearray([
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = (
        unified_logging.LocationClientManagerStateFormatStringDecoder())

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA)
    self.assertEqual(formatted_value, (
        '{"locationRestricted":false,"locationServicesEnabledStatus":0}'))


class LocationLocationManagerStateFormatStringDecoderTest(
    test_lib.BaseTestCase):
  """Location location manager state value format string decoder tests."""

  _VALUE_DATA_V1 = bytes(bytearray([
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf0, 0xbf, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x59, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf0, 0x3f, 0x01, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00]))

  _VALUE_DATA_V2 = bytes(bytearray([
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf0, 0xbf, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x59, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf0, 0x3f, 0x01, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = (
        unified_logging.LocationLocationManagerStateFormatStringDecoder())

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA_V1)
    self.assertEqual(formatted_value, (
        '{"previousAuthorizationStatusValid":false,"paused":false,'
        '"requestingLocation":false,"desiredAccuracy":100,'
        '"allowsBackgroundLocationUpdates":false,'
        '"dynamicAccuracyReductionEnabled":false,"distanceFilter":-1,'
        '"allowsLocationPrompts":true,"activityType":72057594037927937,'
        '"pausesLocationUpdatesAutomatially":0,'
        '"showsBackgroundLocationIndicator":false,"updatingLocation":false,'
        '"requestingRanging":false,"updatingHeading":false,'
        '"previousAuthorizationStatus":0,"allowsMapCorrection":false,'
        '"allowsAlteredAccessoryLoctions":false,"updatingRanging":false,'
        '"limitsPrecision":false,"headingFilter":1}'))

    test_decoder = (
        unified_logging.LocationLocationManagerStateFormatStringDecoder())

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA_V2)
    self.assertEqual(formatted_value, (
        '{"previousAuthorizationStatusValid":false,"paused":false,'
        '"requestingLocation":false,"updatingVehicleSpeed":false,'
        '"desiredAccuracy":100,"allowsBackgroundLocationUpdates":false,'
        '"dynamicAccuracyReductionEnabled":false,"distanceFilter":-1,'
        '"allowsLocationPrompts":true,"activityType":0,'
        '"groundAltitudeEnabled":false,"pausesLocationUpdatesAutomatially":1,'
        '"fusionInfoEnabled":false,"isAuthorizedForWidgetUpdates":false,'
        '"updatingVehicleHeading":false,"batchingLocation":false,'
        '"showsBackgroundLocationIndicator":false,"updatingLocation":false,'
        '"requestingRanging":false,"updatingHeading":false,'
        '"previousAuthorizationStatus":0,"allowsMapCorrection":true,'
        '"matchInfoEnabled":false,"allowsAlteredAccessoryLoctions":false,'
        '"updatingRanging":false,"limitsPrecision":false,'
        '"courtesyPromptNeeded":false,"headingFilter":1}'))


class LocationEscapeOnlyFormatStringDecoderTest(test_lib.BaseTestCase):
  """Location escape only format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.LocationEscapeOnlyFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'')
    self.assertEqual(formatted_value, '""')

    formatted_value = test_decoder.FormatValue(
        b'NSBundle </System/Library/LocationBundles/TimeZone.bundle>')
    self.assertEqual(formatted_value, (
        '"NSBundle <\\/System\\/Library\\/LocationBundles\\/TimeZone.bundle>"'))


class LocationSQLiteResultFormatStringDecoderTest(test_lib.BaseTestCase):
  """Location SQLite result format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.LocationSQLiteResultFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'\x00\x00\x00\x00')
    self.assertEqual(formatted_value, '"SQLITE_OK"')


class MaskHashFormatStringDecoderTest(test_lib.BaseTestCase):
  """Mask hash format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.MaskHashFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(
        b'\x1d\x1f\xd3\xfb\xe9\xa6Fj\xb72\x7f\xb6\x98a\x02\xb2')
    self.assertEqual(formatted_value, (
        '<mask.hash: \'HR/T++mmRmq3Mn+2mGECsg==\'>'))

    formatted_value = test_decoder.FormatValue(b'')
    self.assertEqual(formatted_value, '<mask.hash: (null)>')


class MDNSDNSCountersFormatStringDecoderTest(test_lib.BaseTestCase):
  """mDNS DNS counters format string decoder tests."""

  _VALUE_DATA = bytes(bytearray([
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00]))

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.MDNSDNSCountersFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA)
    self.assertEqual(formatted_value, '1/0/0/0')


class MDNSDNSHeaderFormatStringDecoderTest(test_lib.BaseTestCase):
  """mDNS DNS header format string decoder tests."""

  _VALUE_DATA = bytes(bytearray([
      0x00, 0x00, 0x81, 0x80, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.MDNSDNSHeaderFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA)
    self.assertEqual(formatted_value, (
        'id: 0x0000 (0), flags: 0x8180 (R/Query, RD, RA, NoError), '
        'counts: 1/0/0/0'))


class MDNSDNSIdentifierAndFlagsFormatStringDecoder(test_lib.BaseTestCase):
  """mDNS DNS header format string decoder tests."""

  _VALUE_DATA = bytes(bytearray([
      0x00, 0x01, 0xe9, 0x62, 0x00, 0x00, 0x00, 0x00]))

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = (
        unified_logging.MDNSDNSIdentifierAndFlagsFormatStringDecoder())

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA)
    self.assertEqual(formatted_value, (
        'id: 0x62E9 (25321), flags: 0x0100 (Q/Query, RD, NoError)'))


class MDNSProtocolFormatStringDecoderTest(test_lib.BaseTestCase):
  """mDNS protocol format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.MDNSProtocolFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'\x01\x00\x00\x00')
    self.assertEqual(formatted_value, 'UDP')


class MDNSReasonFormatStringDecoder(test_lib.BaseTestCase):
  """mDNS reason format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.MDNSReasonFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'\x03\x00\x00\x00')
    self.assertEqual(formatted_value, 'query-suppressed')


class MDNSResourceRecordTypeFormatStringDecoderTest(test_lib.BaseTestCase):
  """mDNS resource record type format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.MDNSResourceRecordTypeFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'\x01\x00\x00\x00')
    self.assertEqual(formatted_value, 'A')


class OpenDirectoryErrorFormatStringDecoderTest(test_lib.BaseTestCase):
  """Open Directory error format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.OpenDirectoryErrorFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'\x00\x00\x00\x00')
    self.assertEqual(formatted_value, 'ODNoError')


class OpenDirectoryMembershipDetailsFormatStringDecoderTest(
    test_lib.BaseTestCase):
  """Open Directory membership details format string decoder tests."""

  _VALUE_DATA1 = bytes(bytearray([
      0x23, 0x58, 0x00, 0x00, 0x00, 0x2f, 0x4c, 0x6f, 0x63, 0x61, 0x6c, 0x2f,
      0x44, 0x65, 0x66, 0x61, 0x75, 0x6c, 0x74, 0x00]))

  _VALUE_DATA2 = bytes(bytearray([
      0x44, 0x77, 0x68, 0x65, 0x65, 0x6c, 0x00, 0x2f, 0x4c, 0x6f, 0x63, 0x61,
      0x6c, 0x2f, 0x44, 0x65, 0x66, 0x61, 0x75, 0x6c, 0x74, 0x00]))

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = (
        unified_logging.OpenDirectoryMembershipDetailsFormatStringDecoder())

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA1)
    self.assertEqual(formatted_value, 'user: 88@/Local/Default')

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA2)
    self.assertEqual(formatted_value, 'group: wheel@/Local/Default')


class OpenDirectoryMembershipTypeFormatStringDecoderTest(test_lib.BaseTestCase):
  """Open Directory membership type format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = (
        unified_logging.OpenDirectoryMembershipTypeFormatStringDecoder())

    formatted_value = test_decoder.FormatValue(b'\x06\x00\x00\x00')
    self.assertEqual(formatted_value, 'UUID')


class SignedIntegerFormatStringDecoderTest(test_lib.BaseTestCase):
  """Signed integer format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.SignedIntegerFormatStringDecoder()

    format_string_operator = unified_logging.FormatStringOperator(specifier='d')

    formatted_value = test_decoder.FormatValue(
        b'\x01', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '1')

    formatted_value = test_decoder.FormatValue(
        b'\x02\x01', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '258')

    formatted_value = test_decoder.FormatValue(
        b'\x04\x03\x02\x01', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '16909060')

    formatted_value = test_decoder.FormatValue(
        b'\x08\x07\x06\x05\x04\x03\x02\x01',
        format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '72623859790382856')


class SignpostDescriptionAttributeFormatStringDecoderTest(
    test_lib.BaseTestCase):
  """Signpost description attribute value format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = (
        unified_logging.SignpostDescriptionAttributeFormatStringDecoder())

    format_string_operator = unified_logging.FormatStringOperator(specifier='s')

    formatted_value = test_decoder.FormatValue(
        b'', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, (
        '__##__signpost.description#____#attribute#_##_###__##'))

    formatted_value = test_decoder.FormatValue(
        b'efilogin-helper', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, (
        '__##__signpost.description#____#attribute#_##_#efilogin-helper##__##'))

    format_string_operator = unified_logging.FormatStringOperator(specifier='d')

    formatted_value = test_decoder.FormatValue(
        b'\x1d\xc6\x00\x00', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, (
        '__##__signpost.description#____#attribute#_##_#50717##__##'))

    format_string_operator = unified_logging.FormatStringOperator(specifier='f')

    formatted_value = test_decoder.FormatValue(
        b'\xff\xff\xff\xff\x91\xff\xb9\x3f',
        format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, (
        '__##__signpost.description#____#attribute#_##_#'
        '0.1015559434890747##__##'))


class SignpostDescriptionTimeFormatStringDecoderTest(test_lib.BaseTestCase):
  """Signpost description time value format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.SignpostDescriptionTimeFormatStringDecoder(
        time='begin')

    formatted_value = test_decoder.FormatValue(
        b'\x9f\x3b\xa6\x1e\xea\x00\x00\x00')
    self.assertEqual(formatted_value, (
        '__##__signpost.description#____#begin_time#_##_#1005536557983##__##'))

    test_decoder = unified_logging.SignpostDescriptionTimeFormatStringDecoder(
        time='end')

    formatted_value = test_decoder.FormatValue(
        b'\x4f\x2f\xc4\x2b\xea\x00\x00\x00')
    self.assertEqual(formatted_value, (
        '__##__signpost.description#____#end_time#_##_#1005756624719##__##'))


class SignpostTelemetryNumberFormatStringDecoderTest(test_lib.BaseTestCase):
  """Signpost telemetry number value format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.SignpostTelemetryNumberFormatStringDecoder()

    format_string_operator = unified_logging.FormatStringOperator(specifier='d')

    formatted_value = test_decoder.FormatValue(
        b'\x09\x00\x00\x00', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, (
        '__##__signpost.telemetry#____#number1#_##_#9##__##'))

    format_string_operator = unified_logging.FormatStringOperator(specifier='f')

    formatted_value = test_decoder.FormatValue(
        b'\x00\x60\xbc\x40', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, (
        '__##__signpost.telemetry#____#number1#_##_#5.88671875##__##'))

    formatted_value = test_decoder.FormatValue(
        b'\x00\x80\xbb\x40', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, (
        '__##__signpost.telemetry#____#number1#_##_#5.859375##__##'))

    test_decoder = unified_logging.SignpostTelemetryNumberFormatStringDecoder(
        number=2)

    format_string_operator = unified_logging.FormatStringOperator(specifier='d')

    formatted_value = test_decoder.FormatValue(
        b'\x09\x00\x00\x00', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, (
        '__##__signpost.telemetry#____#number2#_##_#9##__##'))


class SignpostTelemetryStringFormatStringDecoderTest(test_lib.BaseTestCase):
  """Signpost telemetry string value format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.SignpostTelemetryStringFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'executeQueryBegin')
    self.assertEqual(formatted_value, (
        '__##__signpost.telemetry#____#string1#_##_#executeQueryBegin##__##'))

    test_decoder = unified_logging.SignpostTelemetryStringFormatStringDecoder(
        number=2)

    formatted_value = test_decoder.FormatValue(b'executeQueryBegin')
    self.assertEqual(formatted_value, (
        '__##__signpost.telemetry#____#string2#_##_#executeQueryBegin##__##'))


class SocketAddressFormatStringDecoderTest(test_lib.BaseTestCase):
  """Socket address value format string decoder tests."""

  _VALUE_DATA1 = bytes(bytearray([
      0x10, 0x02, 0x00, 0x00, 0x17, 0x32, 0x62, 0x82, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00]))

  _VALUE_DATA2 = bytes(bytearray([
      0x1c, 0x1e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00]))

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.SocketAddressFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(b'')
    self.assertEqual(formatted_value, '<NULL>')

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA1)
    self.assertEqual(formatted_value, '23.50.98.130')

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA2)
    self.assertEqual(formatted_value, '::')


class StringFormatStringDecoderTest(test_lib.BaseTestCase):
  """String format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.StringFormatStringDecoder()

    format_string_operator = unified_logging.FormatStringOperator(specifier='s')

    formatted_value = test_decoder.FormatValue(
        b'', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '(null)')

    formatted_value = test_decoder.FormatValue(
        b'test', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, 'test')


class UnsignedIntegerFormatStringDecoderTest(test_lib.BaseTestCase):
  """Unsigned integer format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.UnsignedIntegerFormatStringDecoder()

    format_string_operator = unified_logging.FormatStringOperator(specifier='u')

    formatted_value = test_decoder.FormatValue(
        b'\x01', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '1')

    formatted_value = test_decoder.FormatValue(
        b'\x02\x01', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '258')

    formatted_value = test_decoder.FormatValue(
        b'\x04\x03\x02\x01', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '16909060')

    formatted_value = test_decoder.FormatValue(
        b'\x08\x07\x06\x05\x04\x03\x02\x01',
       format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '72623859790382856')

    format_string_operator = unified_logging.FormatStringOperator(
        flags='#', specifier='x')

    formatted_value = test_decoder.FormatValue(
        b'\x00\x00\x00\x00', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '0')

    formatted_value = test_decoder.FormatValue(
        b'\x01\x00\x00\x00', format_string_operator=format_string_operator)
    self.assertEqual(formatted_value, '0x1')


class UUIDFormatStringDecoderTest(test_lib.BaseTestCase):
  """UUID value format string decoder tests."""

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = unified_logging.UUIDFormatStringDecoder()

    formatted_value = test_decoder.FormatValue(
        b'\x1d\x1f\xd3\xfb\xe9\xa6Fj\xb72\x7f\xb6\x98a\x02\xb2')
    self.assertEqual(formatted_value, '1D1FD3FB-E9A6-466A-B732-7FB6986102B2')


class WindowsNTSecurityIdentifierFormatStringDecoderTest(test_lib.BaseTestCase):
  """Open Directory membership details format string decoder tests."""

  _VALUE_DATA = bytes(bytearray([
      0x01, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x05, 0x15, 0x00, 0x00, 0x00,
      0x16, 0x00, 0x00, 0x00, 0x17, 0x00, 0x00, 0x00, 0x18, 0x00, 0x00, 0x00,
      0x19, 0x00, 0x00, 0x00]))

  def testFormatValue(self):
    """Tests the FormatValue function."""
    test_decoder = (
        unified_logging.WindowsNTSecurityIdentifierFormatStringDecoder())

    formatted_value = test_decoder.FormatValue(self._VALUE_DATA)
    self.assertEqual(formatted_value, 'S-1-5-21-22-23-24-25')


class DSCFileTest(test_lib.BaseTestCase):
  """Shared-Cache Strings (dsc) file tests."""

  # pylint: disable=protected-access

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_header = test_file._ReadFileHeader(file_object)

    self.assertEqual(file_header.signature, b'hcsd')
    self.assertEqual(file_header.major_format_version, 2)
    self.assertEqual(file_header.minor_format_version, 0)
    self.assertEqual(file_header.number_of_ranges, 263)
    self.assertEqual(file_header.number_of_uuids, 200)

  # TODO: add test for _ReadString

  def testReadImagePath(self):
    """Tests the _ReadImagePath function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      uuid_path = test_file._ReadImagePath(file_object, 3202606)

    expected_uuid_path = (
        '/System/Library/Extensions/AppleBCMWLANFirmware_Hashstore.kext/'
        'AppleBCMWLANFirmware_Hashstore')
    self.assertEqual(uuid_path, expected_uuid_path)

  def testReadRangeDescriptors(self):
    """Test the _ReadRangeDescriptors function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    # Testing Version 1
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      ranges = list(test_file._ReadRangeDescriptors(file_object, 16, 1, 252))

    self.assertEqual(len(ranges), 252)
    self.assertEqual(ranges[64].range_offset, 1756712)
    self.assertEqual(ranges[64].range_size, 3834)

    # Testing version 2
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      ranges = list(test_file._ReadRangeDescriptors(file_object, 16, 2, 263))

    self.assertEqual(len(ranges), 263)
    self.assertEqual(ranges[10].data_offset, 64272)
    self.assertEqual(ranges[10].range_offset, 194710)
    self.assertEqual(ranges[10].range_size, 39755)

  def testReadUUIDDescriptors(self):
    """Test the _ReadUUIDDescriptors function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    # Testing Version 1
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version1'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      uuids = list(test_file._ReadUUIDDescriptors(file_object, 4048, 1, 196))

    self.assertEqual(len(uuids), 196)
    self.assertEqual(uuids[42].text_offset, 9191424)
    self.assertEqual(uuids[42].text_size, 223732)
    expected_path = '/System/Library/Extensions/AppleH8ADBE0.kext/AppleH8ADBE0'
    self.assertEqual(uuids[42].image_path, expected_path)

    # Testing Version 2
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      uuids = list(test_file._ReadUUIDDescriptors(file_object, 6328, 2, 200))

    self.assertEqual(len(uuids), 200)
    self.assertEqual(uuids[197].text_offset, 26816512)
    self.assertEqual(uuids[197].text_size, 43736)
    expected_path = (
        '/System/Library/Extensions/AppleD2207PMU.kext/AppleD2207PMU')
    self.assertEqual(uuids[197].image_path, expected_path)

  # TODO: add test for GetImageValuesAndString

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.DSCFile(output_writer=output_writer)

    # TODO: test of 8E21CAB1DCF936B49F85CF860E6F34EC currently failing.
    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', 'dsc', 'dsc-version1'])
        # 'unified_logging', 'uuidtext', 'dsc',
        # '8E21CAB1DCF936B49F85CF860E6F34EC'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)
    test_file.Close()


class TimesyncDatabaseFileTest(test_lib.BaseTestCase):
  """Tests for the timesync database file."""

  # pylint: disable=protected-access

  def testReadFileRecord(self):
    """Tests the _ReadRecord method."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TimesyncDatabaseFile(
        output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'timesync', '0000000000000002.timesync'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      # Boot record
      record, _ = test_file._ReadRecord(file_object, 0)

      self.assertEqual(record.signature, b'\xb0\xbb')
      self.assertEqual(record.record_size, 48)
      self.assertEqual(record.timebase_numerator, 125)
      self.assertEqual(record.timebase_denominator, 3)
      self.assertEqual(record.timestamp, 1541730321839294000)
      self.assertEqual(record.time_zone_offset, 480)
      self.assertEqual(record.daylight_saving_flag, 0)

      # sync record
      record, _ = test_file._ReadRecord(file_object, 48)

      self.assertEqual(record.signature, b'Ts')
      self.assertEqual(record.record_size, 32)
      self.assertEqual(record.kernel_time, 494027973)
      self.assertEqual(record.timestamp, 1541730337313716000)
      self.assertEqual(record.time_zone_offset, 480)
      self.assertEqual(record.daylight_saving_flag, 0)

  def testReadFileObject(self):
    """Tests the ReadFileObject method."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TimesyncDatabaseFile(
        output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'timesync', '0000000000000002.timesync'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)


class TraceV3FileTest(test_lib.BaseTestCase):
  """Apple Unified Logging and Activity Tracing (tracev3) file tests."""

  # pylint: disable=protected-access

  _FIREHOSE_CHUNK_DATA = bytes(bytearray([
      0x92, 0x16, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0xd0, 0x3b, 0x15, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x18, 0x01, 0x00, 0x10, 0x00, 0x00, 0x01, 0x02,
      0x30, 0xb3, 0x7d, 0x7a, 0x48, 0x5b, 0x00, 0x00, 0x04, 0x00, 0x05, 0x06,
      0xcd, 0x83, 0x7c, 0x08, 0x0f, 0xe8, 0xae, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0xa0, 0x00, 0x20, 0x3b, 0xea, 0x00,
      0x00, 0x00, 0x00, 0x80, 0x64, 0xca, 0x6c, 0x08, 0x61, 0x00, 0x15, 0x22,
      0x02, 0x42, 0x04, 0x00, 0x00, 0x2c, 0x00, 0x22, 0x04, 0x2c, 0x00, 0x57,
      0x00, 0x73, 0x79, 0x73, 0x74, 0x65, 0x6d, 0x67, 0x72, 0x6f, 0x75, 0x70,
      0x2e, 0x63, 0x6f, 0x6d, 0x2e, 0x61, 0x70, 0x70, 0x6c, 0x65, 0x2e, 0x63,
      0x6f, 0x6e, 0x66, 0x69, 0x67, 0x75, 0x72, 0x61, 0x74, 0x69, 0x6f, 0x6e,
      0x70, 0x72, 0x6f, 0x66, 0x69, 0x6c, 0x65, 0x73, 0x00, 0x2f, 0x70, 0x72,
      0x69, 0x76, 0x61, 0x74, 0x65, 0x2f, 0x76, 0x61, 0x72, 0x2f, 0x63, 0x6f,
      0x6e, 0x74, 0x61, 0x69, 0x6e, 0x65, 0x72, 0x73, 0x2f, 0x53, 0x68, 0x61,
      0x72, 0x65, 0x64, 0x2f, 0x53, 0x79, 0x73, 0x74, 0x65, 0x6d, 0x47, 0x72,
      0x6f, 0x75, 0x70, 0x2f, 0x73, 0x79, 0x73, 0x74, 0x65, 0x6d, 0x67, 0x72,
      0x6f, 0x75, 0x70, 0x2e, 0x63, 0x6f, 0x6d, 0x2e, 0x61, 0x70, 0x70, 0x6c,
      0x65, 0x2e, 0x63, 0x6f, 0x6e, 0x66, 0x69, 0x67, 0x75, 0x72, 0x61, 0x74,
      0x69, 0x6f, 0x6e, 0x70, 0x72, 0x6f, 0x66, 0x69, 0x6c, 0x65, 0x73, 0x00,
      0x04, 0x00, 0x04, 0x06, 0xb8, 0x4b, 0xa8, 0x01, 0x79, 0xe8, 0xae, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x6d, 0x72, 0xc4, 0x2c, 0x10, 0x00, 0x09, 0x00,
      0x94, 0x5a, 0xa2, 0x01, 0x7f, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x04, 0x06, 0xb8, 0x4b, 0xa8, 0x01,
      0x79, 0xe8, 0xae, 0x00, 0x00, 0x00, 0x00, 0x00, 0xcb, 0xbc, 0xc4, 0x2c,
      0x10, 0x00, 0x09, 0x00, 0x94, 0x5a, 0xa2, 0x01, 0x7f, 0x00, 0x03, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

  _FIREHOSE_TRACEPOINT_ACTIVITY_DATA = bytes(bytearray([
      0xe0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x3b, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80,
      0xe1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x48, 0x7e, 0x04, 0x00]))

  _FIREHOSE_TRACEPOINT_BACKTRACE_DATA = bytes(bytearray([
      0x01, 0x00, 0x12, 0x04, 0x0f, 0x00, 0x4c, 0xbc, 0x4b, 0x90, 0x32, 0x9d,
      0x37, 0xf0, 0xb9, 0x4a, 0x0d, 0x62, 0x25, 0x42, 0x73, 0xd0, 0xc3, 0x91,
      0x23, 0xbf, 0x9d, 0x62, 0x35, 0x77, 0xa1, 0x1f, 0x0a, 0x97, 0xcc, 0x4d,
      0x99, 0x91, 0x51, 0x15, 0xc8, 0xef, 0xbc, 0x57, 0x32, 0xdb, 0x91, 0xc6,
      0x71, 0xb6, 0x1a, 0x79, 0x96, 0x6e, 0x4b, 0xe7, 0x11, 0x04, 0x3c, 0x12,
      0x38, 0xbd, 0xb2, 0xf8, 0x2c, 0x1e, 0xd6, 0xa3, 0xfd, 0x8d, 0x7e, 0x99,
      0x0e, 0x00, 0x89, 0x0f, 0x08, 0x00, 0x25, 0x13, 0x07, 0x00, 0x9f, 0x14,
      0x07, 0x00, 0xcc, 0x20, 0x00, 0x00, 0x17, 0x33, 0x00, 0x00, 0x78, 0xfc,
      0x00, 0x00, 0xbb, 0xf8, 0x00, 0x00, 0x17, 0xdf, 0x0b, 0x00, 0xff, 0xef,
      0x07, 0x00, 0x6c, 0xde, 0x07, 0x00, 0x0a, 0xfd, 0x05, 0x00, 0x87, 0xa7,
      0x0e, 0x00, 0x1b, 0xf8, 0x0a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x03,
      0x03, 0x03, 0x02, 0x02, 0x02, 0x02, 0x01, 0x01, 0x01, 0x00, 0x00, 0x03,
      0xff]))

  _FIREHOSE_TRACEPOINT_LOG_DATA = bytes(bytearray([
      0x6c, 0x86, 0x03, 0x00, 0x06, 0x00, 0x08, 0x23, 0x01, 0x41, 0x04, 0x00,
      0x00, 0x00, 0x00]))

  _FIREHOSE_TRACEPOINT_LOSS_DATA = bytes(bytearray([
      0xce, 0x9a, 0x31, 0x07, 0x00, 0x00, 0x00, 0x00, 0x95, 0xaa, 0xef, 0x56,
      0x00, 0x00, 0x00, 0x00, 0x3f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

  _FIREHOSE_TRACEPOINT_TRACE_DATA = bytes(bytearray([
      0x2b, 0xf4, 0x03, 0x00, 0x00]))

  _HEADER_CHUNK_DATA = bytes(bytearray([
      0x7d, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0xc2, 0x55, 0xe0, 0xb5,
      0x32, 0x3f, 0x00, 0x00, 0xb6, 0xcc, 0x56, 0x62, 0x00, 0x00, 0x00, 0x00,
      0x9a, 0x34, 0x05, 0x00, 0x2c, 0x01, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
      0x01, 0x00, 0x00, 0x00, 0x00, 0x61, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00,
      0xc9, 0x23, 0xa5, 0x1e, 0x8c, 0x5b, 0x00, 0x00, 0x01, 0x61, 0x00, 0x00,
      0x38, 0x00, 0x00, 0x00, 0x0c, 0x00, 0x00, 0x01, 0x01, 0x00, 0x00, 0x00,
      0x31, 0x39, 0x44, 0x35, 0x32, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x4a, 0x39, 0x36, 0x41, 0x50, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x02, 0x61, 0x00, 0x00, 0x18, 0x00, 0x00, 0x00, 0xa6, 0xeb, 0xc8, 0xe3,
      0x0a, 0x1c, 0x40, 0xe8, 0x93, 0xb9, 0xda, 0x3a, 0x7f, 0x67, 0x1d, 0x19,
      0x1e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x61, 0x00, 0x00,
      0x30, 0x00, 0x00, 0x00, 0x2f, 0x76, 0x61, 0x72, 0x2f, 0x64, 0x62, 0x2f,
      0x74, 0x69, 0x6d, 0x65, 0x7a, 0x6f, 0x6e, 0x65, 0x2f, 0x7a, 0x6f, 0x6e,
      0x65, 0x69, 0x6e, 0x66, 0x6f, 0x2f, 0x41, 0x6d, 0x65, 0x72, 0x69, 0x63,
      0x61, 0x2f, 0x54, 0x6f, 0x72, 0x6f, 0x6e, 0x74, 0x6f, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00]))

  _SIMPLEDUMP_CHUNK_DATA = bytes(bytearray([
      0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x4f, 0x95, 0xd2, 0x21, 0x00, 0x00, 0x00, 0x00,
      0x5f, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x44, 0x85, 0x03, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x1d, 0x62, 0x53, 0x53, 0xa9, 0xfa, 0x3e, 0xc9,
      0x94, 0xc0, 0xb2, 0x95, 0x23, 0x15, 0xb2, 0xd2, 0xbe, 0x7f, 0xe6, 0xad,
      0x45, 0x60, 0x3a, 0xe2, 0x88, 0x3e, 0x43, 0x2f, 0x78, 0xb4, 0x50, 0x62,
      0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2a, 0x00, 0x00, 0x00,
      0x53, 0x6b, 0x69, 0x70, 0x70, 0x69, 0x6e, 0x67, 0x20, 0x62, 0x6f, 0x6f,
      0x74, 0x2d, 0x74, 0x61, 0x73, 0x6b, 0x3a, 0x20, 0x72, 0x65, 0x73, 0x74,
      0x6f, 0x72, 0x65, 0x2d, 0x64, 0x61, 0x74, 0x61, 0x70, 0x61, 0x72, 0x74,
      0x69, 0x74, 0x69, 0x6f, 0x6e, 0x00 ]))

  _STATEDUMP_CHUNK_DATA = bytes(bytearray([
      0x91, 0x75, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0xca, 0x5b, 0x0d, 0x00,
      0x0e, 0x00, 0x00, 0x00, 0x83, 0xa3, 0x1d, 0x3a, 0x8d, 0x5b, 0x00, 0x00,
      0x29, 0xd2, 0xea, 0x00, 0x00, 0x00, 0x00, 0x80, 0x08, 0x1b, 0x5e, 0x9e,
      0x59, 0xea, 0x39, 0xcd, 0x83, 0xc9, 0xee, 0xdb, 0x68, 0xa8, 0x40, 0x76,
      0x01, 0x00, 0x00, 0x00, 0x2a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x53, 0x70, 0x72, 0x69, 0x6e, 0x67, 0x42, 0x6f,
      0x61, 0x72, 0x64, 0x20, 0x2d, 0x20, 0x43, 0x6f, 0x6d, 0x62, 0x69, 0x6e,
      0x65, 0x64, 0x20, 0x4c, 0x69, 0x73, 0x74, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x62, 0x70, 0x6c, 0x69,
      0x73, 0x74, 0x30, 0x30, 0x50, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x09]))

  def testCalculateFormatStringReference(self):
    """Tests the _CalculateFormatStringReference function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    tracepoint_data_object_tuple = collections.namedtuple(
        'tracepoint_data_object', [
            'large_offset_data', 'large_shared_cache_data'])

    tracepoint_data_object = tracepoint_data_object_tuple(
        large_offset_data=0, large_shared_cache_data=0)

    string_reference, is_dynamic = test_file._CalculateFormatStringReference(
        tracepoint_data_object, 0x00964b95)
    self.assertEqual(string_reference, 0x964b95)
    self.assertFalse(is_dynamic)

    string_reference, is_dynamic = test_file._CalculateFormatStringReference(
        tracepoint_data_object, 0x8000d8e2)
    self.assertEqual(string_reference, 0xd8e2)
    self.assertTrue(is_dynamic)

    tracepoint_data_object = tracepoint_data_object_tuple(
        large_offset_data=0xff4b, large_shared_cache_data=0)

    string_reference, is_dynamic = test_file._CalculateFormatStringReference(
        tracepoint_data_object, 0x28dd2b31)
    self.assertEqual(string_reference, 0x7fa5a8dd2b31)
    self.assertFalse(is_dynamic)

    tracepoint_data_object = tracepoint_data_object_tuple(
        large_offset_data=0x0001, large_shared_cache_data=0x0002)

    string_reference, is_dynamic = test_file._CalculateFormatStringReference(
        tracepoint_data_object, 0x15a557c5)
    self.assertEqual(string_reference, 0x115a557c5)
    self.assertFalse(is_dynamic)

    tracepoint_data_object = tracepoint_data_object_tuple(
        large_offset_data=0x0001, large_shared_cache_data=0x0011)

    string_reference, is_dynamic = test_file._CalculateFormatStringReference(
        tracepoint_data_object, 0x6c8fbbd0)
    self.assertEqual(string_reference, 0x8ec8fbbd0)
    self.assertFalse(is_dynamic)

    tracepoint_data_object = tracepoint_data_object_tuple(
        large_offset_data=0x8008, large_shared_cache_data=0x0002)

    string_reference, is_dynamic = test_file._CalculateFormatStringReference(
        tracepoint_data_object, 0x117a0720)
    self.assertEqual(string_reference, 0x1117a0720)
    self.assertFalse(is_dynamic)

  def testCalculateNameStringReference(self):
    """Tests the _CalculateNameStringReference function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    tracepoint_data_object_tuple = collections.namedtuple(
        'tracepoint_data_object', [
            'name_string_reference_lower', 'name_string_reference_upper'])

    tracepoint_data_object = tracepoint_data_object_tuple(
        name_string_reference_lower=0x05f327b0,
        name_string_reference_upper=0x0002)

    string_reference, is_dynamic = test_file._CalculateNameStringReference(
        tracepoint_data_object)
    self.assertEqual(string_reference, 0x105f327b0)
    self.assertFalse(is_dynamic)

    # TODO: improve tests

  def testCalculateProgramCounter(self):
    """Tests the _CalculateProgramCounter function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    tracepoint_data_object_tuple = collections.namedtuple(
        'tracepoint_data_object', [
            'large_offset_data', 'large_shared_cache_data',
            'load_address_lower', 'load_address_upper'])

    # TODO: improve tests

    tracepoint_data_object = tracepoint_data_object_tuple(
        large_offset_data=0x0001, large_shared_cache_data=0x0002,
        load_address_lower=0x05dfebdb, load_address_upper=0)

    program_counter = test_file._CalculateProgramCounter(
        tracepoint_data_object, 0x105de1000)
    self.assertEqual(program_counter, 0x0001dbdb)

    tracepoint_data_object = tracepoint_data_object_tuple(
        large_offset_data=0x8008, large_shared_cache_data=0x0002,
        load_address_lower=0xecf707e9, load_address_upper=0)

    program_counter = test_file._CalculateProgramCounter(
        tracepoint_data_object, 0)
    self.assertEqual(program_counter, 0x8008ecf707e9)

  # TODO: add tests for _FormatArrayOfStrings
  # TODO: add tests for _FormatArrayOfUUIDS
  # TODO: add tests for _FormatStreamAsSignature

  def testReadCatalog(self):
    """Tests the _ReadCatalog function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', '0000000000000030.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      chunk_header = test_file._ReadChunkHeader(file_object, 0x000000e0)
      catalog = test_file._ReadCatalog(file_object, 0x000000f0, chunk_header)

    self.assertIsNotNone(catalog)

  def testReadChunkHeader(self):
    """Tests the _ReadChunkHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', '0000000000000030.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      chunk_header = test_file._ReadChunkHeader(file_object, 0)

    self.assertIsNotNone(chunk_header)

  def testReadChunkSet(self):
    """Tests the _ReadChunkSet function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', '0000000000000030.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      chunk_header = test_file._ReadChunkHeader(file_object, 0x000001a8)
      test_file._ReadChunkSet(file_object, 0x000001b8, chunk_header, {})

  def testReadBacktraceData(self):
    """Tests the _ReadBacktraceData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    backtrace_frames = test_file._ReadBacktraceData(
        self._FIREHOSE_TRACEPOINT_BACKTRACE_DATA, 0)

    self.assertEqual(len(backtrace_frames), 15)

    self.assertEqual(backtrace_frames[0].image_identifier, uuid.UUID(
        '4be71104-3c12-38bd-b2f8-2c1ed6a3fd8d'))
    self.assertEqual(backtrace_frames[0].image_offset, 0x000e997e)

  def testReadFirehoseChunkData(self):
    """Tests the _ReadFirehoseChunkData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file._ReadFirehoseChunkData(
        self._FIREHOSE_CHUNK_DATA, len(self._FIREHOSE_CHUNK_DATA), 0, {})

  def testReadFirehoseTracepointActivityData(self):
    """Tests the _ReadFirehoseTracepointActivityData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    activity, _ = test_file._ReadFirehoseTracepointActivityData(
        0x01, 0x0213, self._FIREHOSE_TRACEPOINT_ACTIVITY_DATA, 0)

    self.assertIsNotNone(activity)
    self.assertEqual(activity.current_activity_identifier, 0x80000000000000e0)
    self.assertEqual(activity.process_identifier, 59)
    self.assertEqual(activity.other_activity_identifier, 0x80000000000000e0)
    self.assertEqual(activity.new_activity_identifier, 0x80000000000000e1)
    self.assertEqual(activity.load_address_lower, 0x00047e48)

    with self.assertRaises(errors.ParseError):
      test_file._ReadFirehoseTracepointActivityData(
          0x01, 0xffff, self._FIREHOSE_TRACEPOINT_ACTIVITY_DATA, 0)

  def testReadFirehoseTracepointLogData(self):
    """Tests the _ReadFirehoseTracepointLogData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    log, _ = test_file._ReadFirehoseTracepointLogData(
        0x0602, self._FIREHOSE_TRACEPOINT_LOG_DATA, 0)

    self.assertIsNotNone(log)
    self.assertEqual(log.load_address_lower, 0x0003866c)
    self.assertEqual(log.sub_system_identifier, 6)
    self.assertEqual(log.ttl, 8)
    self.assertEqual(log.unknown1, 0x23)
    self.assertEqual(log.number_of_data_items, 1)

    with self.assertRaises(errors.ParseError):
      test_file._ReadFirehoseTracepointLogData(
          0xffff, self._FIREHOSE_TRACEPOINT_LOG_DATA, 0)

  def testReadFirehoseTracepointLossData(self):
    """Tests the _ReadFirehoseTracepointLossData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    loss, _ = test_file._ReadFirehoseTracepointLossData(
        0x0000, self._FIREHOSE_TRACEPOINT_LOSS_DATA, 0)

    self.assertIsNotNone(loss)
    self.assertEqual(loss.start_time, 120691406)
    self.assertEqual(loss.end_time, 1458547349)
    self.assertEqual(loss.number_of_messages, 63)

    with self.assertRaises(errors.ParseError):
      test_file._ReadFirehoseTracepointLossData(
          0xffff, self._FIREHOSE_TRACEPOINT_LOSS_DATA, 0)

  def testReadFirehoseTracepointTraceData(self):
    """Tests the _ReadFirehoseTracepointTraceData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    trace, _ = test_file._ReadFirehoseTracepointTraceData(
        0x0000, self._FIREHOSE_TRACEPOINT_TRACE_DATA,
        len(self._FIREHOSE_TRACEPOINT_TRACE_DATA), 0)

    self.assertIsNotNone(trace)
    self.assertEqual(trace.load_address_lower, 0x0003f42b)
    self.assertEqual(trace.number_of_values, 0)

    with self.assertRaises(errors.ParseError):
      test_file._ReadFirehoseTracepointTraceData(
          0xffff, self._FIREHOSE_TRACEPOINT_TRACE_DATA,
        len(self._FIREHOSE_TRACEPOINT_TRACE_DATA), 0)

  def testReadHeaderChunk(self):
    """Tests the _ReadHeaderChunk function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    with io.BytesIO(self._HEADER_CHUNK_DATA) as file_object:
      header_chunk = test_file._ReadHeaderChunk(file_object, 0)

    self.assertIsNotNone(header_chunk)
    self.assertEqual(header_chunk.timebase_numerator, 125)
    self.assertEqual(header_chunk.timebase_denominator, 3)
    self.assertEqual(header_chunk.time_zone_offset, 300)

    self.assertEqual(header_chunk.continuous.sub_chunk_tag, 0x6100)

    self.assertEqual(header_chunk.system_information.sub_chunk_tag, 0x6101)
    self.assertEqual(header_chunk.system_information.build_version, '19D52')
    self.assertEqual(header_chunk.system_information.hardware_model, 'J96AP')

    self.assertEqual(header_chunk.generation.sub_chunk_tag, 0x6102)
    self.assertEqual(header_chunk.generation.boot_identifier, uuid.UUID(
        'a6ebc8e3-0a1c-40e8-93b9-da3a7f671d19'))

    self.assertEqual(header_chunk.time_zone.sub_chunk_tag, 0x6103)
    self.assertEqual(header_chunk.time_zone.path, (
        '/var/db/timezone/zoneinfo/America/Toronto'))

  def testReadOversizeChunkData(self):
    """Tests the _ReadOversizeChunkData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', '0000000000000f85.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    # The 8th chunkset chunk of the first set
    with open(test_file_path, 'rb') as file_object:
      file_object.seek(0x1cc48, os.SEEK_SET)
      chunk_data = file_object.read(16519)

    uncompressed_data = lz4.block.decompress(
        chunk_data[12:12 + 16503], uncompressed_size=64624)

    # data block #17
    data_offset = 0xfc8
    data_type_map = test_file._GetDataTypeMap('tracev3_chunk_header')
    chunkset_chunk_header = test_file._ReadStructureFromByteStream(
        uncompressed_data[data_offset:], data_offset, data_type_map,
        'chunk header')

    self.assertEqual(chunkset_chunk_header.chunk_tag, 0x6002)
    self.assertEqual(chunkset_chunk_header.chunk_data_size, 2078)

    data_offset += 16
    data_end_offset = data_offset + chunkset_chunk_header.chunk_data_size

    oversize_chunk = test_file._ReadOversizeChunkData(
        uncompressed_data[data_offset:data_end_offset],
        chunkset_chunk_header.chunk_data_size, data_offset)

    self.assertIsNotNone(oversize_chunk)
    self.assertEqual(oversize_chunk.proc_id_upper, 449241)
    self.assertEqual(oversize_chunk.proc_id_lower, 1345727)
    self.assertEqual(oversize_chunk.ttl, 30)
    self.assertEqual(oversize_chunk.unknown1, 0x00)
    self.assertEqual(oversize_chunk.unknown2, 0x0000)
    self.assertEqual(oversize_chunk.continuous_time, 100657868900985)
    self.assertEqual(oversize_chunk.data_reference, 82)
    self.assertEqual(oversize_chunk.data_size, 2046)
    self.assertEqual(oversize_chunk.private_data_size, 0)
    self.assertEqual(oversize_chunk.unknown3, 0x22)
    self.assertEqual(oversize_chunk.number_of_data_items, 1)

  def testReadSimpleDumpChunkData(self):
    """Tests the _ReadSimpleDumpChunkData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    log_entries = list(test_file._ReadSimpleDumpChunkData(
        self._SIMPLEDUMP_CHUNK_DATA, len(self._SIMPLEDUMP_CHUNK_DATA), 0))

    self.assertEqual(len(log_entries), 1)

    log_entry = log_entries[0]
    self.assertEqual(len(log_entry.backtrace_frames), 1)
    # Not set due to test without catalog.
    self.assertIsNone(log_entry.boot_identifier)
    self.assertEqual(log_entry.event_message, (
        'Skipping boot-task: restore-datapartition'))
    self.assertEqual(log_entry.event_type, 'logEvent')
    self.assertEqual(log_entry.mach_timestamp, 567448911)
    self.assertEqual(log_entry.message_type, 'Default')
    # Not set due to test without catalog.
    self.assertEqual(log_entry.process_identifier, 0)
    self.assertIsNone(log_entry.process_image_identifier)
    self.assertIsNone(log_entry.process_image_path)
    self.assertEqual(log_entry.sender_image_identifier, uuid.UUID(
        '1d625353-a9fa-3ec9-94c0-b2952315b2d2'))
    self.assertIsNone(log_entry.sender_image_path)
    self.assertEqual(log_entry.sender_program_counter, 230724)
    self.assertEqual(log_entry.sub_system, '')
    self.assertEqual(log_entry.thread_identifier, 1887)
    # Not converted due to test without catalog.
    self.assertEqual(log_entry.timestamp, 567448911)
    self.assertEqual(log_entry.trace_identifier, 0)

  def testReadStateDumpChunkData(self):
    """Tests the _ReadStateDumpChunkData function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    log_entries = list(test_file._ReadStateDumpChunkData(
        self._STATEDUMP_CHUNK_DATA, len(self._STATEDUMP_CHUNK_DATA), 0))

    self.assertEqual(len(log_entries), 1)

    log_entry = log_entries[0]
    self.assertEqual(log_entry.activity_identifier, 15389225)
    self.assertEqual(len(log_entry.backtrace_frames), 1)
    # Not set due to test without catalog.
    self.assertIsNone(log_entry.boot_identifier)
    self.assertEqual(log_entry.event_message, '')
    self.assertEqual(log_entry.event_type, 'stateEvent')
    self.assertEqual(log_entry.mach_timestamp, 100662123537283)
    # Not set due to test without catalog.
    self.assertEqual(log_entry.process_identifier, 0)
    self.assertIsNone(log_entry.process_image_identifier)
    self.assertIsNone(log_entry.process_image_path)
    self.assertEqual(log_entry.sender_image_identifier, uuid.UUID(
        '081b5e9e-59ea-39cd-83c9-eedb68a84076'))
    self.assertIsNone(log_entry.sender_image_path)
    # Not converted due to test without catalog.
    self.assertEqual(log_entry.timestamp, 100662123537283)
    self.assertEqual(log_entry.trace_identifier, 0)

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.TraceV3File(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', '0000000000000030.tracev3'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)
    test_file.Close()


class UUIDTextFileTest(test_lib.BaseTestCase):
  """Apple Unified Logging and Activity Tracing (uuidtext) file tests."""

  # pylint: disable=protected-access

  def testReadFileFooter(self):
    """Tests the _ReadFileFooter function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_footer = test_file._ReadFileFooter(file_object, 0x00000010)

    self.assertIsNotNone(file_footer)
    self.assertEqual(file_footer.image_path, '/usr/libexec/lsd')

  def testReadFileHeader(self):
    """Tests the _ReadFileHeader function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_header = test_file._ReadFileHeader(file_object)

    self.assertIsNotNone(file_header)
    self.assertEqual(file_header.major_format_version, 2)
    self.assertEqual(file_header.minor_format_version, 1)
    self.assertEqual(file_header.number_of_entries, 0)

  def testReadString(self):
    """Tests the _ReadString function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', '00', '7EF56328D53A78B59CCCE3E3189F57'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)

    try:
      string = test_file._ReadString(test_file._file_object, 0x00000018)
    finally:
      test_file.Close()

    self.assertEqual(string, 'system.install.apple-software')

  def testGetImagePath(self):
    """Tests the GetImagePath function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)

    try:
      image_path = test_file.GetImagePath()
    finally:
      test_file.Close()

    self.assertEqual(image_path, '/usr/libexec/lsd')

  def testGetString(self):
    """Tests the GetString function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', '00', '7EF56328D53A78B59CCCE3E3189F57'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)

    try:
      string = test_file.GetString(0x00005591)
    finally:
      test_file.Close()

    self.assertEqual(string, 'system.install.apple-software')

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    output_writer = test_lib.TestOutputWriter()
    test_file = unified_logging.UUIDTextFile(output_writer=output_writer)

    test_file_path = self._GetTestFilePath([
        'unified_logging', 'uuidtext', '22', '0D3C2953A33917B333DD8366AC25F2'])
    self._SkipIfPathNotExists(test_file_path)

    test_file.Open(test_file_path)
    test_file.Close()


if __name__ == '__main__':
  unittest.main()
