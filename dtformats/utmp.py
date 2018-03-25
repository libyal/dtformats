# -*- coding: utf-8 -*-
"""UTMP files."""

from __future__ import unicode_literals

import datetime
import os

from dtfabric.runtime import fabric as dtfabric_fabric

from dtformats import data_format


class UTMPFile(data_format.BinaryDataFile):
  """An UTMP file."""

  _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
      os.path.dirname(__file__), 'utmp.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _UTMP_ENTRY = _DATA_TYPE_FABRIC.CreateDataTypeMap('utmp_entry_linux')

  _UTMP_ENTRY_SIZE = _UTMP_ENTRY.GetByteSize()

  def _DebugPrintEntry(self, entry):
    """Prints entry debug information.

    Args:
      entry (utmp_entry_linux): entry.
    """
    value_string = '0x{0:08x}'.format(entry.type)
    self._DebugPrintValue('Type', value_string)

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

    value_string = '0x{0:04x}'.format(entry.termination)
    self._DebugPrintValue('Termination', value_string)

    value_string = '0x{0:04x}'.format(entry.exit)
    self._DebugPrintValue('Exit', value_string)

    value_string = '{0:d}'.format(entry.session)
    self._DebugPrintValue('Session', value_string)

    date_time = (datetime.datetime(1970, 1, 1) + datetime.timedelta(
        seconds=int(entry.timestamp)))

    value_string = '{0!s} ({1:d})'.format(date_time, entry.timestamp)
    self._DebugPrintValue('Timestamp', value_string)

    value_string = '{0:d}'.format(entry.micro_seconds)
    self._DebugPrintValue('Micro seconds', value_string)

    value_string = '0x{0:08x}'.format(entry.address_a)
    self._DebugPrintValue('Address A', value_string)

    value_string = '0x{0:08x}'.format(entry.address_b)
    self._DebugPrintValue('Address B', value_string)

    value_string = '0x{0:08x}'.format(entry.address_c)
    self._DebugPrintValue('Address C', value_string)

    value_string = '0x{0:08x}'.format(entry.address_d)
    self._DebugPrintValue('Address D', value_string)

    self._DebugPrintData('Unknown1', entry.unknown1)

  def _ReadEntries(self, file_object):
    """Reads entries.

    Args:
      file_object (file): file-like object.
    """
    file_offset = 0
    while file_offset < self._file_size:
      entry = self._ReadStructure(
          file_object, file_offset, self._UTMP_ENTRY_SIZE, self._UTMP_ENTRY,
          'entry')

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
