# -*- coding: utf-8 -*-
"""macOS Spotlight Database V2 files."""

from __future__ import unicode_literals

import datetime

from dtfabric.runtime import data_maps as dtfabric_data_maps

from dtformats import data_format
from dtformats import errors

class MacOSSpotlightDatabaseV2File(data_format.BinaryDataFile):
  """macOS Spotlight Database V2 file."""

  _DEFINITION_FILE = 'macos_spotlight_v2.yaml'

  _FILE_SIGNATURE = b'8tsd'
  _BLOCK_SIGNATURE = b'2pbd'
  _BLOCK_0_SIGNATURE = b'2mbd'

  _BLOCK_INDEX_MULTIPLIER = 0x1000

  def __init__(self, debug=False, output_writer=None):
    """Initializes a macOS Spotlight Database V2 file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(MacOSSpotlightDatabaseV2File, self).__init__(
        debug=debug, output_writer=output_writer)

    # Data gathered from header
    self.header_size = None
    self.block_0_size = None
    self.block_size = None
    self.property_block_location = None
    self.category_block_location = None
    self.unknown_block_location = None # unused for now
    self.index_1_block_location = None
    self.index_2_block_location = None
    self.original_filename = None

    # Data gathered from blocks
    self.block0_indexes = None

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """

    data_type_map = self._GetDataTypeMap('macos_spotlight_v2_file_header')
    header, size = self._ReadStructureFromFileObject(file_object, 0,
        data_type_map, 'file header')

    if header.signature != self._FILE_SIGNATURE:
      raise errors.ParseError('Unsupported file signature')

    self.header_size = header.header_size
    self.block_0_size = header.block_0_size
    self.block_size = header.block_size
    self.property_block_location = header.property_block_location
    self.category_block_location = header.category_block_location
    self.unknown_block_location = header.unknown_block_location
    self.index_1_block_location = header.index_1_block_location
    self.index_2_block_location = header.index_2_block_location
    self.original_filename = header.original_filename

    return header

  def _ReadBlock0(self, file_object):
    """Reads block 0, which contains the locations of the metadata blocks.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """

    data_type_map = self._GetDataTypeMap('macos_spotlight_v2_block0')
    index = self.header_size # Block 0 starts after the header

    block0, size = self._ReadStructureFromFileObject(file_object, index,
        data_type_map, 'block 0')

    if block0.signature != self._BLOCK_0_SIGNATURE:
      raise errors.ParseError('Unsupported block 0 signature')

    if block0.item_count != len(block0.metadata_block_indexes):
      raise errors.ParseError('Block 0 item count does not match items parsed')

    self.block0_indexes = block0.metadata_block_indexes

  def _ReadCategoryBlock(self, file_object, location):
    """Reads in a category block from a location and populates data from it.

    Args:
      file_object (file): file-like object.
      location (int): file location to read from.

    Raises:
      ParseError: if the file header cannot be read.
    """

    data_type_map = self._GetDataTypeMap('macos_spotlight_v2_category_block')

    block, size = self._ReadStructureFromFileObject(file_object, location,
        data_type_map, 'category block')



  def ReadFileObject(self, file_object):
    """Reads a Safari Cookies (Cookies.binarycookies) file-like object.

    Args:
      file_object (file): file-like object.
    """

    self._ReadFileHeader(file_object)
    self._ReadBlock0(file_object)
    self._ReadCategoryBlock(file_object, self.category_block_location * self._BLOCK_INDEX_MULTIPLIER)



