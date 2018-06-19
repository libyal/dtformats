# -*- coding: utf-8 -*-
"""Utmp files."""

from __future__ import unicode_literals

from dtformats import data_format
from dtformats import errors


class LinuxLibc6UtmpFile(data_format.BinaryDataFile):
  """A Linux libc6 utmp file."""

  _DEFINITION_FILE = 'utmp.yaml'

  _EMPTY_IP_ADDRESS = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

  _TYPES_OF_LOGIN = {
      0: 'EMPTY',
      1: 'RUN_LVL',
      2: 'BOOT_TIME',
      3: 'NEW_TIME',
      4: 'OLD_TIME',
      5: 'INIT_PROCESS',
      6: 'LOGIN_PROCESS',
      7: 'USER_PROCESS',
      8: 'DEAD_PROCESS',
      9: 'ACCOUNTING'}

  def _DebugPrintEntry(self, entry):
    """Prints entry debug information.

    Args:
      entry (linux_libc6_utmp_entry): entry.
    """
    type_of_login_string = self._TYPES_OF_LOGIN.get(entry.type, 'UNKNOWN')
    value_string = '0x{0:08x} ({1:s})'.format(entry.type, type_of_login_string)
    self._DebugPrintValue('Type of login', value_string)

    value_string = '{0:d}'.format(entry.pid)
    self._DebugPrintValue('PID', value_string)

    value_string = entry.terminal.replace(b'\0', b'')
    value_string = value_string.decode('utf-8')
    self._DebugPrintValue('Terminal', value_string)

    value_string = '{0:d}'.format(entry.terminal_identifier)
    self._DebugPrintValue('Terminal ID', value_string)

    value_string = entry.username.replace(b'\0', b'')
    value_string = value_string.decode('utf-8')
    self._DebugPrintValue('Username', value_string)

    value_string = entry.hostname.replace(b'\0', b'')
    value_string = value_string.decode('utf-8')
    self._DebugPrintValue('Hostname', value_string)

    value_string = '0x{0:04x}'.format(entry.termination_status)
    self._DebugPrintValue('Termination status', value_string)

    value_string = '0x{0:04x}'.format(entry.exit_status)
    self._DebugPrintValue('Exit status', value_string)

    value_string = '{0:d}'.format(entry.session)
    self._DebugPrintValue('Session', value_string)

    self._DebugPrintPosixTimeValue('Timestamp', entry.timestamp)

    value_string = '{0:d}'.format(entry.microseconds)
    self._DebugPrintValue('Microseconds', value_string)

    if entry.ip_address[4:] == self._EMPTY_IP_ADDRESS[4:]:
      value_string = self._FormatPackedIPv4Address(entry.ip_address[:4])
    else:
      value_string = self._FormatPackedIPv6Address(entry.ip_address)

    self._DebugPrintValue('IP address', value_string)

    self._DebugPrintData('Unknown1', entry.unknown1)

  def _DecodeString(self, byte_stream, encoding='utf8'):
    """Decodes a string.

    Args:
      byte_stream (bytes): byte stream that contains the encoded string.
      encoding (Optional[str]): name of the encoding.

    Returns:
      str: decoded string.
    """
    try:
      string = byte_stream.decode(encoding)
    except UnicodeDecodeError:
      string = 'INVALID'

    return string.rstrip('\x00')

  def _FormatPackedIPv4Address(self, packed_ip_address):
    """Formats a packed IPv4 address as a human readable string.

    Args:
      packed_ip_address (list[int]): packed IPv4 address.

    Returns:
      str: human readable IPv4 address.
    """
    return '.'.join(['{0:d}'.format(octet) for octet in packed_ip_address[:4]])

  def _FormatPackedIPv6Address(self, packed_ip_address):
    """Formats a packed IPv6 address as a human readable string.

    Args:
      packed_ip_address (list[int]): packed IPv6 address.

    Returns:
      str: human readable IPv6 address.
    """
    # Note that socket.inet_ntop() is not supported on Windows.
    octet_pairs = zip(packed_ip_address[0::2], packed_ip_address[1::2])
    octet_pairs = [octet1 << 8 | octet2 for octet1, octet2 in octet_pairs]
    # TODO: omit ":0000" from the string.
    return ':'.join([
        '{0:04x}'.format(octet_pair) for octet_pair in octet_pairs])

  def _ReadEntries(self, file_object):
    """Reads entries.

    Args:
      file_object (file): file-like object.
    """
    file_offset = 0
    data_type_map = self._GetDataTypeMap('linux_libc6_utmp_entry')

    while file_offset < self._file_size:
      entry, entry_data_size = self._ReadStructureFromFileObject(
          file_object, file_offset, data_type_map, 'entry')

      if self._debug:
        self._DebugPrintEntry(entry)

      file_offset += entry_data_size

  def ReadFileObject(self, file_object):
    """Reads an utmp file-like object.

    Args:
      file_object (file): file-like object.
    """
    self._ReadEntries(file_object)

    # TODO: print trailing data


class MacOSXUtmpxFile(data_format.BinaryDataFile):
  """A Mac OS X 10.5 utmpx file."""

  _DEFINITION_FILE = 'utmp.yaml'

  _TYPES_OF_LOGIN = {
      0: 'EMPTY',
      1: 'RUN_LVL',
      2: 'BOOT_TIME',
      3: 'OLD_TIME',
      4: 'NEW_TIME',
      5: 'INIT_PROCESS',
      6: 'LOGIN_PROCESS',
      7: 'USER_PROCESS',
      8: 'DEAD_PROCESS',
      9: 'ACCOUNTING',
      10: 'SIGNATURE',
      11: 'SHUTDOWN_TIME'}

  def _DebugPrintEntry(self, entry):
    """Prints entry debug information.

    Args:
      entry (macosx_utmpx_entry): entry.
    """
    value_string = entry.username.replace(b'\0', b'')
    value_string = value_string.decode('utf-8')
    self._DebugPrintValue('Username', value_string)

    value_string = '{0:d}'.format(entry.terminal_identifier)
    self._DebugPrintValue('Terminal ID', value_string)

    value_string = entry.terminal.replace(b'\0', b'')
    value_string = value_string.decode('utf-8')
    self._DebugPrintValue('Terminal', value_string)

    value_string = '{0:d}'.format(entry.pid)
    self._DebugPrintValue('PID', value_string)

    type_of_login_string = self._TYPES_OF_LOGIN.get(entry.type, 'UNKNOWN')
    value_string = '0x{0:04x} ({1:s})'.format(entry.type, type_of_login_string)
    self._DebugPrintValue('Type of login', value_string)

    value_string = '0x{0:04x}'.format(entry.unknown1)
    self._DebugPrintValue('Unknown1', value_string)

    self._DebugPrintPosixTimeValue('Timestamp', entry.timestamp)

    value_string = '{0:d}'.format(entry.microseconds)
    self._DebugPrintValue('Microseconds', value_string)

    value_string = entry.hostname.replace(b'\0', b'')
    value_string = value_string.decode('utf-8')
    self._DebugPrintValue('Hostname', value_string)

    self._DebugPrintData('Unknown2', entry.unknown2)

  def _DecodeString(self, byte_stream, encoding='utf8'):
    """Decodes a string.

    Args:
      byte_stream (bytes): byte stream that contains the encoded string.
      encoding (Optional[str]): name of the encoding.

    Returns:
      str: decoded string.
    """
    try:
      string = byte_stream.decode(encoding)
    except UnicodeDecodeError:
      string = 'INVALID'

    return string.rstrip('\x00')

  def _ReadEntries(self, file_object):
    """Reads entries.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the entries cannot be read.
    """
    file_offset = 0
    data_type_map = self._GetDataTypeMap('macosx_utmpx_entry')

    entry, entry_data_size = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'entry')

    if self._debug:
      self._DebugPrintEntry(entry)

    if not entry.username.startswith(b'utmpx-1.00\x00'):
      raise errors.ParseError('Unsupported file header signature.')

    if entry.type != 10:
      raise errors.ParseError('Unsupported file header type of login.')

    file_offset += entry_data_size

    while file_offset < self._file_size:
      entry, entry_data_size = self._ReadStructureFromFileObject(
          file_object, file_offset, data_type_map, 'entry')

      if self._debug:
        self._DebugPrintEntry(entry)

      file_offset += entry_data_size

  def ReadFileObject(self, file_object):
    """Reads an utmp file-like object.

    Args:
      file_object (file): file-like object.
    """
    self._ReadEntries(file_object)

    # TODO: print trailing data
