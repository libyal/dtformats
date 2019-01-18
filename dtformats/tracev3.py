# -*- coding: utf-8 -*-
"""Apple Unified Logging and Activity Tracing (tracev3) files."""

from __future__ import unicode_literals

import lz4.block

from dtformats import data_format
from dtformats import errors


class TraceV3File(data_format.BinaryDataFile):
  """Apple Unified Logging and Activity Tracing (tracev3) file."""

  _DEFINITION_FILE = 'tracev3.yaml'

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
    chunkset_data = file_object.read(chunk_header.chunk_data_size)

    data_type_map = self._GetDataTypeMap('tracev3_lz4_block_header')

    lz4_block_header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'LZ4 block header')

    if self._debug:
      self._DebugPrintStructureObject(
          lz4_block_header, self._DEBUG_INFO_LZ4_BLOCK_HEADER)

    end_of_compressed_data_offset = 12 + lz4_block_header.compressed_data_size

    if lz4_block_header.signature == b'bv41':
      uncompressed_data = lz4.block.decompress(
          chunkset_data[12:end_of_compressed_data_offset],
          uncompressed_size=lz4_block_header.uncompressed_data_size)

    elif lz4_block_header.signature == b'bv4-':
      uncompressed_data = chunkset_data[12:end_of_compressed_data_offset]

    else:
      raise errors.ParseError('Unsupported start of compressed data marker')

    end_of_compressed_data_identifier = chunkset_data[
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

      if chunk_header.chunk_tag == 0x600d:
        self._ReadChunkSet(file_object, file_offset, chunk_header)

      file_offset += chunk_header.chunk_data_size

      _, alignment = divmod(file_offset, 8)
      if alignment > 0:
        alignment = 8 - alignment

      file_offset += alignment
