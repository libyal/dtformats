# -*- coding: utf-8 -*-
"""Windows AMCache (AMCache.hve) files."""

from __future__ import unicode_literals

import pyregf

from dtformats import data_format
from dtformats import errors


class WindowsAMCacheFile(data_format.BinaryDataFile):
  """Windows AMCache (AMCache.hve) file."""

  _FILE_REFERENCE_KEY_VALUES = {
      '0': 'Product name',
      '1': 'Company name',
      '3': 'Language code',
      '5': 'File version',
      '6': 'File size',
      'c': 'File description',
      'f': 'Linker time',
      '11': 'Modification time',
      '12': 'Creation time',
      '15': 'Path',
      '100': 'Program identifier',
      '101': 'SHA-1'}

  def _GetValueDataAsObject(self, value):
    """Retrieves the value data as an object.

    Args:
      value (pyregf_value): value.

    Returns:
      object: data as a Python type.

    Raises:
      ParseError: if the value data cannot be read.
    """
    try:
      if value.type in (1, 2, 6):
        value_data = value.get_data_as_string()

      elif value.type in (4, 5, 11):
        value_data = value.get_data_as_integer()

      elif value.type == 7:
        value_data = value.get_data_as_multi_string()

      else:
        value_data = value.data

    except (IOError, OverflowError) as exception:
      raise errors.ParseError(
          'Unable to read data from value: {0:s} with error: {1!s}'.format(
              value.name, exception))

    return value_data

  def _ReadFileKey(self, file_key):
    """Reads a File key.

    Args:
      file_key (pyregf_key): File key.
    """
    for volume_key in file_key.sub_keys:
      for file_reference_key in volume_key.sub_keys:
        self._ReadFileReferenceKey(file_reference_key)

  def _ReadFileReferenceKey(self, file_reference_key):
    """Reads a file reference key.

    Args:
      file_reference_key (pyregf_key): file reference key.
    """
    if self._debug:
      sequence_number, mft_entry = file_reference_key.name.split('0000')
      mft_entry = int(mft_entry, 16)
      sequence_number = int(sequence_number, 16)
      self._DebugPrintText('{0:s} ({1:d}-{2:d})\n'.format(
        file_reference_key.name, mft_entry, sequence_number))

    for value in file_reference_key.values:
      description = self._FILE_REFERENCE_KEY_VALUES.get(
          value.name, value.name)
      value_data = self._GetValueDataAsObject(value)

      if self._debug:
        if value.name == 'f':
          self._DebugPrintPosixTimeValue(description, value_data)
        elif value.name in ('11', '12', '17'):
          self._DebugPrintFiletimeValue(description, value_data)
        else:
          self._DebugPrintValue(description, value_data)

    if self._debug:
      self._DebugPrintText('\n')

  def ReadFileObject(self, file_object):
    """Reads a Windows AMCache file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    regf_file = pyregf.file()
    regf_file.open_file_object(file_object)

    root_key = regf_file.get_key_by_path('\\Root')
    if root_key:
      file_key = root_key.get_sub_key_by_path('File')
      if file_key:
        self._ReadFileKey(file_key)
