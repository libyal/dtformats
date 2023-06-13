# -*- coding: utf-8 -*-
"""GZip files."""

# Note: do not rename file to gzip.py this can cause the exception:
# AttributeError: 'module' object has no attribute 'GzipFile'
# when using pip.

import os
import zlib

from dtformats import data_format
from dtformats import errors


class GZipFile(data_format.BinaryDataFile):
  """GZip (.gz) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric and dtFormats definition files.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('gzipfile.yaml')

  _DEBUG_INFORMATION = data_format.BinaryDataFile.ReadDebugInformationFile(
      'gzipfile.debug.yaml', custom_format_callbacks={
          'posix_time': '_FormatIntegerAsPosixTime'})

  _GZIP_SIGNATURE = 0x8b1f

  _COMPRESSION_METHOD_DEFLATE = 8

  _FLAG_FTEXT = 0x01
  _FLAG_FHCRC = 0x02
  _FLAG_FEXTRA = 0x04
  _FLAG_FNAME = 0x08
  _FLAG_FCOMMENT = 0x10

  _BUFFER_SIZE = 16 * 1024 * 1024

  def _ReadCompressedData(self, zlib_decompressor, compressed_data):
    """Reads compressed data.

    Args:
      zlib_decompressor (zlib.Decompress): zlib decompressor.
      compressed_data (bytes): compressed data.

    Returns:
      tuple[bytes, bytes]: decompressed data and remaining data.
    """
    data_segments = []
    while compressed_data:
      data = zlib_decompressor.decompress(compressed_data)
      if not data:
        break

      data_segments.append(data)
      compressed_data = getattr(zlib_decompressor, 'unused_data', b'')

    return b''.join(data_segments), compressed_data

  def _ReadMemberCompressedData(self, file_object):
    """Reads a member compressed data.

    Args:
      file_object (file): file-like object.
    """
    zlib_decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
    compressed_data = file_object.read(self._BUFFER_SIZE)
    while compressed_data:
      data, compressed_data = self._ReadCompressedData(
          zlib_decompressor, compressed_data)
      if compressed_data:
        file_object.seek(-len(compressed_data), os.SEEK_CUR)

      if not data:
        break

      compressed_data = file_object.read(self._BUFFER_SIZE)

  def _ReadMemberFooter(self, file_object):
    """Reads a member footer.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the member footer cannot be read.
    """
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('gzip_member_footer')

    member_footer, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'member footer')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('gzip_member_footer', None)
      self._DebugPrintStructureObject(member_footer, debug_info)

  def _ReadMemberHeader(self, file_object):
    """Reads a member header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the member header cannot be read.
    """
    file_offset = file_object.tell()
    data_type_map = self._GetDataTypeMap('gzip_member_header')

    member_header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'member header')

    if self._debug:
      debug_info = self._DEBUG_INFORMATION.get('gzip_member_header', None)
      self._DebugPrintStructureObject(member_header, debug_info)

    if member_header.signature != self._GZIP_SIGNATURE:
      raise errors.ParseError(
          f'Unsupported signature: 0x{member_header.signature:04x}.')

    if member_header.compression_method != self._COMPRESSION_METHOD_DEFLATE:
      raise errors.ParseError((
          f'Unsupported compression method: '
          f'{member_header.compression_method:d}.'))

    if member_header.flags & self._FLAG_FEXTRA:
      file_offset = file_object.tell()
      data_type_map = self._GetDataTypeMap('uint16le')

      extra_field_data_size, _ = self._ReadStructureFromFileObject(
          file_object, file_offset, data_type_map, 'extra field data size')

      file_object.seek(extra_field_data_size, os.SEEK_CUR)

    if member_header.flags & self._FLAG_FNAME:
      file_offset = file_object.tell()
      data_type_map = self._GetDataTypeMap('cstring')

      value_string, _ = self._ReadStructureFromFileObject(
          file_object, file_offset, data_type_map, 'original filename')

      if self._debug:
        self._DebugPrintValue('Original filename', value_string)

    if member_header.flags & self._FLAG_FCOMMENT:
      file_offset = file_object.tell()
      data_type_map = self._GetDataTypeMap('cstring')

      value_string, _ = self._ReadStructureFromFileObject(
          file_object, file_offset, data_type_map, 'comment')

      if self._debug:
        self._DebugPrintValue('Comment', value_string)

    if member_header.flags & self._FLAG_FHCRC:
      file_object.read(2)

  def ReadFileObject(self, file_object):
    """Reads a GZip file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_offset = 0
    while file_offset < self._file_size:
      self._ReadMemberHeader(file_object)
      self._ReadMemberCompressedData(file_object)
      self._ReadMemberFooter(file_object)

      file_offset = file_object.tell()
