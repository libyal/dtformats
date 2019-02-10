# -*- coding: utf-8 -*-
"""Apple Unified Logging and Activity Tracing files."""

from __future__ import unicode_literals

import lz4.block

from dtformats import data_format
from dtformats import errors


class DSCFile(data_format.BinaryDataFile):
  """Shared-Cache Strings (dsc) file."""

  _DEFINITION_FILE = 'unified_logging.yaml'

  _DEBUG_INFO_FILE_HEADER = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('major_format_version', 'Major format version',
       '_FormatIntegerAsDecimal'),
      ('minor_format_version', 'Minor format version',
       '_FormatIntegerAsDecimal'),
      ('number_of_ranges', 'Number of ranges', '_FormatIntegerAsDecimal'),
      ('number_of_uuids', 'Number of UUIDs', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_RANGE_DESCRIPTOR = [
      ('uuid_descriptor_index', 'UUID descriptor index',
       '_FormatIntegerAsDecimal'),
      ('range_offset', 'Range offset', '_FormatIntegerAsHexadecimal8'),
      ('data_offset', 'Data offset', '_FormatIntegerAsHexadecimal8'),
      ('range_size', 'Range size', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_UUID_DESCRIPTOR = [
      ('text_offset', 'Text offset', '_FormatIntegerAsHexadecimal8'),
      ('text_size', 'Text size', '_FormatIntegerAsDecimal'),
      ('sender_identifier', 'Sender identifier', '_FormatUUIDAsString'),
      ('path_offset', 'Path offset', '_FormatIntegerAsHexadecimal8')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a timezone information file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(DSCFile, self).__init__(
        debug=debug, output_writer=output_writer)

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

      for range_index, range_descriptor in enumerate(
          file_header.range_descriptors):
        self._output_writer.WriteText(
            'Range: {0:d} descriptor\n'.format(range_index))
        self._DebugPrintStructureObject(
            range_descriptor, self._DEBUG_INFO_RANGE_DESCRIPTOR)

      for uuid_index, uuid_descriptor in enumerate(
          file_header.uuid_descriptors):
        self._output_writer.WriteText(
            'UUID: {0:d} descriptor\n'.format(uuid_index))
        self._DebugPrintStructureObject(
            uuid_descriptor, self._DEBUG_INFO_UUID_DESCRIPTOR)

    if file_header.signature != b'hcsd':
      raise errors.ParseError('Unsupported signature.')

    format_version = (
        file_header.major_format_version, file_header.minor_format_version)
    if format_version != (1, 0):
      raise errors.ParseError(
          'Unsupported format version: {0:d}.{1:d}.'.format(
              file_header.major_format_version,
              file_header.minor_format_version))

    return file_header

  def ReadFileObject(self, file_object):
    """Reads a timezone information file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadFileHeader(file_object)


class TraceV3File(data_format.BinaryDataFile):
  """Apple Unified Logging and Activity Tracing (tracev3) file."""

  _DEFINITION_FILE = 'unified_logging.yaml'

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
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal8'),
      ('unknown3', 'Unknown3', '_FormatIntegerAsHexadecimal8'),
      ('uuids', 'UUIDs', '_FormatArrayOfUUIDS'),
      ('sub_system_strings', 'Sub system strings', '_FormatArrayOfStrings')]

  _DEBUG_INFO_CHUNK_HEADER = [
      ('chunk_tag', 'Chunk tag', '_FormatIntegerAsHexadecimal8'),
      ('chunk_sub_tag', 'Chunk sub tag', '_FormatIntegerAsHexadecimal8'),
      ('chunk_data_size', 'Chunk data size', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8')]

  _DEBUG_INFO_LZ4_BLOCK_HEADER = [
      ('signature', 'Signature', '_FormatStreamAsSignature'),
      ('uncompressed_data_size', 'Uncompressed data size',
       '_FormatIntegerAsDecimal'),
      ('compressed_data_size', 'Compressed data size',
       '_FormatIntegerAsDecimal')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a timezone information file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(TraceV3File, self).__init__(
        debug=debug, output_writer=output_writer)

  def _FormatArrayOfStrings(self, array_of_strings):
    """Formats an array of strings.

    Args:
      array_of_strings (list[str]): array of strings.

    Returns:
      str: formatted array of strings.
    """
    return '{0:s}\n'.format('\n'.join([
        '\t[{0:03d}] {1:s}'.format(string_index, string)
        for string_index, string in enumerate(array_of_strings)]))

  def _FormatArrayOfUUIDS(self, array_of_uuids):
    """Formats an array of UUIDs.

    Args:
      array_of_uuids (list[uuid]): array of UUIDs.

    Returns:
      str: formatted array of UUIDs.
    """
    return '{0:s}\n'.format('\n'.join([
        '\t[{0:03d}] {1!s}'.format(uuid_index, uuid)
        for uuid_index, uuid in enumerate(array_of_uuids)]))

  def _FormatStreamAsSignature(self, stream):
    """Formats a stream as a signature.

    Args:
      stream (bytes): stream.

    Returns:
      str: stream formatted as a signature.
    """
    return stream.decode('ascii')

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

  def _ReadCatalog(self, file_object, file_offset, chunk_header):
    """Reads a catalog.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the catalog data relative to the start
          of the file.
      chunk_header (tracev3_chunk_header): the chunk header of the catalog.

    Raises:
      ParseError: if the chunk header cannot be read.
    """
    chunk_data = file_object.read(chunk_header.chunk_data_size)

    # TODO: use chunk_data or remove
    _ = chunk_data

    data_type_map = self._GetDataTypeMap('tracev3_catalog')

    catalog, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'Catalog')

    if self._debug:
      self._DebugPrintStructureObject(catalog, self._DEBUG_INFO_CATALOG)

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
          uncompressed_data, data_offset, data_type_map, 'chunk header')
      data_offset += 16

      if self._debug:
        self._DebugPrintStructureObject(
            chunkset_chunk_header, self._DEBUG_INFO_CHUNK_HEADER)

      if self._debug:
        self._DebugPrintData('Chunk data', uncompressed_data[
            data_offset:data_offset + chunkset_chunk_header.chunk_data_size])

      data_offset += chunkset_chunk_header.chunk_data_size

      _, alignment = divmod(data_offset, 8)
      if alignment > 0:
        alignment = 8 - alignment

      data_offset += alignment

  def ReadFileObject(self, file_object):
    """Reads a timezone information file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_offset = 0

    while file_offset < self._file_size:
      chunk_header = self._ReadChunkHeader(file_object, file_offset)
      file_offset += 16

      if chunk_header.chunk_tag == 0x600b:
        self._ReadCatalog(file_object, file_offset, chunk_header)

      elif chunk_header.chunk_tag == 0x600d:
        self._ReadChunkSet(file_object, file_offset, chunk_header)

      file_offset += chunk_header.chunk_data_size

      _, alignment = divmod(file_offset, 8)
      if alignment > 0:
        alignment = 8 - alignment

      file_offset += alignment


class UUIDTextFile(data_format.BinaryDataFile):
  """Apple Unified Logging and Activity Tracing (uuidtext) file."""

  _DEFINITION_FILE = 'unified_logging.yaml'

  _DEBUG_INFO_FILE_FOOTER = [
      ('library_path', 'Library path', '_FormatString')]

  _DEBUG_INFO_FILE_HEADER = [
      ('signature', 'Signature', '_FormatIntegerAsHexadecimal8'),
      ('major_format_version', 'Major format version',
       '_FormatIntegerAsDecimal'),
      ('minor_format_version', 'Minor format version',
       '_FormatIntegerAsDecimal'),
      ('number_of_entries', 'Number of entries', '_FormatIntegerAsDecimal'),
      ('entry_descriptors', 'Entry descriptors',
       '_FormatArrayOfEntryDescriptors')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a timezone information file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(UUIDTextFile, self).__init__(
        debug=debug, output_writer=output_writer)

  def _FormatArrayOfEntryDescriptors(self, array_of_entry_descriptors):
    """Formats an array of entry descriptors.

    Args:
      array_of_entry_descriptors (list[uuidtext_entry_descriptor]): array of
          entry descriptors.

    Returns:
      str: formatted array of entry descriptors.
    """
    return '{0:s}\n'.format('\n'.join([
        '\t[{0:03d}] offset: 0x{1:08x}, data size: {2:d}'.format(
            entry_index, entry_descriptor.offset, entry_descriptor.data_size)
        for entry_index, entry_descriptor in enumerate(
            array_of_entry_descriptors)]))

  def _ReadFileFooter(self, file_object, file_offset):
    """Reads a file footer.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the file footer relative to the start
          of the file.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    data_type_map = self._GetDataTypeMap('uuidtext_file_footer')

    file_footer, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file footer')

    if self._debug:
      self._DebugPrintStructureObject(
          file_footer, self._DEBUG_INFO_FILE_FOOTER)

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

    if file_header.signature != 0x66778899:
      raise errors.ParseError(
          'Unsupported signature: 0x{0:04x}.'.format(file_header.signature))

    format_version = (
        file_header.major_format_version, file_header.minor_format_version)
    if format_version != (2, 1):
      raise errors.ParseError(
          'Unsupported format version: {0:d}.{1:d}.'.format(
              file_header.major_format_version,
              file_header.minor_format_version))

    return file_header

  def ReadFileObject(self, file_object):
    """Reads a timezone information file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_header = self._ReadFileHeader(file_object)

    file_offset = file_object.tell()
    for entry_descriptor in file_header.entry_descriptors:
      file_offset += entry_descriptor.data_size

    self._ReadFileFooter(file_object, file_offset)
