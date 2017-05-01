# -*- coding: utf-8 -*-
"""Windows Task Scheduler job files."""

import construct

from dtfabric import fabric as dtfabric_fabric

from dtformats import data_format


class WindowsTaskSchedularJobFile(data_format.BinaryDataFile):
  """Windows Task Scheduler job (.job) file."""

  _DATA_TYPE_FABRIC_DEFINITION = b'\n'.join([
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
      b'name: job_fixed_size_data_section',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: product_version',
      b'  data_type: uint16',
      b'- name: format_version',
      b'  data_type: uint16',
      b'- name: job_identifier',
      b'  type: uuid',
      b'- name: application_name_size_offset',
      b'  data_type: uint16',
      b'- name: trigger_offset',
      b'  data_type: uint16',
      b'- name: error_retry_count',
      b'  data_type: uint16',
      b'- name: error_retry_interval',
      b'  data_type: uint16',
      b'- name: idle_deadline',
      b'  data_type: uint16',
      b'- name: idle_wait',
      b'  data_type: uint16',
      b'- name: priority',
      b'  data_type: uint32',
      b'- name: maximum_run_time',
      b'  data_type: uint32',
      b'- name: exit_code',
      b'  data_type: uint32',
      b'- name: status',
      b'  data_type: uint32',
      b'- name: flags',
      b'  data_type: uint32',
      b'- name: year',
      b'  data_type: uint16',
      b'- name: month',
      b'  data_type: uint16',
      b'- name: weekday',
      b'  data_type: uint16',
      b'- name: day_of_month',
      b'  data_type: uint16',
      b'- name: hours',
      b'  data_type: uint16',
      b'- name: minutes',
      b'  data_type: uint16',
      b'- name: seconds',
      b'  data_type: uint16',
      b'- name: milliseconds',
      b'  data_type: uint16',
  ])

  # TODO: move system time into separate structure.

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _FIXED_SIZE_DATA_SECTION = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'job_fixed_size_data_section')

  _FIXED_SIZE_DATA_SECTION_SIZE = _FIXED_SIZE_DATA_SECTION.GetByteSize()

  _JOB_VARIABLE_SIZE_DATA_STRUCT = construct.Struct(
      u'job_variable_size_data',
      construct.Bytes(u'data', 1))

  def _DebugPrinFixedSizeDataSection(self, fixed_size_data_section):
    """Prints fixed-size data section debug information.

    Args:
      fixed_size_data_section (job_fixed_size_data_section): fixed-size data
          section.
    """
    value_string = u'0x{0:04x}'.format(fixed_size_data_section.product_version)
    self._DebugPrintValue(u'Product version', value_string)

    value_string = u'0x{0:04x}'.format(fixed_size_data_section.format_version)
    self._DebugPrintValue(u'Format version', value_string)

    value_string = u'{0!s}'.format(fixed_size_data_section.job_identifier)
    self._DebugPrintValue(u'Job identifier', value_string)

    value_string = u'0x{0:04x}'.format(
        fixed_size_data_section.application_name_size_offset)
    self._DebugPrintValue(u'Application name size offset', value_string)

    value_string = u'0x{0:04x}'.format(fixed_size_data_section.trigger_offset)
    self._DebugPrintValue(u'Trigger offset', value_string)

    value_string = u'{0:d}'.format(fixed_size_data_section.error_retry_count)
    self._DebugPrintValue(u'Error retry count', value_string)

    value_string = u'{0:d} minutes'.format(
        fixed_size_data_section.error_retry_interval)
    self._DebugPrintValue(u'Error retry interval', value_string)

    value_string = u'{0:d} minutes'.format(
        fixed_size_data_section.idle_deadline)
    self._DebugPrintValue(u'Idle deadline', value_string)

    value_string = u'{0:d} minutes'.format(fixed_size_data_section.idle_wait)
    self._DebugPrintValue(u'Idle wait', value_string)

    value_string = u'0x{0:08x}'.format(fixed_size_data_section.priority)
    self._DebugPrintValue(u'Priority', value_string)

    value_string = u'{0:d} milliseconds'.format(
        fixed_size_data_section.maximum_run_time)
    self._DebugPrintValue(u'Maximum run time', value_string)

    value_string = u'0x{0:08x}'.format(fixed_size_data_section.exit_code)
    self._DebugPrintValue(u'Exit code', value_string)

    value_string = u'0x{0:08x}'.format(fixed_size_data_section.status)
    self._DebugPrintValue(u'Status', value_string)

    value_string = u'0x{0:08x}'.format(fixed_size_data_section.flags)
    self._DebugPrintValue(u'Flags', value_string)

    value_string = u'{0:d}'.format(fixed_size_data_section.year)
    self._DebugPrintValue(u'Year', value_string)

    value_string = u'{0:d}'.format(fixed_size_data_section.month)
    self._DebugPrintValue(u'Month', value_string)

    value_string = u'{0:d}'.format(fixed_size_data_section.weekday)
    self._DebugPrintValue(u'Weekday', value_string)

    value_string = u'{0:d}'.format(fixed_size_data_section.day_of_month)
    self._DebugPrintValue(u'Day of month', value_string)

    value_string = u'{0:d}'.format(fixed_size_data_section.hours)
    self._DebugPrintValue(u'Hours', value_string)

    value_string = u'{0:d}'.format(fixed_size_data_section.minutes)
    self._DebugPrintValue(u'Minutes', value_string)

    value_string = u'{0:d}'.format(fixed_size_data_section.seconds)
    self._DebugPrintValue(u'Seconds', value_string)

    value_string = u'{0:d}'.format(fixed_size_data_section.milliseconds)
    self._DebugPrintValue(u'Milliseconds', value_string)

    self._DebugPrintText(u'\n')

  def _ReadFixedSizeDataSection(self, file_object):
    """Reads the fixed size data section.

    Args:
      file_object (file): file-like object.

    Raises:
      IOError: if the fixed size data section cannot be read.
    """
    file_offset = file_object.tell()
    fixed_size_data_section = self._ReadStructure(
        file_object, file_offset, self._FIXED_SIZE_DATA_SECTION_SIZE,
        self._FIXED_SIZE_DATA_SECTION, u'fixed size data section')

    if self._debug:
      self._DebugPrinFixedSizeDataSection(fixed_size_data_section)

  def _ReadVariableSizeDataSection(self, file_object):
    """Reads the variable size data section.

    Args:
      file_object (file): file-like object.

    Raises:
      IOError: if the variable size data section cannot be read.
    """
    # TODO: implement.
    _ = file_object

  def ReadFileObject(self, file_object):
    """Reads a Windows Task Scheduler job file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadFixedSizeDataSection(file_object)
    self._ReadVariableSizeDataSection(file_object)
