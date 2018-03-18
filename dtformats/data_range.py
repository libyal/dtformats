# -*- coding: utf-8 -*-
"""Data range file-like object."""

from __future__ import unicode_literals

import os


class DataRange(object):
  """In-file data range file-like object.

  Attributes:
    data_offset (int): offset of the data.
    data_size (int): size of the data.
  """

  def __init__(self, file_object, data_offset=0, data_size=0):
    """Initializes a file-like object.

    Args:
      file_object (file): parent file-like object.
      data_offset (Optional[int]): offset of the data.
      data_size (Optional[int]): size of the data.
    """
    super(DataRange, self).__init__()
    self._current_offset = 0
    self._file_object = file_object

    self.data_offset = data_offset
    self.data_size = data_size

  # The following methods are part of the file-like object interface.
  # pylint: disable=invalid-name

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
    if self.data_offset < 0:
      raise IOError('Invalid data offset: {0:d} value out of bounds.'.format(
          self.data_offset))

    if self.data_size < 0:
      raise IOError('Invalid data size: {0:d} value out of bounds.'.format(
          self.data_size))

    if self._current_offset >= self.data_size:
      return b''

    if size is None:
      size = self.data_size
    if self._current_offset + size > self.data_size:
      size = self.data_size - self._current_offset

    self._file_object.seek(
        self.data_offset + self._current_offset, os.SEEK_SET)

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
    if self.data_size < 0:
      raise IOError('Invalid data size: {0:d} value out of bounds.'.format(
          self.data_size))

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self.data_size
    elif whence != os.SEEK_SET:
      raise IOError('Unsupported whence.')

    if offset < 0:
      raise IOError('Invalid offset value less than zero.')

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
    return self.data_size

  def seekable(self):
    """Determines if a file-like object is seekable.

    Returns:
      bool: True if seekable.
    """
    return True
