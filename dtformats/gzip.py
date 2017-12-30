# -*- coding: utf-8 -*-
"""GZip files."""

from __future__ import unicode_literals

import os
import zlib

import construct

from dtfabric.runtime import fabric as dtfabric_fabric

from dtformats import data_format
from dtformats import errors


class GZipFile(data_format.BinaryDataFile):
  """GZip (.gz) file."""

  _DATA_TYPE_FABRIC_DEFINITION = b"""\
name: int8
type: integer
attributes:
  format: signed
  size: 1
  units: bytes
---
name: int32
type: integer
attributes:
  format: signed
  size: 4
  units: bytes
---
name: uint8
type: integer
attributes:
  format: unsigned
  size: 1
  units: bytes
---
name: uint16
type: integer
attributes:
  format: unsigned
  size: 2
  units: bytes
---
name: uint32
type: integer
attributes:
  format: unsigned
  size: 4
  units: bytes
---
name: gzip_member_header
type: structure
urls: ["http://www.gzip.org/format.txt"]
attributes:
  byte_order: little-endian
members:
- name: signature
  data_type: uint16
- name: compression_method
  data_type: int8
- name: flags
  data_type: uint8
- name: modification_time
  data_type: int32
- name: compression_flags
  data_type: uint8
- name: operating_system
  data_type: uint8
---
name: gzip_member_footer
type: structure
attributes:
  byte_order: little-endian
members:
- name: checksum
  data_type: uint32
- name: uncompressed_data_size
  data_type: uint32
"""

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _MEMBER_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'gzip_member_header')

  _MEMBER_HEADER_SIZE = _MEMBER_HEADER.GetByteSize()

  _MEMBER_FOOTER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'gzip_member_footer')

  _MEMBER_FOOTER_SIZE = _MEMBER_FOOTER.GetByteSize()

  _FLAG_FTEXT = 0x01
  _FLAG_FHCRC = 0x02
  _FLAG_FEXTRA = 0x04
  _FLAG_FNAME = 0x08
  _FLAG_FCOMMENT = 0x10

  _BUFFER_SIZE = 16 * 1024 * 1024

  def _DebugPrintMemberHeader(self, member_header):
    """Prints member header debug information.

    Args:
      member_header (gzip_member_header): member header.
    """
    value_string = '0x{0:04x}'.format(member_header.signature)
    self._DebugPrintValue('Signature', value_string)

    value_string = '{0:d}'.format(member_header.compression_method)
    self._DebugPrintValue('Compression method', value_string)

    value_string = '0x{0:02x}'.format(member_header.flags)
    self._DebugPrintValue('Flags', value_string)

    value_string = '{0:d}'.format(member_header.modification_time)
    self._DebugPrintValue('Modification time', value_string)

    value_string = '{0:d}'.format(member_header.operating_system)
    self._DebugPrintValue('Operating system', value_string)

    value_string = '0x{0:02x}'.format(member_header.compression_flags)
    self._DebugPrintValue('Compression flags', value_string)

    self._DebugPrintText('\n')

  def _DebugPrintMemberFooter(self, member_footer):
    """Prints member footer debug information.

    Args:
      member_footer (gzip_member_footer): member footer.
    """
    value_string = '0x{0:08x}'.format(member_footer.checksum)
    self._DebugPrintValue('Checksum', value_string)

    value_string = '{0:d}'.format(member_footer.uncompressed_data_size)
    self._DebugPrintValue('Uncompressed data size', value_string)

    self._DebugPrintText('\n')

  def _ReadMemberHeader(self, file_object):
    """Reads a member header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the member header cannot be read.
    """
    file_offset = file_object.tell()
    member_header = self._ReadStructure(
        file_object, file_offset, self._MEMBER_HEADER_SIZE,
        self._MEMBER_HEADER, 'member header')

    if self._debug:
      self._DebugPrintMemberHeader(member_header)

    if member_header.signature != 0x8b1f:
      raise errors.ParseError('Unsupported signature')

    if member_header.flags & self._FLAG_FEXTRA:
      extra_field_data_size = construct.ULInt16(
          'extra_field_data_size').parse_stream(file_object)
      file_object.seek(extra_field_data_size, os.SEEK_CUR)

    if member_header.flags & self._FLAG_FNAME:
      # Since encoding is set construct will convert the C string to Unicode.
      # Note that construct 2 does not support the encoding to be a Unicode
      # string.
      struct = construct.CString('original_filename', encoding=b'iso-8859-1')
      struct.parse_stream(file_object)

    if member_header.flags & self._FLAG_FCOMMENT:
      # Since encoding is set construct will convert the C string to Unicode.
      # Note that construct 2 does not support the encoding to be a Unicode
      # string.
      struct = construct.CString('comment', encoding=b'iso-8859-1')
      struct.parse_stream(file_object)

    if member_header.flags & self._FLAG_FHCRC:
      file_object.read(2)

  def _ReadMemberFooter(self, file_object):
    """Reads a member footer.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the member footer cannot be read.
    """
    file_offset = file_object.tell()
    member_footer = self._ReadStructure(
        file_object, file_offset, self._MEMBER_FOOTER_SIZE,
        self._MEMBER_FOOTER, 'member footer')

    if self._debug:
      self._DebugPrintMemberFooter(member_footer)

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
