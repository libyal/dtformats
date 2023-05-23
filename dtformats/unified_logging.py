# -*- coding: utf-8 -*-
"""Apple Unified Logging and Activity Tracing files."""

import abc
import base64
import collections
import re
import uuid

import lz4.block

from dfdatetime import posix_time as dfdatetime_posix_time

from dtfabric.runtime import data_maps as dtfabric_data_maps

from dtformats import darwin
from dtformats import data_format
from dtformats import errors


class DSCRange(object):
  """Shared-Cache Strings (dsc) range.

  Attributes:
    data_offset (int): offset of the format string data.
    path (str): path.
    range_offset (int): the offset of the range.
    range_sizes (int): the size of the range.
    uuid (uuid.UUID): the UUID.
    uuid_index (int): index of the UUID.
  """

  def __init__(self):
    """Initializes a Shared-Cache Strings (dsc) range."""
    super(DSCRange, self).__init__()
    self.data_offset = None
    self.path = None
    self.range_offset = None
    self.range_size = None
    self.uuid = None
    self.uuid_index = None


class DSCUUID(object):
  """Shared-Cache Strings (dsc) UUID.

  Attributes:
    path (str): path.
    sender_identifier (uuid.UUID): the sender identifier.
    text_offset (int): the offset of the text.
    text_sizes (int): the size of the text.
  """

  def __init__(self):
    """Initializes a Shared-Cache Strings (dsc) UUID."""
    super(DSCUUID, self).__init__()
    self.path = None
    self.sender_identifier = None
    self.text_offset = None
    self.text_size = None


class StringFormatter(object):
  """String formatter."""

  _OPERATOR_REGEX = re.compile(
      r'(%'
      r'(?:\{([^\}]{1,64})\})?'         # Optional value type decoder.
      r'([-+0 #]{0,5})'                 # Optional flags.
      r'([0-9]+|\*)?'                   # Optional width.
      r'(\.(?:[0-9]+|\*))?'             # Optional precision.
      r'(?:h|hh|j|l|ll|L|t|q|z)?'       # Optional length modifier.
      r'([@aAcCdDeEfFgGinoOpPsSuUxX])'  # Conversion specifier.
      r'|%%)')

  _PYTHON_SPECIFIERS = {
      '@': 's',
      'D': 'd',
      'i': 'd',
      'O': 'o',
      'p': 'x',
      'P': 's',
      'u': 'd',
      'U': 'd'}

  _TYPE_HINTS = {
      'd': 'signed',
      'D': 'signed',
      'i': 'signed',
      'o': 'unsigned',
      'O': 'unsigned',
      'p': 'unsigned',
      'u': 'unsigned',
      'U': 'unsigned',
      'x': 'unsigned',
      'X': 'unsigned'}

  def __init__(self):
    """Initializes a string formatter."""
    super(StringFormatter, self).__init__()
    self._decoders = []
    self._format_string = None
    self._formatters = []
    self._type_hints = []

  @property
  def number_of_formatters(self):
    """int: number of formatters."""
    return len(self._formatters)

  def FormatString(self, values):
    """Formats the string.

    Args:
      values (list[str]): values.

    Returns:
      str: formatted string.
    """
    # Add place holders for missing values.
    while len(values) < len(self._formatters):
      values.append('<decode: missing data>')

    if self._format_string is None:
      # TODO: determine what the MacOS log tool shows.
      formatted_string = 'ERROR: missing format string\n'
    elif self._formatters:
      formatted_string = self._format_string.format(*values)
    else:
      formatted_string = self._format_string

    if not formatted_string or formatted_string[-1] != '\n':
      return f'{formatted_string:s}\n'

    return formatted_string

  def FormatValue(self, value_index, value, precision=None):
    """Formats a value.

    Args:
      value_index (int): value index.
      value (object): value.
      precision (int): precision.

    Returns:
      str: formatted value or None if not available.
    """
    try:
      formatter = self._formatters[value_index]
    except IndexError:
      return None

    # TODO: add precision support.
    _ = precision
    return formatter.format(value)

  def GetDecoderNamesByIndex(self, value_index):
    """Retrieves the decoder names of a specific value.

    Args:
      value_index (int): value index.

    Returns:
      list[str]: decoder names.
    """
    try:
      return self._decoders[value_index]
    except IndexError:
      return []

  def GetTypeHintByIndex(self, value_index):
    """Retrieves the specific type of a specific value..

    Args:
      value_index (int): value index.

    Returns:
      list[str]: type hint or None if not available.
    """
    try:
      return self._type_hints[value_index]
    except IndexError:
      return None

  def ParseFormatString(self, format_string):
    """Parses an Unified Logging format string.

    Args:
      format_string (str): Unified Logging format string.
    """
    self._decoders = []
    self._format_string = None
    self._formatters = []
    self._type_hints = []

    if not format_string:
      return

    specifier_index = 0
    last_match_end = 0
    segments = []

    for match in self._OPERATOR_REGEX.finditer(format_string):
      literal, decoder, flags, width, precision, specifier = match.groups()

      match_start, match_end = match.span()
      if match_start > last_match_end:
        string_segment = format_string[last_match_end:match_start]
        string_segment = string_segment.replace('{', '{{')
        string_segment = string_segment.replace('}', '}}')
        segments.append(string_segment)

      if literal == '%%':
        literal = '%'
      elif specifier:
        flags = flags.replace('-', '>')

        decoder = decoder or ''
        decoder_names = [value.strip() for value in decoder.split(',')]

        # Remove private, public and sensitive value type decoders.
        decoder_names = [
            value for value in decoder_names
            if value not in ('', 'private', 'public', 'sensitive')]

        width = width or ''

        if decoder_names:
          python_specifier = 's'
        else:
          python_specifier = self._PYTHON_SPECIFIERS.get(specifier, specifier)

        # Ignore the precision of specifier "P" since it refers to the binary
        # data not the resulting string.

        # Prevent: "ValueError: Precision not allowed in integer format
        # specifier", "Format specifier missing precision" and ".0" formatting
        # as an empty string.
        if specifier == 'P' or python_specifier in ('d', 'o', 'x', 'X') or (
            python_specifier == 's' and precision in ('.0', '.*')):
          precision = ''
        else:
          precision = precision or ''

        if specifier == 'p':
          formatter = (
              f'0x{{0:{flags:s}{precision:s}{width:s}{python_specifier:s}}}')
        else:
          formatter = (
              f'{{0:{flags:s}{precision:s}{width:s}{python_specifier:s}}}')

        type_hint = self._TYPE_HINTS.get(specifier, None)

        self._decoders.append(decoder_names)
        self._formatters.append(formatter)
        self._type_hints.append(type_hint)

        literal = f'{{{specifier_index:d}:s}}'
        specifier_index += 1

      last_match_end = match_end

      segments.append(literal)

    string_size = len(format_string)
    if string_size > last_match_end:
      string_segment = format_string[last_match_end:string_size]
      string_segment = string_segment.replace('{', '{{')
      string_segment = string_segment.replace('}', '}}')
      segments.append(string_segment)

    self._format_string = ''.join(segments)


class BaseFormatStringDecoder(object):
  """Format string decoder interface."""

  @abc.abstractmethod
  def FormatValue(self, value):
    """Formats a value.

    Args:
      value (object): value.

    Returns:
      str: formatted value.
    """


class BooleanFormatStringDecoder(BaseFormatStringDecoder):
  """Boolean value format string decoder."""

  def FormatValue(self, value):
    """Formats a boolean value.

    Args:
      value (int): boolean value.

    Returns:
      str: formatted boolean value.
    """
    if value:
      return 'true'

    return 'false'


class DateTimeInSecondsFormatStringDecoder(BaseFormatStringDecoder):
  """Date and time value in seconds format string decoder."""

  def FormatValue(self, value):
    """Formats a date and time value in seconds.

    Args:
      value (int): timestamp that contains the number of seconds since
          1970-01-01 00:00:00.

    Returns:
      str: formatted date and time value in seconds.
    """
    date_time = dfdatetime_posix_time.PosixTime(timestamp=value)
    return date_time.CopyToDateTimeString()


class ErrorCodeFormatStringDecoder(BaseFormatStringDecoder):
  """Error code format string decoder."""

  def FormatValue(self, value):
    """Formats an error code value.

    Args:
      value (int): error code.

    Returns:
      str: formatted error code value.
    """
    error_message = darwin.DARWIN_ERROR_CODES.get(
        value, 'UNKNOWN: {0:d}'.format(value))

    # TODO: determine what the MacOS log tool shows when an error message is
    # not defined.
    return f'[{value:d}: {error_message:s}]'


class FileModeFormatStringDecoder(BaseFormatStringDecoder):
  """File mode format string decoder."""

  _FILE_TYPES = {
      0x1000: 'p',
      0x2000: 'c',
      0x4000: 'd',
      0x6000: 'b',
      0xa000: 'l',
      0xc000: 's'}

  def FormatValue(self, value):
    """Formats a file mode value.

    Args:
      value (int): file mode.

    Returns:
      str: formatted file mode value.
    """
    string_parts = 10 * ['-']

    if value & 0x0001:
      string_parts[9] = 'x'
    if value & 0x0002:
      string_parts[8] = 'w'
    if value & 0x0004:
      string_parts[7] = 'r'

    if value & 0x0008:
      string_parts[6] = 'x'
    if value & 0x0010:
      string_parts[5] = 'w'
    if value & 0x0020:
      string_parts[4] = 'r'

    if value & 0x0040:
      string_parts[3] = 'x'
    if value & 0x0080:
      string_parts[2] = 'w'
    if value & 0x0100:
      string_parts[1] = 'r'

    string_parts[0] = self._FILE_TYPES.get(value & 0xf000, '-')

    return ''.join(string_parts)


class IPv4FormatStringDecoder(BaseFormatStringDecoder):
  """IPv4 value format string decoder."""

  def FormatValue(self, value):
    """Formats an IPv4 value.

    Args:
      value (bytes): IPv4 value.

    Returns:
      str: formatted IPv4 value.
    """
    if len(value) != 4:
      # TODO: determine what the MacOS log tool shows.
      return 'ERROR: unsupported value'

    return '.'.join([f'{octet:d}' for octet in value])


class IPv6FormatStringDecoder(BaseFormatStringDecoder):
  """IPv6 value format string decoder."""

  def FormatValue(self, value):
    """Formats an IPv6 value.

    Args:
      value (bytes): IPv6 value.

    Returns:
      str: formatted IPv6 value.
    """
    if len(value) != 16:
      # TODO: determine what the MacOS log tool shows.
      return 'ERROR: unsupported value'

    # Note that socket.inet_ntop() is not supported on Windows.
    octet_pairs = zip(value[0::2], value[1::2])
    octet_pairs = [octet1 << 8 | octet2 for octet1, octet2 in octet_pairs]
    # TODO: determine if ":0000" should be omitted from the string.
    return ':'.join([f'{octet_pair:04x}' for octet_pair in octet_pairs])


class LocationStructureFormatStringDecoder(
    BaseFormatStringDecoder, data_format.BinaryDataFormat):
  """Shared functionality for location structure format string decoders."""

  # pylint: disable=abstract-method

  def _FormatStructure(self, structure, value_mappings):
    """Formats a structure.

    Args:
      structure (object): structure object to format.
      value_mappings (tuple[str, str]): mappings of output values to structure
          values.

    Return:
      str: formatted structure.
    """
    values = []

    for name, attribute_name in value_mappings:
      attribute_value = getattr(structure, attribute_name, None)
      if isinstance(attribute_value, bool):
        if attribute_value:
          attribute_value = 'true'
        else:
          attribute_value = 'false'

      elif isinstance(attribute_value, int):
        attribute_value = f'{attribute_value:d}'

      elif isinstance(attribute_value, float):
        attribute_value = f'{attribute_value:.0f}'

      values.append(f'"{name:s}":{attribute_value:s}')

    values_string = ','.join(values)

    return f'{{{values_string:s}}}'


class LocationClientManagerStateFormatStringDecoder(
    LocationStructureFormatStringDecoder):
  """Location client manager state format string decoder."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile(
      'macos_core_location.yaml')

  _VALUE_MAPPINGS = [
      ('locationRestricted', 'location_restricted'),
      ('locationServicesEnabledStatus', 'location_enabled_status')]

  def FormatValue(self, value):
    """Formats a location client manager state value.

    Args:
      value (bytes): location client manager state value.

    Returns:
      str: formatted location client manager state value.
    """
    if len(value) != 8:
      # TODO: determine what the MacOS log tool shows.
      return 'ERROR: unsupported value'

    data_type_map = self._GetDataTypeMap('client_manager_state_tracker_state')

    tracker_state = self._ReadStructureFromByteStream(
        value, 0, data_type_map, 'client manager state tracker state')

    return self._FormatStructure(tracker_state, self._VALUE_MAPPINGS)


class LocationLocationManagerStateFormatStringDecoder(
    LocationStructureFormatStringDecoder):
  """Location location manager state format string decoder."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile(
      'macos_core_location.yaml')

  _VALUE_MAPPINGS = [
      ('previousAuthorizationStatusValid',
       'previous_authorization_status_valid'),
      ('paused', 'paused'),
      ('requestingLocation', 'requesting_location'),
      ('updatingVehicleSpeed', 'updating_vehicle_speed'),
      ('desiredAccuracy', 'desired_accuracy'),
      ('allowsBackgroundLocationUpdates', 'allows_background_location_updates'),
      ('dynamicAccuracyReductionEnabled', 'dynamic_accuracy_reduction_enabled'),
      ('distanceFilter', 'distance_filter'),
      ('allowsLocationPrompts', 'allows_location_prompts'),
      ('activityType', 'activity_type'),
      ('groundAltitudeEnabled', 'ground_altitude_enabled'),
      ('pausesLocationUpdatesAutomatially',
       'pauses_location_updates_automatially'),
      ('fusionInfoEnabled', 'fusion_information_enabled'),
      ('isAuthorizedForWidgetUpdates', 'is_authorized_for_widget_updates'),
      ('updatingVehicleHeading', 'updating_vehicle_heading'),
      ('batchingLocation', 'batching_location'),
      ('showsBackgroundLocationIndicator',
       'shows_background_location_indicator'),
      ('updatingLocation', 'updating_location'),
      ('requestingRanging', 'requesting_ranging'),
      ('updatingHeading', 'updating_heading'),
      ('previousAuthorizationStatus', 'previous_authorization_status'),
      ('allowsMapCorrection', 'allows_map_correction'),
      ('matchInfoEnabled', 'match_information_enabled'),
      ('allowsAlteredAccessoryLoctions', 'allows_altered_accessory_location'),
      ('updatingRanging', 'updating_ranging'),
      ('limitsPrecision', 'limits_precision'),
      ('courtesyPromptNeeded', 'courtesy_prompt_needed'),
      ('headingFilter', 'heading_filter')]

  def FormatValue(self, value):
    """Formats a location location manager state value.

    Args:
      value (bytes): location location manager state value.

    Returns:
      str: formatted location location manager state value.
    """
    value_size = len(value)
    if value_size == 64:
      data_type_name = 'location_manager_state_tracker_state_v1'
    elif value_size == 72:
      data_type_name = 'location_manager_state_tracker_state_v2'
    else:
      # TODO: determine what the MacOS log tool shows.
      return 'ERROR: unsupported value'

    data_type_map = self._GetDataTypeMap(data_type_name)

    tracker_state = self._ReadStructureFromByteStream(
        value, 0, data_type_map, 'location manager state tracker state')

    return self._FormatStructure(tracker_state, self._VALUE_MAPPINGS)


class LocationEscapeOnlyFormatStringDecoder(BaseFormatStringDecoder):
  """Location escape only format string decoder."""

  def FormatValue(self, value):
    """Formats a location value.

    Args:
      value (str): location value.

    Returns:
      str: formatted location value.
    """
    value = value or ''
    value = value.replace('/', '\\/')
    return ''.join(['"', value, '"'])


class LocationSQLiteResultFormatStringDecoder(BaseFormatStringDecoder):
  """Location SQLite result format string decoder."""

  _SQLITE_RESULTS = {
      0: 'SQLITE_OK',
      1: 'SQLITE_ERROR',
      2: 'SQLITE_INTERNAL',
      3: 'SQLITE_PERM',
      4: 'SQLITE_ABORT',
      5: 'SQLITE_BUSY',
      6: 'SQLITE_LOCKED',
      7: 'SQLITE_NOMEM',
      8: 'SQLITE_READONLY',
      9: 'SQLITE_INTERRUPT',
      10: 'SQLITE_IOERR',
      11: 'SQLITE_CORRUPT',
      12: 'SQLITE_NOTFOUND',
      13: 'SQLITE_FULL',
      14: 'SQLITE_CANTOPEN',
      15: 'SQLITE_PROTOCOL',
      16: 'SQLITE_EMPTY',
      17: 'SQLITE_SCHEMA',
      18: 'SQLITE_TOOBIG',
      19: 'SQLITE_CONSTRAINT',
      20: 'SQLITE_MISMATCH',
      21: 'SQLITE_MISUSE',
      22: 'SQLITE_NOLFS',
      23: 'SQLITE_AUTH',
      24: 'SQLITE_FORMAT',
      25: 'SQLITE_RANGE',
      26: 'SQLITE_NOTADB',
      27: 'SQLITE_NOTICE',
      28: 'SQLITE_WARNING',
      100: 'SQLITE_ROW',
      101: 'SQLITE_DONE',
      266: 'SQLITE IO ERR READ'}

  def FormatValue(self, value):
    """Formats a SQLite result value.

    Args:
      value (bytes): SQLite result.

    Returns:
      str: formatted SQLite result value.
    """
    if len(value) != 4:
      # TODO: determine what the MacOS log tool shows.
      return 'ERROR: unsupported value'

    integer_value = int.from_bytes(value, 'little', signed=False)
    string_value = self._SQLITE_RESULTS.get(
        integer_value, 'SQLITE UNKNOWN: {0:d}'.format(integer_value))

    # TODO: determine what the MacOS log tool shows when an SQLite result is
    # not defined.
    return f'"{string_value:s}"'


class MaskHashFormatStringDecoder(BaseFormatStringDecoder):
  """Mask hash format string decoder."""

  def FormatValue(self, value):
    """Formats a value as a mask hash.

    Args:
      value (bytes): value.

    Returns:
      str: formatted value as a mask hash.
    """
    base64_string = base64.b64encode(value).decode('ascii')
    return f'<mask.hash: \'{base64_string:s}\'>'


class MDNSDNSHeaderFormatStringDecoder(
    BaseFormatStringDecoder, data_format.BinaryDataFormat):
  """mDNS DNS header format string decoder."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('macos_mdns.yaml')

  # Note that the flag names have a specific formatting order.
  _FLAG_NAMES = [
      (0x0400, 'AA'),  # Authoritative Answer
      (0x0200, 'TC'),  # Truncated Response
      (0x0100, 'RD'),  # Recursion Desired
      (0x0080, 'RA'),  # Recursion Available
      (0x0020, 'AD'),  # Authentic Data
      (0x0010, 'CD')]  # Checking Disabled

  _OPERATION_BITMASK = 0x7800

  _OPERATION_NAMES = {
      0: 'Query',
      1: 'IQuery',
      2: 'Status',
      3: 'Unassigned',
      4: 'Notify',
      5: 'Update',
      6: 'DSO'}

  _RESPONSE_CODE_BITMASK = 0x000f

  _RESPONSE_CODES = {
      0: 'NoError',
      1: 'FormErr',
      2: 'ServFail',
      3: 'NXDomain',
      4: 'NotImp',
      5: 'Refused',
      6: 'YXDomain',
      7: 'YXRRSet',
      8: 'NXRRSet',
      9: 'NotAuth',
      10: 'NotZone',
      11: 'DSOTypeNI'}

  _RESPONSE_OR_QUERY_BITMASK = 0x8000

  def _FormatFlags(self, flags):
    """Formats the flags value.

    Args:
      flags (int): flags

    Returns:
      str: formatted flags value.
    """
    reponse_code = flags & self._RESPONSE_CODE_BITMASK
    reponse_code = self._RESPONSE_CODES.get(reponse_code, '?')

    flag_names = []

    for bitmask, name in self._FLAG_NAMES:
      if flags & bitmask:
        flag_names.append(name)

    flag_names = ', '.join(flag_names)

    operation = (flags & self._OPERATION_BITMASK) >> 11
    operation_name = self._OPERATION_NAMES.get(operation, '?')

    query_or_response = (
        'R' if flags & self._RESPONSE_OR_QUERY_BITMASK else 'Q')

    return (f'{query_or_response:s}/{operation_name:s}, {flag_names:s}, '
            f'{reponse_code:s}')

  def FormatValue(self, value):
    """Formats a mDNS DNS header state value.

    Args:
      value (bytes): mDNS DNS header state value.

    Returns:
      str: formatted location client manager state value.
    """
    if len(value) != 12:
      # TODO: determine what the MacOS log tool shows.
      return 'ERROR: unsupported value'

    data_type_map = self._GetDataTypeMap('mdsn_dns_header')

    dns_header = self._ReadStructureFromByteStream(
        value, 0, data_type_map, 'DNS header')

    formatted_flags = self._FormatFlags(dns_header.flags)

    return (f'id: 0x{dns_header.identifier:04x} '
            f'({dns_header.identifier:d}), '
            f'flags: 0x{dns_header.flags:04x} '
            f'({formatted_flags:s}), counts: '
            f'{dns_header.number_of_questions:d}/'
            f'{dns_header.number_of_answers:d}/'
            f'{dns_header.number_of_authority_records:d}/'
            f'{dns_header.number_of_additional_records:d}')


class UUIDFormatStringDecoder(BaseFormatStringDecoder):
  """UUID value format string decoder."""

  def FormatValue(self, value):
    """Formats an UUID value.

    Args:
      value (bytes): UUID value.

    Returns:
      str: formatted UUID value.
    """
    uuid_value = uuid.UUID(bytes=value)
    return f'{uuid_value!s}'.upper()


class YesNoFormatStringDecoder(BaseFormatStringDecoder):
  """Yes/No value format string decoder."""

  def FormatValue(self, value):
    """Formats a yes/no value.

    Args:
      value (int): yes/no value.

    Returns:
      str: formatted yes/no value.
    """
    if value:
      return 'YES'

    return 'NO'


class DSCFile(data_format.BinaryDataFile):
  """Shared-Cache Strings (dsc) file.

  Attributes:
    ranges (list[DSCRange]): the ranges.
    uuids (list[DSCUUID]): the UUIDs.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('aul_dsc.yaml')

  _DEBUG_INFO_FILE_HEADER = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('major_format_version', 'Major format version',
       '_FormatIntegerAsDecimal'),
      ('minor_format_version', 'Minor format version',
       '_FormatIntegerAsDecimal'),
      ('number_of_ranges', 'Number of ranges', '_FormatIntegerAsDecimal'),
      ('number_of_uuids', 'Number of UUIDs', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_RANGE_DESCRIPTOR = [
      ('data_offset', 'Data offset', '_FormatIntegerAsHexadecimal8'),
      ('range_offset', 'Range offset', '_FormatIntegerAsHexadecimal8'),
      ('range_size', 'Range size', '_FormatIntegerAsDecimal'),
      ('uuid_descriptor_index', 'UUID descriptor index',
       '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_UUID_DESCRIPTOR = [
      ('text_offset', 'Text offset', '_FormatIntegerAsHexadecimal8'),
      ('text_size', 'Text size', '_FormatIntegerAsDecimal'),
      ('sender_identifier', 'Sender identifier', '_FormatUUIDAsString'),
      ('path_offset', 'Path offset', '_FormatIntegerAsHexadecimal8')]

  def __init__(self, debug=False, file_system_helper=None, output_writer=None):
    """Initializes a shared-cache strings (dsc) file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      file_system_helper (Optional[FileSystemHelper]): file system helper.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(DSCFile, self).__init__(
        debug=debug, file_system_helper=file_system_helper,
        output_writer=output_writer)
    self.ranges = []
    self.uuids = []

  def _FormatStreamAsSignature(self, stream):
    """Formats a stream as a signature.

    Args:
      stream (bytes): stream.

    Returns:
      str: stream formatted as a signature.
    """
    return stream.decode('ascii')

  def _ReadFileHeader(self, file_object):
    """Reads a file header.

    Args:
      file_object (file): file-like object.

    Returns:
      dsc_file_header: a file header.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('dsc_file_header')

    file_header, _ = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'file header')

    if self._debug:
      self._DebugPrintStructureObject(
          file_header, self._DEBUG_INFO_FILE_HEADER)

    if file_header.signature != b'hcsd':
      raise errors.ParseError('Unsupported signature.')

    format_version = (
        file_header.major_format_version, file_header.minor_format_version)
    if format_version not in [(1, 0), (2, 0)]:
      format_version_string = '.'.join([
          f'{file_header.major_format_version:d}',
          f'{file_header.minor_format_version:d}'])
      raise errors.ParseError(
          f'Unsupported format version: {format_version_string:s}')

    return file_header

  def _ReadFormatString(self, file_object, file_offset):
    """Reads a format string.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the format string data relative to the start
          of the file.

    Returns:
      str: format string.

    Raises:
      ParseError: if the format string cannot be read.
    """
    data_type_map = self._GetDataTypeMap('cstring')

    format_string, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'format string')

    if self._debug:
      self._DebugPrintValue('Format string', format_string)

    return format_string

  def _ReadRangeDescriptors(
      self, file_object, file_offset, version, number_of_ranges):
    """Reads the range descriptors.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the start of range descriptors data relative
          to the start of the file.
      version (int): major version of the file.
      number_of_ranges (int): the number of range descriptions to retrieve.

    Yields:
      DSCRange: a range.

    Raises:
      ParseError: if the file cannot be read.
    """
    if version not in (1, 2):
      raise errors.ParseError(f'Unsupported format version: {version:d}.')

    if version == 1:
      data_type_map_name = 'dsc_range_descriptor_v1'
      description = 'range descriptor v1'
    else:
      data_type_map_name = 'dsc_range_descriptor_v2'
      description = 'range descriptor v2'

    data_type_map = self._GetDataTypeMap(data_type_map_name)

    for _ in range(number_of_ranges):
      range_descriptor, record_size = self._ReadStructureFromFileObject(
          file_object, file_offset, data_type_map, description)

      file_offset += record_size

      if self._debug:
        self._DebugPrintStructureObject(
            range_descriptor, self._DEBUG_INFO_RANGE_DESCRIPTOR)

      dsc_range = DSCRange()
      dsc_range.data_offset = range_descriptor.data_offset
      dsc_range.range_offset = range_descriptor.range_offset
      dsc_range.range_size = range_descriptor.range_size
      dsc_range.uuid_index = range_descriptor.uuid_descriptor_index
      yield dsc_range

  def _ReadUUIDDescriptors(
      self, file_object, file_offset, version, number_of_uuids):
    """Reads the UUID descriptors.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the start of UUID descriptors data relative
          to the start of the file.
      version (int): major version of the file
      number_of_uuids (int): the number of UUID descriptions to retrieve.

    Yields:
      DSCUUId: an UUID.

    Raises:
      ParseError: if the file cannot be read.
    """
    if version not in (1, 2):
      raise errors.ParseError(f'Unsupported format version: {version:d}.')

    if version == 1:
      data_type_map_name = 'dsc_uuid_descriptor_v1'
      description = 'UUID descriptor v1'
    else:
      data_type_map_name = 'dsc_uuid_descriptor_v2'
      description = 'UUID descriptor v2'

    data_type_map = self._GetDataTypeMap(data_type_map_name)

    for _ in range(number_of_uuids):
      uuid_descriptor, record_size = self._ReadStructureFromFileObject(
          file_object, file_offset, data_type_map, description)

      file_offset += record_size

      if self._debug:
        self._DebugPrintStructureObject(
            uuid_descriptor, self._DEBUG_INFO_UUID_DESCRIPTOR)

      dsc_uuid = DSCUUID()
      dsc_uuid.sender_identifier = uuid_descriptor.sender_identifier
      dsc_uuid.text_offset = uuid_descriptor.text_offset
      dsc_uuid.text_size = uuid_descriptor.text_size

      dsc_uuid.path = self._ReadUUIDPath(
          file_object, uuid_descriptor.path_offset)

      yield dsc_uuid

  def _ReadUUIDPath(self, file_object, file_offset):
    """Reads an UUID path.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the UUID path data relative to the start of
          the file.

    Returns:
      str: UUID path.

    Raises:
      ParseError: if the file cannot be read.
    """
    data_type_map = self._GetDataTypeMap('cstring')

    uuid_path, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'UUID path')

    if self._debug:
      self._DebugPrintValue('UUID path', uuid_path)

    return uuid_path

  def GetFormatString(self, format_string_location):
    """Retrieves a format string.

    Args:
      format_string_location (int): location of the format string.

    Returns:
      str: format string or None if not available.

    Raises:
      ParseError: if the format string cannot be read.
    """
    for dsc_range in self.ranges:
      if format_string_location < dsc_range.range_offset:
        continue

      relative_offset = format_string_location - dsc_range.range_offset
      if relative_offset <= dsc_range.range_size:
        file_offset = dsc_range.data_offset + relative_offset
        return self._ReadFormatString(self._file_object, file_offset)

    return None

  def ReadFileObject(self, file_object):
    """Reads a shared-cache strings (dsc) file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_header = self._ReadFileHeader(file_object)

    file_offset = file_object.tell()

    self.ranges = list(self._ReadRangeDescriptors(
        file_object, file_offset, file_header.major_format_version,
        file_header.number_of_ranges))

    file_offset = file_object.tell()

    self.uuids = list(self._ReadUUIDDescriptors(
        file_object, file_offset, file_header.major_format_version,
        file_header.number_of_uuids))

    for dsc_range in self.ranges:
      dsc_uuid = self.uuids[dsc_range.uuid_index]

      dsc_range.path = dsc_uuid.path
      dsc_range.uuid = dsc_uuid.sender_identifier


class TimesyncDatabaseFile(data_format.BinaryDataFile):
  """Timesync database file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('aul_timesync.yaml')

  _BOOT_RECORD_SIGNATURE = b'\xb0\xbb'
  _SYNC_RECORD_SIGNATURE = b'Ts'

  _DEBUG_INFO_BOOT_RECORD = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('record_size', 'Record size', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal'),
      ('boot_identifier', 'Boot identifier', '_FormatUUIDAsString'),
      ('timebase_numerator', 'Timebase numerator',
       '_FormatIntegerAsHexadecimal'),
      ('timebase_denominator', 'Timebase denominator',
       '_FormatIntegerAsHexadecimal'),
      ('timestamp', 'Timestamp', '_FormatIntegerAsPosixTimeInNanoseconds'),
      ('time_zone_offset', 'Time zone offset', '_FormatIntegerAsDecimal'),
      ('daylight_saving_flag', 'Daylight saving flag',
       '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_SYNC_RECORD = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('record_size', 'Record size', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal'),
      ('kernel_time', 'Kernel Time', '_FormatIntegerAsDecimal'),
      ('timestamp', 'Timestamp', '_FormatIntegerAsPosixTimeInNanoseconds'),
      ('time_zone_offset', 'Time zone offset', '_FormatIntegerAsDecimal'),
      ('daylight_saving_flag', 'Daylight saving flag',
       '_FormatIntegerAsDecimal')]

  def __init__(self, debug=False, file_system_helper=None, output_writer=None):
    """Initializes a timesync database file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      file_system_helper (Optional[FileSystemHelper]): file system helper.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(TimesyncDatabaseFile, self).__init__(
        debug=debug, file_system_helper=file_system_helper,
        output_writer=output_writer)
    self._boot_record_data_type_map = self._GetDataTypeMap(
        'timesync_boot_record')
    self._sync_record_data_type_map = self._GetDataTypeMap(
        'timesync_sync_record')

  def _ReadRecord(self, file_object, file_offset):
    """Reads a boot or sync record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the start of the record relative to the start
          of the file.

    Returns:
      tuple[object, int]: boot or sync record and number of bytes read.

    Raises:
      ParseError: if the file cannot be read.
    """
    signature = self._ReadData(file_object, file_offset, 2, 'signature')

    if signature == self._BOOT_RECORD_SIGNATURE:
      data_type_map = self._boot_record_data_type_map
      description = 'boot record'
      debug_info = self._DEBUG_INFO_BOOT_RECORD

    elif signature == self._SYNC_RECORD_SIGNATURE:
      data_type_map = self._sync_record_data_type_map
      description = 'sync record'
      debug_info = self._DEBUG_INFO_SYNC_RECORD

    else:
      signature = repr(signature)
      raise errors.ParseError(f'Unsupported signature: {signature:s}.')

    record, bytes_read = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, description)

    if self._debug:
      self._DebugPrintStructureObject(record, debug_info)

    return record, bytes_read

  def ReadFileObject(self, file_object):
    """Reads a timesync file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_offset = 0

    while file_offset < self._file_size:
      record, _ = self._ReadRecord(file_object, file_offset)
      file_offset += record.record_size


class TraceV3File(data_format.BinaryDataFile):
  """Apple Unified Logging and Activity Tracing (tracev3) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('aul_tracev3.yaml')

  _ACTIVITY_TYPE_ACTIVITY = 0x02
  _ACTIVITY_TYPE_TRACE = 0x03
  _ACTIVITY_TYPE_LOG = 0x04
  _ACTIVITY_TYPE_SIGNPOST = 0x06
  _ACTIVITY_TYPE_LOSS = 0x07

  _ACTIVITY_TYPE_DESCRIPTIONS = {
      _ACTIVITY_TYPE_ACTIVITY: 'Activity',
      _ACTIVITY_TYPE_LOG: 'Log',
      _ACTIVITY_TYPE_LOSS: 'Loss',
      _ACTIVITY_TYPE_SIGNPOST: 'Signpost',
      _ACTIVITY_TYPE_TRACE: 'Trace'}

  _CHUNK_TAG_HEADER = 0x00001000
  _CHUNK_TAG_FIREHOSE = 0x00006001
  _CHUNK_TAG_OVERSIZE = 0x00006002
  _CHUNK_TAG_STATEDUMP = 0x00006003
  _CHUNK_TAG_SIMPLEDUMP = 0x00006004
  _CHUNK_TAG_CATALOG = 0x0000600b
  _CHUNK_TAG_CHUNK_SET = 0x0000600d

  _CHUNK_TAG_DESCRIPTIONS = {
      _CHUNK_TAG_HEADER: 'Header',
      _CHUNK_TAG_FIREHOSE: 'Firehose',
      _CHUNK_TAG_OVERSIZE: 'Oversize',
      _CHUNK_TAG_STATEDUMP: 'StateDump',
      _CHUNK_TAG_SIMPLEDUMP: 'SimpleDump',
      _CHUNK_TAG_CATALOG: 'Catalog',
      _CHUNK_TAG_CHUNK_SET: 'ChunkSet'}

  _DATA_ITEM_VALUE_TYPE_DESCRIPTIONS = {}

  _DATA_ITEM_BINARY_DATA_VALUE_TYPES = (0x32, 0xf2)
  _DATA_ITEM_INTEGER_VALUE_TYPES = (0x00, 0x02)
  _DATA_ITEM_PRIVATE_VALUE_TYPES = (0x01, 0x21, 0x25, 0x31, 0x41)
  _DATA_ITEM_STRING_VALUE_TYPES = (0x20, 0x22, 0x40, 0x42)

  _DATA_ITEM_INTEGER_DATA_MAP_NAMES = {
      'signed': {
          1: 'int8',
          2: 'int16le',
          4: 'int32le',
          8: 'int64le'},
      'unsigned': {
          1: 'uint8',
          2: 'uint16le',
          4: 'uint32le',
          8: 'uint64le'}}

  _FLAG_HAS_ACTIVITY_IDENTIFIER = 0x0001
  _FLAG_HAS_LARGE_OFFSET = 0x0020
  _FLAG_HAS_PRIVATE_STRINGS_RANGE = 0x0100

  _LOG_TYPE_DESCRIPTIONS = {
      0x00: 'Default',
      0x01: 'Info',
      0x02: 'Debug',
      0x03: 'Useraction',
      0x10: 'Error',
      0x11: 'Fault',
      0x40: 'Thread Signpost Event',
      0x41: 'Thread Signpost Start',
      0x42: 'Thread Signpost End',
      0x80: 'Process Signpost Event',
      0x81: 'Process Signpost Start',
      0x82: 'Process Signpost End',
      0xc0: 'System Signpost Event',
      0xc1: 'System Signpost Start',
      0xc2: 'System Signpost End'}

  _DEBUG_INFO_CATALOG = [
      ('sub_system_strings_offset', 'Sub system strings offset',
       '_FormatIntegerAsHexadecimal8'),
      ('process_information_entries_offset',
       'Process information entries offset', '_FormatIntegerAsHexadecimal8'),
      ('number_of_process_information_entries',
       'Number of process information entries', '_FormatIntegerAsDecimal'),
      ('sub_chunks_offset', 'Sub chunks offset',
       '_FormatIntegerAsHexadecimal8'),
      ('number_of_sub_chunks', 'Number of sub chunks',
       '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatDataInHexadecimal'),
      ('earliest_firehose_timestamp', 'Earliest firehose timestamp',
       '_FormatIntegerAsDecimal'),
      ('uuids', 'UUIDs', '_FormatArrayOfUUIDS'),
      ('sub_system_strings', 'Sub system strings', '_FormatArrayOfStrings')]

  _DEBUG_INFO_CATALOG_PROCESS_INFORMATION_ENTRY = [
      ('entry_index', 'Entry index', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal4'),
      ('main_uuid_index', 'Main UUID index', '_FormatIntegerAsDecimal'),
      ('main_uuid', 'Main UUID', '_FormatUUIDAsString'),
      ('dsc_uuid_index', 'DSC UUID index', '_FormatIntegerAsDecimal'),
      ('dsc_uuid', 'DSC UUID', '_FormatUUIDAsString'),
      ('proc_id_upper', 'proc_id (upper 64-bit)', '_FormatIntegerAsDecimal'),
      ('proc_id_lower', 'proc_id (lower 32-bit)', '_FormatIntegerAsDecimal'),
      ('process_identifier', 'Process identifier (PID)',
       '_FormatIntegerAsDecimal'),
      ('effective_user_identifier', 'Effective user identifier (euid)',
       '_FormatIntegerAsDecimal'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal4'),
      ('number_of_uuid_entries', 'Number of UUID information entries',
       '_FormatIntegerAsDecimal'),
      ('unknown3', 'Unknown3', '_FormatIntegerAsHexadecimal4'),
      ('uuid_entries', 'UUID entries', '_FormatArrayOfCatalogUUIDEntries'),
      ('number_of_sub_system_entries', 'Number of sub system entries',
       '_FormatIntegerAsDecimal'),
      ('unknown4', 'Unknown4', '_FormatIntegerAsHexadecimal4'),
      ('sub_system_entries', 'Sub system entries',
       '_FormatArrayOfCatalogSubSystemEntries'),
      ('alignment_padding', 'Alignment padding', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_CHUNK_HEADER = [
      ('chunk_tag', 'Chunk tag', '_FormatChunkTag'),
      ('chunk_sub_tag', 'Chunk sub tag', '_FormatIntegerAsHexadecimal8'),
      ('chunk_data_size', 'Chunk data size', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_FIREHOSE_HEADER = [
      ('proc_id_upper', 'proc_id (upper 64-bit)', '_FormatIntegerAsDecimal'),
      ('proc_id_lower', 'proc_id (lower 32-bit)', '_FormatIntegerAsDecimal'),
      ('ttl', 'Time to live (TTL)', '_FormatIntegerAsDecimal'),
      ('collapsed', 'Collapsed', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal4'),
      ('public_data_size', 'Public data size', '_FormatIntegerAsDecimal'),
      ('private_data_virtual_offset', 'Private data virtual offset',
       '_FormatIntegerAsHexadecimal4'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal4'),
      ('unknown3', 'Unknown3', '_FormatIntegerAsHexadecimal4'),
      ('base_continuous_time', 'Base continuous time',
       '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_FIREHOSE_TRACEPOINT = [
      ('activity_type', 'Activity type', '_FormatActivityType'),
      ('log_type', 'Log type', '_FormatLogType'),
      ('flags', 'Flags', '_FormatFirehoseTracepointFlags'),
      ('format_string_location', 'Format string location',
       '_FormatIntegerAsHexadecimal8'),
      ('thread_identifier', 'Thread identifier', '_FormatIntegerAsDecimal'),
      ('continuous_time_lower', 'Continous time (lower 32-bit)',
       '_FormatIntegerAsDecimal'),
      ('continuous_time_upper', 'Continous time (upper 16-bit)',
       '_FormatIntegerAsDecimal'),
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('data', 'Data', '_FormatDataInHexadecimal'),
      ('alignment_padding', 'Alignment padding', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_FIREHOSE_TRACEPOINT_DATA_ITEM = [
      ('value_type', 'Value type', '_FormatDataItemValueType'),
      ('data_size', 'Data item data size', '_FormatIntegerAsDecimal'),
      ('data', 'Data item data', '_FormatDataInHexadecimal'),
      ('value_data_offset', 'Value data offset',
       '_FormatIntegerAsHexadecimal4'),
      ('value_data_size', 'Value data size', '_FormatIntegerAsDecimal'),
      ('value_data', 'Value data', '_FormatDataInHexadecimal'),
      ('integer', 'Integer', '_FormatIntegerAsDecimal'),
      ('private_string', 'Private string', '_FormatString'),
      ('string', 'String', '_FormatString'),
      ('uuid', 'UUID', '_FormatUUIDAsString')]

  _DEBUG_INFO_FIREHOSE_TRACEPOINT_ACTIVITY = [
      ('current_activity_identifier', 'Current activity identifier',
       '_FormatIntegerAsHexadecimal8'),
      ('process_identifier', 'Process identifier (PID)',
       '_FormatIntegerAsDecimal'),
      ('other_activity_identifier', 'Other activity identifier',
       '_FormatIntegerAsHexadecimal8'),
      ('new_activity_identifier', 'New activity identifier',
       '_FormatIntegerAsHexadecimal8'),
      ('load_address_lower', 'UUID entry load address (lower 32-bit)',
       '_FormatIntegerAsHexadecimal8'),
      ('large_offset_data', 'Large offset data',
       '_FormatIntegerAsHexadecimal4'),
      ('load_address_upper', 'UUID entry load address (upper 16-bit)',
       '_FormatIntegerAsHexadecimal4'),
      ('uuidtext_file_identifier', 'UUIDText file identifier',
       '_FormatUUIDAsString'),
      ('large_shared_cache_data', 'Large shared cache data',
       '_FormatIntegerAsHexadecimal4'),
      ('sub_system_value', 'Sub system value', '_FormatIntegerAsHexadecimal4'),
      ('ttl_value', 'TTL value', '_FormatIntegerAsDecimal'),
      ('data_reference_value', 'Data reference value',
       '_FormatIntegerAsHexadecimal4'),
      ('signpost_name_reference_value', 'Signpost name reference value',
       '_FormatIntegerAsHexadecimal8'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal2'),
      ('number_of_data_items', 'Number of data items',
       '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_FIREHOSE_TRACEPOINT_LOSS = [
      ('start_time', 'Start time', '_FormatIntegerAsDecimal'),
      ('end_time', 'End time', '_FormatIntegerAsDecimal'),
      ('number_of_messages', 'Number of messages', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_FIREHOSE_TRACEPOINT_LOG = [
      ('current_activity_identifier', 'Current activity identifier',
       '_FormatIntegerAsHexadecimal8'),
      ('private_data_range', 'Private data range', '_FormatDataRange'),
      ('load_address_lower', 'UUID entry load address (lower 32-bit)',
       '_FormatIntegerAsHexadecimal8'),
      ('large_offset_data', 'Large offset data',
       '_FormatIntegerAsHexadecimal4'),
      ('load_address_upper', 'UUID entry load address (upper 16-bit)',
       '_FormatIntegerAsHexadecimal4'),
      ('uuidtext_file_identifier', 'UUIDText file identifier',
       '_FormatUUIDAsString'),
      ('large_shared_cache_data', 'Large shared cache data',
       '_FormatIntegerAsHexadecimal4'),
      ('sub_system_value', 'Sub system value', '_FormatIntegerAsHexadecimal4'),
      ('ttl_value', 'TTL value', '_FormatIntegerAsDecimal'),
      ('data_reference_value', 'Data reference value',
       '_FormatIntegerAsHexadecimal4'),
      ('signpost_name_reference_value', 'Signpost name reference value',
       '_FormatIntegerAsHexadecimal8'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal2'),
      ('number_of_data_items', 'Number of data items',
       '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_FIREHOSE_TRACEPOINT_SIGNPOST = [
      ('current_activity_identifier', 'Current activity identifier',
       '_FormatIntegerAsHexadecimal8'),
      ('private_data_range', 'Private data range', '_FormatDataRange'),
      ('load_address_lower', 'UUID entry load address (lower 32-bit)',
       '_FormatIntegerAsHexadecimal8'),
      ('large_offset_data', 'Large offset data',
       '_FormatIntegerAsHexadecimal4'),
      ('load_address_upper', 'UUID entry load address (upper 16-bit)',
       '_FormatIntegerAsHexadecimal4'),
      ('uuidtext_file_identifier', 'UUIDText file identifier',
       '_FormatUUIDAsString'),
      ('large_shared_cache_data', 'Large shared cache data',
       '_FormatIntegerAsHexadecimal4'),
      ('signpost_identifier', 'Signpost identifier',
       '_FormatIntegerAsHexadecimal8'),
      ('sub_system_value', 'Sub system value', '_FormatIntegerAsHexadecimal4'),
      ('ttl_value', 'TTL value', '_FormatIntegerAsDecimal'),
      ('data_reference_value', 'Data reference value',
       '_FormatIntegerAsHexadecimal4'),
      ('signpost_name_reference_value', 'Signpost name reference value',
       '_FormatIntegerAsHexadecimal8'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal2'),
      ('number_of_data_items', 'Number of data items',
       '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_HEADER = [
      ('timebase_numerator', 'Timebase numerator', '_FormatIntegerAsDecimal'),
      ('timebase_denominator', 'Timebase denominator',
       '_FormatIntegerAsDecimal'),
      ('start_time', 'Start time', '_FormatIntegerAsDecimal'),
      ('unknown_time', 'Unknown time', 'FormatIntegerAsPosixTime'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal4'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal4'),
      ('time_zone_offset', 'Time zone offset', '_FormatIntegerAsDecimal'),
      ('daylight_savings_flag', 'Daylight Savings Flag',
       '_FormatIntegerAsDecimal'),
      ('unknown_flags', 'Unknown flags', '_FormatIntegerAsHexadecimal4')]

  _DEBUG_INFO_HEADER_CONTINOUS_TIME_SUB_CHUNK = [
      ('sub_chunk_tag', 'Sub chunk tag', '_FormatIntegerAsHexadecimal4'),
      ('sub_chunk_data_size', 'Sub chunk data size', '_FormatIntegerAsDecimal'),
      ('continuous_time', 'Continuous time', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_HEADER_SYSTEM_INFORMATION_SUB_CHUNK = [
      ('sub_chunk_tag', 'Sub chunk tag', '_FormatIntegerAsHexadecimal4'),
      ('sub_chunk_data_size', 'Sub chunk data size', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal4'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal4'),
      ('build_version', 'Build version', '_FormatString'),
      ('hardware_model', 'Hardware model', '_FormatString')]

  _DEBUG_INFO_HEADER_GENERATION_SUB_CHUNK = [
      ('sub_chunk_tag', 'Sub chunk tag', '_FormatIntegerAsHexadecimal4'),
      ('sub_chunk_data_size', 'Sub chunk data size', '_FormatIntegerAsDecimal'),
      ('boot_identifier', 'Boot identifier', '_FormatUUIDAsString'),
      ('logd_process_identifier', 'logd process identifier (PID)',
       '_FormatIntegerAsDecimal'),
      ('logd_exit_status', 'logd exit status', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_HEADER_TIME_ZONE_SUB_CHUNK = [
      ('sub_chunk_tag', 'Sub chunk tag', '_FormatIntegerAsHexadecimal4'),
      ('sub_chunk_data_size', 'Sub chunk data size', '_FormatIntegerAsDecimal'),
      ('path', 'Path', '_FormatString')]

  _DEBUG_INFO_LZ4_BLOCK_HEADER = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('uncompressed_data_size', 'Uncompressed data size',
       '_FormatIntegerAsDecimal'),
      ('compressed_data_size', 'Compressed data size',
       '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_OVERSIZE_CHUNK = [
      ('proc_id_upper', 'proc_id (upper 64-bit)', '_FormatIntegerAsDecimal'),
      ('proc_id_lower', 'proc_id (lower 32-bit)', '_FormatIntegerAsDecimal'),
      ('ttl', 'Time to live (TTL)', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal2'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal4'),
      ('continuous_time', 'Continuous time', '_FormatIntegerAsDecimal'),
      ('data_reference_index', 'Data reference index',
       '_FormatIntegerAsDecimal'),
      ('data_size', 'Data Size', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_SIMPLEDUMP_CHUNK = [
      ('proc_id_upper', 'proc_id (upper 64-bit)', '_FormatIntegerAsDecimal'),
      ('proc_id_lower', 'proc_id (lower 32-bit)', '_FormatIntegerAsDecimal'),
      ('ttl', 'Time to live (TTL)', '_FormatIntegerAsDecimal'),
      ('type', 'Type', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal4'),
      ('timestamp', 'Timestamp', '_FormatIntegerAsDecimal'),
      ('thread_identifier', 'Thread identifier', '_FormatIntegerAsDecimal'),
      ('offset', 'Offset', '_FormatIntegerAsHexadecimal8'),
      ('sender_identifier', 'Sender identifier', '_FormatUUIDAsString'),
      ('dsc_identifier', 'DSC identifier', '_FormatUUIDAsString'),
      ('unknown6', 'Unknown6', '_FormatIntegerAsHexadecimal8'),
      ('sub_system_string_size', 'Sub system string size',
       '_FormatIntegerAsDecimal'),
      ('message_string_size', 'Message string size', '_FormatIntegerAsDecimal'),
      ('sub_system_string', 'Sub system string', '_FormatString'),
      ('message_string', 'Message string', '_FormatString')]

  _DEBUG_INFO_STATEDUMP_CHUNK = [
      ('proc_id_upper', 'proc_id (upper 64-bit)', '_FormatIntegerAsDecimal'),
      ('proc_id_lower', 'proc_id (lower 32-bit)', '_FormatIntegerAsDecimal'),
      ('ttl', 'Time to live (TTL)', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal2'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal4'),
      ('continuous_time', 'Continuous time', '_FormatIntegerAsDecimal'),
      ('activity_identifier', 'Activity identifier',
       '_FormatIntegerAsHexadecimal8'),
      ('unknown3', 'Unknown3', '_FormatUUIDAsString'),
      ('data_type', 'Data type', '_FormatIntegerAsDecimal'),
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('unknown4', 'Unknown4', '_FormatDataInHexadecimal'),
      ('unknown5', 'Unknown5', '_FormatDataInHexadecimal'),
      ('name', 'Name', '_FormatString'),
      ('data', 'Data', '_FormatDataInHexadecimal')]

  _FORMAT_STRING_DECODERS = {
      'bool': BooleanFormatStringDecoder(),
      'BOOL': YesNoFormatStringDecoder(),
      'darwin.errno': ErrorCodeFormatStringDecoder(),
      'darwin.mode': FileModeFormatStringDecoder(),
      'errno': ErrorCodeFormatStringDecoder(),
      'in_addr': IPv4FormatStringDecoder(),
      'in6_addr': IPv6FormatStringDecoder(),
      'location:_CLClientManagerStateTrackerState': (
          LocationClientManagerStateFormatStringDecoder()),
      'location:_CLLocationManagerStateTrackerState': (
          LocationLocationManagerStateFormatStringDecoder()),
      'location:escape_only': LocationEscapeOnlyFormatStringDecoder(),
      'location:SqliteResult': LocationSQLiteResultFormatStringDecoder(),
      'mdns:dnshdr': MDNSDNSHeaderFormatStringDecoder(),
      'network:in_addr': IPv4FormatStringDecoder(),
      'network:in6_addr': IPv6FormatStringDecoder(),
      'mask.hash': MaskHashFormatStringDecoder(),
      'time_t': DateTimeInSecondsFormatStringDecoder(),
      'uuid_t': UUIDFormatStringDecoder()}

  _FORMAT_STRING_DECODER_NAMES = frozenset(_FORMAT_STRING_DECODERS.keys())

  _MAXIMUM_CACHED_FILES = 64
  _MAXIMUM_CACHED_FORMAT_STRINGS = 1024

  def __init__(self, debug=False, file_system_helper=None, output_writer=None):
    """Initializes a tracev3 file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      file_system_helper (Optional[FileSystemHelper]): file system helper.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(TraceV3File, self).__init__(
        debug=debug, file_system_helper=file_system_helper,
        output_writer=output_writer)
    self._cached_dsc_files = collections.OrderedDict()
    self._cached_uuidtext_files = collections.OrderedDict()
    self._catalog = None
    self._catalog_process_information_entries = {}
    self._uuidtext_path = None

  def _BuildCatalogProcessInformationEntries(self, catalog):
    """Builds the catalog process information lookup table.

    Args:
      catalog (tracev3_catalog): catalog.
    """
    catalog_strings_map = self._GetCatalogSubSystemStringMap(catalog)

    self._catalog_process_information_entries = {}

    for process_information_entry in catalog.process_information_entries:
      if process_information_entry.main_uuid_index >= 0:
        process_information_entry.main_uuid = catalog.uuids[
            process_information_entry.main_uuid_index]

      if process_information_entry.dsc_uuid_index >= 0:
        process_information_entry.dsc_uuid = catalog.uuids[
            process_information_entry.dsc_uuid_index]

      if self._debug:
        self._DebugPrintStructureObject(
            process_information_entry,
            self._DEBUG_INFO_CATALOG_PROCESS_INFORMATION_ENTRY)

      for sub_system_entry in process_information_entry.sub_system_entries:
        sub_system = catalog_strings_map.get(
            sub_system_entry.sub_system_offset, None)
        category = catalog_strings_map.get(
            sub_system_entry.category_offset, None)
        if self._debug:
          self._DebugPrintText((
              f'Identifier: {sub_system_entry.identifier:d}, '
              f'Sub system: {sub_system:s}, Category: {category:s}\n'))

      if self._debug:
        self._DebugPrintText('\n')

      proc_id = (f'{process_information_entry.proc_id_upper:d}@'
                 f'{process_information_entry.proc_id_lower:d}')
      if proc_id in self._catalog_process_information_entries:
        raise errors.ParseError(f'proc_id: {proc_id:s} already set')

      self._catalog_process_information_entries[proc_id] = (
          process_information_entry)

  def _CalculateFormatFormatStringLocation(
    self, firehose_tracepoint, tracepoint_data_object):
    """Calculates the format string location.

    Args:
      firehose_tracepoint (tracev3_firehose_tracepoint): firehose tracepoint.
      tracepoint_data_object (object): firehose tracepoint data object.

    Returns:
      int: format string location.
    """
    format_string_location = firehose_tracepoint.format_string_location

    large_offset_data = tracepoint_data_object.large_offset_data
    large_shared_cache_data = tracepoint_data_object.large_shared_cache_data
    if large_shared_cache_data:
      if self._debug:
        calculated_large_offset_data = large_shared_cache_data >> 1
        if large_offset_data != calculated_large_offset_data:
          self._DebugPrintText((
              f'Large offset data mismatch stored: ('
              f'0x{large_offset_data:04x}, calculated: '
              f'0x{calculated_large_offset_data:04x})\n'))

      large_offset_data = tracepoint_data_object.large_shared_cache_data

    if large_offset_data:
      format_string_location |= large_offset_data << 31

    if self._debug:
      value_string, _ = self._FormatIntegerAsHexadecimal8(
          format_string_location)
      self._DebugPrintValue('Calculated format string location', value_string)
      self._DebugPrintText('\n')

    return format_string_location

  def _FormatActivityType(self, integer):
    """Formats an activity type.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as activity type.
    """
    description = self._ACTIVITY_TYPE_DESCRIPTIONS.get(integer, None)
    if description:
      return f'0x{integer:02x} ({description:s})'

    return f'0x{integer:02x}'

  def _FormatArrayOfStrings(self, array_of_strings):
    """Formats an array of strings.

    Args:
      array_of_strings (list[str]): array of strings.

    Returns:
      str: formatted array of strings.
    """
    value = '\n'.join([
        f'\t[{string_index:03d}] {string:s}'
        for string_index, string in enumerate(array_of_strings)])
    return f'{value:s}\n'

  def _FormatArrayOfCatalogSubSystemEntries(self, array_of_entries):
    """Formats an array of catalog sub system entries.

    Args:
      array_of_entries (list[tracev3_catalog_sub_system_entry]): array of
          catalog sub system entries.

    Returns:
      str: formatted array of catalog sub system entries.
    """
    value = '\n'.join([
        (f'\tidentifier: {entry.identifier:d}, '
         f'sub_system_offset: {entry.sub_system_offset:d}, '
         f'category_offset: {entry.category_offset:d}')
        for entry in array_of_entries])
    return f'{value:s}\n'

  def _FormatArrayOfCatalogUUIDEntries(self, array_of_entries):
    """Formats an array of catalog UUID entries.

    Args:
      array_of_entries (list[tracev3_catalog_uuid_entry]): array of catalog
          UUID entries.

    Returns:
      str: formatted array of catalog UUID entries.
    """
    value = '\n'.join([
        (f'\tload address: 0x{entry.load_address_upper:04x}'
         f'{entry.load_address_lower:08x}, size: {entry.size:d}, '
         f'UUID index: {entry.uuid_index:d}, unknown1: 0x{entry.unknown1:x}')
        for entry in array_of_entries])
    return f'{value:s}\n'

  def _FormatArrayOfUUIDS(self, array_of_uuids):
    """Formats an array of UUIDs.

    Args:
      array_of_uuids (list[uuid]): array of UUIDs.

    Returns:
      str: formatted array of UUIDs.
    """
    value = '\n'.join([
        f'\t[{uuid_index:03d}] {uuid!s}'
        for uuid_index, uuid in enumerate(array_of_uuids)])
    return f'{value:s}\n'

  def _FormatChunkTag(self, integer):
    """Formats a chunk tag.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as chunk tag.
    """
    description = self._CHUNK_TAG_DESCRIPTIONS.get(integer, None)
    if description:
      return f'0x{integer:08x} ({description:s})'

    return f'0x{integer:08x}'

  def _FormatDataItemValueType(self, integer):
    """Formats a data item value type.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as data item value type.
    """
    description = self._DATA_ITEM_VALUE_TYPE_DESCRIPTIONS.get(integer, None)
    if description:
      return f'0x{integer:02x} ({description:s})'

    return f'0x{integer:02x}'

  def _FormatFirehoseTracepointFlags(self, integer):
    """Formats firehost tracepoint flags.

    Args:
      integer (int): integer.

    Returns:
      tuple[str, bool]: integer formatted as firehost tracepoint flags and
          False to indicate there should be no new line after value description.
    """
    lines = [f'0x{integer:04x}']

    if integer & 0x0001:
      lines.append('\tHas current activity identfier (0x0001)')

    format_string_type = integer & 0x000e
    if format_string_type == 0x0002:
      lines.append('\tFormat string in uuidtext file by proc_id (0x0002)')
    elif format_string_type == 0x0004:
      lines.append('\tFormat string in DSC file (0x0004)')
    elif format_string_type == 0x0008:
      lines.append('\tFormat string in uuidtext file by reference (0x0008)')
    elif format_string_type == 0x000a:
      lines.append('\tFormat string in uuidtext file by identifier (0x000a)')
    elif format_string_type == 0x000c:
      lines.append('\tFormat string in DSC file (0x000c)')

    if integer & 0x0010:
      lines.append('\tHas process identifier (PID) value (0x0010)')
    if integer & 0x0020:
      lines.append('\tHas large offset data (0x0020)')

    if integer & 0x0100:
      lines.append('\tHas private data range (0x0100)')
    if integer & 0x0200:
      lines.append('\tHas sub system value (0x0200)')
    if integer & 0x0400:
      lines.append('\tHas TTL value (0x0400)')
    if integer & 0x0800:
      lines.append('\tHas data reference value (0x0800)')

    if integer & 0x8000:
      lines.append('\tHas signpost name reference value (0x8000)')

    lines.extend(['', ''])
    return '\n'.join(lines), False

  def _FormatLogType(self, integer):
    """Formats a log type.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as log type.
    """
    description = self._LOG_TYPE_DESCRIPTIONS.get(integer, None)
    if description:
      return f'0x{integer:02x} ({description:s})'

    return f'0x{integer:02x}'

  def _FormatStreamAsSignature(self, stream):
    """Formats a stream as a signature.

    Args:
      stream (bytes): stream.

    Returns:
      str: stream formatted as a signature.
    """
    return stream.decode('ascii')

  def _FormatDataRange(self, data_range):
    """Formats a data range.

    Args:
      data_range (tracev3_firehose_tracepoint_data_range): data range.

    Returns:
      str: formatted data range.
    """
    return f'offset: 0x{data_range.offset:04x}, size: {data_range.size:d}'

  def _GetCatalogSubSystemStringMap(self, catalog):
    """Retrieves a map of the catalog sub system strings and offsets.

    Args:
      catalog (tracev3_catalog): catalog.

    Returns:
      dict[int, str]: catalog sub system string per offset.
    """
    strings_map = {}

    map_offset = 0
    for string in catalog.sub_system_strings:
      strings_map[map_offset] = string
      map_offset += len(string) + 1

    return strings_map

  def _GetFirehostTracepointFormatString(
      self, proc_id, firehose_tracepoint, tracepoint_data_object):
    """Retrieves a firehost tracepoint format string.

    Args:
      proc_id (str): identifier of the process information entry in the catalog.
      firehose_tracepoint (tracev3_firehose_tracepoint): firehose tracepoint.
      tracepoint_data_object (object): firehose tracepoint data object.

    Returns:
      str: format string or None if not available.

    Raises:
      ParseError: if the format string cannot be retrieved.
    """
    format_string_type = firehose_tracepoint.flags & 0x000e
    if format_string_type not in (0x0002, 0x0004, 0x0008, 0x000a, 0x000c):
      return None

    if firehose_tracepoint.format_string_location & 0x80000000 != 0:
      return '%s'

    process_information_entry = (
        self._catalog_process_information_entries.get(proc_id, None))
    if not process_information_entry:
      raise errors.ParseError((
          f'Unable to retrieve process information entry: {proc_id:s} from '
          f'catalog'))

    uuid_string = None
    if format_string_type == 0x0002:
      uuid_string = process_information_entry.main_uuid.hex.upper()

    elif format_string_type in (0x0004, 0x000c):
      uuid_string = process_information_entry.dsc_uuid.hex.upper()

    elif format_string_type == 0x0008:
      load_address_upper = tracepoint_data_object.load_address_upper
      load_address_lower = tracepoint_data_object.load_address_lower

      for uuid_entry in process_information_entry.uuid_entries:
        if (load_address_upper != uuid_entry.load_address_upper or
            load_address_lower < uuid_entry.load_address_lower):
          continue

        if load_address_lower <= (
            uuid_entry.load_address_lower + uuid_entry.size):
          uuid_value = self._catalog.uuids[uuid_entry.uuid_index]
          uuid_string = uuid_value.hex.upper()
          break

    elif format_string_type == 0x000a:
      uuid_string = tracepoint_data_object.uuidtext_file_identifier.hex.upper()

    format_string_location = self._CalculateFormatFormatStringLocation(
        firehose_tracepoint, tracepoint_data_object)

    format_string = None
    if format_string_type in (0x0002, 0x0008, 0x000a):
      uuidtext_file = self._GetUUIDTextFile(uuid_string)
      if uuidtext_file:
        format_string = uuidtext_file.GetFormatString(format_string_location)

    else:
      dsc_file = self._GetDSCFile(uuid_string)
      if dsc_file:
        format_string = dsc_file.GetFormatString(format_string_location)

    if self._debug and format_string:
      self._DebugPrintValue('Format string', format_string)
      self._DebugPrintText('\n')

    return format_string

  def _GetDSCFile(self, uuid_string):
    """Retrieves a specific shared-cache strings (DSC) file.

    Args:
      uuid_string (str): string representation of the UUID.

    Returns:
      DSCFile: a shared-cache strings (DSC) file or None if not available.
    """
    dsc_file = self._cached_dsc_files.get(uuid_string, None)
    if not dsc_file:
      dsc_file = self._ReadDSCFile(uuid_string)
      if len(self._cached_dsc_files) >= self._MAXIMUM_CACHED_FILES:
        _, cached_dsc_file = self._cached_dsc_files.popitem(last=True)
        if cached_dsc_file:
          cached_dsc_file.Close()

      self._cached_dsc_files[uuid_string] = dsc_file

    self._cached_dsc_files.move_to_end(uuid_string, last=False)

    return dsc_file

  def _GetUUIDTextFile(self, uuid_string):
    """Retrieves a specific uuidtext file.

    Args:
      uuid_string (str): string representation of the UUID.

    Returns:
      UUIDTextFile: an uuidtext file or None if not available.
    """
    uuidtext_file = self._cached_uuidtext_files.get(uuid_string, None)
    if not uuidtext_file:
      uuidtext_file = self._ReadUUIDTextFile(uuid_string)
      if len(self._cached_uuidtext_files) >= self._MAXIMUM_CACHED_FILES:
        _, cached_uuidtext_file = self._cached_uuidtext_files.popitem(last=True)
        if cached_uuidtext_file:
          cached_uuidtext_file.Close()

      self._cached_uuidtext_files[uuid_string] = uuidtext_file

    self._cached_uuidtext_files.move_to_end(uuid_string, last=False)

    return uuidtext_file

  def _ReadCatalog(self, file_object, file_offset, chunk_header):
    """Reads a catalog.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the catalog data relative to the start
          of the file.
      chunk_header (tracev3_chunk_header): the chunk header of the catalog.

    Returns:
      tracev3_catalog: catalog.

    Raises:
      ParseError: if the chunk header cannot be read.
    """
    if self._debug:
      chunk_data = file_object.read(chunk_header.chunk_data_size)
      self._DebugPrintData('Catalog chunk data', chunk_data)

    data_type_map = self._GetDataTypeMap('tracev3_catalog')

    catalog, bytes_read = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'Catalog')

    file_offset += bytes_read

    if self._debug:
      self._DebugPrintStructureObject(catalog, self._DEBUG_INFO_CATALOG)

    return catalog

  def _ReadChunkHeader(self, file_object, file_offset):
    """Reads a chunk header.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the chunk header relative to the start
          of the file.

    Returns:
      tracev3_chunk_header: a chunk header.

    Raises:
      ParseError: if the chunk header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('tracev3_chunk_header')

    chunk_header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'chunk header')

    if self._debug:
      self._DebugPrintStructureObject(
          chunk_header, self._DEBUG_INFO_CHUNK_HEADER)

    return chunk_header

  def _ReadChunkSet(self, file_object, file_offset, chunk_header):
    """Reads a chunk set.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the chunk set data relative to the start
          of the file.
      chunk_header (tracev3_chunk_header): the chunk header of the chunk set.

    Raises:
      ParseError: if the chunk header cannot be read.
    """
    chunk_data = file_object.read(chunk_header.chunk_data_size)

    data_type_map = self._GetDataTypeMap('tracev3_lz4_block_header')

    lz4_block_header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'LZ4 block header')

    if self._debug:
      self._DebugPrintStructureObject(
          lz4_block_header, self._DEBUG_INFO_LZ4_BLOCK_HEADER)

    end_of_compressed_data_offset = 12 + lz4_block_header.compressed_data_size

    if lz4_block_header.signature == b'bv41':
      uncompressed_data = lz4.block.decompress(
          chunk_data[12:end_of_compressed_data_offset],
          uncompressed_size=lz4_block_header.uncompressed_data_size)

    elif lz4_block_header.signature == b'bv4-':
      uncompressed_data = chunk_data[12:end_of_compressed_data_offset]

    else:
      raise errors.ParseError('Unsupported start of compressed data marker')

    end_of_compressed_data_identifier = chunk_data[
        end_of_compressed_data_offset:end_of_compressed_data_offset + 4]

    if end_of_compressed_data_identifier != b'bv4$':
      raise errors.ParseError('Unsupported end of compressed data marker')

    data_type_map = self._GetDataTypeMap('tracev3_chunk_header')

    data_offset = 0
    while data_offset < lz4_block_header.uncompressed_data_size:
      if self._debug:
        self._DebugPrintData('Chunk header data', uncompressed_data[
            data_offset:data_offset + 16])

      chunkset_chunk_header = self._ReadStructureFromByteStream(
          uncompressed_data[data_offset:], data_offset, data_type_map,
          'chunk header')
      data_offset += 16

      if self._debug:
        self._DebugPrintStructureObject(
            chunkset_chunk_header, self._DEBUG_INFO_CHUNK_HEADER)

      data_end_offset = data_offset + chunkset_chunk_header.chunk_data_size
      chunkset_chunk_data = uncompressed_data[data_offset:data_end_offset]
      if self._debug:
        self._DebugPrintData('Chunk data', chunkset_chunk_data)

      if chunkset_chunk_header.chunk_tag == self._CHUNK_TAG_FIREHOSE:
        self._ReadFirehoseChunkData(
            chunkset_chunk_data, chunkset_chunk_header.chunk_data_size,
            data_offset)

      elif chunkset_chunk_header.chunk_tag == self._CHUNK_TAG_OVERSIZE:
        self._ReadOversizeChunkData(
            chunkset_chunk_data, chunkset_chunk_header.chunk_data_size,
            data_offset)

      elif chunkset_chunk_header.chunk_tag == self._CHUNK_TAG_STATEDUMP:
        self._ReadStateDumpChunkData(
            chunkset_chunk_data, chunkset_chunk_header.chunk_data_size,
            data_offset)

      elif chunkset_chunk_header.chunk_tag == self._CHUNK_TAG_SIMPLEDUMP:
        self._ReadSimpleDumpChunkData(
            chunkset_chunk_data, chunkset_chunk_header.chunk_data_size,
            data_offset)

      data_offset = data_end_offset

      _, alignment = divmod(data_offset, 8)
      if alignment > 0:
        alignment = 8 - alignment

      data_offset += alignment

  def _ReadDSCFile(self, uuid_string):
    """Reads a specific shared-cache strings (DSC) file.

    Args:
      uuid_string (str): string representation of the UUID.

    Returns:
      DSCFile: a shared-cache strings (DSC) file or None if not available.
    """
    if not self._uuidtext_path:
      return None

    dsc_file_path = self._file_system_helper.JoinPath([
        self._uuidtext_path, 'dsc', uuid_string])
    if not self._file_system_helper.CheckFileExistsByPath(dsc_file_path):
      return None

    dsc_file = DSCFile(file_system_helper=self._file_system_helper)
    dsc_file.Open(dsc_file_path)

    return dsc_file

  def _ReadFirehoseChunkData(self, chunk_data, chunk_data_size, data_offset):
    """Reads firehose chunk data.

    Args:
      chunk_data (bytes): firehose chunk data.
      chunk_data_size (int): size of the firehose chunk data.
      data_offset (int): offset of the firehose chunk relative to the start
          of the chunk set.

    Raises:
      ParseError: if the firehose chunk cannot be read.
    """
    data_type_map = self._GetDataTypeMap('tracev3_firehose_header')

    firehose_header = self._ReadStructureFromByteStream(
        chunk_data, data_offset, data_type_map, 'firehose header')

    if self._debug:
      self._DebugPrintStructureObject(
          firehose_header, self._DEBUG_INFO_FIREHOSE_HEADER)

    proc_id = (f'{firehose_header.proc_id_upper:d}@'
               f'{firehose_header.proc_id_lower:d}')

    private_data_virtual_offset = (
        firehose_header.private_data_virtual_offset & 0x0fff)
    if not private_data_virtual_offset:
      private_data_size = 0
      private_data = b''
    else:
      private_data_size = 4096 - private_data_virtual_offset
      private_data = chunk_data[-private_data_size:]
      if self._debug:
        self._DebugPrintData('Private data', private_data)

    chunk_data_offset = 32
    while chunk_data_offset < firehose_header.public_data_size:
      firehose_tracepoint = self._ReadFirehoseTracepointData(
          chunk_data[chunk_data_offset:], data_offset + chunk_data_offset)

      chunk_data_offset += 24

      activity_type = firehose_tracepoint.activity_type
      if activity_type not in (
          self._ACTIVITY_TYPE_ACTIVITY, self._ACTIVITY_TYPE_TRACE,
          self._ACTIVITY_TYPE_LOG, self._ACTIVITY_TYPE_SIGNPOST,
          self._ACTIVITY_TYPE_LOSS):
        raise errors.ParseError(
            f'Unsupported activity type: 0x{activity_type:02x}.')

      tracepoint_data_object = None
      bytes_read = 0

      if activity_type == self._ACTIVITY_TYPE_ACTIVITY:
        if firehose_tracepoint.log_type not in (0x01, 0x03):
          raise errors.ParseError(
              f'Unsupported log type: 0x{firehose_tracepoint.log_type:02x}.')

        tracepoint_data_object, bytes_read = (
            self._ReadFirehoseTracepointActivityData(
                firehose_tracepoint.log_type, firehose_tracepoint.flags,
                firehose_tracepoint.data, data_offset + chunk_data_offset))

      elif activity_type == self._ACTIVITY_TYPE_TRACE:
        # TODO: implement.
        raise errors.ParseError('Unsupported trace activity type.')

      elif activity_type == self._ACTIVITY_TYPE_LOG:
        if firehose_tracepoint.log_type not in (0x00, 0x01, 0x02, 0x10, 0x11):
          raise errors.ParseError(
              f'Unsupported log type: 0x{firehose_tracepoint.log_type:02x}.')

        tracepoint_data_object, bytes_read = (
            self._ReadFirehoseTracepointLogData(
                firehose_tracepoint.flags, firehose_tracepoint.data,
                data_offset + chunk_data_offset))

      elif activity_type == self._ACTIVITY_TYPE_SIGNPOST:
        if firehose_tracepoint.log_type not in (0x80, 0x81, 0x82, 0xc1, 0xc2):
          raise errors.ParseError(
              f'Unsupported log type: 0x{firehose_tracepoint.log_type:02x}.')

        tracepoint_data_object, bytes_read = (
            self._ReadFirehoseTracepointSignpostData(
                firehose_tracepoint.flags, firehose_tracepoint.data,
                data_offset + chunk_data_offset))

      elif activity_type == self._ACTIVITY_TYPE_LOSS:
        if firehose_tracepoint.log_type not in (0x00, ):
          raise errors.ParseError(
              f'Unsupported log type: 0x{firehose_tracepoint.log_type:02x}.')

        tracepoint_data_object, bytes_read = (
            self._ReadFirehoseTracepointLossData(
                firehose_tracepoint.flags, firehose_tracepoint.data,
                data_offset + chunk_data_offset))

      if tracepoint_data_object:
        string_formatter = StringFormatter()
        if self._catalog:
          format_string = self._GetFirehostTracepointFormatString(
              proc_id, firehose_tracepoint, tracepoint_data_object)
          string_formatter.ParseFormatString(format_string)

        data_items = getattr(tracepoint_data_object, 'data_items', None)
        if data_items is None:
          values = []
        else:
          private_data_range = getattr(
              tracepoint_data_object, 'private_data_range', None)
          if private_data_range is None:
            private_data_offset = 0
          else:
            # TODO: error if private_data_virtual_offset >
            # private_data_range.offset
            private_data_offset = (
                private_data_range.offset - private_data_virtual_offset)

          values = self._ReadFirehoseTracepointDataItems(
              firehose_tracepoint.data, data_offset + chunk_data_offset,
              data_items, bytes_read, private_data, private_data_offset,
              string_formatter)

        if self._catalog:
          output_string = string_formatter.FormatString(values)
          # TODO: move this to the script.
          print(output_string, end='')

      chunk_data_offset += firehose_tracepoint.data_size

      _, alignment = divmod(chunk_data_offset, 8)
      if alignment > 0:
        alignment = 8 - alignment

      chunk_data_offset += alignment

    if private_data_size:
      chunk_data_size -= private_data_size

    if self._debug and chunk_data_offset < chunk_data_size:
      self._DebugPrintData(
          'Trailing firehose chunk data',
          chunk_data[chunk_data_offset:chunk_data_size])

  def _ReadFirehoseTracepointData(self, tracepoint_data, data_offset):
    """Reads firehose tracepoint data.

    Args:
      tracepoint_data (bytes): firehose tracepoint data.
      data_offset (int): offset of the firehose tracepoint relative to
          the start of the chunk set.

    Returns:
      tracev3_firehose_tracepoint: firehose tracepoint.

    Raises:
      ParseError: if the firehose tracepoint cannot be read.
    """
    data_type_map = self._GetDataTypeMap('tracev3_firehose_tracepoint')

    firehose_tracepoint = self._ReadStructureFromByteStream(
        tracepoint_data, data_offset, data_type_map, 'firehose tracepoint')

    if self._debug:
      self._DebugPrintStructureObject(
          firehose_tracepoint, self._DEBUG_INFO_FIREHOSE_TRACEPOINT)

    return firehose_tracepoint

  def _ReadFirehoseTracepointActivityData(
      self, log_type, flags, tracepoint_data, data_offset):
    """Reads firehose tracepoint activity data.

    Args:
      log_type (bytes): firehose tracepoint log type.
      flags (bytes): firehose tracepoint flags.
      tracepoint_data (bytes): firehose tracepoint data.
      data_offset (int): offset of the firehose tracepoint data relative to
          the start of the chunk set.

    Returns:
      tuple[tracev3_firehose_tracepoint_activity, int]: activity and the number
          of bytes read.

    Raises:
      ParseError: if the activity data cannot be read.
    """
    supported_flags = 0x0001 | 0x000e | 0x0010 | 0x0020 | 0x0100 | 0x0200

    if flags & ~supported_flags != 0:
      raise errors.ParseError(f'Unsupported flags: 0x{flags:04x}.')

    data_type_map = self._GetDataTypeMap('tracev3_firehose_tracepoint_activity')

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'tracev3_firehose_tracepoint_flags': flags,
        'tracev3_firehose_tracepoint_format_string_type': flags & 0x000e,
        'tracev3_firehose_tracepoint_log_type': log_type})

    activity = self._ReadStructureFromByteStream(
        tracepoint_data, data_offset, data_type_map, 'activity',
        context=context)

    if self._debug:
      self._DebugPrintStructureObject(
          activity, self._DEBUG_INFO_FIREHOSE_TRACEPOINT_ACTIVITY)

    return activity, context.byte_size

  def _ReadFirehoseTracepointDataItems(
      self, tracepoint_data, data_offset, data_items, values_data_offset,
      private_data, private_data_range_offset, string_formatter):
    """Reads firehose tracepoint data items.

    Args:
      tracepoint_data (bytes): firehose tracepoint data.
      data_offset (int): offset of the firehose tracepoint data relative to
          the start of the chunk set.
      data_items (list[tracev3_firehose_tracepoint_data_item]): data items.
      values_data_offset (int): offset of the values data relative to the start
          of the firehose tracepoint data.
      private_data (bytes): firehose private data.
      private_data_range_offset (int): offset of the private data range
          relative to the start of the private data.
      string_formatter (StringFormatter): string formatter.

    Returns:
      list[str]: values formatted as strings.

    Raises:
      ParseError: if the data items cannot be read.
    """
    values = []

    value_index = 0
    precision = None

    for data_item in data_items:
      value = None

      if data_item.value_type in self._DATA_ITEM_INTEGER_VALUE_TYPES:
        type_hint = string_formatter.GetTypeHintByIndex(value_index)
        data_type_map_name = self._DATA_ITEM_INTEGER_DATA_MAP_NAMES.get(
            type_hint or 'unsigned', {}).get(data_item.data_size, None)

        if data_type_map_name:
          data_type_map = self._GetDataTypeMap(data_type_map_name)

          # TODO: calculate data offset for debugging purposes.
          _ = data_offset

          value = self._ReadStructureFromByteStream(
              data_item.data, 0, data_type_map, data_type_map_name)

          if self._debug:
            data_item.integer = value

      elif data_item.value_type in self._DATA_ITEM_STRING_VALUE_TYPES:
        if data_item.value_data_size > 0:
          # Note that the string data does not necessarily include
          # an end-of-string character hence the cstring data_type_map is not
          # used here.
          value_data_offset = values_data_offset + data_item.value_data_offset
          string_data = tracepoint_data[
              value_data_offset:value_data_offset + data_item.value_data_size]

          try:
            value = string_data.decode('utf-8').rstrip('\x00')
          except UnicodeDecodeError:
            pass

        if self._debug:
          data_item.string = value

      elif data_item.value_type == 0x21:
        if data_item.value_data_size > 0:
          # Note that the string data does not necessarily include
          # an end-of-string character hence the cstring data_type_map is not
          # used here.
          value_data_offset = (
              private_data_range_offset + data_item.value_data_offset)
          string_data = private_data[
              value_data_offset:value_data_offset + data_item.value_data_size]

          try:
            value = string_data.decode('utf-8').rstrip('\x00')
          except UnicodeDecodeError:
            pass

        if self._debug:
          data_item.private_string = value

      elif data_item.value_type in self._DATA_ITEM_BINARY_DATA_VALUE_TYPES:
        value_data_offset = values_data_offset + data_item.value_data_offset
        value = tracepoint_data[
            value_data_offset:value_data_offset + data_item.value_data_size]

        if self._debug:
          data_item.value_data = value

      if self._debug:
        self._DebugPrintStructureObject(
            data_item, self._DEBUG_INFO_FIREHOSE_TRACEPOINT_DATA_ITEM)

        if data_item.value_type not in (
            0x00, 0x01, 0x02, 0x12, 0x20, 0x21, 0x22, 0x25, 0x31, 0x32,
            0x40, 0x41, 0x42, 0x72, 0xf2):
          raise errors.ParseError((
              f'Unsupported data item value type: '
              f'0x{data_item.value_type:02x}.'))

      if data_item.value_type == 0x12:
        precision = value
        continue

      decoder_names = string_formatter.GetDecoderNamesByIndex(value_index)
      if data_item.value_type in self._DATA_ITEM_PRIVATE_VALUE_TYPES:
        value = '<private>'

      elif decoder_names:
        decoder_class = self._FORMAT_STRING_DECODERS.get(decoder_names[0], None)
        if decoder_class:
          value = decoder_class.FormatValue(value)
        else:
          value = f'<decode: unsupported decoder: {decoder_names[0]:s}>'

      elif data_item.value_type in self._DATA_ITEM_STRING_VALUE_TYPES:
        if value is None:
          value = '(null)'

      else:
        value = string_formatter.FormatValue(
            value_index, value, precision=precision)

      precision = None

      values.append(value)

      value_index += 1

    return values

  def _ReadFirehoseTracepointLogData(self, flags, tracepoint_data, data_offset):
    """Reads firehose tracepoint log data.

    Args:
      flags (bytes): firehose tracepoint flags.
      tracepoint_data (bytes): firehose tracepoint data.
      data_offset (int): offset of the firehose tracepoint data relative to
          the start of the chunk set.

    Returns:
      tuple[tracev3_firehose_tracepoint_log, int]: log and the number of bytes
          read.

    Raises:
      ParseError: if the log data cannot be read.
    """
    supported_flags = (
        0x0001 | 0x000e | 0x0020 | 0x0100 | 0x0200 | 0x0400 | 0x0800 | 0x1000)

    if flags & ~supported_flags != 0:
      raise errors.ParseError(f'Unsupported flags: 0x{flags:04x}.')

    data_type_map = self._GetDataTypeMap('tracev3_firehose_tracepoint_log')

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'tracev3_firehose_tracepoint_flags': flags,
        'tracev3_firehose_tracepoint_format_string_type': flags & 0x000e})

    log = self._ReadStructureFromByteStream(
        tracepoint_data, data_offset, data_type_map, 'log', context=context)

    if self._debug:
      self._DebugPrintStructureObject(
          log, self._DEBUG_INFO_FIREHOSE_TRACEPOINT_LOG)

    return log, context.byte_size

  def _ReadFirehoseTracepointLossData(
      self, flags, tracepoint_data, data_offset):
    """Reads firehose tracepoint loss data.

    Args:
      flags (bytes): firehose tracepoint flags.
      tracepoint_data (bytes): firehose tracepoint data.
      data_offset (int): offset of the firehose tracepoint data relative to
          the start of the chunk set.

    Returns:
      tuple[tracev3_firehose_tracepoint_loss, int]: loss and the number of bytes
          read.

    Raises:
      ParseError: if the loss data cannot be read.
    """
    supported_flags = 0x0000

    if flags & ~supported_flags != 0:
      raise errors.ParseError(f'Unsupported flags: 0x{flags:04x}.')

    data_type_map = self._GetDataTypeMap('tracev3_firehose_tracepoint_loss')

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'tracev3_firehose_tracepoint_flags': flags,
        'tracev3_firehose_tracepoint_format_string_type': flags & 0x000e})

    loss = self._ReadStructureFromByteStream(
        tracepoint_data, data_offset, data_type_map, 'loss', context=context)

    if self._debug:
      self._DebugPrintStructureObject(
          loss, self._DEBUG_INFO_FIREHOSE_TRACEPOINT_LOSS)

    return loss, context.byte_size

  def _ReadFirehoseTracepointSignpostData(
      self, flags, tracepoint_data, data_offset):
    """Reads firehose tracepoint signpost data.

    Args:
      flags (bytes): firehose tracepoint flags.
      tracepoint_data (bytes): firehose tracepoint data.
      data_offset (int): offset of the firehose tracepoint data relative to
          the start of the chunk set.

    Returns:
      tuple[tracev3_firehose_tracepoint_signpost, int]: signpost and the number
          of bytes read.

    Raises:
      ParseError: if the signpost data cannot be read.
    """
    supported_flags = (
        0x0001 | 0x000e | 0x0020 | 0x0100 | 0x0200 | 0x0400 | 0x0800 | 0x8000)

    if flags & ~supported_flags != 0:
      raise errors.ParseError(f'Unsupported flags: 0x{flags:04x}.')

    data_type_map = self._GetDataTypeMap('tracev3_firehose_tracepoint_signpost')

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'tracev3_firehose_tracepoint_flags': flags,
        'tracev3_firehose_tracepoint_format_string_type': flags & 0x000e})

    signpost = self._ReadStructureFromByteStream(
        tracepoint_data, data_offset, data_type_map, 'signpost',
        context=context)

    if self._debug:
      self._DebugPrintStructureObject(
          signpost, self._DEBUG_INFO_FIREHOSE_TRACEPOINT_SIGNPOST)

    return signpost, context.byte_size

  def _ReadHeaderChunk(self, file_object, file_offset):
    """Reads a header chunk.

    Args:
       file_object (file): file-like object.
       file_offset (int): offset of the chunk relative to the start of the file.

    Returns:
      header_chunk: a header chunk.

    Raises:
      ParseError: if the header chunk cannot be read.
    """
    data_type_map = self._GetDataTypeMap('tracev3_header_chunk')

    header_chunk, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'header chunk')

    if self._debug:
      self._DebugPrintStructureObject(
          header_chunk, self._DEBUG_INFO_HEADER)
      self._DebugPrintStructureObject(
          header_chunk.continuous,
          self._DEBUG_INFO_HEADER_CONTINOUS_TIME_SUB_CHUNK)
      self._DebugPrintStructureObject(
          header_chunk.system_information,
          self._DEBUG_INFO_HEADER_SYSTEM_INFORMATION_SUB_CHUNK)
      self._DebugPrintStructureObject(
          header_chunk.generation, self._DEBUG_INFO_HEADER_GENERATION_SUB_CHUNK)
      self._DebugPrintStructureObject(
          header_chunk.time_zone, self._DEBUG_INFO_HEADER_TIME_ZONE_SUB_CHUNK)

    return header_chunk

  def _ReadOversizeChunkData(self, chunk_data, chunk_data_size, data_offset):
    """Reads Oversize chunk data.

    Args:
      chunk_data (bytes): Oversize chunk data.
      chunk_data_size (int): size of the Oversize chunk data.
      data_offset (int): offset of the Oversize chunk relative to the start
          of the chunk set.

    Returns:
      oversize_chunk: an Oversize chunk.

    Raises:
      ParseError: if the chunk cannot be read.
    """
    data_type_map = self._GetDataTypeMap('tracev3_oversize_chunk')

    context = dtfabric_data_maps.DataTypeMapContext()

    oversize_chunk = self._ReadStructureFromByteStream(
        chunk_data, data_offset, data_type_map, 'Oversize chunk',
        context=context)

    if self._debug:
      self._DebugPrintStructureObject(
          oversize_chunk, self._DEBUG_INFO_OVERSIZE_CHUNK)

    if self._debug and context.byte_size < chunk_data_size:
      self._DebugPrintData(
          'Trailing Oversize chunk data', chunk_data[context.byte_size:])

    return oversize_chunk

  def _ReadSimpleDumpChunkData(self, chunk_data, chunk_data_size, data_offset):
    """Reads SimpleDump chunk data.

    Args:
      chunk_data (bytes): SimpleDump chunk data.
      chunk_data_size (int): size of the SimpleDump chunk data.
      data_offset (int): offset of the SimpleDump chunk relative to the start
          of the chunk set.

    Returns:
      simpledump_chunk: a SimpleDump chunk.

    Raises:
      ParseError: if the chunk cannot be read.
    """
    data_type_map = self._GetDataTypeMap('tracev3_simpledump_chunk')

    context = dtfabric_data_maps.DataTypeMapContext()

    simpledump_chunk = self._ReadStructureFromByteStream(
        chunk_data, data_offset, data_type_map, 'SimpleDump chunk',
        context=context)

    if self._debug:
      self._DebugPrintStructureObject(
          simpledump_chunk, self._DEBUG_INFO_SIMPLEDUMP_CHUNK)

    if self._debug and context.byte_size < chunk_data_size:
      self._DebugPrintData(
          'Trailing SimpleDump chunk data', chunk_data[context.byte_size:])

    return simpledump_chunk

  def _ReadStateDumpChunkData(self, chunk_data, chunk_data_size, data_offset):
    """Reads StateDump chunk data.

    Args:
      chunk_data (bytes): StateDump chunk data.
      chunk_data_size (int): size of the StateDump chunk data.
      data_offset (int): offset of the StateDump chunk relative to the start
          of the chunk set.

    Returns:
      statedump_chunk: a StateDump chunk.

    Raises:
      ParseError: if the chunk cannot be read.
    """
    data_type_map = self._GetDataTypeMap('tracev3_statedump_chunk')

    context = dtfabric_data_maps.DataTypeMapContext()

    statedump_chunk = self._ReadStructureFromByteStream(
        chunk_data, data_offset, data_type_map, 'StateDump chunk',
        context=context)

    if self._debug:
      self._DebugPrintStructureObject(
          statedump_chunk, self._DEBUG_INFO_STATEDUMP_CHUNK)

    if self._debug and context.byte_size < chunk_data_size:
      self._DebugPrintData(
          'Trailing StateDump chunk data', chunk_data[context.byte_size:])

    return statedump_chunk

  def _ReadUUIDTextFile(self, uuid_string):
    """Reads a specific uuidtext file.

    Args:
      uuid_string (str): string representation of the UUID.

    Returns:
      UUIDTextFile: an uuidtext file or None if not available.
    """
    if not self._uuidtext_path:
      return None

    uuidtext_file_path = self._file_system_helper.JoinPath([
        self._uuidtext_path, uuid_string[0:2], uuid_string[2:]])
    result = self._file_system_helper.CheckFileExistsByPath(uuidtext_file_path)
    if not result:
      return None

    uuidtext_file = UUIDTextFile(file_system_helper=self._file_system_helper)
    uuidtext_file.Open(uuidtext_file_path)

    return uuidtext_file

  def Close(self):
    """Closes a binary data file.

    Raises:
      IOError: if the file is not opened.
      OSError: if the file is not opened.
    """
    for dsc_file in self._cached_dsc_files.values():
      if dsc_file:
        dsc_file.Close()

    for uuidtext_file in self._cached_uuidtext_files.values():
      if uuidtext_file:
        uuidtext_file.Close()

    super(TraceV3File, self).Close()

  def ReadFileObject(self, file_object):
    """Reads a tracev3 file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    # The uuidtext files can be stored in multiple locations relative from
    # the tracev3 file.
    # * in ../ for *.logarchive/logdata.LiveData.tracev3
    # * in ../../ for .logarchive/*/*.tracev3
    # * in ../../uuidtext/ for /private/var/db/diagnostics/*/*.tracev3
    path_segments = self._file_system_helper.SplitPath(self._path)
    # Remove the filename from the path.
    path_segments.pop(-1)
    # Traverse into parent directory.
    path_segments.pop(-1)

    if not path_segments[-1].lower().endswith('.logarchive'):
      path_segments.pop(-1)

    if path_segments[-1].lower().endswith('.logarchive'):
      path_segments.append('dsc')
      dsc_path = self._file_system_helper.JoinPath(path_segments)
      if self._file_system_helper.CheckFileExistsByPath(dsc_path):
        path_segments.pop(-1)
        self._uuidtext_path = self._file_system_helper.JoinPath(path_segments)

    else:
      path_segments.append('uuidtext')
      uuidtext_path = self._file_system_helper.JoinPath(path_segments)
      if self._file_system_helper.CheckFileExistsByPath(uuidtext_path):
        self._uuidtext_path = uuidtext_path

    file_offset = 0

    while file_offset < self._file_size:
      chunk_header = self._ReadChunkHeader(file_object, file_offset)
      file_offset += 16

      if chunk_header.chunk_tag == self._CHUNK_TAG_HEADER:
        self._ReadHeaderChunk(file_object, file_offset)

      elif chunk_header.chunk_tag == self._CHUNK_TAG_CATALOG:
        self._catalog = self._ReadCatalog(
            file_object, file_offset, chunk_header)
        self._BuildCatalogProcessInformationEntries(self._catalog)

      elif chunk_header.chunk_tag == self._CHUNK_TAG_CHUNK_SET:
        self._ReadChunkSet(file_object, file_offset, chunk_header)

      file_offset += chunk_header.chunk_data_size

      _, alignment = divmod(file_offset, 8)
      if alignment > 0:
        alignment = 8 - alignment

      file_offset += alignment


class UUIDTextFile(data_format.BinaryDataFile):
  """Apple Unified Logging and Activity Tracing (uuidtext) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('aul_uuidtext.yaml')

  _DEBUG_INFO_FILE_FOOTER = [
      ('library_path', 'Library path', '_FormatString')]

  _DEBUG_INFO_FILE_HEADER = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('major_format_version', 'Major format version',
       '_FormatIntegerAsDecimal'),
      ('minor_format_version', 'Minor format version',
       '_FormatIntegerAsDecimal'),
      ('number_of_entries', 'Number of entries', '_FormatIntegerAsDecimal'),
      ('entry_descriptors', 'Entry descriptors',
       '_FormatArrayOfEntryDescriptors')]

  def __init__(self, debug=False, file_system_helper=None, output_writer=None):
    """Initializes an uuidtext file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      file_system_helper (Optional[FileSystemHelper]): file system helper.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(UUIDTextFile, self).__init__(
        debug=debug, file_system_helper=file_system_helper,
        output_writer=output_writer)
    self._entry_descriptors = []
    self._file_footer = None

  @property
  def library_name(self):
    """str: library path associated with the file."""
    return getattr(self._file_footer, 'library_path', None)

  def _FormatArrayOfEntryDescriptors(self, array_of_entry_descriptors):
    """Formats an array of entry descriptors.

    Args:
      array_of_entry_descriptors (list[uuidtext_entry_descriptor]): array of
          entry descriptors.

    Returns:
      str: formatted array of entry descriptors.
    """
    value = '\n'.join([
        (f'\t[{entry_index:03d}] offset: 0x{entry_descriptor.offset:08x}, '
         f'data size: {entry_descriptor.data_size:d}')
        for entry_index, entry_descriptor in enumerate(
            array_of_entry_descriptors)])
    return f'{value:s}\n'

  def _FormatStreamAsSignature(self, stream):
    """Formats a stream as a signature.

    Args:
      stream (bytes): stream.

    Returns:
      str: stream formatted as a signature.
    """
    return (f'\\x{stream[0]:02x}\\x{stream[1]:02x}\\x{stream[2]:02x}'
            f'\\x{stream[3]:02x}')

  def _ReadFileFooter(self, file_object, file_offset):
    """Reads a file footer.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the file footer relative to the start
          of the file.

    Returns:
      uuidtext_file_footer: a file footer.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    data_type_map = self._GetDataTypeMap('uuidtext_file_footer')

    file_footer, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file footer')

    if self._debug:
      self._DebugPrintStructureObject(
          file_footer, self._DEBUG_INFO_FILE_FOOTER)

    return file_footer

  def _ReadFileHeader(self, file_object):
    """Reads a file header.

    Args:
      file_object (file): file-like object.

    Returns:
      uuidtext_file_header: a file header.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('uuidtext_file_header')

    file_header, _ = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'file header')

    if self._debug:
      self._DebugPrintStructureObject(
          file_header, self._DEBUG_INFO_FILE_HEADER)

    format_version = (
        file_header.major_format_version, file_header.minor_format_version)
    if format_version != (2, 1):
      format_version_string = '.'.join([
          f'{file_header.major_format_version:d}',
          f'{file_header.minor_format_version:d}'])
      raise errors.ParseError(
          f'Unsupported format version: {format_version_string:s}')

    return file_header

  def _ReadFormatString(self, file_object, file_offset):
    """Reads a format string.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the format string data relative to the start
          of the file.

    Returns:
      str: format string.

    Raises:
      ParseError: if the format string cannot be read.
    """
    data_type_map = self._GetDataTypeMap('cstring')

    format_string, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'format string')

    if self._debug:
      self._DebugPrintValue('Format string', format_string)

    return format_string

  def GetFormatString(self, format_string_location):
    """Retrieves a format string.

    Args:
      format_string_location (int): location of the format string.

    Returns:
      str: format string or None if not available.

    Raises:
      ParseError: if the format string cannot be read.
    """
    for file_offset, entry_descriptor in self._entry_descriptors:
      if format_string_location < entry_descriptor.offset:
        continue

      relative_offset = format_string_location - entry_descriptor.offset
      if relative_offset <= entry_descriptor.data_size:
        file_offset += relative_offset
        return self._ReadFormatString(self._file_object, file_offset)

    return None

  def ReadFileObject(self, file_object):
    """Reads an uuidtext file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_header = self._ReadFileHeader(file_object)

    self._entry_descriptors = []

    file_offset = file_object.tell()
    for entry_descriptor in file_header.entry_descriptors:
      self._entry_descriptors.append((file_offset, entry_descriptor))

      file_offset += entry_descriptor.data_size

    self._file_footer = self._ReadFileFooter(file_object, file_offset)
