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
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('gzipfile.yaml')

  _GZIP_SIGNATURE = 0x8b1f

  _COMPRESSION_METHOD_DEFLATE = 8

  _FLAG_FTEXT = 0x01
  _FLAG_FHCRC = 0x02
  _FLAG_FEXTRA = 0x04
  _FLAG_FNAME = 0x08
  _FLAG_FCOMMENT = 0x10

  _BUFFER_SIZE = 16 * 1024 * 1024

  _DEBUG_INFO_MEMBER_FOOTER = [
      ('checksum', 'Checksum', '_FormatIntegerAsHexadecimal8'),
      ('uncompressed_data_size', 'Uncompressed data size',
       '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_MEMBER_HEADER = [
      ('signature', 'Signature', '_FormatIntegerAsHexadecimal4'),
      ('compression_method', 'Compression method', '_FormatStreamAsDecimal'),
      ('flags', 'Flags', '_FormatIntegerAsHexadecimal2'),
      ('modification_time', 'Modification time', '_FormatIntegerAsPosixTime'),
      ('operating_system', 'Operating system', '_FormatStreamAsDecimal'),
      ('compression_flags', 'Compression flags',
       '_FormatIntegerAsHexadecimal2')]

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
      self._DebugPrintStructureObject(
          member_footer, self._DEBUG_INFO_MEMBER_FOOTER)

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
      self._DebugPrintStructureObject(
          member_header, self._DEBUG_INFO_MEMBER_HEADER)

    if member_header.signature != self._GZIP_SIGNATURE:
      raise errors.ParseError(
          'Unsupported signature: 0x{0:04x}.'.format(member_header.signature))

    if member_header.compression_method != self._COMPRESSION_METHOD_DEFLATE:
      raise errors.ParseError(
          'Unsupported compression method: {0:d}.'.format(
              member_header.compression_method))

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
