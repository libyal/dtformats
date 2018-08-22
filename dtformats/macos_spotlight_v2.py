# -*- coding: utf-8 -*-
"""macOS Spotlight Database V2 files."""

from __future__ import unicode_literals

import datetime

from dtfabric.runtime import data_maps as dtfabric_data_maps

from dtformats import data_format
from dtformats import errors

from enum import Enum

class MacOSSpotlightDatabaseV2File(data_format.BinaryDataFile):
  """macOS Spotlight Database V2 file."""

  _DEFINITION_FILE = 'macos_spotlight_v2.yaml'

  _FILE_SIGNATURE = b'8tsd'
  _BLOCK_SIGNATURE = b'2pbd'
  _BLOCK_0_SIGNATURE = b'2mbd'

  _BLOCK_INDEX_MULTIPLIER = 0x1000
  _BLOCK_PREFIX_SIZE = 32

  _BLOCK_TYPES = {
    'metadata': 0x09,
    'property': 0x11,
    'category': 0x21,
    'unknown': 0x31,
    'index': 0x81
  }

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
    self.categories = {}
    self.properties = {}
    self.indexes_1 = {}
    self.indexes_2 = {}

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

  def _ReadBlockPrefix(self, file_object, location):
    """Reads in and returns the prefix of a standard block

    Args:
      file_object (file): file-like object.
      location (int): offset from which to read.

    Raises:
      ParseError: if the file header cannot be read.

    Returns:
      A block header object containing metadata about the block.
    """

    data_type_map = self._GetDataTypeMap('macos_spotlight_v2_block_prefix')

    block_prefix, size = self._ReadStructureFromFileObject(file_object, location,
        data_type_map, 'block prefix')
    if block_prefix.signature != self._BLOCK_SIGNATURE:
      raise errors.ParseError('Invalid block signature: {}'.format(
          block_prefix.signature))

    return block_prefix

  def _ReadCategoryBlock(self, file_object, location):
    """Reads in a category block from a location and extracts it's data.

    Args:
      file_object (file): file-like object.
      location (int): file location to read from.

    Raises:
      ParseError: if the file header cannot be read.
    """

    prefix = self._ReadBlockPrefix(file_object, location)
    data_type_map = self._GetDataTypeMap('macos_spotlight_v2_category_entry')

    location += self._BLOCK_PREFIX_SIZE
    bytes_read = 0
    while bytes_read < prefix.logical_size - self._BLOCK_PREFIX_SIZE:
      category_mapping, size = self._ReadStructureFromFileObject(file_object,
          location, data_type_map, 'category block entry')
      location += size
      bytes_read += size

      result = self.categories.get(category_mapping.index, None)
      if result != None:
        raise errors.ParseError(
            'Duplicate category at index {}. Existing: {}, New: {}'.format(
                category_mapping.index, result, category_mapping.value))
      self.categories[category_mapping.index] = category_mapping.value

  def _ReadPropertyBlock(self, file_object, location):
    """Reads in a property block from a location and extracts it's data.

    Args:
      file_object (file): file-like object.
      location (int): file location to read from.

    Raises:
      ParseError: if the file header cannot be read.
    """

    prefix = self._ReadBlockPrefix(file_object, location)
    data_type_map = self._GetDataTypeMap('macos_spotlight_v2_property_entry')

    location += self._BLOCK_PREFIX_SIZE
    bytes_read = 0
    while bytes_read < prefix.logical_size - self._BLOCK_PREFIX_SIZE:
      property_mapping, size = self._ReadStructureFromFileObject(file_object,
          location, data_type_map, 'property block entry')
      location += size
      bytes_read += size

      result = self.properties.get(property_mapping.index)
      if result != None:
        raise errors.ParseError(
              'Duplicate property at index {}. Existing name: {} New: {}'.format(
                property_mapping.index, result.value, property_mapping.value))
      self.properties[property_mapping.index] = property_mapping

  def _ReadIndexBlockEntry(self, file_object, location, count):
    """Reads a single entry from an index block and extracts it's data.

    Args:
      file_object (file): file-like object.
      location (int): file location to read from.
      count (int): the number of elements in the entry.

    Raises:
      ParseError: if the file header cannot be read.
    """

    data_type_map = self._GetDataTypeMap('macos_spotlight_v2_index_entry_element')
    bytes_read = 0
    for _ in range(0, count):
      element, size = self._ReadStructureFromFileObject(file_object, location,
          data_type_map, 'index block entry element')
      location += size
      bytes_read += size
      print(element.value)

    return bytes_read

  def _ReadVariableLengthQuantity(self, file_object, location):
    """Reads a VLQ and returns the value and number of bytes it takes up.

    Args:
      file_object (file): file-like object.
      location (int): file location to read from.

    Raises:
      ParseError: if the file header cannot be read.

    Returns:
      count: the number.
      bytes_read: the number of bytes this number takes up.
    """
    final_byte = False
    value = 0
    bytes_read = 0

    while not final_byte:
      full_byte = int.from_bytes(file_object.read(1), byteorder='big')
      bytes_read += 1
      final_byte = not (full_byte & 0x80) # If prefix is 1, not the last byte
      new_value = full_byte & 0x7F # Actual value is 7 least significant bits

      value = value << 7
      value = value | new_value

    return value, bytes_read


  def _ReadIndexBlock(self, file_object, location):
    """Reads in an index block from a location and extracts it's data.
    Args:
      file_object (file): file-like object.
      location (int): file location to read from.

    Raises:
      ParseError: if the file header cannot be read.
    """

    prefix = self._ReadBlockPrefix(file_object, location)
    data_type_map = self._GetDataTypeMap('macos_spotlight_v2_index_entry')

    location += self._BLOCK_PREFIX_SIZE
    bytes_read = 0

    for i in range(1, 2):
    # while bytes_read < prefix.logical_size - self._BLOCK_PREFIX_SIZE:
      index_block, size = self._ReadStructureFromFileObject(file_object, location,
          data_type_map, 'index block entry')
      location += size
      bytes_read += size

      data_size, byte_offset = self._ReadVariableLengthQuantity(
          file_object, location)
      location += byte_offset
      bytes_read += byte_offset

      location += data_size % 4
      bytes_read += data_size % 4

      data_byte_count = int(data_size/4)
      uint32_map = self._GetDataTypeMap('uint32')
      id_tuple = ()
      for id_index in range(0, data_byte_count):
        i, size = self._ReadStructureFromFileObject(file_object, location,
            uint32_map, 'uint32')
        location += size
        bytes_read += size

        id_tuple = id_tuple + (i,)

      print(id_tuple)
      print(index_block.index)
      print(data_size)
      print(byte_offset)

      print('-----------=')

  def _ReadBlockData(self, file_object, location, block_type):
    """Checks a block's type and passes parsing to the relevant method.

    Args:
      file_bject (file): file-like object.
      location (int): file location to read from.

    Raises:
      ParseError: if the file header cannot be read.
    """
    if block_type == self._BLOCK_TYPES['category']:
      self._ReadCategoryBlock(file_object, location)
    elif block_type == self._BLOCK_TYPES['property']:
      self._ReadPropertyBlock(file_object, location)
    else:
      raise errors.ParseError('Invalid block type: {}'.format(block_type))

  def _ReadBlocks(self, file_object, location):
    """Parses a block and all it's subsequent blocks.

    Args:
      file_object (file): file-like object.
      location (int): file location to read from.

    Raises:
      ParseError: if the file header cannot be read.
    """

    prefix = self._ReadBlockPrefix(file_object, location)
    self._ReadBlockData(file_object, location, prefix.block_type)
    while prefix.next_block != 0:
      location = prefix.next_block * self._BLOCK_INDEX_MULTIPLIER
      prefix = self._ReadBlockPrefix(file_object, location)
      self._ReadBlockData(file_object, location, prefix.block_type)

  def ReadFileObject(self, file_object):
    """Reads a Safari Cookies (Cookies.binarycookies) file-like object.

    Args:
      file_object (file): file-like object.
    """

    self._ReadFileHeader(file_object)
    self._ReadBlock0(file_object)
    # self._ReadBlocks(file_object, self.category_block_location * self._BLOCK_INDEX_MULTIPLIER)
    # self._ReadBlocks(file_object, self.property_block_location * self._BLOCK_INDEX_MULTIPLIER)
    self._ReadIndexBlock(file_object, self.index_1_block_location * self._BLOCK_INDEX_MULTIPLIER)


