# -*- coding: utf-8 -*-
"""Timezone information files (TZif)."""

from __future__ import unicode_literals

import os

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import data_maps as dtfabric_data_maps
from dtfabric.runtime import fabric as dtfabric_fabric

from dtformats import data_format
from dtformats import data_range
from dtformats import errors


class TimeZoneInformationFile(data_format.BinaryDataFile):
  """Timezone information file (TZif).

  Attributes:
    format_version (int): format version.
  """

  _DATA_TYPE_FABRIC_DEFINITION = b'\n'.join([
      b'name: byte',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 1',
      b'  units: bytes',
      b'---',
      b'name: uint32',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 4',
      b'  units: bytes',
      b'---',
      b'name: tzif_file_header',
      b'type: structure',
      b'description: file header.',
      b'attributes:',
      b'  byte_order: big-endian',
      b'members:',
      b'- name: signature',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 4',
      b'- name: format_version',
      b'  data_type: byte',
      b'- name: unknown1',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 15',
      b'- name: number_of_utc_time_indicators',
      b'  data_type: uint32',
      b'- name: number_of_standard_time_indicators',
      b'  data_type: uint32',
      b'- name: number_of_leap_seconds',
      b'  data_type: uint32',
      b'- name: number_of_transition_times',
      b'  data_type: uint32',
      b'- name: number_of_local_time_types',
      b'  data_type: uint32',
      b'- name: timezone_abbreviation_strings_size',
      b'  data_type: uint32',
      b'---',
      b'name: tzif_transition_times',
      b'type: structure',
      b'description: transition times.',
      b'attributes:',
      b'  byte_order: big-endian',
      b'members:',
      b'- name: transition_times',
      b'  type: sequence',
      b'  element_data_type: uint32',
      b'  number_of_elements: tzif_file_header.number_of_transition_times',
      b'- name: types_of_local_time',
      b'  type: sequence',
      b'  element_data_type: byte',
      b'  number_of_elements: tzif_file_header.number_of_transition_times',
  ])

  # TODO: move path into structure.

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _FILE_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap('tzif_file_header')

  _FILE_HEADER_SIZE = _FILE_HEADER.GetByteSize()

  _TZIF_TRANSITION_TIMES = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'tzif_transition_times')

  _FILE_SIGNATURE = b'TZif'

  def __init__(self, debug=False, output_writer=None):
    """Initializes a timezone information file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(TimeZoneInformationFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self.format_version = None

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (tzif_file_header): file header.
    """
    value_string = '{0!s}'.format(file_header.signature)
    self._DebugPrintValue('Signature', value_string)

    value_string = '0x{0:02x}'.format(file_header.format_version)
    self._DebugPrintValue('Format version', value_string)

    self._DebugPrintData('Unknown1', file_header.unknown1)

    value_string = '{0:d}'.format(file_header.number_of_utc_time_indicators)
    self._DebugPrintValue('Number of UTC time indicators', value_string)

    value_string = '{0:d}'.format(
        file_header.number_of_standard_time_indicators)
    self._DebugPrintValue('Number of standard time indicators', value_string)

    value_string = '{0:d}'.format(file_header.number_of_leap_seconds)
    self._DebugPrintValue('Number of leap seconds', value_string)

    value_string = '{0:d}'.format(file_header.number_of_transition_times)
    self._DebugPrintValue('Number of transition times', value_string)

    value_string = '{0:d}'.format(file_header.number_of_local_time_types)
    self._DebugPrintValue('Number of local time types', value_string)

    value_string = '{0:d}'.format(
        file_header.timezone_abbreviation_strings_size)
    self._DebugPrintValue('Timezone abbreviation strings size', value_string)

    self._DebugPrintText('\n')

  def _DebugPrintTransitionTimes(self, transition_times):
    """Prints transition times debug information.

    Args:
      transition_times (tzif_transition_times): transition times.
    """
    for index, transition_time in enumerate(transition_times.transition_times):
      description_string = 'Transition time: {0:d}'.format(index)
      value_string = '{0:d}'.format(transition_time)
      self._DebugPrintValue(description_string, value_string)

    for index, type_of_localtime in enumerate(
        transition_times.types_of_local_time):
      description_string = 'Type of local time: {0:d}'.format(index)
      value_string = '{0:d}'.format(type_of_localtime)
      self._DebugPrintValue(description_string, value_string)

    self._DebugPrintText('\n')

  def _ReadFileHeader(self, file_object):
    """Reads a file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()
    file_header = self._ReadStructure(
        file_object, file_offset, self._FILE_HEADER_SIZE, self._FILE_HEADER,
        'file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

    if file_header.signature != self._FILE_SIGNATURE:
        raise errors.ParseError('Unsupported file signature.')

    if file_header.format_version not in (0x00, 0x32, 0x33):
        raise errors.ParseError('Unsupported format version: {0:d}.'.format(
            file_header.format_version))

    self._ReadTransitionTimes(file_object, file_header)

  def _ReadTransitionTimes(self, file_object, file_header):
    """Reads transition times.

    Args:
      file_object (file): file-like object.
      file_header (tzif_file_header): file header.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'tzif_file_header': file_header})

    transition_times_data_size = 5 * file_header.number_of_transition_times

    transition_times_data = file_object.read(transition_times_data_size)

    if self._debug:
      self._DebugPrintData('Transition times data', transition_times_data)

    transition_times = self._ReadStructureFromByteStream(
        transition_times_data, file_offset, self._TZIF_TRANSITION_TIMES,
        'transition times', context=context)

    if self._debug:
      self._DebugPrintTransitionTimes(transition_times)

  def ReadFileObject(self, file_object):
    """Reads a timezone information file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadFileHeader(file_object)
