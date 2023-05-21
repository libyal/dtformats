# -*- coding: utf-8 -*-
"""Binary data format."""

import abc
import os

from dfdatetime import filetime as dfdatetime_filetime
from dfdatetime import posix_time as dfdatetime_posix_time

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import data_maps as dtfabric_data_maps
from dtfabric.runtime import fabric as dtfabric_fabric

from dtformats import errors
from dtformats import file_system


class BinaryDataFormat(object):
  """Binary data format."""

  # The dtFabric fabric, which must be set by a subclass using the
  # ReadDefinitionFile class method.
  _FABRIC = None

  # Preserve the absolute path value of __file__ in case it is changed
  # at run-time.
  _DEFINITION_FILES_PATH = os.path.dirname(__file__)

  _HEXDUMP_CHARACTER_MAP = [
      '.' if byte < 0x20 or byte > 0x7e else chr(byte) for byte in range(256)]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a binary data format.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(BinaryDataFormat, self).__init__()
    self._data_type_maps = {}
    self._debug = debug
    self._output_writer = output_writer

  def _DebugPrintData(self, description, data):
    """Prints data for debugging.

    Args:
      description (str): description.
      data (bytes): data.
    """
    if self._output_writer:
      lines, _ = self._FormatDataInHexadecimal(data)
      self._output_writer.WriteText(f'{description:s}:\n{lines:s}')

  def _DebugPrintDecimalValue(self, description, value):
    """Prints a decimal value for debugging.

    Args:
      description (str): description.
      value (int): value.
    """
    self._DebugPrintValue(description, f'{value:d}')

  def _DebugPrintFiletimeValue(self, description, value):
    """Prints a FILETIME timestamp value for debugging.

    Args:
      description (str): description.
      value (object): value.
    """
    if value == 0:
      date_time_string = 'Not set (0)'
    elif value == 0x7fffffffffffffff:
      date_time_string = 'Never (0x7fffffffffffffff)'
    else:
      date_time = dfdatetime_filetime.Filetime(timestamp=value)
      date_time_string = date_time.CopyToDateTimeString()
      if date_time_string:
        date_time_string = f'{date_time_string:s} UTC'
      else:
        date_time_string = f'0x{value:08x}'

    self._DebugPrintValue(description, date_time_string)

  def _DebugPrintStructureObject(self, structure_object, debug_info):
    """Prints structure object debug information.

    Args:
      structure_object (object): structure object.
      debug_info (list[tuple[str, str, int]]): debug information.
    """
    text = self._FormatStructureObject(structure_object, debug_info)
    self._output_writer.WriteText(text)

  def _DebugPrintPosixTimeValue(self, description, value):
    """Prints a POSIX timestamp value for debugging.

    Args:
      description (str): description.
      value (object): value.
    """
    if value == 0:
      date_time_string = 'Not set (0)'
    else:
      date_time = dfdatetime_posix_time.PosixTime(timestamp=value)
      date_time_string = date_time.CopyToDateTimeString()
      if date_time_string:
        date_time_string = f'{date_time_string:s} UTC'
      else:
        date_time_string = f'0x{value:08x}'

    self._DebugPrintValue(description, date_time_string)

  def _DebugPrintText(self, text):
    """Prints text for debugging.

    Args:
      text (str): text.
    """
    if self._output_writer:
      self._output_writer.WriteText(text)

  def _DebugPrintValue(self, description, value):
    """Prints a value for debugging.

    Args:
      description (str): description.
      value (object): value.
    """
    if self._output_writer:
      text = self._FormatValue(description, value)
      self._output_writer.WriteText(text)

  def _FormatDataInHexadecimal(self, data):
    """Formats data in a hexadecimal representation.

    Args:
      data (bytes): data.

    Returns:
      tuple[str, bool]: hexadecimal representation of the data and True to
          indicate there should be a new line after value description.
    """
    in_group = False
    previous_hexadecimal_string = None

    lines = []
    data_size = len(data)
    for block_index in range(0, data_size, 16):
      data_string = data[block_index:block_index + 16]

      hexadecimal_byte_values = []
      printable_values = []
      for byte_value in data_string:
        if isinstance(byte_value, str):
          byte_value = ord(byte_value)

        hexadecimal_byte_values.append(f'{byte_value:02x}')

        printable_value = self._HEXDUMP_CHARACTER_MAP[byte_value]
        printable_values.append(printable_value)

      remaining_size = 16 - len(data_string)
      if remaining_size == 0:
        whitespace = ''
      elif remaining_size >= 8:
        whitespace = ' ' * ((3 * remaining_size) - 1)
      else:
        whitespace = ' ' * (3 * remaining_size)

      hexadecimal_string_part1 = ' '.join(hexadecimal_byte_values[0:8])
      hexadecimal_string_part2 = ' '.join(hexadecimal_byte_values[8:16])
      hexadecimal_string = (
          f'{hexadecimal_string_part1:s}  {hexadecimal_string_part2:s}'
          f'{whitespace:s}')

      if (previous_hexadecimal_string is not None and
          previous_hexadecimal_string == hexadecimal_string and
          block_index + 16 < data_size):

        if not in_group:
          in_group = True

          lines.append('...')

      else:
        printable_string = ''.join(printable_values)

        lines.append((f'0x{block_index:08x}  {hexadecimal_string:s}  '
                      f'{printable_string:s}'))

        in_group = False
        previous_hexadecimal_string = hexadecimal_string

    lines.extend(['', ''])
    return '\n'.join(lines), True

  def _FormatArrayOfIntegersAsDecimals(self, array_of_integers):
    """Formats an array of integers as decimals.

    Args:
      array_of_integers (list[int]): array of integers.

    Returns:
      tuple[str, bool]: array of integers formatted as decimals and False to
          indicate there should be no new line after value description.
    """
    lines = ', '.join([f'{integer:d}' for integer in array_of_integers])
    return lines, False

  def _FormatArrayOfIntegersAsOffsets(self, array_of_integers):
    """Formats an array of integers as offset.

    Args:
      array_of_integers (list[int]): array of integers.

    Returns:
      tuple[str, bool]: array of integers formatted as offsets and False to
          indicate there should be no new line after value description.
    """
    lines = ', '.join([
        f'{integer:d} (0x{integer:08x})' for integer in array_of_integers])
    return lines, False

  def _FormatArrayOfIntegersAsIPv4Address(self, array_of_integers):
    """Formats an array of integers as an IPv4 address.

    Args:
      array_of_integers (list[int]): array of integers.

    Returns:
      tuple[str, bool]: array of integers formatted as an IPv4 address or None
          if the number of integers in the array is not supported and False to
          indicate there should be no new line after value description.
    """
    lines = None
    if len(array_of_integers) == 4:
      lines = '.'.join([f'{octet:d}' for octet in array_of_integers])

    return lines, False

  def _FormatArrayOfIntegersAsIPv6Address(self, array_of_integers):
    """Formats an array of integers as an IPv6 address.

    Args:
      array_of_integers (list[int]): array of integers.

    Returns:
      tuple[str, bool]: array of integers formatted as an IPv6 address or None
          if the number of integers in the array is not supported and False to
          indicate there should be no new line after value description.
    """
    lines = None
    if len(array_of_integers) == 16:
      # Note that socket.inet_ntop() is not supported on Windows.
      octet_pairs = zip(array_of_integers[0::2], array_of_integers[1::2])
      octet_pairs = [octet1 << 8 | octet2 for octet1, octet2 in octet_pairs]
      # TODO: omit ":0000" from the string.
      lines = ':'.join([f'{octet_pair:04x}' for octet_pair in octet_pairs])

    return lines, False

  def _FormatFloatingPoint(self, floating_point):
    """Formats a floating-point number.

    Args:
      floating_point (float): floating-point number.

    Returns:
      tuple[str, bool]: formatted floating-point number and False to indicate
          there should be no new line after value description.
    """
    return f'{floating_point:f}', False

  def _FormatIntegerAsDecimal(self, integer):
    """Formats an integer as a decimal.

    Args:
      integer (int): integer.

    Returns:
      tuple[str, bool]: integer formatted as a decimal and False to indicate
          there should be no new line after value description.
    """
    return f'{integer:d}', False

  def _FormatIntegerAsFiletime(self, integer):
    """Formats an integer as a FILETIME date and time value.

    Args:
      integer (int): integer.

    Returns:
      tuple[str, bool]: integer formatted as a FILETIME date and time value and
          False to indicate there should be no new line after value description.
    """
    if integer == 0:
      return 'Not set (0)', False

    if integer == 0x7fffffffffffffff:
      return 'Never (0x7fffffffffffffff)', False

    date_time = dfdatetime_filetime.Filetime(timestamp=integer)
    date_time_string = date_time.CopyToDateTimeString()
    if not date_time_string:
      return f'0x{integer:08x}', False

    return f'{date_time_string:s} UTC', False

  def _FormatIntegerAsHexadecimal2(self, integer):
    """Formats an integer as an 2-digit hexadecimal.

    Args:
      integer (int): integer.

    Returns:
      tuple[str, bool]: integer formatted as a 2-digit hexadecimal and False
          to indicate there should be no new line after value description.
    """
    return f'0x{integer:02x}', False

  def _FormatIntegerAsHexadecimal4(self, integer):
    """Formats an integer as an 4-digit hexadecimal.

    Args:
      integer (int): integer.

    Returns:
      tuple[str, bool]: integer formatted as a 4-digit hexadecimal and False
          to indicate there should be no new line after value description.
    """
    return f'0x{integer:04x}', False

  def _FormatIntegerAsHexadecimal8(self, integer):
    """Formats an integer as an 8-digit hexadecimal.

    Args:
      integer (int): integer.

    Returns:
      tuple[str, bool]: integer formatted as a 8-digit hexadecimal and False
          to indicate there should be no new line after value description.
    """
    return f'0x{integer:08x}', False

  def _FormatIntegerAsPosixTime(self, integer):
    """Formats an integer as a POSIX date and time value.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a POSIX date and time value.
    """
    if integer == 0:
      return 'Not set (0)'

    date_time = dfdatetime_posix_time.PosixTime(timestamp=integer)
    date_time_string = date_time.CopyToDateTimeString()
    if not date_time_string:
      return f'0x{integer:08x}'

    return f'{date_time_string:s} UTC'

  def _FormatIntegerAsPosixTimeInMicroseconds(self, integer):
    """Formats an integer as a POSIX date and time in microseconds value.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a POSIX date and time in microseconds value.
    """
    if integer == 0:
      return 'Not set (0)'

    date_time = dfdatetime_posix_time.PosixTimeInMicroseconds(timestamp=integer)
    date_time_string = date_time.CopyToDateTimeString()
    if not date_time_string:
      return f'0x{integer:08x}'

    return f'{date_time_string:s} UTC'

  def _FormatIntegerAsPosixTimeInNanoseconds(self, integer):
    """Formats an integer as a POSIX date and time in nanoseconds value.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a POSIX date and time in nanoseconds value.
    """
    if integer == 0:
      return 'Not set (0)'

    date_time = dfdatetime_posix_time.PosixTimeInNanoseconds(timestamp=integer)
    date_time_string = date_time.CopyToDateTimeString()
    if not date_time_string:
      return f'0x{integer:08x}'

    return f'{date_time_string:s} UTC'

  def _FormatIntegerAsOffset(self, integer):
    """Formats an integer as an offset.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as an offset.
    """
    return f'{integer:d} (0x{integer:08x})'

  def _FormatString(self, string):
    """Formats a string.

    Args:
      string (str): string.

    Returns:
      str: formatted string.
    """
    return string.rstrip('\x00')

  def _FormatStructureObject(self, structure_object, debug_info):
    """Formats a structure object debug information.

    Args:
      structure_object (object): structure object.
      debug_info (list[tuple[str, str, int]]): debug information.

    Returns:
      str: structure object debug information.
    """
    lines = []

    for attribute_name, description, value_format_callback in debug_info:
      attribute_value = getattr(structure_object, attribute_name, None)
      if attribute_value is None:
        continue

      value_format_function = None
      if value_format_callback:
        value_format_function = getattr(self, value_format_callback, None)
      if value_format_function:
        attribute_value = value_format_function(attribute_value)

      # TODO: refactor formatting callbacks to return tuple.
      if isinstance(attribute_value, tuple):
        attribute_value, new_line_after_description = attribute_value
      else:
        new_line_after_description = True

      if isinstance(attribute_value, str) and '\n' in attribute_value:
        text = ''
        if description is not None:
          if new_line_after_description:
            text = f'{description:s}:\n'
          else:
            alignment, _ = divmod(len(description), 8)
            alignment_string = '\t' * (8 - alignment + 1)
            text = f'{description:s}{alignment_string:s}: '

        text = ''.join([text, attribute_value])

      else:
        text = self._FormatValue(description, attribute_value)

      lines.append(text)

    if not lines[-1] or lines[-1][-2:] != '\n\n':
      lines.append('\n')

    return ''.join(lines)

  def _FormatUUIDAsString(self, uuid):
    """Formats an UUID as string.

    Args:
      uuid (uuid.UUID): UUID.

    Returns:
      str: UUID formatted as string.
    """
    return f'{uuid!s}'

  def _FormatValue(self, description, value):
    """Formats a value for debugging.

    Args:
      description (str): description.
      value (object): value.

    Returns:
      str: formatted value.
    """
    alignment, _ = divmod(len(description), 8)
    alignment_string = '\t' * (8 - alignment + 1)
    return f'{description:s}{alignment_string:s}: {value!s}\n'

  def _GetDataTypeMap(self, name):
    """Retrieves a data type map defined by the definition file.

    The data type maps are cached for reuse.

    Args:
      name (str): name of the data type as defined by the definition file.

    Returns:
      dtfabric.DataTypeMap: data type map which contains a data type definition,
          such as a structure, that can be mapped onto binary data.

    Raises:
      RuntimeError: if '_FABRIC' is not set.
    """
    if not getattr(self, '_FABRIC', None):
      raise RuntimeError('Missing _FABRIC value')

    data_type_map = self._data_type_maps.get(name, None)
    if not data_type_map:
      data_type_map = self._FABRIC.CreateDataTypeMap(name)
      self._data_type_maps[name] = data_type_map

    return data_type_map

  def _ReadData(self, file_object, file_offset, data_size, description):
    """Reads data.

    Args:
      file_object (file): a file-like object.
      file_offset (int): offset of the data relative to the start of
          the file-like object.
      data_size (int): size of the data.
      description (str): description of the data.

    Returns:
      bytes: byte stream containing the data.

    Raises:
      ParseError: if the data cannot be read.
      ValueError: if the file-like object is missing.
    """
    if not file_object:
      raise ValueError('Missing file-like object.')

    file_object.seek(file_offset, os.SEEK_SET)

    read_error = ''

    try:
      data = file_object.read(data_size)
      read_count = len(data)

      if read_count != data_size:
        read_error = (
            f'missing data (read: {read_count:d}, requested: {data_size:d})')

    except IOError as exception:
      read_error = f'{exception!s}'

    if read_error:
      raise errors.ParseError((
          f'Unable to read {description:s} data at offset: {file_offset:d} '
          f'(0x{file_offset:08x}) with error: {read_error:s}'))

    return data

  def _ReadStructureFromByteStream(
      self, byte_stream, file_offset, data_type_map, description, context=None):
    """Reads a structure from a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      file_offset (int): offset of the structure data relative to the start
          of the file-like object.
      data_type_map (dtfabric.DataTypeMap): data type map of the structure.
      description (str): description of the structure.
      context (Optional[dtfabric.DataTypeMapContext]): data type map context.

    Returns:
      object: structure values object.

    Raises:
      ParseError: if the structure cannot be read.
      ValueError: if file-like object or data type map is missing.
    """
    if not byte_stream:
      raise ValueError('Missing byte stream.')

    if not data_type_map:
      raise ValueError('Missing data type map.')

    try:
      return data_type_map.MapByteStream(byte_stream, context=context)
    except (dtfabric_errors.ByteStreamTooSmallError,
            dtfabric_errors.MappingError) as exception:
      raise errors.ParseError((
          f'Unable to map {description:s} data at offset: {file_offset:d} '
          f'(0x{file_offset:08x}) with error: {exception!s}'))

  def _ReadStructureFromFileObject(
      self, file_object, file_offset, data_type_map, description):
    """Reads a structure from a file-like object.

    If the data type map has a fixed size this method will read the predefined
    number of bytes from the file-like object. If the data type map has a
    variable size, depending on values in the byte stream, this method will
    continue to read from the file-like object until the data type map can be
    successfully mapped onto the byte stream or until an error occurs.

    Args:
      file_object (file): a file-like object to parse.
      file_offset (int): offset of the structure data relative to the start
          of the file-like object.
      data_type_map (dtfabric.DataTypeMap): data type map of the structure.
      description (str): description of the structure.

    Returns:
      tuple[object, int]: structure values object and data size of
          the structure.

    Raises:
      ParseError: if the structure cannot be read.
      ValueError: if the file-like object is missing.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading {description:s} at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    context = None
    data = b''
    last_data_size = 0

    data_size = data_type_map.GetSizeHint()
    while data_size != last_data_size:
      read_offset = file_offset + last_data_size
      read_size = data_size - last_data_size
      data_segment = self._ReadData(
          file_object, read_offset, read_size, description)

      data = b''.join([data, data_segment])

      try:
        context = dtfabric_data_maps.DataTypeMapContext()
        structure_values_object = data_type_map.MapByteStream(
            data, context=context)

        if self._debug:
          first_letter = description[0].upper()
          self._DebugPrintData(
              f'{first_letter:s}{description[1:]:s} data', data)

        return structure_values_object, data_size

      except dtfabric_errors.ByteStreamTooSmallError:
        pass

      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError((
            f'Unable to map {description:s} data at offset: {file_offset:d} '
            f'(0x{file_offset:08x}) with error: {exception!s}'))

      last_data_size = data_size
      data_size = data_type_map.GetSizeHint(context=context)

    raise errors.ParseError((
        f'Unable to read {description:s} at offset: {file_offset:d} '
        f'(0x{file_offset:08x})'))

  def _ReadStructureObjectFromFileObject(
      self, file_object, file_offset, data_type_map_name, description,
      debug_info):
    """Reads a structure object from a file-like object.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the structure data relative to the start
          of the file-like object.
      data_type_map_name (str): name of the data type map of the structure.
      description (str): description of the structure.
      debug_info (list[tuple[str, str, int]]): debug information.

    Returns:
      object: structure object.

    Raises:
      ParseError: if the structure cannot be read.
      RuntimeError: if '_FABRIC' is not set.
      ValueError: if the file-like object is missing.
    """
    data_type_map = self._GetDataTypeMap(data_type_map_name)

    structure_object, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, description)

    if self._debug:
      self._DebugPrintStructureObject(structure_object, debug_info)

    return structure_object

  @classmethod
  def ReadDefinitionFile(cls, filename):
    """Reads a dtFabric definition file.

    Args:
      filename (str): name of the dtFabric definition file.

    Returns:
      dtfabric.DataTypeFabric: data type fabric which contains the data format
          data type maps of the data type definition, such as a structure, that
          can be mapped onto binary data or None if no filename is provided.
    """
    if not filename:
      return None

    path = os.path.join(cls._DEFINITION_FILES_PATH, filename)
    with open(path, 'rb') as file_object:
      definition = file_object.read()

    return dtfabric_fabric.DataTypeFabric(yaml_definition=definition)


class BinaryDataFile(BinaryDataFormat):
  """Binary data file."""

  def __init__(self, debug=False, file_system_helper=None, output_writer=None):
    """Initializes a binary data file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      file_system_helper (Optional[FileSystemHelper]): file system helper.
      output_writer (Optional[OutputWriter]): output writer.
    """
    if not file_system_helper:
      file_system_helper = file_system.NativeFileSystemHelper()

    super(BinaryDataFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._file_object = None
    self._file_object_opened_in_object = False
    self._file_size = 0
    self._file_system_helper = file_system_helper
    self._path = None

  def Close(self):
    """Closes a binary data file.

    Raises:
      IOError: if the file is not opened.
      OSError: if the file is not opened.
    """
    if not self._file_object:
      raise IOError('File not opened')

    if self._file_object_opened_in_object:
      self._file_object.close()
      self._file_object_opened_in_object = False
    self._file_object = None
    self._path = None

  def Open(self, path):
    """Opens a binary data file.

    Args:
      path (str): path to the file.

    Raises:
      IOError: if the file is already opened.
      OSError: if the file is already opened.
    """
    if self._file_object:
      raise IOError('File already opened')

    self._file_size = self._file_system_helper.GetFileSizeByPath(path)
    self._path = path

    file_object = self._file_system_helper.OpenFileByPath(path)

    self.ReadFileObject(file_object)

    self._file_object = file_object
    self._file_object_opened_in_object = True

  @abc.abstractmethod
  def ReadFileObject(self, file_object):
    """Reads binary data from a file-like object.

    Args:
      file_object (file): file-like object.
    """
