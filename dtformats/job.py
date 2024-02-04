# -*- coding: utf-8 -*-
"""Windows Task Scheduler job files."""

from dtformats import data_format


class WindowsTaskConfiguration(object):
  """Windows Task configuration.

  Attributes:
    application_name (str): application name.
    author (str): author.
    comment (str): comment.
    error_retry_count (int): error retry count.
    error_retry_interval (int): error retry interval.
    identifier (str): identifier.
    parameters (str): parameters.
    priority (int): priority.
    working_directory (str): working directory.
  """

  def __init__(self):
    """Initializes a Windows Task configuration."""
    super(WindowsTaskConfiguration, self).__init__()
    self.application_name = None
    self.author = None
    self.comment = None
    self.error_retry_count = None
    self.error_retry_interval = None
    self.identifier = None
    self.parameters = None
    self.priority = None
    self.working_directory = None


class WindowsTaskSchedulerJobFile(data_format.BinaryDataFile):
  """Windows Task Scheduler job (.job) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('job.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'job.debug.yaml', custom_format_callbacks={
          'data_stream': '_FormatDataStream',
          'date': '_FormatDate',
          'interval_in_milliseconds': '_FormatIntegerAsIntervalInMilliseconds',
          'interval_in_minutes': '_FormatIntegerAsIntervalInMinutes',
          'product_version': '_FormatIntegerAsProductVersion',
          'system_time': '_FormatSystemTime',
          'time': '_FormatTime'})

  # TODO: add job signature
  # https://msdn.microsoft.com/en-us/library/cc248299.aspx

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Windows Task Scheduler job (.job) file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(WindowsTaskSchedulerJobFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._task_configuration = WindowsTaskConfiguration()

  def _FormatDataStream(self, data_stream):
    """Formats a data stream structure.

    Args:
      data_stream (job_reserved_data|job_user_data): data stream structure

    Returns:
      str: formatted data stream structure
    """
    # TODO: print data_stream.size on a separate line
    lines, _ = self._FormatDataInHexadecimal(data_stream.stream)
    return lines

  def _FormatDate(self, date):
    """Formats a date structure.

    Args:
      date (job_trigger_date): date structure.

    Returns:
      str: formatted date structure.
    """
    return f'{date.year:04d}-{date.month:02d}-{date.day_of_month:02d}'

  def _FormatIntegerAsIntervalInMilliseconds(self, integer):
    """Formats an integer as an interval in milliseconds.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as an interval in milliseconds.
    """
    return f'{integer:d} milliseconds'

  def _FormatIntegerAsIntervalInMinutes(self, integer):
    """Formats an integer as an interval in minutes.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as an interval in minutes.
    """
    return f'{integer:d} minutes'

  def _FormatIntegerAsProductVersion(self, integer):
    """Formats an integer as a product version.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a product version.
    """
    major_version = (integer >> 8) & 0xff
    minor_version = (integer >> 8) & 0xff
    return f'0x{integer:04x} ({major_version:d}.{minor_version:d})'

  def _FormatString(self, string):
    """Formats a string structure.

    Args:
      string (job_string): string structure

    Returns:
      str: formatted string structure
    """
    # TODO: print string.number_of_characters on a separate line
    number_of_bytes = string.number_of_characters * 2
    return f'({number_of_bytes:d} bytes) {string.string:s}'

  def _FormatSystemTime(self, systemtime):
    """Formats a SYSTEMTIME structure.

    Args:
      systemtime (system_time): SYSTEMTIME structure.

    Returns:
      str: formatted SYSTEMTIME structure.
    """
    return (f'{systemtime.year:04d}-{systemtime.month:02d}-'
            f'{systemtime.day_of_month:02d} {systemtime.hours:02d}:'
            f'{systemtime.minutes:02d}:{systemtime.seconds:02d}.'
            f'{systemtime.milliseconds:03d}')

  def _FormatTime(self, time):
    """Formats a time structure.

    Args:
      time (job_trigger_time): time structure.

    Returns:
      str: formatted time structure.
    """
    return f'{time.hours:02d}:{time.minutes:02d}'

  def GetWindowsTaskConfiguration(self):
    """Retrieves the Windows task configuration represented by the job file.

    Return:
     WindowsTaskConfiguration: Windows task configuration.
    """
    return self._task_configuration

  def ReadFileObject(self, file_object):
    """Reads a Windows Task Scheduler job file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    data_section = self._ReadStructureObjectFromFileObject(
        file_object, 0, 'job_fixed_length_data_section',
        'fixed-length data section')

    self._task_configuration.error_retry_count = data_section.error_retry_count
    self._task_configuration.error_retry_interval = (
        data_section.error_retry_interval)
    self._task_configuration.identifier = str(data_section.job_identifier)
    self._task_configuration.priority = data_section.priority

    file_offset = file_object.tell()
    data_section = self._ReadStructureObjectFromFileObject(
        file_object, file_offset, 'job_variable_length_data_section',
        'variable-length data section')

    if self._debug:
      # TODO: refactor job_trigger debug info into
      # job_variable_length_data_section debug info?
      for trigger in data_section.triggers.triggers_array:
        debug_info = self._DEBUG_INFORMATION.get('job_trigger', None)
        self._DebugPrintStructureObject(trigger, debug_info)

    self._task_configuration.application_name = (
        data_section.application_name.string)
    self._task_configuration.parameters = data_section.parameters.string
    self._task_configuration.working_directory = (
        data_section.working_directory.string)
    self._task_configuration.author = data_section.author.string
    self._task_configuration.comment = data_section.comment.string
