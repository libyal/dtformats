# -*- coding: utf-8 -*-
"""UTMP files."""

import datetime

from dtfabric import fabric as dtfabric_fabric

from dtformats import data_format


class UTMPFile(data_format.BinaryDataFile):
  """An UTMP file."""

  _DATA_TYPE_FABRIC_DEFINITION = b'\n'.join([
      b'name: byte',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 1',
      b'  units: bytes',
      b'---',
      b'name: uint16',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 2',
      b'  units: bytes',
      b'---',
      b'name: uint32',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 4',
      b'  units: bytes',
      b'---',
      b'name: utmp_entry_linux',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: type',
      b'  data_type: uint32',
      b'- name: pid',
      b'  data_type: uint32',
      b'- name: terminal',
      b'  type: sequence',
      b'  element_data_type: byte',
      b'  number_of_elements: 32',
      b'- name: terminal_identifier',
      b'  data_type: uint32',
      b'- name: username',
      b'  type: sequence',
      b'  element_data_type: byte',
      b'  number_of_elements: 32',
      b'- name: hostname',
      b'  type: sequence',
      b'  element_data_type: byte',
      b'  number_of_elements: 256',
      b'- name: termination',
      b'  data_type: uint16',
      b'- name: exit',
      b'  data_type: uint16',
      b'- name: session',
      b'  data_type: uint32',
      b'- name: timestamp',
      b'  data_type: uint32',
      b'- name: micro_seconds',
      b'  data_type: uint32',
      b'- name: address_a',
      b'  data_type: uint32',
      b'- name: address_b',
      b'  data_type: uint32',
      b'- name: address_c',
      b'  data_type: uint32',
      b'- name: address_d',
      b'  data_type: uint32',
      b'- name: unknown1',
      b'  type: sequence',
      b'  element_data_type: byte',
      b'  number_of_elements: 20',
  ])

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _UTMP_ENTRY = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'utmp_entry_linux')

  _UTMP_ENTRY_SIZE = _UTMP_ENTRY.GetByteSize()

  def _DebugPrintEntry(self, entry):
    """Prints entry debug information.

    Args:
      entry (utmp_entry_linux): entry.
    """
    value_string = u'0x{0:08x}'.format(entry.type)
    self._DebugPrintValue(u'Type', value_string)

    value_string = u'{0:d}'.format(entry.pid)
    self._DebugPrintValue(u'PID', value_string)

    # TODO: add dtfabric string support.
    value_string = bytes(bytearray(entry.terminal))
    value_string = value_string.replace(b'\0', b'')
    value_string = value_string.decode(u'utf-8')
    self._DebugPrintValue(u'Terminal', value_string)

    value_string = u'{0:d}'.format(entry.terminal_identifier)
    self._DebugPrintValue(u'Terminal ID', value_string)

    value_string = bytes(bytearray(entry.username))
    value_string = value_string.replace(b'\0', b'')
    value_string = value_string.decode(u'utf-8')
    self._DebugPrintValue(u'Username', value_string)

    value_string = bytes(bytearray(entry.hostname))
    value_string = value_string.replace(b'\0', b'')
    value_string = value_string.decode(u'utf-8')
    self._DebugPrintValue(u'Hostname', value_string)

    value_string = u'0x{0:04x}'.format(entry.termination)
    self._DebugPrintValue(u'Termination', value_string)

    value_string = u'0x{0:04x}'.format(entry.exit)
    self._DebugPrintValue(u'Exit', value_string)

    value_string = u'{0:d}'.format(entry.session)
    self._DebugPrintValue(u'Session', value_string)

    date_time = (datetime.datetime(1970, 1, 1) + datetime.timedelta(
        seconds=int(entry.timestamp)))

    value_string = u'{0!s} ({1:d})'.format(date_time, entry.timestamp)
    self._DebugPrintValue(u'Timestamp', value_string)

    value_string = u'{0:d}'.format(entry.micro_seconds)
    self._DebugPrintValue(u'Micro seconds', value_string)

    value_string = u'0x{0:08x}'.format(entry.address_a)
    self._DebugPrintValue(u'Address A', value_string)

    value_string = u'0x{0:08x}'.format(entry.address_b)
    self._DebugPrintValue(u'Address B', value_string)

    value_string = u'0x{0:08x}'.format(entry.address_c)
    self._DebugPrintValue(u'Address C', value_string)

    value_string = u'0x{0:08x}'.format(entry.address_d)
    self._DebugPrintValue(u'Address D', value_string)

    # TODO: add dtfabric byte array support.
    self._DebugPrintData(u'Unknown1', bytes(bytearray(entry.unknown1)))

  def _ReadEntries(self, file_object):
    """Reads entries.

    Args:
      file_object (file): file-like object.
    """
    file_offset = 0
    while file_offset < self._file_size:
      entry = self._ReadStructure(
          file_object, file_offset, self._UTMP_ENTRY_SIZE, self._UTMP_ENTRY,
          u'entry')

      if self._debug:
        self._DebugPrintEntry(entry)

      file_offset += self._UTMP_ENTRY_SIZE

  def ReadFileObject(self, file_object):
    """Reads an UTMP file-like object.

    Args:
      file_object (file): file-like object.
    """
    self._ReadEntries(file_object)

    # TODO: print trailing data
