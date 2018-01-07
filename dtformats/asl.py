# -*- coding: utf-8 -*-
"""Apple System Log (ASL) files."""

from __future__ import unicode_literals

from dtfabric.runtime import fabric as dtfabric_fabric

from dtformats import data_format


class AppleSystemLogFile(data_format.BinaryDataFile):
  """Apple System Log (.asl) file."""

  _DATA_TYPE_FABRIC_DEFINITION = b"""\
name: byte
type: integer
attributes:
  format: unsigned
  size: 1
  units: bytes
---
name: uint32
type: integer
attributes:
  format: unsigned
  size: 4
  units: bytes
---
name: uint64
type: integer
attributes:
  format: unsigned
  size: 8
  units: bytes
---
name: asl_header
type: structure
attributes:
  byte_order: big-endian
members:
- name: signature
  type: stream
  element_data_type: byte
  elements_data_size: 12
- name: format_version
  data_type: uint32
- name: first_log_entry_offset
  data_type: uint64
- name: creation_time
  data_type: uint64
- name: cache_size
  data_type: uint32
- name: last_log_entry_offset
  data_type: uint64
- name: unknown1
  type: stream
  element_data_type: byte
  elements_data_size: 36
"""

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap('asl_header')

  _HEADER_SIZE = _HEADER.GetByteSize()

  def _DebugPrintHeader(self, header):
    """Prints header debug information.

    Args:
      header (asl_header): header.
    """
    self._DebugPrintValue('Signature', header.signature)

    value_string = '{0:d}'.format(header.format_version)
    self._DebugPrintValue('Format version', value_string)

    value_string = '0x{0:08x}'.format(header.first_log_entry_offset)
    self._DebugPrintValue('First log entry offset', value_string)

    value_string = '{0:d}'.format(header.timestamp)
    self._DebugPrintValue('Creation time', value_string)

    value_string = '{0:d}'.format(header.cache_size)
    self._DebugPrintValue('Cache size', value_string)

    value_string = '0x{0:08x}'.format(header.last_log_entry_offset)
    self._DebugPrintValue('Last log entry offset', value_string)

    self._DebugPrintData('Unknown1', header.unknown1)

    self._DebugPrintText('\n')

  def _ReadHeader(self, file_object):
    """Reads the heaader.

    Args:
      file_object (file): file-like object.

    Raises:
      IOError: if the header section cannot be read.
    """
    file_offset = file_object.tell()
    header = self._ReadStructure(
        file_object, file_offset, self._HEADER_SIZE, self._HEADER, 'header')

    if self._debug:
      self._DebugPrintHeader(header)

  def ReadFileObject(self, file_object):
    """Reads an Apple System Log file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadHeader(file_object)
