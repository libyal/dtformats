#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse copy in and out (CPIO) archive files."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import bz2
import gzip
import hashlib
import logging
import os
import sys

try:
  import lzma
except ImportError:
  try:
    from backports import lzma
  except ImportError:
    lzma = None

from dtformats import cpio
from dtformats import data_range
from dtformats import output_writers


class CPIOArchiveFileHasher(object):
  """CPIO archive file hasher."""

  _BZIP_SIGNATURE = b'BZ'
  _CPIO_SIGNATURE_BINARY_BIG_ENDIAN = b'\x71\xc7'
  _CPIO_SIGNATURE_BINARY_LITTLE_ENDIAN = b'\xc7\x71'
  _CPIO_SIGNATURE_PORTABLE_ASCII = b'070707'
  _CPIO_SIGNATURE_NEW_ASCII = b'070701'
  _CPIO_SIGNATURE_NEW_ASCII_WITH_CHECKSUM = b'070702'
  _GZIP_SIGNATURE = b'\x1f\x8b'
  _XZ_SIGNATURE = b'\xfd7zXZ\x00'

  def __init__(self, path, debug=False, output_writer=None):
    """Initializes the CPIO archive file hasher object.

    Args:
      path (str): path of the CPIO archive file.
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(CPIOArchiveFileHasher, self).__init__()
    self._debug = debug
    self._output_writer = output_writer
    self._path = path

  def HashFileEntries(self):
    """Hashes the file entries stored in the CPIO archive file."""
    stat_object = os.stat(self._path)

    file_object = open(self._path, 'rb')

    file_offset = 0
    file_size = stat_object.st_size

    # initrd files can consist of an uncompressed and compressed cpio archive.
    # Keeping the functionality in this script for now, but this likely
    # needs to be in a separate initrd hashing script.
    while file_offset < stat_object.st_size:
      file_object.seek(file_offset, os.SEEK_SET)
      signature_data = file_object.read(6)

      file_type = None
      if len(signature_data) > 2:
        if (signature_data[:2] in (
            self._CPIO_SIGNATURE_BINARY_BIG_ENDIAN,
            self._CPIO_SIGNATURE_BINARY_LITTLE_ENDIAN) or
            signature_data in (
                self._CPIO_SIGNATURE_PORTABLE_ASCII,
                self._CPIO_SIGNATURE_NEW_ASCII,
                self._CPIO_SIGNATURE_NEW_ASCII_WITH_CHECKSUM)):
          file_type = 'cpio'
        elif signature_data[:2] == self._GZIP_SIGNATURE:
          file_type = 'gzip'
        elif signature_data[:2] == self._BZIP_SIGNATURE:
          file_type = 'bzip'
        elif signature_data == self._XZ_SIGNATURE:
          file_type = 'xz'

      if not file_type:
        self._output_writer.WriteText(
            'Unsupported file type at offset: 0x{0:08x}.\n'.format(
                file_offset))
        return

      if file_type == 'cpio':
        file_object.seek(file_offset, os.SEEK_SET)
        cpio_file_object = file_object
      elif file_type in ('bzip', 'gzip', 'xz'):
        compressed_data_size = file_size - file_offset
        compressed_data_file_object = data_range.DataRange(
            file_object, data_offset=file_offset,
            data_size=compressed_data_size)

        if file_type == 'bzip':
          cpio_file_object = bz2.BZ2File(compressed_data_file_object)
        elif file_type == 'gzip':
          cpio_file_object = gzip.GzipFile(fileobj=compressed_data_file_object)  # pylint: disable=no-member
        elif file_type == 'xz' and lzma:
          cpio_file_object = lzma.LZMAFile(compressed_data_file_object)

      cpio_archive_file = cpio.CPIOArchiveFile(debug=self._debug)
      cpio_archive_file.ReadFileObject(cpio_file_object)

      for file_entry in sorted(cpio_archive_file.GetFileEntries()):
        if file_entry.data_size == 0:
          continue

        sha256_context = hashlib.sha256()
        file_data = file_entry.read(4096)
        while file_data:
          sha256_context.update(file_data)
          file_data = file_entry.read(4096)

        self._output_writer.WriteText('{0:s}\t{1:s}\n'.format(
            sha256_context.hexdigest(), file_entry.path))

      file_offset += cpio_archive_file.size

      padding_size = file_offset %  16
      if padding_size > 0:
        file_offset += 16 - padding_size

      cpio_archive_file.Close()


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from CPIO archive files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      '--hash', dest='hash', action='store_true', default=False,
      help='calculate the SHA-256 sum of the file entries.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the CPIO archive file.')

  options = argument_parser.parse_args()

  if not options.source:
    print('Source file missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  output_writer = output_writers.StdoutWriter()

  try:
    output_writer.Open()
  except IOError as exception:
    print('Unable to open output writer with error: {0!s}'.format(exception))
    print('')
    return False

  if options.hash:
    cpio_archive_file_hasher = CPIOArchiveFileHasher(
        options.source, debug=options.debug, output_writer=output_writer)

    cpio_archive_file_hasher.HashFileEntries()

  else:
    # TODO: move functionality to CPIOArchiveFileInfo.
    cpio_archive_file = cpio.CPIOArchiveFile(
        debug=options.debug, output_writer=output_writer)
    cpio_archive_file.Open(options.source)

    output_writer.WriteText('CPIO archive information:\n')
    output_writer.WriteText('\tFormat\t\t: {0:s}\n'.format(
        cpio_archive_file.file_format))
    output_writer.WriteText('\tSize\t\t: {0:d} bytes\n'.format(
        cpio_archive_file.size))

    cpio_archive_file.Close()

  output_writer.WriteText('\n')
  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
