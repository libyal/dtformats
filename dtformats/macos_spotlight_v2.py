# -*- coding: utf-8 -*-
"""macOS Spotlight Database V2 files."""

from __future__ import unicode_literals

import datetime
import zlib

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
    self.inode_mappings = {}

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

  def _ReadVarSizeNum(self, file_object, location):
    """From:
    https://github.com/ydkhatri/spotlight_parser/blob/master/spotlight_parser.py#L421
    """
    file_object.seek(location)
    num = int.from_bytes(file_object.read(1), byteorder='little')

    extra = 0
    use_lower_nibble = True
    if num == 0:
        return num, 1
    elif (num & 0xF0) == 0xF0: # 4 or more
        use_lower_nibble = False
        if (num & 0x0F)==0x0F: extra = 8
        elif (num & 0x0E)==0x0E: extra = 7
        elif (num & 0x0C)==0x0C: extra = 6
        elif (num & 0x08)==0x08: extra = 5
        else:
            extra = 4
            use_lower_nibble = True
            num -= 0xF0
    elif (num & 0xE0) == 0xE0:
        extra = 3
        num -= 0xE0
    elif (num & 0xC0) == 0xC0:
        extra = 2
        num -=0xC0
    elif (num & 0x80) == 0x80:
        extra = 1
        num -= 0x80

    if extra:
        num2 = 0
        for x in range(1, extra + 1):
            num_x = int.from_bytes(file_object.read(1), byteorder='big')
            num2 += (num_x << (extra - x)*8)
        if use_lower_nibble:
            num2 = num2 + ((num) << (extra*8))
        return num2, extra + 1
    return num, extra + 1

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
    value = 0
    bytes_read = 0
    file_object.seek(location)
    shift = 1

    while True:
      full_byte = int.from_bytes(file_object.read(1), byteorder='little')
      print(full_byte)
      bytes_read += 1
      value += (full_byte & 0x7F) * shift
      if (full_byte & 0x80) == 0: # If prefix is 1, not the last byte
        break

      shift << 7
      value += shift

    return value, bytes_read


  def _ReadIndexBlock(self, file_object, location, dictionary):
    """Reads in an index block from a location and extracts it's data.
    Args:
      file_object (file): file-like object.
      location (int): file location to read from.
      dictionary (dict) : the dict to store the values in. Only used for index
        blocks

    Raises:
      ParseError: if the file header cannot be read.
    """

    prefix = self._ReadBlockPrefix(file_object, location)
    data_type_map = self._GetDataTypeMap('macos_spotlight_v2_index_entry')

    end_position = location + prefix.logical_size
    location += self._BLOCK_PREFIX_SIZE

    while location < end_position:
      index_block, size = self._ReadStructureFromFileObject(file_object, location,
          data_type_map, 'index block entry')
      location += size

      data_size, byte_offset = self._ReadVarSizeNum(
          file_object, location)
      location += byte_offset

      location += data_size % 4

      data_size = 4 * int(data_size/4)
      data_byte_count = int(data_size/4)

      index_size = 0
      id_tuple = ()
      for id_index in range(0, data_byte_count):
        i, size = self._ReadStructureFromFileObject(file_object, location,
            data_type_map, 'uint32')
        location += size
        index_size += size

        id_tuple = id_tuple + (i.index,)

      dictionary[id] = id_tuple

  def _DecompressMetadataLZ4(self, file_object, location):
    """Decompresses the data from a metadata block.

    Args:
      file_object (file): file-like object.
      location (int): file location where the block starts.

    Raises:
      ParseError: if the data cannot be uncompressed.

    Returns:
      uncompressed (bytestream): uncompressed data.
    """

    # TODO: implement lz4 decompression method

  def _ParseMetadataItem(self, data, size):
    """Parses a single metadata item and stores its data.

    Args:
      data (bytestream): the raw metadata item data.
      size (int): the size of the data.
    """

    # TODO: implement metadata item parsing

  def _ReadMetadataBlock(self, file_object, location):
    """Reads in a metadatablock from a location and extracts it's data.

    Args:
      file_object (file): file-like object.
      location (int): file location to read from.
      dictionary (dict) : the dict to store the values in. Only used for index
        blocks

    Raises:
      ParseError: if the file header cannot be read.
    """

    data_type_map = self._GetDataTypeMap('macos_spotlight_v2_metadata_block')
    block, size = self._ReadStructureFromFileObject(file_object, location,
        data_type_map, 'metadata block')
    if block.block_type != self._BLOCK_TYPES['metadata']:
      errors.ParseError('Not a metadata block')

    # Check for LZ4 compression
    if block.block_type & 0x1000 == 0x1000:
      uncompressed = self._DecompressMetadataLZ4(file_object, location)
    # Else it's zlib compressed
    else:
      uncompressed = zlib.decompress(block.compressed_data)

    items_in_block = []
    position = 0
    count = 0
    data_size = len(uncompressed)
    while position < data_size:
      data_type_map = self._GetDataTypeMap('macos_spotlight_v2_metadata_item')
      item, size = self._ReadStructureFromByteStream(uncompressed, position,
          data_type_map, 'metadata item')
      position += size
      self._ParseMetadataItem(item, size)


  def _ReadBlockData(self, file_object, location, block_type, dictionary=None):
    """Checks a block's type and passes parsing to the relevant method.

    Args:
      file_bject (file): file-like object.
      location (int): file location to read from.
      dictionary (dict) : the dict to store the values in. Only used for index
        blocks

    Raises:
      ParseError: if the file header cannot be read.
    """
    if block_type == self._BLOCK_TYPES['category']:
      self._ReadCategoryBlock(file_object, location)
    elif block_type == self._BLOCK_TYPES['property']:
      self._ReadPropertyBlock(file_object, location)
    elif block_type == self._BLOCK_TYPES['index']:
      self._ReadIndexBlock(file_object, location, dictionary)
    else:
      raise errors.ParseError('Invalid block type: {}'.format(block_type))

  def _ReadBlocks(self, file_object, location, dictionary=None):
    """Parses a block and all it's subsequent blocks.

    Args:
      file_object (file): file-like object.
      location (int): file location to read from.
      dictionary (dict) : the dict to store the values in. Only used for index
        blocks

    Raises:
      ParseError: if the file header cannot be read.
    """

    prefix = self._ReadBlockPrefix(file_object, location)
    self._ReadBlockData(file_object, location, prefix.block_type, dictionary)
    while prefix.next_block != 0:
      location = prefix.next_block * self._BLOCK_INDEX_MULTIPLIER
      prefix = self._ReadBlockPrefix(file_object, location)
      self._ReadBlockData(file_object, location, prefix.block_type, dictionary)

  def ReadFileObject(self, file_object):
    """Reads a Safari Cookies (Cookies.binarycookies) file-like object.

    Args:
      file_object (file): file-like object.
    """

    self._ReadFileHeader(file_object)
    self._ReadBlock0(file_object)
    # self._ReadBlocks(file_object, self.category_block_location * self._BLOCK_INDEX_MULTIPLIER)
    # self._ReadBlocks(file_object, self.property_block_location * self._BLOCK_INDEX_MULTIPLIER)
    # self._ReadBlocks(file_object, self.index_1_block_location * self._BLOCK_INDEX_MULTIPLIER, self.indexes_1)
    # self._ReadBlocks(file_object, self.index_2_block_location * self._BLOCK_INDEX_MULTIPLIER, self.indexes_2)
    self._ReadMetadataBlock(file_object, self.block0_indexes[0].offset_index * self._BLOCK_INDEX_MULTIPLIER)


