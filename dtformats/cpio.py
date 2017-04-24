# -*- coding: utf-8 -*-
"""Copy in and out (CPIO) archive format files."""

from __future__ import print_function
import os

from dtfabric import errors as dtfabric_errors
from dtfabric import fabric as dtfabric_fabric

import data_format
import errors


class DataRange(object):
  """In-file data range file-like object."""

  def __init__(self, file_object):
    """Initializes a file-like object.

    Args:
      file_object (file): parent file-like object.
    """
    super(DataRange, self).__init__()
    self._current_offset = 0
    self._file_object = file_object
    self._range_offset = 0
    self._range_size = 0

  def SetRange(self, range_offset, range_size):
    """Sets the data range (offset and size).

    The data range is used to map a range of data within one file
    (e.g. a single partition within a full disk image) as a file-like object.

    Args:
      range_offset (int): start offset of the data range.
      range_size (int): size of the data range.

    Raises:
      ValueError: if the range offset or range size is invalid.
    """
    if range_offset < 0:
      raise ValueError(
          u'Invalid range offset: {0:d} value out of bounds.'.format(
              range_offset))

    if range_size < 0:
      raise ValueError(
          u'Invalid range size: {0:d} value out of bounds.'.format(
              range_size))

    self._range_offset = range_offset
    self._range_size = range_size
    self._current_offset = 0

    # TODO: test upper bound of range_size?

  # The following methods are part of the file-like object interface.

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      size (Optional[int]): number of bytes to read, where None represents
          all remaining data.

    Returns:
      bytes: data read.

    Raises:
      IOError: if the read failed.
    """
    if self._current_offset >= self._range_size:
      return b''

    if size is None:
      size = self._range_size
    if self._current_offset + size > self._range_size:
      size = self._range_size - self._current_offset

    self._file_object.seek(
        self._range_offset + self._current_offset, os.SEEK_SET)

    data = self._file_object.read(size)

    self._current_offset += len(data)

    return data

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset (int): offset to seek.
      whence (Optional[int]): indicates whether offset is an absolute
          or relative position within the file.

    Raises:
      IOError: if the seek failed.
    """
    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._range_size
    elif whence != os.SEEK_SET:
      raise IOError(u'Unsupported whence.')

    if offset < 0:
      raise IOError(u'Invalid offset value less than zero.')

    self._current_offset = offset

  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: offset.
    """
    return self._current_offset

  # Pythonesque alias for get_offset().
  def tell(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: offset.
    """
    return self.get_offset()

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size.
    """
    return self._range_size

  def seekable(self):
    """Determines if a file-like object is seekable.

    Returns:
      bool: True if seekable.
    """
    return True


class CPIOArchiveFileEntry(object):
  """CPIO archive file entry."""

  def __init__(self, file_object):
    """Initializes the CPIO archive file entry object.

    Args:
      file_object (file): file-like object of the CPIO archive file.
    """
    super(CPIOArchiveFileEntry, self).__init__()
    self._current_offset = 0
    self._file_object = file_object

    self.data_offset = None
    self.data_size = None
    self.group_identifier = None
    self.inode_number = None
    self.mode = None
    self.modification_time = None
    self.path = None
    self.size = None
    self.user_identifier = None

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      size (Optional[int]): number of bytes to read, where None represents
          all remaining data.

    Returns:
      bytes: data read.

    Raises:
      IOError: if the read failed.
    """
    if self._current_offset >= self.data_size:
      return b''

    read_size = self.data_size - self._current_offset
    if read_size > size:
      read_size = size

    file_offset = self.data_offset + self._current_offset
    self._file_object.seek(file_offset, os.SEEK_SET)
    data = self._file_object.read(read_size)
    self._current_offset += len(data)
    return data

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset (int): offset to seek.
      whence (Optional[int]): indicates whether offset is an absolute
          or relative position within the file.

    Raises:
      IOError: if the seek failed.
    """
    if whence == os.SEEK_CUR:
      self._current_offset += offset

    elif whence == os.SEEK_END:
      self._current_offset = self.data_size + offset

    elif whence == os.SEEK_SET:
      self._current_offset = offset

    else:
      raise IOError(u'Unsupported whence.')

  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: offset.
    """
    return self._current_offset

  # Pythonesque alias for get_offset().
  def tell(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: offset.
    """
    return self.get_offset()

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size.
    """
    return self.data_size


class CPIOArchiveFile(data_format.BinaryDataFile):
  """CPIO archive file.

  Attributes:
    file_format (str): CPIO file format.
    size (int): size of the CPIO file data.
  """

  _DATA_TYPE_FABRIC_DEFINITION = b'\n'.join([
      b'name: byte',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 1',
      b'  units: bytes',
      b'---',
      b'name: uint16',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 2',
      b'  units: bytes',
      b'---',
      b'name: cpio_binary_big_endian_file_entry',
      b'type: structure',
      b'description: big-endian CPIO file entry',
      b'attributes:',
      b'  byte_order: big-endian',
      b'members:',
      b'- name: signature',
      b'  data_type: uint16',
      b'- name: device_number',
      b'  data_type: uint16',
      b'- name: inode_number',
      b'  data_type: uint16',
      b'- name: mode',
      b'  data_type: uint16',
      b'- name: user_identifier',
      b'  data_type: uint16',
      b'- name: group_identifier',
      b'  data_type: uint16',
      b'- name: number_of_links',
      b'  data_type: uint16',
      b'- name: special_device_number',
      b'  data_type: uint16',
      b'- name: modification_time_upper',
      b'  data_type: uint16',
      b'- name: modification_time_lower',
      b'  data_type: uint16',
      b'- name: path_string_size',
      b'  data_type: uint16',
      b'- name: file_size_upper',
      b'  data_type: uint16',
      b'- name: file_size_lower',
      b'  data_type: uint16',
      b'---',
      b'name: cpio_binary_little_endian_file_entry',
      b'type: structure',
      b'description: little-endian CPIO file entry',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: signature',
      b'  data_type: uint16',
      b'- name: device_number',
      b'  data_type: uint16',
      b'- name: inode_number',
      b'  data_type: uint16',
      b'- name: mode',
      b'  data_type: uint16',
      b'- name: user_identifier',
      b'  data_type: uint16',
      b'- name: group_identifier',
      b'  data_type: uint16',
      b'- name: number_of_links',
      b'  data_type: uint16',
      b'- name: special_device_number',
      b'  data_type: uint16',
      b'- name: modification_time_upper',
      b'  data_type: uint16',
      b'- name: modification_time_lower',
      b'  data_type: uint16',
      b'- name: path_string_size',
      b'  data_type: uint16',
      b'- name: file_size_upper',
      b'  data_type: uint16',
      b'- name: file_size_lower',
      b'  data_type: uint16',
      b'---',
      b'name: cpio_portable_ascii_file_entry',
      b'type: structure',
      b'description: portable ASCII CPIO file entry',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: signature',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 6',
      b'- name: device_number',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 6',
      b'- name: inode_number',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 6',
      b'- name: mode',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 6',
      b'- name: user_identifier',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 6',
      b'- name: group_identifier',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 6',
      b'- name: number_of_links',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 6',
      b'- name: special_device_number',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 6',
      b'- name: modification_time',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 11',
      b'- name: path_string_size',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 6',
      b'- name: file_size',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 11',
      b'---',
      b'name: cpio_new_ascii_file_entry',
      b'type: structure',
      b'description: new ASCII CPIO file entry',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: signature',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 6',
      b'- name: inode_number',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: mode',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: user_identifier',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: group_identifier',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: number_of_links',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: modification_time',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: file_size',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: device_major_number',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: device_minor_number',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: special_device_major_number',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: special_device_minor_number',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: path_string_size',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
      b'- name: checksum',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  number_of_elements: 8',
  ])

  # TODO: move split uint32 into structure.
  # TODO: move path into structure.

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _CPIO_BINARY_BIG_ENDIAN_FILE_ENTRY = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'cpio_binary_big_endian_file_entry')

  _CPIO_BINARY_BIG_ENDIAN_FILE_ENTRY_SIZE = (
      _CPIO_BINARY_BIG_ENDIAN_FILE_ENTRY.GetByteSize())

  _CPIO_BINARY_LITTLE_ENDIAN_FILE_ENTRY = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'cpio_binary_little_endian_file_entry')

  _CPIO_BINARY_LITTLE_ENDIAN_FILE_ENTRY_SIZE = (
      _CPIO_BINARY_LITTLE_ENDIAN_FILE_ENTRY.GetByteSize())

  _CPIO_PORTABLE_ASCII_FILE_ENTRY = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'cpio_portable_ascii_file_entry')

  _CPIO_PORTABLE_ASCII_FILE_ENTRY_SIZE = (
      _CPIO_PORTABLE_ASCII_FILE_ENTRY.GetByteSize())

  _CPIO_NEW_ASCII_FILE_ENTRY = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'cpio_new_ascii_file_entry')

  _CPIO_NEW_ASCII_FILE_ENTRY_SIZE = _CPIO_NEW_ASCII_FILE_ENTRY.GetByteSize()

  _CPIO_SIGNATURE_BINARY_BIG_ENDIAN = b'\x71\xc7'
  _CPIO_SIGNATURE_BINARY_LITTLE_ENDIAN = b'\xc7\x71'
  _CPIO_SIGNATURE_PORTABLE_ASCII = b'070707'
  _CPIO_SIGNATURE_NEW_ASCII = b'070701'
  _CPIO_SIGNATURE_NEW_ASCII_WITH_CHECKSUM = b'070702'

  def __init__(self, debug=False, output_writer=None):
    """Initializes a CPIO archive file object.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(CPIOArchiveFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._file_entries = None

    self.file_format = None
    self.size = None

  def _DebugPrintFileEntry(self, file_entry):
    """Prints file entry debug information.

    Args:
      file_entry (cpio_new_file_entry): entry.
    """
    if self.file_format in (u'bin-big-endian', u'bin-little-endian'):
      value_string = u'0x{0:04x}'.format(file_entry.signature)
    else:
      value_string = u'{0!s}'.format(file_entry.signature)

    self._DebugPrintValue(u'Signature', value_string)

    if self.file_format not in (u'crc', u'newc'):
      value_string = u'{0:d}'.format(file_entry.device_number)
      self._DebugPrintValue(u'Device number', value_string)

    value_string = u'{0:d}'.format(file_entry.inode_number)
    self._DebugPrintValue(u'Inode number', value_string)

    value_string = u'{0:o}'.format(file_entry.mode)
    self._DebugPrintValue(u'Mode', value_string)

    value_string = u'{0:d}'.format(file_entry.user_identifier)
    self._DebugPrintValue(u'User identifier (UID)', value_string)

    value_string = u'{0:d}'.format(file_entry.group_identifier)
    self._DebugPrintValue(u'Group identifier (GID)', value_string)

    value_string = u'{0:d}'.format(file_entry.number_of_links)
    self._DebugPrintValue(u'Number of links', value_string)

    if self.file_format not in (u'crc', u'newc'):
      value_string = u'{0:d}'.format(file_entry.special_device_number)
      self._DebugPrintValue(u'Special device number', value_string)

    value_string = u'{0:d}'.format(file_entry.modification_time)
    self._DebugPrintValue(u'Modification time', value_string)

    if self.file_format not in (u'crc', u'newc'):
      value_string = u'{0:d}'.format(file_entry.path_string_size)
      self._DebugPrintValue(u'Path string size', value_string)

    value_string = u'{0:d}'.format(file_entry.file_size)
    self._DebugPrintValue(u'File size', value_string)

    if self.file_format in (u'crc', u'newc'):
      value_string = u'{0:d}'.format(file_entry.device_major_number)
      self._DebugPrintValue(u'Device major number', value_string)

      value_string = u'{0:d}'.format(file_entry.device_minor_number)
      self._DebugPrintValue(u'Device minor number', value_string)

      value_string = u'{0:d}'.format(file_entry.special_device_major_number)
      self._DebugPrintValue(u'Special device major number', value_string)

      value_string = u'{0:d}'.format(file_entry.special_device_minor_number)
      self._DebugPrintValue(u'Special device minor number', value_string)

      value_string = u'{0:d}'.format(file_entry.path_string_size)
      self._DebugPrintValue(u'Path string size', value_string)

      value_string = u'0x{0:08x}'.format(file_entry.checksum)
      self._DebugPrintValue(u'Checksum', value_string)

  def _ReadFileEntry(self, file_object, file_offset):
    """Reads a file entry.

    Args:
      file_object (file): file-like object.
      file_offset (int): current file offset.

    Raises:
      ParseError: if the file entry cannot be read.
    """
    if self._debug:
      print(u'Seeking file entry at offset: 0x{0:08x}'.format(file_offset))

    file_object.seek(file_offset, os.SEEK_SET)

    if self.file_format == u'bin-big-endian':
      data_type_map = self._CPIO_BINARY_BIG_ENDIAN_FILE_ENTRY
      file_entry_data_size = self._CPIO_BINARY_BIG_ENDIAN_FILE_ENTRY_SIZE
    elif self.file_format == u'bin-little-endian':
      data_type_map = self._CPIO_BINARY_LITTLE_ENDIAN_FILE_ENTRY
      file_entry_data_size = self._CPIO_BINARY_LITTLE_ENDIAN_FILE_ENTRY_SIZE
    elif self.file_format == u'odc':
      data_type_map = self._CPIO_PORTABLE_ASCII_FILE_ENTRY
      file_entry_data_size = self._CPIO_PORTABLE_ASCII_FILE_ENTRY_SIZE
    elif self.file_format in (u'crc', u'newc'):
      data_type_map = self._CPIO_NEW_ASCII_FILE_ENTRY
      file_entry_data_size = self._CPIO_NEW_ASCII_FILE_ENTRY_SIZE

    file_entry_data = file_object.read(file_entry_data_size)
    file_offset += file_entry_data_size

    if self._debug:
      self._DebugPrintData(u'File entry data', file_entry_data)

    try:
      file_entry = data_type_map.MapByteStream(file_entry_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          u'Unable to parse file entry data section with error: '
          u'{0:s}').file_format(exception))

    if self.file_format in (u'bin-big-endian', u'bin-little-endian'):
      file_entry.modification_time = (
          (file_entry.modification_time_upper << 16) |
          file_entry.modification_time_lower)

      file_entry.file_size = (
          (file_entry.file_size_upper << 16) | file_entry.file_size_lower)

    if self.file_format == u'odc':
      for attribute_name in (
          u'device_number', u'inode_number', u'mode', u'user_identifier',
          u'group_identifier', u'number_of_links', u'special_device_number',
          u'modification_time', u'path_string_size', u'file_size'):

        value = getattr(file_entry, attribute_name, None)
        try:
          value = int(value, 8)
        except ValueError:
          raise errors.ParseError(
              u'Unable to convert attribute: {0:s} into an integer'.format(
                  attribute_name))

        value = setattr(file_entry, attribute_name, value)

    elif self.file_format in (u'crc', u'newc'):
      for attribute_name in (
          u'inode_number', u'mode', u'user_identifier', u'group_identifier',
          u'number_of_links', u'modification_time', u'path_string_size',
          u'file_size', u'device_major_number', u'device_minor_number',
          u'special_device_major_number', u'special_device_minor_number',
          u'checksum'):

        value = getattr(file_entry, attribute_name, None)
        try:
          value = int(value, 16)
        except ValueError:
          raise errors.ParseError(
              u'Unable to convert attribute: {0:s} into an integer'.format(
                  attribute_name))

        value = setattr(file_entry, attribute_name, value)

    if self._debug:
      self._DebugPrintFileEntry(file_entry)

    path_string_data = file_object.read(file_entry.path_string_size)
    file_offset += file_entry.path_string_size

    # TODO: should this be ASCII?
    path_string = path_string_data.decode(u'ascii')
    path_string, _, _ = path_string.partition(u'\x00')

    if self._debug:
      self._DebugPrintValue(u'Path string', path_string)

    if self.file_format in (u'bin-big-endian', u'bin-little-endian'):
      padding_size = file_offset % 2
      if padding_size > 0:
        padding_size = 2 - padding_size

    elif self.file_format == u'odc':
      padding_size = 0

    elif self.file_format in (u'crc', u'newc'):
      padding_size = file_offset % 4
      if padding_size > 0:
        padding_size = 4 - padding_size

    if self._debug:
      padding_data = file_object.read(padding_size)
      self._DebugPrintData(u'Path string alignment padding', padding_data)

    file_offset += padding_size

    archive_file_entry = CPIOArchiveFileEntry(file_object)

    archive_file_entry.data_offset = file_offset
    archive_file_entry.data_size = file_entry.file_size
    archive_file_entry.group_identifier = file_entry.group_identifier
    archive_file_entry.inode_number = file_entry.inode_number
    archive_file_entry.modification_time = file_entry.modification_time
    archive_file_entry.path = path_string
    archive_file_entry.mode = file_entry.mode
    archive_file_entry.size = (
        file_entry_data_size + file_entry.path_string_size + padding_size +
        file_entry.file_size)
    archive_file_entry.user_identifier = file_entry.user_identifier

    if self.file_format in (u'crc', u'newc'):
      file_offset += file_entry.file_size

      padding_size = file_offset % 4
      if padding_size > 0:
        padding_size = 4 - padding_size

      if self._debug:
        file_object.seek(file_offset, os.SEEK_SET)
        padding_data = file_object.read(padding_size)

        self._DebugPrintData(u'File data alignment padding', padding_data)

      archive_file_entry.size += padding_size

    if self._debug:
      print(u'')

    return archive_file_entry

  def _ReadFileEntries(self, file_object):
    """Reads the file entries from the cpio archive.

    Args:
      file_object (file): file-like object.
    """
    file_offset = 0
    while file_offset < self._file_size or self._file_size == 0:
      file_entry = self._ReadFileEntry(file_object, file_offset)
      file_offset += file_entry.size
      if file_entry.path == u'TRAILER!!!':
        break

      if file_entry.path in self._file_entries:
        continue

      self._file_entries[file_entry.path] = file_entry

    self.size = file_offset

  def Close(self):
    """Closes the CPIO archive file."""
    super(CPIOArchiveFile, self).Close()
    self._file_entries = None

  def FileEntryExistsByPath(self, path):
    """Determines if file entry for a specific path exists.

    Args:
      path (str): path of the file entry.

    Returns:
      bool: True if the file entry exists.
    """
    if self._file_entries is None:
      return False

    return path in self._file_entries

  def GetFileEntries(self, path_prefix=u''):
    """Retrieves the file entries.

    Args:
      path_prefix (Optional[str]): path prefix.

    Yields:
      CPIOArchiveFileEntry: CPIO archive file entry.
    """
    for path, file_entry in iter(self._file_entries.items()):
      if path.startswith(path_prefix):
        yield file_entry

  def GetFileEntryByPath(self, path):
    """Retrieves a file entry for a specific path.

    Args:
      path (str): path of the file entry.

    Returns:
      CPIOArchiveFileEntry: CPIO archive file entry or None.
    """
    if self._file_entries is None:
      return

    return self._file_entries.get(path, None)

  def ReadFileObject(self, file_object):
    """Reads binary data from a file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the format signature is not supported.
    """
    file_object.seek(0, os.SEEK_SET)
    signature_data = file_object.read(6)

    self.file_format = None
    if len(signature_data) > 2:
      if signature_data[:2] == self._CPIO_SIGNATURE_BINARY_BIG_ENDIAN:
        self.file_format = u'bin-big-endian'
      elif signature_data[:2] == self._CPIO_SIGNATURE_BINARY_LITTLE_ENDIAN:
        self.file_format = u'bin-little-endian'
      elif signature_data == self._CPIO_SIGNATURE_PORTABLE_ASCII:
        self.file_format = u'odc'
      elif signature_data == self._CPIO_SIGNATURE_NEW_ASCII:
        self.file_format = u'newc'
      elif signature_data == self._CPIO_SIGNATURE_NEW_ASCII_WITH_CHECKSUM:
        self.file_format = u'crc'

    if self.file_format is None:
      raise errors.ParseError(u'Unsupported CPIO format.')

    self._file_entries = {}

    self._ReadFileEntries(file_object)

    # TODO: print trailing data
