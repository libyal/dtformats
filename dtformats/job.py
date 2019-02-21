# -*- coding: utf-8 -*-
"""Windows Task Scheduler job files."""

from __future__ import unicode_literals

from dtformats import data_format


class WindowsTaskSchedularJobFile(data_format.BinaryDataFile):
  """Windows Task Scheduler job (.job) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('job.yaml')

  # TODO: add format definition.
  # https://msdn.microsoft.com/en-us/library/cc248285.aspx

  # TODO: add job signature
  # https://msdn.microsoft.com/en-us/library/cc248299.aspx

  _FIXED_LENGTH_DATA_SECTION = _FABRIC.CreateDataTypeMap(
      'job_fixed_length_data_section')

  _FIXED_LENGTH_DATA_SECTION_SIZE = _FIXED_LENGTH_DATA_SECTION.GetByteSize()

  _VARIABLE_LENGTH_DATA_SECTION = _FABRIC.CreateDataTypeMap(
      'job_variable_length_data_section')

  _DEBUG_INFO_FIXED_LENGTH_DATA_SECTION = [
      ('signature', 'Signature', '_FormatIntegerAsProductVersion'),
      ('format_version', 'Format version', '_FormatIntegerAsDecimal'),
      ('job_identifier', 'Job identifier', '_FormatUUIDAsString'),
      ('application_name_offset', 'Application name offset',
       '_FormatIntegerAsHexadecimal4'),
      ('triggers_offset', 'Triggers offset', '_FormatIntegerAsHexadecimal4'),
      ('error_retry_count', 'Error retry count', '_FormatIntegerAsDecimal'),
      ('error_retry_interval', 'Error retry interval',
       '_FormatIntegerAsIntervalInMinutes'),
      ('idle_deadline', 'Idle deadline', '_FormatIntegerAsIntervalInMinutes'),
      ('idle_wait', 'Idle wait', '_FormatIntegerAsIntervalInMinutes'),
      ('priority', 'Priority', '_FormatIntegerAsHexadecimal8'),
      ('maximum_run_time', 'Maximum run time',
       '_FormatIntegerAsIntervalInMilliseconds'),
      ('exit_code', 'Exit code', '_FormatIntegerAsHexadecimal8'),
      ('status', 'Status', '_FormatIntegerAsHexadecimal8'),
      ('flags', 'Flags', '_FormatIntegerAsHexadecimal8'),
      ('last_run_time', 'Last run time', '_FormatSystemTime')]

  _DEBUG_INFO_TRIGGER = [
      ('size', 'Size', '_FormatIntegerAsDecimal'),
      ('reserved1', 'Reserved1', '_FormatIntegerAsHexadecimal4'),
      ('start_date', 'Start date', '_FormatDate'),
      ('end_date', 'End date', '_FormatDate'),
      ('start_time', 'Start time', '_FormatTime'),
      ('duration', 'Duration', '_FormatIntegerAsIntervalInMinutes'),
      ('interval', 'Interval', '_FormatIntegerAsIntervalInMinutes'),
      ('trigger_flags', 'Trigger flags', '_FormatIntegerAsHexadecimal8'),
      ('trigger_type', 'Trigger type', '_FormatIntegerAsHexadecimal8'),
      ('trigger_arg0', 'Trigger arg0', '_FormatIntegerAsHexadecimal4'),
      ('trigger_arg1', 'Trigger arg1', '_FormatIntegerAsHexadecimal4'),
      ('trigger_arg2', 'Trigger arg2', '_FormatIntegerAsHexadecimal4'),
      ('trigger_padding', 'Trigger padding', '_FormatIntegerAsHexadecimal4'),
      ('trigger_reserved2', 'Trigger reserved2',
       '_FormatIntegerAsHexadecimal4'),
      ('trigger_reserved3', 'Trigger reserved3',
       '_FormatIntegerAsHexadecimal4')]

  _DEBUG_INFO_VARIABLE_LENGTH_DATA_SECTION = [
      ('running_instance_count', 'Running instance count',
       '_FormatIntegerAsDecimal'),
      ('application_name', 'Application name', '_FormatString'),
      ('parameters', 'Parameters', '_FormatString'),
      ('working_directory', 'Working directory', '_FormatString'),
      ('author', 'Author', '_FormatString'),
      ('comment', 'Comment', '_FormatString'),
      ('user_data', 'User data', '_FormatDataStream'),
      ('reserved_data', 'Reserved data', '_FormatDataStream'),
      ('number_of_triggers', 'Number of triggers', '_FormatIntegerAsDecimal')]

  def _FormatDataStream(self, data_stream):
    """Formats a data stream structure

    Args:
      data_stream (job_reserved_data|job_user_data): data stream structure

    Returns:
      str: formatted data stream structure
    """
    # TODO: print data_stream.size on a separate line
    return self._FormatDataInHexadecimal(data_stream.stream)

  def _FormatDate(self, date):
    """Formats a date structure.

    Args:
      date (job_trigger_date): date structure.

    Returns:
      str: formatted date structure.
    """
    return '{0:04d}-{1:02d}-{2:02d}'.format(
        date.year, date.month, date.day_of_month)

  def _FormatIntegerAsIntervalInMilliseconds(self, integer):
    """Formats an integer as an interval in milliseconds.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as an interval in milliseconds.
    """
    return '{0:d} milliseconds'.format(integer)

  def _FormatIntegerAsIntervalInMinutes(self, integer):
    """Formats an integer as an interval in minutes.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as an interval in minutes.
    """
    return '{0:d} minutes'.format(integer)

  def _FormatIntegerAsProductVersion(self, integer):
    """Formats an integer as a product version.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a product version.
    """
    return '0x{0:04x} ({1:d}.{2:d})'.format(
        integer, (integer >> 8) & 0xff, integer & 0xff)

  def _FormatString(self, string):
    """Formats a string structure

    Args:
      string (job_string): string structure

    Returns:
      str: formatted string structure
    """
    # TODO: print string.number_of_characters on a separate line
    return '({0:d} bytes) {1:s}'.format(
        string.number_of_characters * 2, string.string)

  def _FormatSystemTime(self, systemtime):
    """Formats a SYSTEMTIME structure.

    Args:
      systemtime (system_time): SYSTEMTIME structure.

    Returns:
      str: formatted SYSTEMTIME structure.
    """
    return '{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}.{6:03d}'.format(
        systemtime.year, systemtime.month, systemtime.day_of_month,
        systemtime.hours, systemtime.minutes, systemtime.seconds,
        systemtime.milliseconds)

  def _FormatTime(self, time):
    """Formats a time structure.

    Args:
      time (job_trigger_time): time structure.

    Returns:
      str: formatted time structure.
    """
    return '{0:02d}:{1:02d}'.format(time.hours, time.minutes)

  def _ReadFixedLengthDataSection(self, file_object):
    """Reads the fixed-length data section.

    Args:
      file_object (file): file-like object.

    Raises:
      IOError: if the fixed-length data section cannot be read.
    """
    file_offset = file_object.tell()
    data_section = self._ReadStructure(
        file_object, file_offset, self._FIXED_LENGTH_DATA_SECTION_SIZE,
        self._FIXED_LENGTH_DATA_SECTION, 'fixed-length data section')

    if self._debug:
      self._DebugPrintStructureObject(
          data_section, self._DEBUG_INFO_FIXED_LENGTH_DATA_SECTION)

  def _ReadVariableLengthDataSection(self, file_object):
    """Reads the variable-length data section.

    Args:
      file_object (file): file-like object.

    Raises:
      IOError: if the variable-length data section cannot be read.
    """
    file_offset = file_object.tell()
    data_size = self._file_size - file_offset
    data_section = self._ReadStructure(
        file_object, file_offset, data_size,
        self._VARIABLE_LENGTH_DATA_SECTION, 'variable-length data section')

    if self._debug:
      self._DebugPrintStructureObject(
          data_section, self._DEBUG_INFO_VARIABLE_LENGTH_DATA_SECTION)

      for trigger in data_section.triggers.triggers_array:
        self._DebugPrintStructureObject(trigger, self._DEBUG_INFO_TRIGGER)

  def ReadFileObject(self, file_object):
    """Reads a Windows Task Scheduler job file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadFixedLengthDataSection(file_object)
    self._ReadVariableLengthDataSection(file_object)
