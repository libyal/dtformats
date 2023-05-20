# -*- coding: utf-8 -*-
"""Apple Unified Logging and Activity Tracing files."""

import abc
import collections
import re
import os

import lz4.block

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


class BaseFormatStringDecoder(object):
  """Format string decoder interface."""

  @classmethod
  @abc.abstractmethod
  def FormatValue(cls, value):
    """Formats a value.

    Args:
      value (object): value.

    Returns:
      str: formatted value.
    """


class ErrorFormatStringDecoder(BaseFormatStringDecoder):
  """Error format string decoder."""

  @classmethod
  def FormatValue(cls, error_code):  # pylint: disable=arguments-renamed
    """Formats an error code value.

    Args:
      error_code (int): error code.

    Returns:
      str: formatted error code value.
    """
    error_message = darwin.DARWIN_ERROR_CODES.get(
        error_code, 'UNKNOWN: {0:d}'.format(error_code))

    # TODO: determine what the MacOS log tool shows when an error message is
    # not defined.
    return f'[{error_code:d}: {error_message:s}]'


class FileModeFormatStringDecoder(BaseFormatStringDecoder):
  """File mode format string decoder."""

  _FILE_TYPES = {
      0x1000: 'p',
      0x2000: 'c',
      0x4000: 'd',
      0x6000: 'b',
      0xa000: 'l',
      0xc000: 's'}

  @classmethod
  def FormatValue(cls, mode):  # pylint: disable=arguments-renamed
    """Formats a file mode value.

    Args:
      mode (int): file mode.

    Returns:
      str: formatted file mode value.
    """
    string_parts = 10 * ['-']

    if mode & 0x0001:
      string_parts[9] = 'x'
    if mode & 0x0002:
      string_parts[8] = 'w'
    if mode & 0x0004:
      string_parts[7] = 'r'

    if mode & 0x0008:
      string_parts[6] = 'x'
    if mode & 0x0010:
      string_parts[5] = 'w'
    if mode & 0x0020:
      string_parts[4] = 'r'

    if mode & 0x0040:
      string_parts[3] = 'x'
    if mode & 0x0080:
      string_parts[2] = 'w'
    if mode & 0x0100:
      string_parts[1] = 'r'

    string_parts[0] = cls._FILE_TYPES.get(mode & 0xf000, '-')

    return ''.join(string_parts)


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

  def __init__(self, debug=False, output_writer=None):
    """Initializes a shared-cache strings (dsc) file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(DSCFile, self).__init__(debug=debug, output_writer=output_writer)
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

  def __init__(self, debug=False, output_writer=None):
    """Initializes a timesync database file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(TimesyncDatabaseFile, self).__init__(
        debug=debug, output_writer=output_writer)
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

  _DATA_ITEM_VALUE_TYPE_DESCRIPTIONS = {
      }

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
      ('private_strings_range', 'Private strings range', '_FormatStringsRange'),
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
      ('private_strings_range', 'Private strings range', '_FormatStringsRange'),
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

  _FORMAT_STRING_OPERATOR_REGEX = re.compile(
      r'(%'
      r'(?:\{([^\}]{1,64})\})?'         # Optional value type decoder.
      r'([-+0 #]{0,5})'                 # Optional flags.
      r'([0-9]+|\*)?'                   # Optional width.
      r'(\.(?:[0-9]+|\*))?'             # Optional precision.
      r'(?:h|hh|j|l|ll|L|t|q|z)?'       # Optional length modifier.
      r'([@aAcCdDeEfFgGinoOpPsSuUxX])'  # Conversion specifier.
      r'|%%)')

  _FORMAT_STRING_TYPE_HINTS = {
      'd': 'signed',
      'p': 'unsigned',
      'u': 'unsigned',
      'x': 'unsigned'}

  _FORMAT_STRING_DECODERS = {
      'darwin.errno': ErrorFormatStringDecoder,
      'darwin.mode': FileModeFormatStringDecoder,
      'error': ErrorFormatStringDecoder}

  _MAXIMUM_CACHED_FILES = 64
  _MAXIMUM_CACHED_FORMAT_STRINGS = 1024

  def __init__(self, debug=False, output_writer=None):
    """Initializes a tracev3 file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(TraceV3File, self).__init__(debug=debug, output_writer=output_writer)
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
        print(f'Identifier: {sub_system_entry.identifier:d}, '
              f'Sub system: {sub_system:s}, Category: {category:s}')
      print('')

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
      calculated_large_offset_data = large_shared_cache_data >> 1
      if large_offset_data != calculated_large_offset_data:
        print((f'Large offset data mismatch stored: ('
               f'0x{large_offset_data:04x}, calculated: '
               f'0x{calculated_large_offset_data:04x})'))

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
      lines.append('\tHas private strings range (0x0100)')
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

  def _FormatStringsRange(self, strings_range):
    """Formats a strings range.

    Args:
      strings_range (tracev3_firehose_tracepoint_strings_range): strings range.

    Returns:
      str: formatted strings range.
    """
    return f'offset: 0x{strings_range.offset:04x}, size: {strings_range.size:d}'

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
          uuid = self._catalog.uuids[uuid_entry.uuid_index]
          uuid_string = uuid.hex.upper()
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
    dsc_file_path = os.path.join(self._uuidtext_path, 'dsc', uuid_string)
    if not os.path.exists(dsc_file_path):
      return None

    dsc_file = DSCFile()
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
    # TODO: clean up
    _ = chunk_data_size

    data_type_map = self._GetDataTypeMap('tracev3_firehose_header')

    firehose_header = self._ReadStructureFromByteStream(
        chunk_data, data_offset, data_type_map, 'firehose header')

    if self._debug:
      self._DebugPrintStructureObject(
          firehose_header, self._DEBUG_INFO_FIREHOSE_HEADER)

    proc_id = (f'{firehose_header.proc_id_upper:d}@'
               f'{firehose_header.proc_id_lower:d}')

    if firehose_header.private_data_virtual_offset < 4096:
      private_data_size = 4096 - firehose_header.private_data_virtual_offset
      if self._debug:
        self._DebugPrintData('Private data', chunk_data[-private_data_size:])

    chunk_data_offset = 32
    while chunk_data_offset < firehose_header.public_data_size - 16:
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
        # TODO: implement
        pass

      elif activity_type == self._ACTIVITY_TYPE_LOG:
        if firehose_tracepoint.log_type not in (0x00, 0x01, 0x02, 0x10, 0x11):
          raise errors.ParseError(
              f'Unsupported log type: 0x{firehose_tracepoint.log_type:02x}.')

        tracepoint_data_object, bytes_read = (
            self._ReadFirehoseTracepointLogData(
                firehose_tracepoint.flags, firehose_tracepoint.data,
                data_offset + chunk_data_offset))

      elif activity_type == self._ACTIVITY_TYPE_SIGNPOST:
        if firehose_tracepoint.log_type not in (0x80, 0x81, 0x82, 0xc2):
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
        value_type_decoders = []

        if not self._catalog:
          format_string = None
        else:
          format_string = self._GetFirehostTracepointFormatString(
              proc_id, firehose_tracepoint, tracepoint_data_object)
          if format_string:
            format_string, value_type_decoders = self._RewriteFormatString(
                format_string)

        number_of_data_items = getattr(
            tracepoint_data_object, 'number_of_data_items', 0)
        if not number_of_data_items:
          values = []
        else:
          number_of_value_type_decoders = len(value_type_decoders)
          if (number_of_value_type_decoders > 0 and
              number_of_value_type_decoders != number_of_data_items):
            raise errors.ParseError(
                'Mismatch in number of data items and value type decoders.')

          values = self._ReadFirehoseTracepointDataItems(
              firehose_tracepoint.data, data_offset,
              tracepoint_data_object.data_items, bytes_read,
              value_type_decoders)

        if format_string:
          if values:
            print(format_string.format(*values))
          else:
            print(format_string)

      chunk_data_offset += firehose_tracepoint.data_size

      _, alignment = divmod(chunk_data_offset, 8)
      if alignment > 0:
        alignment = 8 - alignment

      chunk_data_offset += alignment

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
    supported_flags = 0x0001 | 0x000e | 0x0010 | 0x0020 | 0x0200

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
      value_type_decoders):
    """Reads firehose tracepoint data items.

    Args:
      tracepoint_data (bytes): firehose tracepoint data.
      data_offset (int): offset of the firehose tracepoint data relative to
          the start of the chunk set.
      data_items (list[tracev3_firehose_tracepoint_data_item]): data items.
      values_data_offset (int): offset of the valuesdata relative to the start
          of the firehose tracepoint data.
      value_type_decoders (list[tuple[str, str]]): value type decoders.

    Returns:
      list[object]: data item values.

    Raises:
      ParseError: if the data items cannot be read.
    """
    values = []

    decoder = None
    type_hint = None

    for item_index, data_item in enumerate(data_items):
      value = None

      if value_type_decoders:
        decoder, type_hint = value_type_decoders[item_index]

      if data_item.value_type in (0x01, 0x02):
        data_type_map_name = self._DATA_ITEM_INTEGER_DATA_MAP_NAMES.get(
            type_hint or 'unsigned', {}).get(data_item.data_size, None)

        if data_type_map_name:
          data_type_map = self._GetDataTypeMap(data_type_map_name)

          # TODO: calculate data offset for debugging purposes.
          data_item.integer = self._ReadStructureFromByteStream(
              data_item.data, 0, data_type_map, data_type_map_name)

          value = data_item.integer

      elif data_item.value_type in self._DATA_ITEM_STRING_VALUE_TYPES:
        if data_item.value_data_size == 0:
          data_item.string = '(null)'
        else:
          # Note that the string data does not necessarily include
          # an end-of-string character hence the cstring data_type_map is not
          # used here.
          value_data_offset = values_data_offset + data_item.value_data_offset
          string_data = tracepoint_data[
              value_data_offset:value_data_offset + data_item.value_data_size]

          try:
            data_item.string = string_data.decode('utf-8').rstrip('\x00')
          except UnicodeDecodeError:
            pass

        value = data_item.string

      elif data_item.value_type == 0x21:
        value = '<private>'

      elif data_item.value_type == 0x32:
        value_data_offset = values_data_offset + data_item.value_data_offset
        data_item.value_data = tracepoint_data[
            value_data_offset:value_data_offset + data_item.value_data_size]

        value = data_item.value_data

      elif data_item.value_type == 0xf2:
        if data_item.value_data_size != 16:
          raise errors.ParseError((
              f'Unsupported data item value size: '
              f'{data_item.value_data_size:d}.'))

        data_type_map = self._GetDataTypeMap('uuid_be')

        value_data_offset = values_data_offset + data_item.value_data_offset
        data_item.uuid = self._ReadStructureFromByteStream(
            tracepoint_data[value_data_offset:],
            data_offset + value_data_offset, data_type_map, 'UUID')

        value = tracepoint_data[value_data_offset:value_data_offset + 16]

      if self._debug:
        self._DebugPrintStructureObject(
            data_item, self._DEBUG_INFO_FIREHOSE_TRACEPOINT_DATA_ITEM)

        if data_item.value_type not in (
            0x00, 0x01, 0x02, 0x12, 0x20, 0x21, 0x22, 0x25, 0x31, 0x32,
            0x40, 0x41, 0x42, 0x72, 0xf2):
          raise errors.ParseError((
              f'Unsupported data item value type: '
              f'0x{data_item.value_type:02x}.'))

      decoder_class = self._FORMAT_STRING_DECODERS.get(decoder, None)
      if decoder_class:
        value = decoder_class.FormatValue(value)

      values.append(value)

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

    oversize_chunk = self._ReadStructureFromByteStream(
        chunk_data, data_offset, data_type_map, 'Oversize chunk')

    if self._debug:
      self._DebugPrintStructureObject(
          oversize_chunk, self._DEBUG_INFO_OVERSIZE_CHUNK)

    # TODO: check for trailing data.
    _ = chunk_data_size

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

    simpledump_chunk = self._ReadStructureFromByteStream(
        chunk_data, data_offset, data_type_map, 'SimpleDump chunk')

    if self._debug:
      self._DebugPrintStructureObject(
          simpledump_chunk, self._DEBUG_INFO_SIMPLEDUMP_CHUNK)

    # TODO: check for trailing data.
    _ = chunk_data_size

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

    statedump_chunk = self._ReadStructureFromByteStream(
        chunk_data, data_offset, data_type_map, 'StateDump chunk')

    if self._debug:
      self._DebugPrintStructureObject(
          statedump_chunk, self._DEBUG_INFO_STATEDUMP_CHUNK)

    # TODO: check for trailing data.
    _ = chunk_data_size

    return statedump_chunk

  def _ReadUUIDTextFile(self, uuid_string):
    """Reads a specific uuidtext file.

    Args:
      uuid_string (str): string representation of the UUID.

    Returns:
      UUIDTextFile: an uuidtext file or None if not available.
    """
    uuidtext_file_path = os.path.join(
        self._uuidtext_path, uuid_string[0:2], uuid_string[2:])
    if not os.path.exists(uuidtext_file_path):
      return None

    uuidtext_file = UUIDTextFile()
    uuidtext_file.Open(uuidtext_file_path)

    return uuidtext_file

  def _RewriteFormatString(self, format_string):
    """Rewrites an Unified Logging format string to a Python format string.

    Args:
      format_string (str): Unified Logging format string.

    Returns:
      tuple[str, list[tuple[str, str]]]: Python format string and value type
          decoders.
    """
    if not format_string:
      return '', []

    format_string_segments = []
    value_type_decoders = []

    last_match_end = 0
    for match in self._FORMAT_STRING_OPERATOR_REGEX.finditer(format_string):
      literal, decoder, flags, width, precision, specifier = match.groups()

      match_start, match_end = match.span()
      if match_start > last_match_end:
        format_string_segments.append(format_string[last_match_end:match_start])

      if literal == '%%':
        literal = '%'
      elif specifier:
        type_hint = self._FORMAT_STRING_TYPE_HINTS.get(specifier, None)

        if specifier in ('p', 'u'):
          specifier = 'd'

        precision = precision or ''
        width = width or ''
        literal = f'{{:{flags:s}{precision:s}{width:s}{specifier:s}}}'

        value_type_decoders.append((decoder, type_hint))

      format_string_segments.append(literal)

      last_match_end = match_end

    string_size = len(format_string)
    if string_size > last_match_end:
      format_string_segments.append(format_string[last_match_end:string_size])

    return ''.join(format_string_segments), value_type_decoders

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
    # The uuidtext files are stored in ../../../uuidtext/ relative from
    # the tracev3 file.
    path_segments = os.path.abspath(self._path).split(os.path.sep)[:-3]
    path_segments.append('uuidtext')
    self._uuidtext_path = os.path.join(os.path.sep, *path_segments)

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

  def __init__(self, debug=False, output_writer=None):
    """Initializes an uuidtext file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(UUIDTextFile, self).__init__(debug=debug, output_writer=output_writer)
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
