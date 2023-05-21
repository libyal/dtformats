# -*- coding: utf-8 -*-
"""WMI Common Information Model (CIM) repository files."""

import glob
import hashlib
import logging
import os

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import data_maps as dtfabric_data_maps

from dtformats import data_format
from dtformats import errors
from dtformats import file_system


class ClassDefinitionProperty(object):
  """Class definition property.

  Attributes:
    index (int): index of the property.
    name (str): name of the property.
    qualifiers (dict[str, object]): qualifiers.
    value_data_offset (int): the property value data offset.
    value_data_type (int): the property value data type.
  """

  def __init__(self):
    """Initializes a class property."""
    super(ClassDefinitionProperty, self).__init__()
    self.index = None
    self.name = None
    self.qualifiers = {}
    self.value_data_offset = None
    self.value_data_type = None


class ClassValueDataMap(object):
  """Class value data map.

  Attributes:
    class_name (str): name of the class.
    derivation (list[str]): name of the classes this class is derived from.
    dynasty (str): name of the parent class of the parent clas or None if not
        available.
    properties (dict[str, PropertyValueDataMap]): value data maps of
        the properties.
    properties_size (int): size of the properties in value data.
    super_class_name (str): name of the parent class or None if not available.
  """

  _PROPERTY_TYPE_VALUE_DATA_SIZE = {
      0x00000002: 2,
      0x00000003: 4,
      0x00000004: 4,
      0x00000005: 8,
      0x0000000b: 2,
      0x00000010: 1,
      0x00000011: 1,
      0x00000012: 2,
      0x00000013: 4,
      0x00000014: 8,
      0x00000015: 8}

  def __init__(self):
    """Initializes a class value data map."""
    super(ClassValueDataMap, self).__init__()
    self.class_name = None
    self.derivation = []
    self.dynasty = None
    self.properties = {}
    self.properties_size = 0
    self.super_class_name = None

  def Build(self, class_definitions):
    """Builds the class map from the class definitions.

    Args:
      class_definitions (list[ClassDefinition]): the class definition and its
          parent class definitions.

    Raises:
      ParseError: if the class map cannot be build.
    """
    self.class_name = class_definitions[-1].name
    self.derivation = [
        class_definition.name for class_definition in class_definitions[:-1]]
    self.derivation.reverse()

    derivation_length = len(self.derivation)
    if derivation_length >= 1:
      self.super_class_name = self.derivation[0]
    if derivation_length >= 2:
      self.dynasty = self.derivation[1]

    largest_offset = None
    largest_property_map = None

    for class_definition in class_definitions:
      for name, property_definition in class_definition.properties.items():
        type_qualifier = property_definition.qualifiers.get('type', None)
        if not type_qualifier:
          name_lower = property_definition.name.lower()
          if name_lower in self.properties:
            continue

          raise errors.ParseError((
              f'Missing type qualifier for property: '
              f'{property_definition.name:s} of class: '
              f'{class_definition.name:s}'))

        value_data_size = self._PROPERTY_TYPE_VALUE_DATA_SIZE.get(
            property_definition.value_data_type, 4)

        property_map = PropertyValueDataMap(
            property_definition.name, property_definition.value_data_type,
            property_definition.value_data_offset, value_data_size)

        type_qualifier_lower = type_qualifier.lower()
        if ':' in type_qualifier_lower:
          type_qualifier_lower, _, _ = type_qualifier_lower.partition(':')

        property_map.type_qualifier = type_qualifier_lower

        # TODO: compare property_map against property map of parent classes.
        self.properties[name.lower()] = property_map

        if (largest_offset is None or
            largest_offset < property_definition.value_data_offset):
          largest_offset = property_definition.value_data_offset
          largest_property_map = property_map

    if largest_property_map:
      self.properties_size = (
          largest_property_map.offset + largest_property_map.size)


class IndexBinaryTreePage(object):
  """Index binary-tree page.

  Attributes:
    keys (list[str]): index binary-tree keys.
    number_of_keys (int): number of keys.
    page_key_segments (list[bytes]): page key segments.
    page_type (int): page type.
    page_value_offsets (list[int]): page value offsets.
    page_values (list[bytes]): page values.
    root_page_number (int): root page number.
    sub_pages (list[int]): sub page numbers.
  """

  def __init__(self):
    """Initializes an index binary-tree page."""
    super(IndexBinaryTreePage, self).__init__()
    self.keys = []
    self.number_of_keys = None
    self.page_key_segments = []
    self.page_type = None
    self.page_value_offsets = None
    self.page_values = []
    self.root_page_number = None
    self.sub_pages = []


class MappingTable(object):
  """Mapping table."""

  def __init__(self, mapping_table):
    """Initializes a mapping table.

    Args:
      mapping_table (mapping_table): mapping table.
    """
    super(MappingTable, self).__init__()
    self._mapping_table = mapping_table

  def ResolveMappedPageNumber(self, mapped_page_number):
    """Resolves a mapped page number.

    Args:
      mapped_page_number (int): mapped page number.

    Returns:
      int: (physical) page number.
    """
    mapping_table_entry = self._mapping_table.entries[mapped_page_number]
    return mapping_table_entry.page_number


class ObjectsDataPage(object):
  """An objects data page.

  Attributes:
    page_offset (int): offset of the page relative to the start of the file.
  """

  def __init__(self, page_offset):
    """Initializes an objects data page.

    Args:
      page_offset (int): offset of the page relative to the start of the file.
    """
    super(ObjectsDataPage, self).__init__()
    self._object_descriptors = []

    self.page_offset = page_offset

  def AppendObjectDescriptor(self, object_descriptor):
    """Appends an object descriptor.

    Args:
      object_descriptor (cim_object_descriptor): object descriptor.
    """
    self._object_descriptors.append(object_descriptor)

  def GetObjectDescriptor(self, record_identifier, data_size):
    """Retrieves a specific object descriptor.

    Args:
      record_identifier (int): object record identifier.
      data_size (int): object record data size.

    Returns:
      cim_object_descriptor: an object descriptor or None.
    """
    object_descriptor_match = None
    for object_descriptor in self._object_descriptors:
      if object_descriptor.identifier == record_identifier:
        object_descriptor_match = object_descriptor
        break

    if not object_descriptor_match:
      logging.warning('Object record data not found.')
      return None

    if object_descriptor_match.data_size != data_size:
      logging.warning('Object record data size mismatch.')
      return None

    return object_descriptor_match


class ObjectRecord(object):
  """Object record.

  Attributes:
    data (bytes): object record data.
    data_type (str): object record data type.
    offset (int): offset of the record data.
  """

  def __init__(self, data_type, data, offset=0):
    """Initializes an object record.

    Args:
      data_type (str): object record data type.
      data (bytes): object record data.
      offset (int): offset of the record data.
    """
    super(ObjectRecord, self).__init__()
    self.data = data
    self.data_type = data_type
    self.offset = offset


class PropertyValueDataMap(object):
  """Property value data map.

  Attributes:
    data_type (int): property value data type.
    name (str): name of the property.
    offset (int): offset of the property in value data.
    size (int): size of the property in value data.
    type_qualifier (str): type qualifier of the property.
  """

  def __init__(self, name, data_type, offset, size):
    """Initializes a property value data map.

    Args:
      name (str): name of the property.
      data_type (int): property value data type.
      offset (int): offset of the property in value data.
      size (int): size of the property in value data.
    """
    super(PropertyValueDataMap, self).__init__()
    self.data_type = data_type
    self.name = name
    self.offset = offset
    self.size = size
    self.type_qualifier = None


class IndexBinaryTreeFile(data_format.BinaryDataFile):
  """Index binary-tree (Index.btr) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _PAGE_SIZE = 8192

  _STRING = _FABRIC.CreateDataTypeMap('string')

  _PAGE_TYPES = {
      0xaccc: 'Is active',
      0xaddd: 'Is administrative',
      0xbadd: 'Is deleted',
  }

  _KEY_SEGMENT_SEPARATOR = '\\'

  _DEBUG_INFO_PAGE_HEADER = [
      ('page_type', 'Page type', '_FormatIntegerAsPageType'),
      ('mapped_page_number', 'Mapped page number', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8'),
      ('root_page_number', 'Root page number', '_FormatIntegerAsDecimal')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes an index binary-tree file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(IndexBinaryTreeFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._unavailable_page_numbers = set([0, 0xffffffff])

  def _DebugPrintPageBody(self, page_body):
    """Prints page body debug information.

    Args:
      page_body (cim_page_body): page body.
    """
    self._DebugPrintDecimalValue('Number of keys', page_body.number_of_keys)

    for index, value in enumerate(page_body.unknown2):
      self._DebugPrintDecimalValue(f'Unknown2: {index:d}', value)

    for index, page_number in enumerate(page_body.sub_pages):
      value_string = self._FormatIntegerAsPageNumber(page_number)
      self._DebugPrintValue(
          f'Sub page: {index:d} mapped page number', value_string)

    for index, key_offset in enumerate(page_body.key_offsets):
      value_string = self._FormatIntegerAsOffset(key_offset)
      self._DebugPrintValue(f'Key: {index:d} offset', value_string)

    number_of_bytes = page_body.key_data_size * 2
    self._DebugPrintValue(
        'Key data size',
        f'{page_body.key_data_size:d} ({number_of_bytes:d} bytes)')

    self._DebugPrintData('Key data', page_body.key_data)

    self._DebugPrintDecimalValue(
        'Number of values', page_body.number_of_values)

    for index, offset in enumerate(page_body.value_offsets):
      value_string = self._FormatIntegerAsOffset(offset)
      self._DebugPrintValue(f'Value: {index:d} offset', value_string)

    number_of_bytes = page_body.value_data_size * 2
    self._DebugPrintValue(
        'Value data size',
        f'{page_body.value_data_size:d} ({number_of_bytes:d} bytes)')

    self._DebugPrintData('Value data', page_body.value_data)

  def _FormatIntegerAsPageNumber(self, integer):
    """Formats an integer as a page number.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a page number.
    """
    if integer in self._unavailable_page_numbers:
      return f'0x{integer:08x} (unavailable)'

    return f'{integer:d}'

  def _FormatIntegerAsPageType(self, integer):
    """Formats an integer as a page type.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a page type.
    """
    page_type_string = self._PAGE_TYPES.get(integer, 'Unknown')
    return f'0x{integer:04x} ({page_type_string:s})'

  def _ReadPage(self, file_object, file_offset):
    """Reads a page.

    Args:
      file_object (file): a file-like object.
      file_offset (int): offset of the page relative to the start of the file.

    Return:
      IndexBinaryTreePage: an index binary-tree page.

    Raises:
      ParseError: if the page cannot be read.
    """
    if self._debug:
      page_number = file_offset // self._PAGE_SIZE
      self._DebugPrintText((
          f'Reading page: {page_number:d} at offset: {file_offset:d} '
          f'(0x{file_offset:08x}).\n'))

    page_data = self._ReadData(
        file_object, file_offset, self._PAGE_SIZE, 'index binary-tree page')

    page_header = self._ReadPageHeader(file_offset, page_data[:16])

    file_offset += 16
    page_data_offset = 16

    index_binary_tree_page = IndexBinaryTreePage()
    index_binary_tree_page.page_type = page_header.page_type
    index_binary_tree_page.root_page_number = page_header.root_page_number

    if page_header.page_type == 0xaccc:
      page_body_data = page_data[page_data_offset:]

      data_type_map = self._GetDataTypeMap('cim_page_body')

      context = dtfabric_data_maps.DataTypeMapContext()

      page_body = self._ReadStructureFromByteStream(
          page_body_data, file_offset, data_type_map, 'page body',
          context=context)

      page_data_offset += context.byte_size

      if self._debug:
        self._DebugPrintData(
            'Page body data', page_body_data[:page_data_offset])

      if self._debug:
        self._DebugPrintPageBody(page_body)

    if self._debug:
      trailing_data_size = self._PAGE_SIZE - page_data_offset
      if trailing_data_size > 0:
        self._DebugPrintData('Trailing data', page_data[page_data_offset:])

    if page_header.page_type == 0xaccc:
      index_binary_tree_page.number_of_keys = page_body.number_of_keys

      for page_number in page_body.sub_pages:
        if page_number not in (0, 0xffffffff):
          index_binary_tree_page.sub_pages.append(page_number)

      index_binary_tree_page.page_value_offsets = page_body.value_offsets

      # TODO: return page_key_segments
      self._ReadPageKeyData(index_binary_tree_page, page_body)
      self._ReadPageValueData(index_binary_tree_page, page_body)

      index_binary_tree_page.keys = []
      for page_key_segments in index_binary_tree_page.page_key_segments:
        key_segments = []
        for segment_index in page_key_segments:
          page_value = index_binary_tree_page.page_values[segment_index]
          key_segments.append(page_value)

        key_path = ''.join([
            self._KEY_SEGMENT_SEPARATOR,
            self._KEY_SEGMENT_SEPARATOR.join(key_segments)])

        index_binary_tree_page.keys.append(key_path)

    return index_binary_tree_page

  def _ReadPageHeader(self, file_offset, page_header_data):
    """Reads a page header.

    Args:
      file_offset (int): offset of the page header relative to the start of
          the file.
      page_header (bytes): page header data.

    Returns:
      page_header: page header.

    Raises:
      ParseError: if the name cannot be read.
    """
    if self._debug:
      self._DebugPrintData('Page header data', page_header_data)

    data_type_map = self._GetDataTypeMap('cim_page_header')

    page_header = self._ReadStructureFromByteStream(
        page_header_data, file_offset, data_type_map, 'page header')

    if self._debug:
      self._DebugPrintStructureObject(page_header, self._DEBUG_INFO_PAGE_HEADER)

    return page_header

  def _ReadPageKeyData(self, index_binary_tree_page, page_body):
    """Reads page key data.

    Args:
      index_binary_tree_page (IndexBinaryTreePage): index binary-tree page.
      page_body (cim_page_body): page body.

    Raises:
      ParseError: if the page key data cannot be read.
    """
    key_data = page_body.key_data

    data_type_map = self._GetDataTypeMap('cim_page_key')

    for page_key_index, key_offset in enumerate(page_body.key_offsets):
      page_key_offset = key_offset * 2

      if self._debug:
        value_string = self._FormatIntegerAsOffset(page_key_offset)
        self._DebugPrintValue(
            f'Page key: {page_key_index:d} offset', value_string)

      context = dtfabric_data_maps.DataTypeMapContext()

      page_key = self._ReadStructureFromByteStream(
          key_data[page_key_offset:], page_key_offset, data_type_map,
          f'page key: {page_key_index:d}', context=context)

      if self._debug:
        page_key_end_offset = page_key_offset + context.byte_size
        self._DebugPrintData(
            f'Page key: {page_key_index:d} data:',
            key_data[page_key_offset:page_key_end_offset])

      index_binary_tree_page.page_key_segments.append(page_key.segments)

      if self._debug:
        self._DebugPrintDecimalValue(
            f'Page key: {page_key_index:d} number of segments',
            page_key.number_of_segments)

        value_string = ', '.join([
            f'{segment_index:d}' for segment_index in page_key.segments])
        self._DebugPrintValue(
            f'Page key: {page_key_index:d} segments', value_string)

        self._DebugPrintText('\n')

  def _ReadPageValueData(self, index_binary_tree_page, page_body):
    """Reads page value data.

    Args:
      index_binary_tree_page (IndexBinaryTreePage): index binary-tree page.
      page_body (cim_page_body): page body.

    Raises:
      ParseError: if the page value data cannot be read.
    """
    value_data = page_body.value_data

    for index, page_value_offset in enumerate(
        index_binary_tree_page.page_value_offsets):
      # TODO: determine size

      try:
        value_string = self._STRING.MapByteStream(
            value_data[page_value_offset:])
      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError((
            f'Unable to parse page value: {index:d} string with error: '
            f'{exception!s}'))

      if self._debug:
        self._DebugPrintValue(f'Page value: {index:d} data', value_string)

      index_binary_tree_page.page_values.append(value_string)

    if self._debug and index_binary_tree_page.page_value_offsets:
      self._DebugPrintText('\n')

  def GetPage(self, page_number):
    """Retrieves a specific page.

    Args:
      page_number (int): page number.

    Returns:
      IndexBinaryTreePage: an index binary-tree page or None.
    """
    file_offset = page_number * self._PAGE_SIZE
    if file_offset >= self._file_size:
      return None

    # TODO: cache pages.
    return self._ReadPage(self._file_object, file_offset)

  def ReadFileObject(self, file_object):
    """Reads an index binary-tree file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    if self._debug:
      file_offset = 0
      while file_offset < self._file_size:
        self._ReadPage(file_object, file_offset)
        file_offset += self._PAGE_SIZE


class MappingFile(data_format.BinaryDataFile):
  """Mappings (*.map) file.

  Attributes:
    format_version (int): format version of the mapping file.
    sequence_number (int): sequence number.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _DEBUG_INFO_FILE_FOOTER = [
      ('signature', 'Signature', '_FormatIntegerAsHexadecimal8')]

  _DEBUG_INFO_FILE_HEADER = [
      ('signature', 'Signature', '_FormatIntegerAsHexadecimal8'),
      ('sequence_number', 'Sequence number', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal8'),
      ('number_of_pages', 'Number of pages', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_TABLE_ENTRY = [
      ('page_number', '    Page number', '_FormatIntegerAsPageNumber'),
      ('unknown1', '    Unknown1', '_FormatIntegerAsHexadecimal8'),
      ('unknown2', '    Unknown2', '_FormatIntegerAsHexadecimal8'),
      ('unknown3', '    Unknown3', '_FormatIntegerAsHexadecimal8'),
      ('unknown4', '    Unknown4', '_FormatIntegerAsHexadecimal8'),
      ('unknown5', '    Unknown5', '_FormatIntegerAsHexadecimal8')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a mappings file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(MappingFile, self).__init__(debug=debug, output_writer=output_writer)
    self._mapping_table1 = None
    self._mapping_table2 = None
    self._unavailable_page_numbers = set([0xffffffff])

    self.format_version = None
    self.sequence_number = None

  def _DebugPrintMappingTable(self, mapping_table):
    """Prints a mapping table debug information.

    Args:
      mapping_table (mapping_table): mapping table.
    """
    self._DebugPrintText('Mapping table:\n')
    self._DebugPrintDecimalValue(
        '  Number of entries', mapping_table.number_of_entries)
    self._DebugPrintText('\n')

    for index, mapping_table_entry in enumerate(mapping_table.entries):
      self._DebugPrintText(f'  Entry: {index:d}:\n')
      self._DebugPrintStructureObject(
          mapping_table_entry, self._DEBUG_INFO_TABLE_ENTRY)

    self._DebugPrintText('\n')

  def _DebugPrintUnknownTable(self, unknown_table):
    """Prints a unknown table debug information.

    Args:
      unknown_table (unknown_table): mapping table.
    """
    self._DebugPrintText('Unknown table:\n')
    self._DebugPrintDecimalValue(
        '  Number of entries', unknown_table.number_of_entries)

    for index, page_number in enumerate(unknown_table.entries):
      value_string = self._FormatIntegerAsPageNumber(page_number)
      self._DebugPrintValue(f'  Entry: {index:d} page number', value_string)

    self._DebugPrintText('\n')

  def _FormatIntegerAsPageNumber(self, integer):
    """Formats an integer as a page number.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a page number.
    """
    if integer in self._unavailable_page_numbers:
      return f'0x{integer:08x} (unavailable)'

    return f'{integer:d}'

  def _ReadDetermineFormatVersion(self, file_object):
    """Reads the file footer to determine the format version.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    file_object.seek(0, os.SEEK_SET)

    file_header = self._ReadFileHeader(file_object, format_version=2)

    if file_header.unknown1 == file_header.unknown2 + 1:
      self.format_version = 2
    else:
      self.format_version = 1

  def _ReadFileFooter(self, file_object):
    """Reads the file footer.

    Args:
      file_object (file): file-like object.
      format_version (Optional[int]): format version.

    Returns:
      cim_map_footer: file footer.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    file_offset = file_object.tell()

    data_type_map = self._GetDataTypeMap('cim_map_footer')

    file_footer, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file footer')

    if self._debug:
      self._DebugPrintStructureObject(file_footer, self._DEBUG_INFO_FILE_FOOTER)

    return file_footer

  def _ReadFileHeader(self, file_object, format_version=None):
    """Reads the file header.

    Args:
      file_object (file): file-like object.
      format_version (Optional[int]): format version.

    Returns:
      cim_map_header: file header.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()

    if format_version == 1:
      data_type_map = self._GetDataTypeMap('cim_map_header_v1')
    else:
      data_type_map = self._GetDataTypeMap('cim_map_header_v2')

    file_header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file header')

    if self._debug:
      self._DebugPrintStructureObject(file_header, self._DEBUG_INFO_FILE_HEADER)

    return file_header

  def _ReadMappingTable(self, file_object):
    """Reads the mapping tables.

    Args:
      file_object (file): file-like object.

    Returns:
      mapping_table: mapping table.

    Raises:
      ParseError: if the mappings cannot be read.
    """
    file_offset = file_object.tell()

    if self.format_version == 1:
      data_type_map = self._GetDataTypeMap('cim_map_mapping_table_v1')
    else:
      data_type_map = self._GetDataTypeMap('cim_map_mapping_table_v2')

    mapping_table, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'mapping table')

    if self._debug:
      self._DebugPrintMappingTable(mapping_table)

    return mapping_table

  def _ReadUnknownTable(self, file_object):
    """Reads the unknown tables.

    Args:
      file_object (file): file-like object.

    Returns:
      unknown_table: unknown table.

    Raises:
      ParseError: if the unknowns cannot be read.
    """
    file_offset = file_object.tell()

    data_type_map = self._GetDataTypeMap('cim_map_unknown_table')

    unknown_table, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'unknown table')

    if self._debug:
      self._DebugPrintUnknownTable(unknown_table)

    return unknown_table

  def GetIndexMappingTable(self):
    """Retrieves the index mapping table.

    Returns:
      MappingTable: index mapping table.
    """
    return MappingTable(self._mapping_table2 or self._mapping_table1)

  def GetObjectsMappingTable(self):
    """Retrieves the objects mapping table.

    Returns:
      MappingTable: objects mapping table.
    """
    return MappingTable(self._mapping_table1)

  def ReadFileObject(self, file_object):
    """Reads a mappings file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadDetermineFormatVersion(file_object)

    file_object.seek(0, os.SEEK_SET)

    file_header = self._ReadFileHeader(
        file_object, format_version=self.format_version)
    self.sequence_number = file_header.sequence_number

    self._mapping_table1 = self._ReadMappingTable(file_object)

    self._ReadUnknownTable(file_object)
    self._ReadFileFooter(file_object)

    file_offset = file_object.tell()

    if self.format_version == 2 or file_offset < self._file_size:
      try:
        file_header = self._ReadFileHeader(
            file_object, format_version=self.format_version)
      except errors.ParseError:
        file_header = None

      if not file_header and self.format_version == 2:
        raise errors.ParseError('Unable to read second file header.')

      # Seen trailing data in Windows XP objects.map file.
      if file_header:
        self._mapping_table2 = self._ReadMappingTable(file_object)

        self._ReadUnknownTable(file_object)
        self._ReadFileFooter(file_object)


class ObjectsDataFile(data_format.BinaryDataFile):
  """An objects data (Objects.data) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _DEBUG_INFO_OBJECT_DESCRIPTOR = [
      ('identifier', 'Identifier', '_FormatIntegerAsHexadecimal8'),
      ('data_offset', 'Data offset (relative)', '_FormatIntegerAsOffset'),
      ('data_file_offset', 'Data offset (file)', '_FormatIntegerAsOffset'),
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('data_checksum', 'Data checksum', '_FormatIntegerAsHexadecimal8')]

  _EMPTY_OBJECT_DESCRIPTOR = b'\x00' * 16

  _PAGE_SIZE = 8192

  def _ReadObjectDescriptor(self, file_object):
    """Reads an object descriptor.

    Args:
      file_object (file): a file-like object.

    Returns:
      cim_object_descriptor: an object descriptor or None if the object
          descriptor is empty.

    Raises:
      ParseError: if the object descriptor cannot be read.
    """
    file_offset = file_object.tell()

    if self._debug:
      self._DebugPrintText((
          f'Reading object descriptor at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    object_descriptor_data = file_object.read(16)

    if self._debug:
      self._DebugPrintData('Object descriptor data', object_descriptor_data)

    # The last object descriptor (terminator) is filled with 0-byte values.
    if object_descriptor_data == self._EMPTY_OBJECT_DESCRIPTOR:
      return None

    data_type_map = self._GetDataTypeMap('cim_object_descriptor')

    object_descriptor = self._ReadStructureFromByteStream(
        object_descriptor_data, file_offset, data_type_map, 'object descriptor')

    setattr(object_descriptor, 'data_file_offset',
            file_offset + object_descriptor.data_offset)

    if self._debug:
      self._DebugPrintStructureObject(
          object_descriptor, self._DEBUG_INFO_OBJECT_DESCRIPTOR)

    return object_descriptor

  def _ReadObjectDescriptors(self, file_object, objects_page):
    """Reads object descriptors.

    Args:
      file_object (file): a file-like object.
      objects_page (ObjectsDataPage): objects data page.

    Raises:
      ParseError: if the object descriptor cannot be read.
    """
    while True:
      object_descriptor = self._ReadObjectDescriptor(file_object)
      if not object_descriptor:
        break

      objects_page.AppendObjectDescriptor(object_descriptor)

  def _ReadPage(self, file_object, file_offset, is_data_page):
    """Reads a page.

    Args:
      file_object (file): a file-like object.
      file_offset (int): offset of the page relative to the start of the file.
      is_data_page (bool): True if the page is a data page.

    Raises:
      ParseError: if the page cannot be read.

    Returns:
      ObjectsDataPage: objects data page or None.
    """
    file_object.seek(file_offset, os.SEEK_SET)

    if self._debug:
      self._DebugPrintText((
          f'Reading objects data page at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    objects_page = ObjectsDataPage(file_offset)

    if not is_data_page:
      self._ReadObjectDescriptors(file_object, objects_page)

    return objects_page

  def GetPage(self, page_number, is_data_page):
    """Retrieves a specific page.

    Args:
      page_number (int): page number.
      is_data_page (bool): True if the page is a data page.

    Returns:
      ObjectsDataPage: objects data page or None.
    """
    file_offset = page_number * self._PAGE_SIZE
    if file_offset >= self._file_size:
      return None

    return self._ReadPage(self._file_object, file_offset, is_data_page)

  def ReadFileObject(self, file_object):
    """Reads an objects data file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._file_object = file_object

  def ReadObjectRecordDataSegment(self, objects_page, data_offset, data_size):
    """Reads a data segment of an object record.

    Args:
      objects_page (ObjectsDataPage): objects data page.
      data_offset (int): offset of the object record data relative to
          the start of the page.
      data_size (int): object record data size.

    Returns:
      bytes: object record data segment.

    Raises:
      ParseError: if the object record data segment cannot be read.
    """
    # Make the offset relative to the start of the file.
    file_offset = objects_page.page_offset + data_offset

    self._file_object.seek(file_offset, os.SEEK_SET)

    if self._debug:
      self._DebugPrintText((
          f'Reading object record data segment at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    available_page_size = self._PAGE_SIZE - data_offset

    if data_size > available_page_size:
      read_size = available_page_size
    else:
      read_size = data_size

    return self._file_object.read(read_size)


class RepositoryFile(data_format.BinaryDataFile):
  """Repository file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _DEBUG_INFO_CHILD_OBJECTS_LIST_NODE = [
      ('list_element_node_offset1', 'List element node offset 1',
       '_FormatIntegerAsOffset'),
      ('first_list_element_node_offset', 'First list element node offset',
       '_FormatIntegerAsOffset'),
      ('last_list_element_node_offset', 'Last list element node offset',
       '_FormatIntegerAsOffset'),
      ('unknown4', 'Unknown4', '_FormatIntegerAsDecimal'),
      ('number_of_elements', 'Number of elements', '_FormatIntegerAsDecimal'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_CHILD_OBJECTS_LIST_ELEMENT_NODE = [
      ('unknown1', 'Unknown1', '_FormatIntegerAsDecimal'),
      ('name_node_offset', 'Name node offset', '_FormatIntegerAsOffset'),
      ('value_node_offset', 'Value node offset', '_FormatIntegerAsOffset'),
      ('list_element_node_offset1', 'Unknown node 3 offset 1',
       '_FormatIntegerAsOffset'),
      ('list_element_node_offset2', 'Unknown node 3 offset 2',
       '_FormatIntegerAsOffset'),
      ('previous_list_element_node_offset', 'Previous list element node offset',
       '_FormatIntegerAsOffset'),
      ('next_list_element_node_offset', 'Next list element node offset',
       '_FormatIntegerAsOffset'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_CHILD_OBJECTS_BRANCH_NODE = [
      ('number_of_leaf_values', 'Number of leaf values',
       '_FormatIntegerAsDecimal'),
      ('maximum_number_of_leaf_values', 'Maximum number of leaf values',
       '_FormatIntegerAsDecimal'),
      ('unknown3', 'Unknown3', '_FormatIntegerAsHexadecimal8'),
      ('leaf_node_offset', 'Leaf node offset', '_FormatIntegerAsOffset'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_CHILD_OBJECTS_LEAF_NODE = [
      ('value_node_offset1', 'Value node offset1', '_FormatIntegerAsOffset'),
      ('value_node_offset2', 'Value node offset2', '_FormatIntegerAsOffset'),
      ('value_node_offset3', 'Value node offset3', '_FormatIntegerAsOffset'),
      ('value_node_offset4', 'Value node offset4', '_FormatIntegerAsOffset'),
      ('value_node_offset5', 'Value node offset5', '_FormatIntegerAsOffset'),
      ('value_node_offset6', 'Value node offset6', '_FormatIntegerAsOffset'),
      ('value_node_offset7', 'Value node offset7', '_FormatIntegerAsOffset'),
      ('value_node_offset8', 'Value node offset8', '_FormatIntegerAsOffset'),
      ('value_node_offset9', 'Value node offset9', '_FormatIntegerAsOffset'),
      ('value_node_offset10', 'Value node offset10', '_FormatIntegerAsOffset'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_CHILD_OBJECTS_ROOT_NODE = [
      ('depth', 'Depth', '_FormatIntegerAsDecimal'),
      ('number_of_leaf_values', 'Number of leaf values',
       '_FormatIntegerAsDecimal'),
      ('branch_node_offset', 'Branch node offset', '_FormatIntegerAsOffset'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_CLASS_DEFINITION_BRANCH_NODE = [
      ('instance_root_node_offset', 'Instance root node offset',
       '_FormatIntegerAsOffset'),
      ('class_definition_root_node_offset', 'Class definition root node offset',
       '_FormatIntegerAsOffset'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal8'),
      ('class_definition_leaf_node_offset', 'Class definition leaf node offset',
       '_FormatIntegerAsOffset'),
      ('unknown3', 'Unknown3 offset', '_FormatIntegerAsOffset'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_CLASS_DEFINITION_LEAF_NODE = [
      ('class_definition_block_size', 'Class definition block size',
       '_FormatIntegerAsDecimal'),
      ('class_definition_block_data', 'Class definition block data',
       '_FormatDataInHexadecimal'),
      ('unknown_block_size', 'Unknown block size', '_FormatIntegerAsDecimal'),
      ('unknown_block_data', 'Unknown block data', '_FormatDataInHexadecimal'),
      ('alignment_padding', 'Alignment padding', '_FormatDataInHexadecimal'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_CLASS_DEFINITION_ROOT_NODE = [
      ('instance_root_node_offset', 'Instance root node offset',
       '_FormatIntegerAsOffset'),
      ('class_definition_branch_node_offset',
       'Class definition branch node offset', '_FormatIntegerAsOffset'),
      ('parent_class_root_node_offset', 'Parent class root node offset',
       '_FormatIntegerAsOffset'),
      ('sub_node_type', 'Sub node type', '_FormatIntegerAsHexadecimal2'),
      ('child_objects_list_node_offset', 'Child objects list node offset',
       '_FormatIntegerAsOffset'),
      ('sub_node_offset', 'Sub node offset', '_FormatIntegerAsOffset'),
      ('unknown4', 'Unknown4', '_FormatIntegerAsHexadecimal8'),
      ('child_objects_root_node_offset', 'Child objects root node offset',
       '_FormatIntegerAsOffset'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_FILE_HEADER = [
      ('system_class_cell_number', 'System class cell number',
       '_FormatIntegerAsDecimal'),
      ('root_namespace_cell_number', 'Root namespace cell number',
       '_FormatIntegerAsDecimal'),
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal8'),
      ('unused_space_offset', 'Unused space offset', '_FormatIntegerAsOffset'),
      ('unknown3', 'Unknown3', '_FormatIntegerAsHexadecimal8'),
      ('unknown4', 'Unknown4', '_FormatIntegerAsHexadecimal8'),
      ('unknown5', 'Unknown5', '_FormatIntegerAsHexadecimal8'),
      ('node_bin_size', 'Node bin size', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_INSTANCE_BRANCH_NODE = [
      ('instance_root_node_offset', 'Instance root node offset',
       '_FormatIntegerAsOffset'),
      ('class_definition_root_node_offset', 'Class definition root node offset',
       '_FormatIntegerAsOffset'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsDecimal'),
      ('instance_leaf_node_offset', 'Instance leaf node offset',
       '_FormatIntegerAsOffset'),
      ('unknown3', 'Unknown3', '_FormatIntegerAsOffset'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_INSTANCE_LEAF_NODE = [
      ('instance_block_size', 'Instance block size', '_FormatIntegerAsDecimal'),
      ('instance_block_data', 'Instance block data',
       '_FormatDataInHexadecimal'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_INSTANCE_LEAF_VALUE_NODE = [
      ('name_node_offset', 'Name node offset', '_FormatIntegerAsOffset'),
      ('instance_root_node_offset', 'Instance root node offset',
       '_FormatIntegerAsOffset'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_INSTANCE_ROOT_NODE = [
      ('child_objects_root_node_offset', 'Child objects root node offset',
       '_FormatIntegerAsOffset'),
      ('name_node_offset', 'Name node offset', '_FormatIntegerAsOffset'),
      ('instance_branch_node_offset', 'Instance branch node offset',
       '_FormatIntegerAsOffset'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsDecimal'),
      ('child_objects_list_node_offset', 'Child objects list node offset',
       '_FormatIntegerAsOffset'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsOffset'),
      ('unknown_node5_offset', 'Unknown node 5 offset',
       '_FormatIntegerAsOffset'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_NAME_NODE = [
      ('name', 'Name', '_FormatString'),
      ('alignment_padding', 'Alignment padding', '_FormatDataInHexadecimal'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_NODE_CELL = [
      ('size', 'Size', '_FormatIntegerAsDecimal'),
      ('data', 'Data', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_NODE_BIN_HEADER = [
      ('node_bin_size', 'Node bin size', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_UNKNOWN_NODE5 = [
      ('unknown_block_size', 'Unknown block size', '_FormatIntegerAsDecimal'),
      ('unknown_block_data', 'Unknown block data', '_FormatDataInHexadecimal'),
      ('footer', 'Footer', '_FormatDataInHexadecimal')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a repository file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(RepositoryFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._root_namespace_node_offset = None
    self._system_class_definition_root_node_offset = None

  def _ReadChildObjectsList(self, file_object, list_node_offset):
    """Reads a child objects list.

    Args:
      file_object (file): file-like object.
      list_node_offset (int): offset of the list node relative to the start
          of the file.

    Yields:
      int: element value offset.
    """
    node_cell = self._ReadNodeCell(file_object, list_node_offset - 4)
    list_node = self._ReadChildObjectsListNode(node_cell.data, list_node_offset)

    list_element = 1
    next_list_element_node_offset = list_node.first_list_element_node_offset

    while next_list_element_node_offset > 40:
      if self._debug:
        self._DebugPrintText(f'Reading list element: {list_element:d}\n')

      node_cell = self._ReadNodeCell(
          file_object, next_list_element_node_offset - 4)
      list_element_node = self._ReadChildObjectsListElementNode(
          node_cell.data, next_list_element_node_offset)

      if list_element_node.name_node_offset > 40:
        node_cell = self._ReadNodeCell(
            file_object, list_element_node.name_node_offset - 4)
        self._ReadNameNode(node_cell.data, list_element_node.name_node_offset)

      yield list_element_node.value_node_offset

      list_element += 1
      next_list_element_node_offset = (
          list_element_node.next_list_element_node_offset)

  def _ReadChildObjectsListNode(self, block_data, file_offset):
    """Reads a child objects list node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_child_objects_list_node: child objects list node.

    Raises:
      ParseError: if the child objects list node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading child objects list node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_child_objects_list_node')

    list_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'child objects list node')

    if self._debug:
      self._DebugPrintStructureObject(
          list_node, self._DEBUG_INFO_CHILD_OBJECTS_LIST_NODE)

    return list_node

  def _ReadChildObjectsListElementNode(self, block_data, file_offset):
    """Reads a child objects list element node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_child_objects_list_element_node: child objects list element node.

    Raises:
      ParseError: if the list element node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading child objects list element node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap(
        'cim_rep_child_objects_list_element_node')

    list_element_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map,
        'child objects list element node')

    if self._debug:
      self._DebugPrintStructureObject(
          list_element_node, self._DEBUG_INFO_CHILD_OBJECTS_LIST_ELEMENT_NODE)

    return list_element_node

  def _ReadChildObjectsTree(self, file_object, root_node_offset):
    """Reads a child objects tree.

    Args:
      file_object (file): file-like object.
      root_node_offset (int): offset of the root node relative to the start of
          the file.

    Yields:
      int: leaf value offset.
    """
    node_cell = self._ReadNodeCell(file_object, root_node_offset - 4)
    root_node = self._ReadChildObjectsTreeRootNode(
        node_cell.data, root_node_offset)

    if root_node.depth == 1:
      yield root_node.branch_node_offset

    elif root_node.depth == 2:
      if root_node.branch_node_offset > 40:
        node_cell = self._ReadNodeCell(
            file_object, root_node.branch_node_offset - 4)
        branch_node = self._ReadChildObjectsTreeBranchNode(
            node_cell.data, root_node.branch_node_offset)

        if branch_node.leaf_node_offset > 40:
          node_cell = self._ReadNodeCell(
              file_object, branch_node.leaf_node_offset - 4)
          leaf_node = self._ReadChildObjectsTreeLeafNode(
              node_cell.data, branch_node.leaf_node_offset)

          for node_offset in (
              leaf_node.value_node_offset1,
              leaf_node.value_node_offset2,
              leaf_node.value_node_offset3,
              leaf_node.value_node_offset4,
              leaf_node.value_node_offset5,
              leaf_node.value_node_offset6,
              leaf_node.value_node_offset7,
              leaf_node.value_node_offset8,
              leaf_node.value_node_offset9,
              leaf_node.value_node_offset10):
            yield node_offset

  # TODO: rename
  def _ReadChildObjectsTreeBranchNode(self, block_data, file_offset):
    """Reads a child objects tree branch node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_child_objects_branch_node: child objects branch node.

    Raises:
      ParseError: if the child objects branch node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading child objects branch node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_child_objects_branch_node')

    branch_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'child objects branch node')

    if self._debug:
      self._DebugPrintStructureObject(
          branch_node, self._DEBUG_INFO_CHILD_OBJECTS_BRANCH_NODE)

    return branch_node

  def _ReadChildObjectsTreeLeafNode(self, block_data, file_offset):
    """Reads a child objects tree leaf node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_child_objects_leaf_node: child objects leaf node.

    Raises:
      ParseError: if the child objects leaf node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading child objects leaf node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_child_objects_leaf_node')

    leaf_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'child objects leaf node')

    if self._debug:
      self._DebugPrintStructureObject(
          leaf_node, self._DEBUG_INFO_CHILD_OBJECTS_LEAF_NODE)

    return leaf_node

  # TODO: rename
  def _ReadChildObjectsTreeRootNode(self, block_data, file_offset):
    """Reads a child objects tree root node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_child_objects_root_node: child objects root node.

    Raises:
      ParseError: if the child objects root node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading child objects root node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_child_objects_root_node')

    root_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'child objects root node')

    if self._debug:
      self._DebugPrintStructureObject(
          root_node, self._DEBUG_INFO_CHILD_OBJECTS_ROOT_NODE)

    return root_node

  # TODO: rename
  def _ReadClassDefinitionBranchNode(self, block_data, file_offset):
    """Reads a class definition branch node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_class_definition_branch_node: class definition branch node.

    Raises:
      ParseError: if the class definition branch node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading class definition branch node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_class_definition_branch_node')

    class_definition_branch_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'class definition branch node')

    if self._debug:
      self._DebugPrintStructureObject(
          class_definition_branch_node,
          self._DEBUG_INFO_CLASS_DEFINITION_BRANCH_NODE)

    return class_definition_branch_node

  def _ReadClassDefinitionLeafNode(self, block_data, file_offset):
    """Reads a class definition leaf node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_class_definition_leaf_node: class definition leaf node.

    Raises:
      ParseError: if the class definition leaf node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading class definition leaf node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_class_definition_leaf_node')

    class_definition_leaf_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'class definition leaf node')

    if self._debug:
      self._DebugPrintStructureObject(
          class_definition_leaf_node,
          self._DEBUG_INFO_CLASS_DEFINITION_LEAF_NODE)

    return class_definition_leaf_node

  def _ReadClassDefinitionRootNode(self, block_data, file_offset):
    """Reads a class definition root node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_class_definition_root_node: class definition root node.

    Raises:
      ParseError: if the class definition root node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading class definition root node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_class_definition_root_node')

    class_definition_root_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'class definition root node')

    if self._debug:
      self._DebugPrintStructureObject(
          class_definition_root_node,
          self._DEBUG_INFO_CLASS_DEFINITION_ROOT_NODE)

    return class_definition_root_node

  def _ReadFileHeader(self, file_object):
    """Reads a file header.

    Args:
      file_object (file): file-like object.

    Returns:
      cim_rep_file_header: file header.

    Raises:
      ParseError: if the file header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('cim_rep_file_header')

    file_header, _ = self._ReadStructureFromFileObject(
        file_object, 0, data_type_map, 'file header')

    if self._debug:
      self._DebugPrintStructureObject(file_header, self._DEBUG_INFO_FILE_HEADER)

    return file_header

  def _ReadInstanceBranchNode(self, block_data, file_offset):
    """Reads an instance branch node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_instance_branch_node: instance branch node.

    Raises:
      ParseError: if the instance branch node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading instance branch node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_instance_branch_node')

    instance_branch_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'instance branch node')

    if self._debug:
      self._DebugPrintStructureObject(
          instance_branch_node, self._DEBUG_INFO_INSTANCE_BRANCH_NODE)

    return instance_branch_node

  def _ReadInstanceLeafNode(self, block_data, file_offset):
    """Reads an instance leaf node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_instance_leaf_node: instance leaf node.

    Raises:
      ParseError: if the instance leaf node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading instance leaf node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_instance_leaf_node')

    instance_leaf_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'instance leaf node')

    if self._debug:
      self._DebugPrintStructureObject(
          instance_leaf_node, self._DEBUG_INFO_INSTANCE_LEAF_NODE)

    return instance_leaf_node

  def _ReadInstanceLeafValueNode(self, block_data, file_offset):
    """Reads an instance leaf value node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_instance_leaf_value_node: instance leaf value node.

    Raises:
      ParseError: if the instance leaf value node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading instance leaf value node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_instance_leaf_value_node')

    instance_leaf_value_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'instance leaf value node')

    if self._debug:
      self._DebugPrintStructureObject(
          instance_leaf_value_node, self._DEBUG_INFO_INSTANCE_LEAF_VALUE_NODE)

    return instance_leaf_value_node

  def _ReadInstanceRootNode(self, block_data, file_offset):
    """Reads an instance root node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_instance_root_node: instance root node.

    Raises:
      ParseError: if the instance root node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading instance root node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_instance_root_node')

    instance_root_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'instance root node')

    if self._debug:
      self._DebugPrintStructureObject(
          instance_root_node, self._DEBUG_INFO_INSTANCE_ROOT_NODE)

    return instance_root_node

  def _ReadNameNode(self, block_data, file_offset):
    """Reads a name node.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_name_node: name node.

    Raises:
      ParseError: if the name node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading name node at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_name_node')

    name_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'name node')

    if self._debug:
      self._DebugPrintStructureObject(name_node, self._DEBUG_INFO_NAME_NODE)

    return name_node

  def _ReadNodeBinHeader(self, file_object, file_offset):
    """Reads a node bin header.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_node_bin_header: node bin header.

    Raises:
      ParseError: if the node bin header cannot be read.
    """
    data_type_map = self._GetDataTypeMap('cim_rep_node_bin_header')

    node_bin_header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'node bin header')

    if self._debug:
      self._DebugPrintStructureObject(
          node_bin_header, self._DEBUG_INFO_NODE_BIN_HEADER)

    return node_bin_header

  def _ReadNodeCell(self, file_object, file_offset, cell_number=None):
    """Reads a node cell.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the node cell relative to the start of
          the file.
      cell_number (Optional[int]): cell number.

    Returns:
      cim_rep_node_cell: node cell.

    Raises:
      ParseError: if the node cell cannot be read.
    """
    data_type_map = self._GetDataTypeMap('cim_rep_node_cell')

    node_cell, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'node cell')

    if self._debug:
      value_string = self._FormatIntegerAsOffset(file_offset)
      self._DebugPrintValue('Node cell offset', value_string)

      value_string = self._FormatIntegerAsOffset(file_offset + 4)
      self._DebugPrintValue('Data offset', value_string)

      if cell_number is not None:
        value_string = self._FormatIntegerAsDecimal(cell_number)
        self._DebugPrintValue('Node cell number', value_string)

      self._DebugPrintStructureObject(node_cell, self._DEBUG_INFO_NODE_CELL)

    return node_cell

  def _ReadUnknownNode5(self, block_data, file_offset):
    """Reads an unknown node 5.

    Args:
      block_data (bytes): block data.
      file_offset (int): offset of the node cell relative to the start of
          the file.

    Returns:
      cim_rep_unknown_node5: unknown node.

    Raises:
      ParseError: if the unknown node cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading unknown node 5 at offset: {file_offset:d} '
          f'(0x{file_offset:08x})\n'))

    data_type_map = self._GetDataTypeMap('cim_rep_unknown_node5')

    unknown_node = self._ReadStructureFromByteStream(
        block_data, file_offset, data_type_map, 'unknown node 5')

    if self._debug:
      self._DebugPrintStructureObject(
          unknown_node, self._DEBUG_INFO_UNKNOWN_NODE5)

    return unknown_node

  def _ReadClassDefinition(self, file_object, branch_node_offset):
    """Reads a class definition.

    Args:
      file_object (file): file-like object.
      branch_node_offset (int): offset of the branch node relative to the start
          of the file.

    Returns:
      ClassDefinition: class definition.
    """
    node_cell = self._ReadNodeCell(file_object, branch_node_offset - 4)
    branch_node = self._ReadClassDefinitionBranchNode(
        node_cell.data, branch_node_offset)

    leaf_node_offset = branch_node.class_definition_leaf_node_offset
    if leaf_node_offset <= 40:
      return None

    node_cell = self._ReadNodeCell(file_object, leaf_node_offset - 4)
    leaf_node = self._ReadClassDefinitionLeafNode(
        node_cell.data, leaf_node_offset)

    class_definition = ClassDefinition(
        debug=self._debug, output_writer=self._output_writer)
    class_definition.ReadClassDefinitionBlock(
        leaf_node.class_definition_block_data,
        record_data_offset=leaf_node_offset)

    return class_definition

  def _ReadClassDefinitionInstance(self, file_object, root_node_offset):
    """Reads an instance from a class definition.

    Args:
      file_object (file): file-like object.
      root_node_offset (int): offset of the root node relative to the start of
          the file.

    Return:
      Instance: instance.
    """

  def _ReadClassDefinitionHierarchy(self, file_object, root_node_offset):
    """Reads the class definition hierarchy.

    Args:
      file_object (file): file-like object.
      root_node_offset (int): offset of the root node relative to the start of
          the file.

    Yields:
      Instance: instance.
    """
    node_cell = self._ReadNodeCell(file_object, root_node_offset - 4)
    root_node = self._ReadClassDefinitionRootNode(
        node_cell.data, root_node_offset)

    branch_node_offset = root_node.class_definition_branch_node_offset
    if branch_node_offset > 40:
      node_cell = self._ReadNodeCell(file_object, branch_node_offset - 4)
      branch_node = self._ReadClassDefinitionBranchNode(
          node_cell.data, branch_node_offset)

      leaf_node_offset = branch_node.class_definition_leaf_node_offset
      if leaf_node_offset > 40:
        node_cell = self._ReadNodeCell(file_object, leaf_node_offset - 4)
        leaf_node = self._ReadClassDefinitionLeafNode(
            node_cell.data, leaf_node_offset)

        class_definition = ClassDefinition(
            debug=self._debug, output_writer=self._output_writer)
        class_definition.ReadClassDefinitionBlock(
            leaf_node.class_definition_block_data,
            record_data_offset=leaf_node_offset)

        if self._debug:
          class_definition.DebugPrint()

    if root_node.child_objects_list_node_offset > 40:
      for value_node_offset in self._ReadChildObjectsList(
          file_object, root_node.child_objects_list_node_offset):
        if value_node_offset > 40:
          instance = self._ReadInstance(file_object, value_node_offset)
          yield instance

    if root_node.sub_node_offset > 40 and root_node.sub_node_type in (9, 10):
      for value_node_offset in self._ReadChildObjectsTree(
          file_object, root_node.sub_node_offset):
        if value_node_offset > 40:
          for instance in self._ReadClassDefinitionHierarchy(
              file_object, value_node_offset):
            yield instance

    if self._debug:
      if root_node.child_objects_root_node_offset > 40:
        for value_node_offset in self._ReadChildObjectsTree(
            file_object, root_node.child_objects_root_node_offset):
          if value_node_offset > 40:
            node_cell = self._ReadNodeCell(file_object, value_node_offset - 4)
            self._ReadNameNode(node_cell.data, value_node_offset)

  def _ReadInstance(self, file_object, branch_node_offset):
    """Reads an instance.

    Args:
      file_object (file): file-like object.
      branch_node_offset (int): offset of the branch node relative to the start
          of the file.

    Returns:
      Instance: instance.
    """
    node_cell = self._ReadNodeCell(file_object, branch_node_offset - 4)
    instance_branch_node = self._ReadInstanceBranchNode(
        node_cell.data, branch_node_offset)

    if instance_branch_node.class_definition_root_node_offset <= 40:
      return None

    if instance_branch_node.instance_leaf_node_offset <= 40:
      return None

    if instance_branch_node.unknown1 != 2:
      return None

    node_cell = self._ReadNodeCell(
        file_object, instance_branch_node.class_definition_root_node_offset - 4)
    root_node = self._ReadClassDefinitionRootNode(
        node_cell.data, instance_branch_node.class_definition_root_node_offset)

    if root_node.class_definition_branch_node_offset <= 40:
      return None

    class_definition = self._ReadClassDefinition(
        file_object, root_node.class_definition_branch_node_offset)

    node_cell = self._ReadNodeCell(
        file_object, instance_branch_node.instance_leaf_node_offset - 4)
    leaf_node = self._ReadInstanceLeafNode(
        node_cell.data, instance_branch_node.instance_leaf_node_offset)

    # TODO: read class definition hierarcy
    class_definitions = [class_definition]

    class_value_data_map = ClassValueDataMap()
    class_value_data_map.Build(class_definitions)

    instance = Instance(
        debug=self._debug, output_writer=self._output_writer)

    instance.ReadInstanceBlockData(
        class_value_data_map, leaf_node.instance_block_data,
        record_data_offset=instance_branch_node.instance_leaf_node_offset)

    # pylint: disable=attribute-defined-outside-init
    instance.class_name = class_value_data_map.class_name
    instance.derivation = class_value_data_map.derivation
    instance.dynasty = class_value_data_map.dynasty
    instance.super_class_name = class_value_data_map.super_class_name

    if self._debug:
      class_definition.DebugPrint()
      instance.DebugPrint()

    return instance

  def _ReadInstanceHierarchy(self, file_object, root_node_offset):
    """Reads an instance hierarchy.

    Args:
      file_object (file): file-like object.
      root_node_offset (int): offset of the root node relative to the start of
          the file.

    Yields:
      Instance: instance.
    """
    node_cell = self._ReadNodeCell(file_object, root_node_offset - 4)
    root_node = self._ReadInstanceRootNode(node_cell.data, root_node_offset)

    if self._debug:
      if root_node.name_node_offset > 40:
        node_cell = self._ReadNodeCell(
            file_object, root_node.name_node_offset - 4)
        self._ReadNameNode(node_cell.data, root_node.name_node_offset)

    if root_node.instance_branch_node_offset > 40:
      instance = self._ReadInstance(
          file_object, root_node.instance_branch_node_offset)

      yield instance

    if self._debug:
      if root_node.unknown_node5_offset > 40 and root_node.unknown2 == 0:
        node_cell = self._ReadNodeCell(
            file_object, root_node.unknown_node5_offset - 4)
        unknown_node5 = self._ReadUnknownNode5(
            node_cell.data, root_node.unknown_node5_offset)

        # TODO: clean up after debugging
        _ = unknown_node5

    if (root_node.child_objects_root_node_offset > 40 and
        root_node.child_objects_root_node_offset != 0xffffffff):
      for value_node_offset in self._ReadChildObjectsTree(
          file_object, root_node.child_objects_root_node_offset):
        if value_node_offset > 40:
          node_cell = self._ReadNodeCell(file_object, value_node_offset - 4)
          instance_leaf_value_node = self._ReadInstanceLeafValueNode(
              node_cell.data, value_node_offset)

          if self._debug:
            if instance_leaf_value_node.name_node_offset > 40:
              node_cell = self._ReadNodeCell(
                  file_object, instance_leaf_value_node.name_node_offset - 4)
              self._ReadNameNode(
                  node_cell.data, instance_leaf_value_node.name_node_offset)

          if instance_leaf_value_node.instance_root_node_offset > 40:
            for instance in self._ReadInstanceHierarchy(
                file_object,
                instance_leaf_value_node.instance_root_node_offset):
              yield instance

    if self._debug:
      if root_node.child_objects_list_node_offset > 40:
        for value_node_offset in self._ReadChildObjectsList(
            file_object, root_node.child_objects_list_node_offset):
          if value_node_offset > 40:
            node_cell = self._ReadNodeCell(file_object, root_node_offset - 4)
            root_node = self._ReadClassDefinitionRootNode(
                node_cell.data, root_node_offset)

            if root_node.class_definition_branch_node_offset > 40:
              self._ReadClassDefinition(
                  file_object, root_node.class_definition_branch_node_offset)

  def _ReadNamespaceInstanceHierarchy(
      self, file_object, root_node_offset, parent_namespace_segments):
    """Reads a namespace instance hierarchy.

    Args:
      file_object (file): file-like object.
      root_node_offset (int): offset of the root node relative to the start of
          the file.
      parent_namespace_segments (list[str]): segments of the parent namespace.

    Yields:
      Instance: instance.
    """
    node_cell = self._ReadNodeCell(file_object, root_node_offset - 4)
    root_node = self._ReadInstanceRootNode(node_cell.data, root_node_offset)

    if root_node.instance_branch_node_offset > 40:
      instance = self._ReadInstance(
          file_object, root_node.instance_branch_node_offset)

      name_property = instance.properties.get('Name', None)

      namespace_segments = list(parent_namespace_segments)
      namespace_segments.append(name_property)
      instance.namespace = '\\'.join(namespace_segments)

      yield instance

      if (root_node.child_objects_root_node_offset > 40 and
          root_node.child_objects_root_node_offset != 0xffffffff):
        for value_node_offset in self._ReadChildObjectsTree(
            file_object, root_node.child_objects_root_node_offset):
          if value_node_offset > 40:
            node_cell = self._ReadNodeCell(file_object, value_node_offset - 4)
            instance_leaf_value_node = self._ReadInstanceLeafValueNode(
                node_cell.data, value_node_offset)

            if instance_leaf_value_node.instance_root_node_offset > 40:
              for instance in self._ReadNamespaceInstanceHierarchy(
                  file_object,
                  instance_leaf_value_node.instance_root_node_offset,
                  namespace_segments):
                yield instance

  def ReadClassDefinitions(self):
    """Reads class definitions.

    Yields:
      Instance: instance.
    """
    if self._system_class_definition_root_node_offset > 40:
      for instance in self._ReadClassDefinitionHierarchy(
          self._file_object, self._system_class_definition_root_node_offset):
        yield instance

  def ReadInstances(self):
    """Reads instances.

    Yields:
      Instance: instance.
    """
    if self._root_namespace_node_offset > 40:
      for instance in self._ReadInstanceHierarchy(
          self._file_object, self._root_namespace_node_offset):
        yield instance

  def ReadNamespaces(self):
    """Reads namespace instances.

    Yields:
      Instance: instance.
    """
    if self._root_namespace_node_offset > 40:
      for instance in self._ReadNamespaceInstanceHierarchy(
          self._file_object, self._root_namespace_node_offset, []):
        yield instance

  def ReadFileObject(self, file_object):
    """Reads a mappings file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_object.seek(0, os.SEEK_END)
    file_size = file_object.tell()

    file_object.seek(0, os.SEEK_SET)

    file_header = self._ReadFileHeader(file_object)

    file_offset = 40
    cell_number = 0

    next_node_bin_offset = file_header.node_bin_size

    self._root_namespace_node_offset = None
    self._system_class_definition_root_node_offset = None

    while file_offset < file_size:
      if file_offset == next_node_bin_offset:
        node_bin_header = self._ReadNodeBinHeader(file_object, file_offset)
        file_offset += 4

        next_node_bin_offset += node_bin_header.node_bin_size

      node_cell = self._ReadNodeCell(
          file_object, file_offset, cell_number=cell_number)
      if node_cell.size == 0:
        break

      if file_header.root_namespace_cell_number == cell_number:
        self._root_namespace_node_offset = file_offset + 4
      elif file_header.system_class_cell_number == cell_number:
        self._system_class_definition_root_node_offset = file_offset + 4

      file_offset += node_cell.size & 0x7ffffff
      cell_number += 1

      if (not self._debug and self._root_namespace_node_offset is not None and
          self._system_class_definition_root_node_offset is not None):
        break


class CIMObject(data_format.BinaryDataFormat):
  """CIM object."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _CIM_DATA_TYPES = _FABRIC.CreateDataTypeMap('cim_data_types')

  def _DebugPrintCIMString(self, cim_string, description):
    """Prints CIM string information.

    Args:
      cim_string (cim_string): CIM string.
      description (str): description of the structure.
    """
    description = ''.join([description[0].upper(), description[1:]])

    self._DebugPrintValue(
        f'{description:s} string flags', f'0x{cim_string.string_flags:02x}')

    self._DebugPrintValue(f'{description:s} string', cim_string.string)

  def _FormatIntegerAsDataType(self, integer):
    """Formats an integer as a data type.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a data type.
    """
    data_type_string = self._CIM_DATA_TYPES.GetName(
        integer & 0x3fff) or 'UNKNOWN'
    # TODO: format flag 0x4000
    return f'0x{integer:08x} ({data_type_string:s})'

  def _ReadCIMString(
      self, string_offset, record_data, record_data_offset, description):
    """Reads a CIM string.

    Args:
      string_offset (int): string offset.
      record_data (bytes): record data.
      record_data_offset (int): offset of the string data relative to
          the start of the record data.
      description (str): description of the structure.

    Returns:
      str: string.

    Raises:
      ParseError: if the qualifier value cannot be read.
    """
    data_type_map = self._GetDataTypeMap('cim_string')

    cim_string = self._ReadStructureFromByteStream(
        record_data[string_offset:], record_data_offset + string_offset,
        data_type_map, description)

    if self._debug:
      self._DebugPrintCIMString(cim_string, description)

    return cim_string.string


class ClassDefinition(CIMObject):
  """Class definition.

  Attributes:
    name (str): name of the class.
    properties (dict[str, ClassDefinitionProperty]): properties.
    qualifiers (dict[str, object]): qualifiers.
    super_class_name (str): name of the parent class.
  """

  _DEBUG_INFO_CLASS_DEFINITION_BLOCK = [
      ('unknown1', 'Unknown1', '_FormatIntegerAsDecimal'),
      ('name_offset', 'Name offset', '_FormatIntegerAsOffset'),
      ('default_value_size', 'Default value size', '_FormatIntegerAsDecimal'),
      ('super_class_name_block_size', 'Super class name block size',
       '_FormatIntegerAsDecimal'),
      ('super_class_name_block_data', 'Super class name block data',
       '_FormatDataInHexadecimal'),
      ('qualifiers_block_size', 'Qualifiers block size',
       '_FormatIntegerAsDecimal'),
      ('qualifiers_block_data', 'Qualifiers block data',
       '_FormatDataInHexadecimal'),
      ('number_of_property_descriptors', 'Number of property descriptors',
       '_FormatIntegerAsDecimal'),
      ('property_descriptors', 'Property descriptors',
       '_FormatArrayOfPropertyDescriptors'),
      ('default_value_data', 'Default value data', '_FormatDataInHexadecimal'),
      ('values_data_size', 'Values data size',
       '_FormatIntegerAsPropertiesBlockSize'),
      ('values_data', 'Values data', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_QUALIFIER_DESCRIPTOR = [
      ('name_offset', 'Name offset', '_FormatIntegerAsOffset'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal2'),
      ('value_data_type', 'Value data type', '_FormatIntegerAsDataType'),
      ('value_boolean', 'Value', '_FormatIntegerAsDecimal'),
      ('value_floating_point', 'Value', '_FormatFloatingPoint'),
      ('value_integer', 'Value', '_FormatIntegerAsDecimal'),
      ('value_offset', 'Value offset', '_FormatIntegerAsOffset')]

  _DEBUG_INFO_PROPERTY_DEFINITION = [
      ('value_data_type', '  Value data type', '_FormatIntegerAsDataType'),
      ('index', '  Index', '_FormatIntegerAsDecimal'),
      ('value_data_offset', '  Value data offset', '_FormatIntegerAsOffset'),
      ('level', '  Level', '_FormatIntegerAsDecimal'),
      ('qualifiers_block_size', '  Qualifiers block size',
       '_FormatIntegerAsDecimal'),
      ('qualifiers_block_data', '  Qualifiers block data',
       '_FormatDataInHexadecimal'),
      ('value_boolean', '  Value', '_FormatIntegerAsDecimal'),
      ('value_floating_point', '  Value', '_FormatFloatingPoint'),
      ('value_integer', '  Value', '_FormatIntegerAsDecimal'),
      ('value_offset', '  Value offset', '_FormatIntegerAsOffset')]

  _PREDEFINED_NAMES = {
      1: 'key',
      3: 'read',
      4: 'write',
      6: 'provider',
      7: 'dynamic',
      10: 'type'}

  def __init__(self, debug=False, output_writer=None):
    """Initializes a class definition.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(ClassDefinition, self).__init__(
        debug=debug, output_writer=output_writer)
    self.name = None
    self.super_class_name = None
    self.properties = {}
    self.qualifiers = {}

  def _FormatArrayOfPropertyDescriptors(self, array_of_property_descriptors):
    """Formats an array of property descriptors.

    Args:
      array_of_property_descriptors (list[property_descriptor]): array of
          property descriptors.

    Returns:
      str: formatted array of property descriptors.
    """
    lines = []
    for index, property_descriptor in enumerate(array_of_property_descriptors):
      value_string = self._FormatIntegerAsOffset(
          property_descriptor.name_offset)
      line = self._FormatValue(
          f'    Property descriptor: {index:d} name offset', value_string)
      lines.append(line)

      value_string = self._FormatIntegerAsOffset(
          property_descriptor.definition_offset)
      line = self._FormatValue(
          f'    Property descriptor: {index:d} definition offset', value_string)
      lines.append(line)

    return ''.join(lines)

  def _FormatIntegerAsPropertiesBlockSize(self, integer):
    """Formats an integer as a properties block size.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a properties block size.
    """
    size_value = integer & 0x7fffffff
    return f'{size_value:d} (0x{integer:08x})'

  def _ReadClassDefinitionMethods(self, class_definition_data):
    """Reads a class definition methods.

    Args:
      class_definition_data (bytes): class definition data.

    Raises:
      ParseError: if the class definition cannot be read.
    """
    # TODO: set record_data_offset
    record_data_offset = 0

    if self._debug:
      self._DebugPrintText((
          f'Reading class definition methods at offset: {record_data_offset:d} '
          f'(0x{record_data_offset:08x}).\n'))

    data_type_map = self._GetDataTypeMap('class_definition_methods')

    class_definition_methods = self._ReadStructureFromByteStream(
        class_definition_data, record_data_offset, data_type_map,
        'class definition methods')

    methods_block_size = class_definition_methods.methods_block_size

    if self._debug:
      size_value = methods_block_size & 0x7fffffff
      self._DebugPrintValue(
          'Methods block size', f'{size_value:d} (0x{methods_block_size:08x})')

      self._DebugPrintData(
          'Methods block data', class_definition_methods.methods_block_data)

  def _ReadClassDefinitionPropertyDefinition(
      self, property_index, definition_offset, values_data, values_data_offset):
    """Reads a class definition property definition.

    Args:
      property_index (int): property index.
      definition_offset (int): definition offset.
      values_data (bytes): values data.
      values_data_offset (int): offset of the values data relative to the start
          of the record data.

    Returns:
      property_definition: property definition.

    Raises:
      ParseError: if the property name cannot be read.
    """
    if self._debug:
      self._DebugPrintText(f'Property: {property_index:d} definition:\n')

    record_data_offset = values_data_offset + definition_offset
    data_type_map = self._GetDataTypeMap('property_definition')

    property_definition = self._ReadStructureFromByteStream(
        values_data[definition_offset:], record_data_offset, data_type_map,
        f'property: {property_index:d} definition')

    if self._debug:
      self._DebugPrintStructureObject(
          property_definition, self._DEBUG_INFO_PROPERTY_DEFINITION)

    return property_definition

  def _ReadClassDefinitionPropertyName(
      self, property_index, name_offset, values_data, values_data_offset):
    """Reads a class definition property name.

    Args:
      property_index (int): property index.
      name_offset (int): name offset.
      values_data (bytes): values data.
      values_dataoffset (int): offset of the values data relative to the start
          of the record data.

    Returns:
      str: property name.

    Raises:
      ParseError: if the property name cannot be read.
    """
    if name_offset & 0x80000000:
      name_index = name_offset & 0x7fffffff
      property_name = self._PREDEFINED_NAMES.get(
          name_index, f'UNKNOWN_{name_index:d}')

      if self._debug:
        self._DebugPrintValue(
            f'Property: {property_index:d} name index', f'{name_index:d}')

        self._DebugPrintValue(
            f'Property: {property_index:d} name', property_name)

    else:
      property_name = self._ReadCIMString(
          name_offset, values_data, values_data_offset,
          f'property: {property_index:d} name')

    return property_name

  def _ReadClassDefinitionProperties(
      self, property_descriptors, values_data, values_data_offset):
    """Reads class definition properties.

    Args:
      property_descriptors (list[property_descriptor]): property descriptors.
      values_data (bytes): properties data.
      values_data_offset (int): offset of the values data relative to the start
          of the record data.

    Returns:
      dict[str, ClassDefinitionProperty]: properties.

    Raises:
      ParseError: if the properties cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading class definition properties.\n')

    properties = {}
    for property_index, property_descriptor in enumerate(property_descriptors):
      property_name = self._ReadClassDefinitionPropertyName(
          property_index, property_descriptor.name_offset, values_data,
          values_data_offset)

      property_definition = self._ReadClassDefinitionPropertyDefinition(
          property_index, property_descriptor.definition_offset, values_data,
          values_data_offset)

      qualifiers_block_offset = property_descriptor.definition_offset + 18

      property_qualifiers = self._ReadQualifiers(
          property_definition.qualifiers_block_data, qualifiers_block_offset,
          values_data, values_data_offset)

      class_definition_property = ClassDefinitionProperty()
      class_definition_property.name = property_name
      class_definition_property.index = property_definition.index
      class_definition_property.value_data_offset = (
          property_definition.value_data_offset)
      class_definition_property.value_data_type = (
          property_definition.value_data_type)
      class_definition_property.qualifiers = property_qualifiers

      properties[property_name] = class_definition_property

    return properties

  def _ReadQualifierName(
      self, qualifier_index, name_offset, values_data, values_data_offset):
    """Reads a qualifier name.

    Args:
      qualifier_index (int): qualifier index.
      name_offset (int): name offset.
      values_data (bytes): values data.
      values_data_offset (int): offset of the values data relative to the start
          of the record data.

    Returns:
      str: qualifier name.

    Raises:
      ParseError: if the qualifier name cannot be read.
    """
    if name_offset & 0x80000000:
      name_index = name_offset & 0x7fffffff
      qualifier_name = self._PREDEFINED_NAMES.get(
          name_index, f'UNKNOWN_{name_index:d}')

      if self._debug:
        self._DebugPrintValue(
            f'Qualifier: {qualifier_index:d} name index', f'{name_index:d}')

        self._DebugPrintValue(
            f'Qualifier: {qualifier_index:d} name', qualifier_name)

    else:
      qualifier_name = self._ReadCIMString(
          name_offset, values_data, values_data_offset,
          f'qualifier: {qualifier_index:d} name')

    return qualifier_name

  def _ReadQualifiers(
      self, qualifiers_data, qualifiers_data_offset, values_data,
      values_data_offset):
    """Reads qualifiers.

    Args:
      qualifiers_data (bytes): qualifiers data.
      qualifiers_data_offset (int): offset of the qualifiers data relative
          to the start of the record data.
      values_data (bytes): values data.
      values_data_offset (int): offset of the values data relative to the start
          of the record data.

    Returns:
      dict[str, object]: qualifier names and values.

    Raises:
      ParseError: if the qualifiers cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading qualifiers at offset: {qualifiers_data_offset:d} '
          f'(0x{qualifiers_data_offset:08x}).\n'))

    qualifiers = {}
    qualifiers_data_offset = 0
    qualifier_index = 0

    while qualifiers_data_offset < len(qualifiers_data):
      record_data_offset = qualifiers_data_offset + qualifiers_data_offset
      data_type_map = self._GetDataTypeMap('qualifier_descriptor')

      context = dtfabric_data_maps.DataTypeMapContext()

      qualifier_descriptor = self._ReadStructureFromByteStream(
          qualifiers_data[qualifiers_data_offset:], record_data_offset,
          data_type_map, 'qualifier descriptor', context=context)

      if self._debug:
        self._DebugPrintStructureObject(
            qualifier_descriptor, self._DEBUG_INFO_QUALIFIER_DESCRIPTOR)

      qualifier_name = self._ReadQualifierName(
          qualifier_index, qualifier_descriptor.name_offset, values_data,
          values_data_offset)

      cim_data_type = self._CIM_DATA_TYPES.GetName(
          qualifier_descriptor.value_data_type)
      if cim_data_type == 'CIM-TYPE-BOOLEAN':
        qualifier_value = qualifier_descriptor.value_boolean

      elif cim_data_type in (
          'CIM-TYPE-SINT16', 'CIM-TYPE-SINT32', 'CIM-TYPE-SINT8',
          'CIM-TYPE-UINT8', 'CIM-TYPE-UINT16', 'CIM-TYPE-UINT16',
          'CIM-TYPE-SINT64', 'CIM-TYPE-UINT64'):
        qualifier_value = qualifier_descriptor.value_integer

      elif cim_data_type in ('CIM-TYPE-REAL32', 'CIM-TYPE-REAL64'):
        qualifier_value = qualifier_descriptor.value_floating_point

      elif cim_data_type == 'CIM-TYPE-STRING':
        qualifier_value = self._ReadCIMString(
            qualifier_descriptor.value_offset, values_data, values_data_offset,
            f'qualifier: {qualifier_index:d} value')

      elif cim_data_type == 'CIM-TYPE-DATETIME':
        # TODO: implement
        qualifier_value = None

      elif cim_data_type == 'CIM-TYPE-REFERENCE':
        # TODO: implement
        qualifier_value = None

      elif cim_data_type == 'CIM-TYPE-CHAR16':
        # TODO: implement
        qualifier_value = None

      else:
        qualifier_value = None

      if self._debug:
        self._DebugPrintText('\n')

      # TODO: preserve case of qualifier names?
      qualifier_name = qualifier_name.lower()
      qualifiers[qualifier_name] = qualifier_value

      qualifiers_data_offset += context.byte_size
      qualifier_index += 1

    return qualifiers

  def DebugPrint(self):
    """Prints class definition information."""
    self._DebugPrintText('Class definition:\n')
    self._DebugPrintValue('    Name', self.name)

    if self.super_class_name:
      self._DebugPrintValue('    Super class name', self.super_class_name)

    for qualifier_name, qualifier_value in self.qualifiers.items():
      self._DebugPrintValue(
          f'    Qualifier: {qualifier_name:s}', f'{qualifier_value!s}')

    for property_name, class_definition_property in self.properties.items():
      self._DebugPrintText(f'    Property: {property_name:s}\n')

      value_string = self._FormatIntegerAsDecimal(
          class_definition_property.index)
      self._DebugPrintValue('        Index', value_string)

      value_string = self._FormatIntegerAsOffset(
          class_definition_property.value_data_offset)
      self._DebugPrintValue('        Value data offset', value_string)

      for qualifier_name, qualifier_value in (
          class_definition_property.qualifiers.items()):
        self._DebugPrintValue(
            f'        Qualifier: {qualifier_name:s}', f'{qualifier_value!s}')

    self._DebugPrintText('\n')

  def IsAbstract(self):
    """Determines if the class is abstract.

    Returns:
      bool: True if abstract, False otherwise.
    """
    return self.qualifiers.get('abstract', False)

  def ReadClassDefinitionBlock(
      self, class_definition_data, record_data_offset=0):
    """Reads a class definition block.

    Args:
      class_definition_data (bytes): class definition data.
      record_data_offset (Optional[int]): offset of the class definition data
          relative to the start of the record data.

    Raises:
      ParseError: if the class definition cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          f'Reading class definition block at offset: {record_data_offset:d} '
          f'(0x{record_data_offset:08x}).\n'))

    data_type_map = self._GetDataTypeMap('class_definition_block')

    class_definition_block = self._ReadStructureFromByteStream(
        class_definition_data, record_data_offset, data_type_map,
        'class definition block')

    if self._debug:
      self._DebugPrintStructureObject(
          class_definition_block, self._DEBUG_INFO_CLASS_DEFINITION_BLOCK)

    super_class_name_block_offset = record_data_offset + 13

    qualifiers_block_offset = (
        super_class_name_block_offset +
        class_definition_block.super_class_name_block_size)

    value_data_offset = (
        qualifiers_block_offset +
        class_definition_block.qualifiers_block_size + (
            class_definition_block.number_of_property_descriptors * 8 ) +
        class_definition_block.default_value_size + 4)

    class_name = self._ReadCIMString(
        class_definition_block.name_offset, class_definition_block.values_data,
        value_data_offset, 'class name')

    super_class_name = None
    if class_definition_block.super_class_name_block_size > 4:
      super_class_name = self._ReadCIMString(
          0, class_definition_block.super_class_name_block_data,
          super_class_name_block_offset, 'super class name')

    class_qualifiers = {}
    if class_definition_block.qualifiers_block_size > 4:
      class_qualifiers = self._ReadQualifiers(
          class_definition_block.qualifiers_block_data, qualifiers_block_offset,
          class_definition_block.values_data, value_data_offset)

    class_properties = self._ReadClassDefinitionProperties(
        class_definition_block.property_descriptors,
        class_definition_block.values_data, value_data_offset)

    self.name = class_name
    self.properties = class_properties
    self.qualifiers = class_qualifiers
    self.super_class_name = super_class_name

    # TODO: complete handling methods
    # data_offset = (
    #     12 + (class_definition_object_record.super_class_name_size * 2) +
    #     class_definition_object_record.class_definition_block_size)

    # if data_offset < len(object_record_data):
    #   if self._debug:
    #     self._DebugPrintData('Methods data', object_record_data[data_offset:])

    #   self._ReadClassDefinitionMethods(object_record_data[data_offset:])


class ClassDefinitionReference(CIMObject):
  """Class definition reference.

  Attributes:
    data (bytes): instance block data.
    offset (int): offset of the instance block data.
    super_class_name (str): name of the parent class.
  """

  _DEBUG_INFO_CLASS_DEFINITION_OBJECT_RECORD = [
      ('super_class_name_size', 'Super class name size',
       '_FormatIntegerAsDecimal'),
      ('super_class_name', 'Super class name', '_FormatString'),
      ('date_time', 'Unknown date and time', '_FormatIntegerAsFiletime'),
      ('class_definition_block_size', 'Class definition block size',
       '_FormatIntegerAsDecimal'),
      ('class_definition_block_data', 'Class definition block data',
       '_FormatDataInHexadecimal')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes an instance reference.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(ClassDefinitionReference, self).__init__()
    self.data = None
    self.offset = None
    self.super_class_name = None

  def ReadObjectRecord(self, object_record_data):
    """Reads an instance reference from object record data.

    Args:
      object_record_data (bytes): object record data.

    Raises:
      ParseError: if the instance reference cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading class definition object record.\n')
      self._DebugPrintData('Object record data', object_record_data)

    data_type_map = self._GetDataTypeMap('class_definition_object_record')

    context = dtfabric_data_maps.DataTypeMapContext()

    class_definition_object_record = self._ReadStructureFromByteStream(
        object_record_data, 0, data_type_map,
        'class definition object record', context=context)

    if self._debug:
      self._DebugPrintStructureObject(
          class_definition_object_record,
          self._DEBUG_INFO_CLASS_DEFINITION_OBJECT_RECORD)

    self.data = class_definition_object_record.class_definition_block_data
    self.offset = context.byte_size
    self.super_class_name = class_definition_object_record.super_class_name


class InstanceReference(CIMObject):
  """Instance reference.

  Attributes:
    class_name(str): class name.
    class_name_hash (str): hash of the class name.
    data (bytes): instance block data.
    offset (int): offset of the instance block data.
  """

  _DEBUG_INFO_INSTANCE_OBJECT_RECORD = [
      ('class_name_hash', 'Class name hash', '_FormatString'),
      ('date_time1', 'Unknown date and time1', '_FormatIntegerAsFiletime'),
      ('date_time2', 'Unknown date and time2', '_FormatIntegerAsFiletime'),
      ('instance_block_size', 'Instance block size', '_FormatIntegerAsDecimal'),
      ('instance_block_data', 'Instance block data',
       '_FormatDataInHexadecimal')]

  def __init__(self, format_version, debug=False, output_writer=None):
    """Initializes an instance reference.

    Args:
      format_version (str): format version.
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(InstanceReference, self).__init__()
    self._format_version = format_version
    self.class_name = None
    self.class_name_hash = None
    self.data = None
    self.offset = None

  def ReadObjectRecord(self, object_record_data):
    """Reads an instance reference from object record data.

    Args:
      object_record_data (bytes): object record data.

    Raises:
      ParseError: if the instance reference cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading instance object record.\n')
      self._DebugPrintData('Object record data', object_record_data)

    if self._format_version == '2.1':
      data_type_map = self._GetDataTypeMap('instance_object_record_v1')
    else:
      data_type_map = self._GetDataTypeMap('instance_object_record_v2')

    instance_object_record = self._ReadStructureFromByteStream(
        object_record_data, 0, data_type_map, 'instance object record')

    if self._debug:
      self._DebugPrintStructureObject(
          instance_object_record, self._DEBUG_INFO_INSTANCE_OBJECT_RECORD)

    if self._format_version == '2.1':
      self.offset = 84
    else:
      self.offset = 144

    self.class_name_hash = instance_object_record.class_name_hash
    self.data = instance_object_record.instance_block_data


class Instance(CIMObject):
  """Instance.

  Attributes:
    class_name (str): class name.
    class_name_hash (str): hash of the class name.
    namespace (str): namespace.
    properties (dict[str, object]): instance property names and values.
  """

  _DEBUG_INFO_INSTANCE_BLOCK = [
      ('class_name_offset', 'Class name offset', '_FormatIntegerAsOffset'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal2'),
      ('property_state_bits', 'Property state bits',
       '_FormatDataInHexadecimal'),
      ('property_values_data', 'Property values data',
       '_FormatDataInHexadecimal'),
      ('qualifiers_block_size', 'Qualifiers block size',
       '_FormatIntegerAsDecimal'),
      ('qualifiers_block_data', 'Qualifiers block data',
       '_FormatDataInHexadecimal'),
      ('dynamic_block_type', 'Dynamic block type', '_FormatIntegerAsDecimal'),
      ('dynamic_block_value1', 'Dynamic block value1',
       '_FormatIntegerAsHexadecimal8')]

  _DEBUG_INFO_DYNAMIC_TYPE2_HEADER = [
      ('number_of_entries', 'Number of entries', '_FormatIntegerAsDecimal')]

  _DEBUG_INFO_DYNAMIC_TYPE2_ENTRY = [
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('data', 'Data', '_FormatDataInHexadecimal')]

  _FIXED_SIZE_VALUE_DATA_TYPES = frozenset([
      0x00000002, 0x00000003, 0x00000004, 0x00000005, 0x0000000b, 0x00000010,
      0x00000011, 0x00000012, 0x00000013, 0x00000014, 0x00000015])

  _STRING_VALUE_DATA_TYPES = frozenset([0x00000008, 0x00000065, 0x00000066])

  def __init__(self, debug=False, output_writer=None):
    """Initializes an instance.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(Instance, self).__init__(debug=debug, output_writer=output_writer)
    self.class_name = None
    self.class_name_hash = None
    self.namespace = None
    self.properties = {}

  def DebugPrint(self):
    """Prints instance information."""
    self._DebugPrintText('Instance:\n')

    if self.namespace:
      self._DebugPrintValue('    Namespace', self.namespace)

    self._DebugPrintValue('    Class name', self.class_name)

    if self.class_name_hash:
      self._DebugPrintValue('    Class name hash', self.class_name_hash)

    for property_name, property_value in self.properties.items():
      self._DebugPrintValue(
          f'    Property: {property_name:s}', f'{property_value!s}')

    self._DebugPrintText('\n')

  def ReadInstanceBlockData(
      self, class_value_data_map, instance_data, record_data_offset=0):
    """Reads the instance block data.

    Args:
      class_value_data_map (ClassValueDataMap): the class value data map.
      instance_data (bytes): instance data.
      record_data_offset (Optional[int]): offset of the class definition data
          relative to the start of the record data.

    Raises:
      ParseError: if the instance block data cannot be read.
    """
    data_type_map = self._GetDataTypeMap('instance_block')

    # 2 state bits per property, stored byte aligned.
    number_of_properties = len(class_value_data_map.properties)
    property_state_bits_size, remainder = divmod(number_of_properties, 4)
    if remainder > 0:
      property_state_bits_size += 1

    if self._debug:
      value_string = self._FormatIntegerAsDecimal(property_state_bits_size)
      self._DebugPrintValue('Property state bits size', value_string)

      value_string = self._FormatIntegerAsDecimal(
          class_value_data_map.properties_size)
      self._DebugPrintValue('Property values data size', value_string)

      self._DebugPrintText('\n')

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'property_state_bits_size': property_state_bits_size,
        'property_values_data_size': class_value_data_map.properties_size})

    instance_block = self._ReadStructureFromByteStream(
        instance_data, record_data_offset, data_type_map,
        'instance block', context=context)

    if self._debug:
      self._DebugPrintStructureObject(
          instance_block, self._DEBUG_INFO_INSTANCE_BLOCK)

    data_offset = context.byte_size

    if instance_block.dynamic_block_type == 2:
      data_type_map = self._GetDataTypeMap(
          'instance_block_dynamic_type2_header')

      dynamic_type2_header = self._ReadStructureFromByteStream(
           instance_data[data_offset:], record_data_offset + data_offset,
           data_type_map, 'dynamic block type 2 header')

      if self._debug:
        self._DebugPrintText('Dynamic type 2 header\n')
        self._DebugPrintStructureObject(
            dynamic_type2_header, self._DEBUG_INFO_DYNAMIC_TYPE2_HEADER)

      data_offset += 4

      data_type_map = self._GetDataTypeMap('instance_block_dynamic_type2_entry')

      for index in range(dynamic_type2_header.number_of_entries):
        context = dtfabric_data_maps.DataTypeMapContext()

        dynamic_type2_entry = self._ReadStructureFromByteStream(
             instance_data[data_offset:], record_data_offset + data_offset,
             data_type_map, 'dynamic block type 2 entry', context=context)

        if self._debug:
          self._DebugPrintText(f'Dynamic type 2 entry: {index:d}\n')
          self._DebugPrintStructureObject(
              dynamic_type2_entry, self._DEBUG_INFO_DYNAMIC_TYPE2_ENTRY)

        data_offset += context.byte_size

    data_type_map = self._GetDataTypeMap('uint32le')

    unknown_offset = self._ReadStructureFromByteStream(
         instance_data[data_offset:], record_data_offset + data_offset,
         data_type_map, 'unknown offset')

    if self._debug:
      value_string = self._FormatIntegerAsOffset(unknown_offset)
      self._DebugPrintValue('Unknown offset', value_string)

    data_offset += 4

    values_data = instance_data[data_offset:]

    if self._debug:
      self._DebugPrintData('Values data', values_data)

    self.class_name = self._ReadCIMString(
        instance_block.class_name_offset, values_data, data_offset,
        'class name')

    property_values_data = instance_block.property_values_data
    property_values_data_offset = 5 + len(instance_block.property_state_bits)

    for property_value_data_map in class_value_data_map.properties.values():
      property_map_offset = property_value_data_map.offset

      description = (
          f'property: {property_value_data_map.name:s} '
          f'value: {property_value_data_map.type_qualifier:s}')

      property_value = None
      if property_value_data_map.data_type in self._FIXED_SIZE_VALUE_DATA_TYPES:
        data_type_map_name = (
            f'property_value_{property_value_data_map.type_qualifier:s}')
        data_type_map = self._GetDataTypeMap(data_type_map_name)

        property_value = self._ReadStructureFromByteStream(
             property_values_data[property_map_offset:],
             property_values_data_offset + property_map_offset, data_type_map,
             description)

        if self._debug:
          description = (
               f'Property: {property_value_data_map.name:s} value: '
               f'{property_value_data_map.type_qualifier:s}')
          self._DebugPrintValue(description, property_value)

      elif property_value_data_map.data_type in self._STRING_VALUE_DATA_TYPES:
        description = (
            f'Property: {property_value_data_map.name:s} value: string offset')

        data_type_map = self._GetDataTypeMap('property_value_offset')

        string_offset = self._ReadStructureFromByteStream(
             property_values_data[property_map_offset:],
             property_values_data_offset + property_map_offset, data_type_map,
             description)

        if self._debug:
          self._DebugPrintValue(description, string_offset)

        # A string offset of 0 appears to indicate not set.
        if string_offset > 0:
          description = f'property: {property_value_data_map.name:s} value'
          property_value = self._ReadCIMString(
              string_offset, values_data, data_offset, description)

      elif property_value_data_map.data_type == 0x00002008:
        description = (
             f'Property: {property_value_data_map.name:s} value: string '
             f'array offset')

        data_type_map = self._GetDataTypeMap('property_value_offset')

        string_array_offset = self._ReadStructureFromByteStream(
             property_values_data[property_map_offset:],
             property_values_data_offset + property_map_offset, data_type_map,
             description)

        if self._debug:
          self._DebugPrintValue(description, string_array_offset)

        # A string array offset of 0 appears to indicate not set.
        if string_array_offset > 0:
          description = (
               f'Property: {property_value_data_map.name:s} value: string '
               f'array')

          data_type_map = self._GetDataTypeMap('cim_string_array')

          string_array = self._ReadStructureFromByteStream(
               values_data[string_array_offset:],
               data_offset + string_array_offset, data_type_map, description)

          property_value = []
          for string_index, string_offset in enumerate(
              string_array.string_offsets):
            description = (
                f'property: {property_value_data_map.name:s} value entry: '
                f'{string_index:d}')
            string_value = self._ReadCIMString(
                string_offset, values_data, data_offset, description)

            property_value.append(string_value)

      else:
        description = (
             f'Property: {property_value_data_map.name:s} value: array offset')

        data_type_map = self._GetDataTypeMap('property_value_offset')

        array_offset = self._ReadStructureFromByteStream(
             property_values_data[property_map_offset:],
             property_values_data_offset + property_map_offset, data_type_map,
             description)

        if self._debug:
          self._DebugPrintValue(description, array_offset)

      self.properties[property_value_data_map.name] = property_value

    if self._debug:
      self._DebugPrintText('\n')


class Registration(CIMObject):
  """Registration.

  Attributes:
    name (str): name of the registration.
  """

  _DEBUG_INFO_REGISTRATION_OBJECT_RECORD = [
      ('name_space_string_size', 'Name space string size',
       '_FormatIntegerAsDecimal'),
      ('name_space_string', 'Name space string', '_FormatString'),
      ('class_name_string_size', 'Class name string size',
       '_FormatIntegerAsDecimal'),
      ('class_name_string', 'Class name string', '_FormatString'),
      ('instance_name_string_size', 'Instance name string size',
       '_FormatIntegerAsDecimal'),
      ('instance_name_string', 'Instance name string', '_FormatString'),
      ('index_key_string_size', 'Index key string size',
       '_FormatIntegerAsDecimal'),
      ('index_key_string', 'Index key string', '_FormatString')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a registration.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(Registration, self).__init__(debug=debug, output_writer=output_writer)
    self.name = None

  def ReadObjectRecord(self, object_record_data):
    """Reads a registration from object record data.

    Args:
      object_record_data (bytes): object record data.

    Raises:
      ParseError: if the registration cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading registration object record.\n')
      self._DebugPrintData('Object record data', object_record_data)

    data_type_map = self._GetDataTypeMap('registration_object_record')

    registration_object_record = self._ReadStructureFromByteStream(
        object_record_data, 0, data_type_map, 'registration object record')

    if self._debug:
      self._DebugPrintStructureObject(
          registration_object_record,
          self._DEBUG_INFO_REGISTRATION_OBJECT_RECORD)


class CIMRepository(data_format.BinaryDataFormat):
  """A CIM repository.

  Attributes:
    format_version (str): format version.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _KEY_SEGMENT_SEPARATOR = '\\'
  _KEY_VALUE_SEPARATOR = '.'

  _KEY_VALUE_PAGE_NUMBER_INDEX = 1
  _KEY_VALUE_RECORD_IDENTIFIER_INDEX = 2
  _KEY_VALUE_DATA_SIZE_INDEX = 3

  _COMMON_NAMESPACES = [
      '__SystemClass',
      'ROOT',
      'ROOT\\Appv',
      'ROOT\\CIMV2',
      'ROOT\\CIMV2\\Applications',
      'ROOT\\CIMV2\\Applications\\MicrosoftIE',
      'ROOT\\CIMV2\\mdm',
      'ROOT\\CIMV2\\mdm\\dmmap',
      'ROOT\\CIMV2\\power',
      'ROOT\\CIMV2\\Security',
      'ROOT\\CIMV2\\Security\\MicrosoftTpm',
      'ROOT\\CIMV2\\Security\\MicrosoftVolumeEncryption',
      'ROOT\\CIMV2\\TerminalServices',
      'ROOT\\Cli',
      'ROOT\\dcim',
      'ROOT\\dcim\\sysman',
      'ROOT\\dcim\\sysman\\biosattributes',
      'ROOT\\dcim\\sysman\\wmisecurity',
      'ROOT\\DEFAULT',
      'ROOT\\directory',
      'ROOT\\directory\\LDAP',
      'ROOT\\Hardware',
      'ROOT\\Intel_ME',
      'ROOT\\Interop',
      'ROOT\\Microsoft',
      'ROOT\\Microsoft\\HomeNet',
      'ROOT\\Microsoft\\protectionManagement',
      'ROOT\\Microsoft\\SecurityClient',
      'ROOT\\Microsoft\\Uev',
      'ROOT\\Microsoft\\Windows',
      'ROOT\\Microsoft\\Windows\\AppBackgroundTask',
      'ROOT\\Microsoft\\Windows\\CI',
      'ROOT\\Microsoft\\Windows\\Defender',
      'ROOT\\Microsoft\\Windows\\DeliveryOptimization',
      'ROOT\\Microsoft\\Windows\\DesiredStateConfiguration',
      'ROOT\\Microsoft\\Windows\\DesiredStateConfigurationProxy',
      'ROOT\\Microsoft\\Windows\\DeviceGuard',
      'ROOT\\Microsoft\\Windows\\dfsn',
      'ROOT\\Microsoft\\Windows\\DHCP',
      'ROOT\\Microsoft\\Windows\\Dns',
      'ROOT\\Microsoft\\Windows\\EventTracingManagement',
      'ROOT\\Microsoft\\Windows\\HardwareManagement',
      'ROOT\\Microsoft\\Windows\\Hgs',
      'ROOT\\Microsoft\\Windows\\Powershellv3',
      'ROOT\\Microsoft\\Windows\\PS_MMAgent',
      'ROOT\\Microsoft\\Windows\\RemoteAccess',
      'ROOT\\Microsoft\\Windows\\RemoteAccess\\Client',
      'ROOT\\Microsoft\\Windows\\SMB',
      'ROOT\\Microsoft\\Windows\\SmbWitness',
      'ROOT\\Microsoft\\Windows\\Storage',
      'ROOT\\Microsoft\\Windows\\Storage\\Providers_v2',
      'ROOT\\Microsoft\\Windows\\Storage\\PT',
      'ROOT\\Microsoft\\Windows\\Storage\\PT\\Alt',
      'ROOT\\Microsoft\\Windows\\StorageReplica',
      'ROOT\\Microsoft\\Windows\\TaskScheduler',
      'ROOT\\Microsoft\\Windows\\Wdac',
      'ROOT\\Microsoft\\Windows\\WindowsUpdate',
      'ROOT\\Microsoft\\Windows\\winrm',
      'ROOT\\MSAPPS10',
      'ROOT\\msdtc',
      'ROOT\\MSPS',
      'ROOT\\nap',
      'ROOT\\NetFrameworkv1',
      'ROOT\\PEH',
      'ROOT\\Policy',
      'ROOT\\RSOP',
      'ROOT\\RSOP\\Computer',
      'ROOT\\RSOP\\User',
      'ROOT\\SECURITY',
      'ROOT\\SecurityCenter',
      'ROOT\\SecurityCenter2',
      'ROOT\\ServiceModel',
      'ROOT\\StandardCimv2',
      'ROOT\\StandardCimv2\\embedded',
      'ROOT\\subscription',
      'ROOT\\WMI']

  def __init__(self, debug=False, file_system_helper=None, output_writer=None):
    """Initializes a CIM repository.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      file_system_helper (Optional[FileSystemHelper]): file system helper.
      output_writer (Optional[OutputWriter]): output writer.
    """
    if not file_system_helper:
      file_system_helper = file_system.NativeFileSystemHelper()

    super(CIMRepository, self).__init__()
    self._debug = debug
    self._class_definitions_by_hash = {}
    self._class_value_data_map_by_hash = {}
    self._file_system_helper = file_system_helper
    self._index_binary_tree_file = None
    self._index_mapping_table = None
    self._index_root_page = None
    self._namespace_instances = []
    self._objects_data_file = None
    self._objects_mapping_table = None
    self._output_writer = output_writer
    self._repository_file = None

    self.format_version = None

  def _DebugPrintText(self, text):
    """Prints text for debugging.

    Args:
      text (str): text.
    """
    if self._output_writer:
      self._output_writer.WriteText(text)

  def _FormatFilenameAsGlob(self, filename):
    """Formats the filename as a case-insensitive glob.

    Args:
      filename (str): name of the file.

    Returns:
      str: case-insensitive glob of representation the filename.
    """
    glob_parts = []
    for character in filename:
      if character.isalpha():
        character_upper = character.upper()
        character_lower = character.lower()
        glob_part = f'[{character_upper:s}{character_lower:s}]'
      else:
        glob_part = character
      glob_parts.append(glob_part)

    return ''.join(glob_parts)

  def _GetActiveMappingFile(self, path):
    """Retrieves the active mapping file.

    Args:
      path (str): path to the CIM repository.

    Returns:
      MappingFile: mapping file or None if not available.

    Raises:
      ParseError: if the mapping version file cannot be read.
    """
    mapping_ver_file_number = None

    file_object = self._OpenMappingVersionFile(path)
    if file_object:
      data_type_map = self._GetDataTypeMap('uint32le')

      try:
        mapping_ver_file_number, _ = self._ReadStructureFromFileObject(
            file_object, 0, data_type_map, 'Mapping.ver')
      finally:
        file_object.close()

      if self._debug:
        self._DebugPrintText(
            f'Mapping.ver file number: {mapping_ver_file_number:d}\n')

    active_mapping_file = None
    active_mapping_file_number = None

    # Unsure how reliable this method is since multiple index[1-3].map files
    # can have the same sequence number but contain different mappings.
    for mapping_file_number in range(1, 4):
      filename_as_glob = self._FormatFilenameAsGlob(
          f'mapping{mapping_file_number:d}.map')
      path_with_glob = self._file_system_helper.JoinPath([
          path, filename_as_glob])
      mapping_file_glob = glob.glob(path_with_glob)
      if not mapping_file_glob:
        continue

      if self._debug:
        self._DebugPrintText(f'Reading: {mapping_file_glob[0]:s}\n')

      mapping_file = MappingFile(
          debug=self._debug, output_writer=self._output_writer)
      # TODO: change to only read limited information.
      mapping_file.Open(mapping_file_glob[0])

      if not active_mapping_file:
        active_mapping_file = mapping_file
        active_mapping_file_number = mapping_file_number
      elif mapping_file.sequence_number > active_mapping_file.sequence_number:
        active_mapping_file.Close()
        active_mapping_file = mapping_file
        active_mapping_file_number = mapping_file_number

    if (mapping_ver_file_number is not None and
        mapping_ver_file_number != active_mapping_file_number):
      logging.warning('Mismatch in active mapping file number.')

    if self._debug:
      self._DebugPrintText(
          f'Active mapping file: mapping{active_mapping_file_number:d}.map\n')

    return active_mapping_file

  def _GetClassDefinitionByName(self, class_name):
    """Retrieves a class definition by name.

    Args:
      class_name (str): name of the class definition.

    Returns:
      ClassDefinition: class definitions or None.
    """
    class_name_hash = self._GetHashFromString(class_name)
    return self._GetClassDefinitionByHash(class_name_hash)

  def _GetClassDefinitionByHash(self, class_name_hash):
    """Retrieves a class definition by hash of the name.

    Args:
      class_name_hash (str): hash of the class name.

    Returns:
      ClassDefinition: class definitions or None.
    """
    # TODO: change to resolve on demand and cache the resulting class
    # definition.
    class_definition = self._class_definitions_by_hash.get(
        class_name_hash.lower(), None)
    return class_definition

  def _GetClassValueMapByHash(self, class_name_hash):
    """Retrieves a class value map by hash of the name.

    Args:
      class_name_hash (str): hash of the class name.

    Returns:
      ClassValueMap: class value map or None.

    Raises:
      RuntimeError: if a class definition cannot be found.
    """
    lookup_key = class_name_hash.lower()

    class_value_data_map = self._class_value_data_map_by_hash.get(
        lookup_key, None)
    if not class_value_data_map:
      class_definition = self._GetClassDefinitionByHash(class_name_hash)
      if not class_definition:
        raise RuntimeError((
            f'Unable to retrieve definition of class with hash: '
            f'{class_name_hash:s}'))

      class_definitions = [class_definition]
      while class_definition.super_class_name:
        class_definition = self._GetClassDefinitionByName(
            class_definition.super_class_name)
        if not class_definition:
          raise RuntimeError((
              f'Unable to retrieve definition of class with name: '
              f'{class_definition.super_class_name:s}'))

        class_definitions.append(class_definition)

      # The ClassValueDataMap.Build functions want the class definitions
      # starting the with the base class first.
      class_definitions.reverse()

      if self._debug:
        for class_definition in class_definitions:
          class_definition.DebugPrint()

      class_value_data_map = ClassValueDataMap()
      class_value_data_map.Build(class_definitions)

      self._class_value_data_map_by_hash[lookup_key] = class_value_data_map

    return class_value_data_map

  def _GetHashFromString(self, string):
    """Retrieves the hash of a string.

    Args:
      string (str): string to hash.

    Returns:
      str: hash of the string.
    """
    string_data = string.upper().encode('utf-16-le')
    if self.format_version in ('2.0', '2.1'):
      string_hash = hashlib.md5(string_data)
    else:
      string_hash = hashlib.sha256(string_data)

    return string_hash.hexdigest()

  def _GetIndexPageByMappedPageNumber(self, mapped_page_number):
    """Retrieves a specific index page by mapped page number.

    Args:
      mapped_page_number (int): mapped page number.

    Returns:
      IndexBinaryTreePage: an index binary-tree page or None.
    """
    page_number = self._index_mapping_table.ResolveMappedPageNumber(
        mapped_page_number)

    index_page = self._index_binary_tree_file.GetPage(page_number)
    if not index_page:
      logging.warning(
          f'Unable to read index binary-tree page: {page_number:d}.')
      return None

    return index_page

  def _GetIndexFirstMappedPage(self):
    """Retrieves the index first mapped page.

    Returns:
      IndexBinaryTreePage: an index binary-tree page or None.

    Raises:
      RuntimeError: if the index first mapped page could not be determined.
    """
    page_number = self._index_mapping_table.ResolveMappedPageNumber(0)

    index_page = self._index_binary_tree_file.GetPage(page_number)
    if not index_page:
      raise RuntimeError((
          f'Unable to determine first mapped index binary-tree page: '
          f'{page_number:d}.'))

    if index_page.page_type != 0xaddd:
      raise RuntimeError((
          f'Unsupported first mapped index binary-tree page type: '
          f'0x{index_page.page_type:04x}'))

    return index_page

  def _GetIndexRootPage(self):
    """Retrieves the index root page.

    Returns:
      IndexBinaryTreePage: an index binary-tree page or None.
    """
    if not self._index_root_page:
      if self.format_version == '2.1':
        first_mapped_page = self._GetIndexFirstMappedPage()
        root_page_number = first_mapped_page.root_page_number
      else:
        root_page_number = 1

      page_number = self._index_mapping_table.ResolveMappedPageNumber(
          root_page_number)

      index_page = self._index_binary_tree_file.GetPage(page_number)
      if not index_page:
        logging.warning(
            f'Unable to read index binary-tree root page: {page_number:d}.')
        return None

      self._index_root_page = index_page

    return self._index_root_page

  def _GetKeysFromIndexPage(self, index_page):
    """Retrieves the keys from an index page.

    Yields:
      str: a CIM key.
    """
    if index_page:
      for key in index_page.keys:
        yield key

      for mapped_page_number in index_page.sub_pages:
        sub_index_page = self._GetIndexPageByMappedPageNumber(
            mapped_page_number)
        for key in self._GetKeysFromIndexPage(sub_index_page):
          yield key

  def _GetObjectsPageByMappedPageNumber(self, mapped_page_number, is_data_page):
    """Retrieves a specific objects page by mapped page number.

    Args:
      mapped_page_number (int): mapped page number.
      is_data_page (bool): True if the page is a data page.

    Returns:
      ObjectsDataPage: objects data page or None.
    """
    page_number = self._objects_mapping_table.ResolveMappedPageNumber(
        mapped_page_number)

    objects_page = self._objects_data_file.GetPage(page_number, is_data_page)
    if not objects_page:
      logging.warning(f'Unable to read objects data page: {page_number:d}.')
      return None

    return objects_page

  def _GetObjectRecord(
      self, data_type, mapped_page_number, record_identifier, data_size):
    """Retrieves a specific object record.

    Args:
      data_type (str): key data type.
      mapped_page_number (int): mapped page number.
      record_identifier (int): record identifier.
      data_size (int): data size.

    Returns:
      ObjectRecord: an object record or None.

    Raises:
      ParseError: if the objects records could not be parsed.
      RuntimeError: if the objects data file was not opened.
    """
    if not self._objects_data_file:
      raise RuntimeError('Objects.data file was not opened.')

    data_segments = []
    is_data_page = False
    data_segment_index = 0
    while data_size > 0:
      object_page = self._GetObjectsPageByMappedPageNumber(
          mapped_page_number, is_data_page)
      if not object_page:
        raise errors.ParseError((
            f'Unable to read objects record: {record_identifier:d} data '
            f'segment: {data_segment_index:d}.'))

      if not is_data_page:
        object_descriptor = object_page.GetObjectDescriptor(
            record_identifier, data_size)

        data_offset = object_descriptor.data_offset
        is_data_page = True
      else:
        data_offset = 0

      data_segment = self._objects_data_file.ReadObjectRecordDataSegment(
          object_page, data_offset, data_size)
      if not data_segment:
        raise errors.ParseError((
            f'Unable to read objects record: {record_identifier:d} data '
            f'segment: {data_segment_index:d}.'))

      data_segments.append(data_segment)
      data_size -= len(data_segment)
      data_segment_index += 1
      mapped_page_number += 1

    object_record_data = b''.join(data_segments)
    return ObjectRecord(data_type, object_record_data)

  def _GetObjectRecordValuesFromKey(self, key_segment):
    """Retrieves the object record values from a key segment.

    Args:
      key_segment (str): an index key segment.

    Returns:
      tuple[str, str, int, int, int]: data type, name hash, page number, record
          identifier and record data size of an object record or None.
    """
    if self._KEY_VALUE_SEPARATOR not in key_segment:
      return None, None, None, None, None

    key_values = key_segment.split(self._KEY_VALUE_SEPARATOR)
    if not len(key_values) == 4:
      logging.warning('Unsupported number of key values.')
      return None, None, None, None, None

    data_type, _, name_hash = key_values[0].partition('_')

    name_hash = name_hash.lower()

    try:
      page_number = int(key_values[self._KEY_VALUE_PAGE_NUMBER_INDEX], 10)
    except ValueError:
      logging.warning('Unsupported key value page number.')
      return None, None, None, None, None

    try:
      record_identifier = int(
          key_values[self._KEY_VALUE_RECORD_IDENTIFIER_INDEX], 10)
    except ValueError:
      logging.warning('Unsupported key value record identifier.')
      return None, None, None, None, None

    try:
      data_size = int(key_values[self._KEY_VALUE_DATA_SIZE_INDEX], 10)
    except ValueError:
      logging.warning('Unsupported key value data size.')
      return None, None, None, None, None

    return data_type, name_hash, page_number, record_identifier, data_size

  def _OpenIndexBinaryTreeFile(self, path):
    """Opens an index binary tree.

    Args:
      path (str): path to the CIM repository.

    Returns:
      IndexBinaryTreeFile: index binary tree file or None if not available.
    """
    filename_as_glob = self._FormatFilenameAsGlob('index.btr')
    index_binary_tree_file_glob = self._file_system_helper.JoinPath([
        path, filename_as_glob])

    index_binary_tree_file_path = glob.glob(index_binary_tree_file_glob)
    if not index_binary_tree_file_path:
      return None

    if self._debug:
      self._DebugPrintText(f'Reading: {index_binary_tree_file_path[0]:s}\n')

    index_binary_tree_file = IndexBinaryTreeFile(
        debug=self._debug, output_writer=self._output_writer)
    index_binary_tree_file.Open(index_binary_tree_file_path[0])

    return index_binary_tree_file

  def _OpenMappingFile(self, path, filename):
    """Opens a mapping file.

    Args:
      path (str): path to the CIM repository.
      filename (str): mapping file name.

    Returns:
      MappingFile: mapping file or None if not available.
    """
    filename_as_glob = self._FormatFilenameAsGlob(filename)
    mapping_file_glob = self._file_system_helper.JoinPath([
        path, filename_as_glob])

    mapping_file_path = glob.glob(mapping_file_glob)
    if not mapping_file_path:
      return None

    if self._debug:
      self._DebugPrintText(f'Reading: {mapping_file_path[0]:s}\n')

    mapping_file = MappingFile(
        debug=self._debug, output_writer=self._output_writer)
    mapping_file.Open(mapping_file_path[0])

    return mapping_file

  def _OpenMappingVersionFile(self, path):
    """Opens a mapping version file.

    Args:
      path (str): path to the CIM repository.

    Returns:
      file: file-like object or None if not available.
    """
    filename_as_glob = self._FormatFilenameAsGlob('mapping.ver')
    mapping_version_file_glob = self._file_system_helper.JoinPath([
        path, filename_as_glob])

    mapping_version_file_path = glob.glob(mapping_version_file_glob)
    if not mapping_version_file_path:
      return None

    return open(mapping_version_file_path[0], 'rb')  # pylint: disable=consider-using-with

  def _OpenObjectsDataFile(self, path):
    """Opens an objects data file.

    Args:
      path (str): path to the CIM repository.

    Returns:
      ObjectsDataFile: objects data file or None if not available.
    """
    filename_as_glob = self._FormatFilenameAsGlob('objects.data')
    objects_data_file_glob = self._file_system_helper.JoinPath([
        path, filename_as_glob])

    objects_data_file_path = glob.glob(objects_data_file_glob)
    if not objects_data_file_path:
      return None

    if self._debug:
      self._DebugPrintText(f'Reading: {objects_data_file_path[0]:s}\n')

    objects_data_file = ObjectsDataFile(
        debug=self._debug, output_writer=self._output_writer)
    objects_data_file.Open(objects_data_file_path[0])

    return objects_data_file

  def _OpenRepositoryFile(self, path):
    """Opens a repository file.

    Args:
      path (str): path to the CIM repository.

    Returns:
      RepositoryFile: repository file or None if not available.
    """
    filename_as_glob = self._FormatFilenameAsGlob('cim.rep')
    repository_file_glob = self._file_system_helper.JoinPath([
        path, filename_as_glob])

    repository_file_path = glob.glob(repository_file_glob)
    if not repository_file_path:
      return None

    if self._debug:
      self._DebugPrintText(f'Reading: {repository_file_path[0]:s}\n')

    repository_file = RepositoryFile(
        debug=self._debug, output_writer=self._output_writer)
    repository_file.Open(repository_file_path[0])

    return repository_file

  def _ReadClassDefinitionObjectRecords(self):
    """Reads class definition object records.

    Yields:
      tuple[str, ObjectRecord]: name hash and class definition object record.
    """
    index_page = self._GetIndexRootPage()
    for key in self._GetKeysFromIndexPage(index_page):
      key_segments = key.split(self._KEY_SEGMENT_SEPARATOR)

      data_type, name_hash, mapped_page_number, record_identifier, data_size = (
          self._GetObjectRecordValuesFromKey(key_segments[-1]))

      if data_type != 'CD':
        continue

      object_record = self._GetObjectRecord(
          data_type, mapped_page_number, record_identifier, data_size)

      yield name_hash, object_record

  def _ReadClassDefinitionsFromObjectRecords(self):
    """Reads the class definitions from object records."""
    for name_hash, object_record in self._ReadClassDefinitionObjectRecords():
      class_definition_reference = ClassDefinitionReference(
          debug=self._debug, output_writer=self._output_writer)
      class_definition_reference.ReadObjectRecord(object_record.data)

      class_definition = ClassDefinition(
          debug=self._debug, output_writer=self._output_writer)
      class_definition.ReadClassDefinitionBlock(
          class_definition_reference.data,
          record_data_offset=class_definition_reference.offset)

      self._class_definitions_by_hash[name_hash] = class_definition

    if self._debug:
      self._DebugPrintText('Class definitions:\n')
      for class_definition in self._class_definitions_by_hash.values():
        class_definition.DebugPrint()

  def _ReadInstance(self, instance_reference):
    """Reads an instance.

    Args:
      instance_reference (InstanceReference): instance reference.

    Returns:
      Instance: instance.
    """
    class_name_hash = instance_reference.class_name_hash
    if not class_name_hash:
      class_name_hash = self._GetHashFromString(instance_reference.class_name)

    class_value_data_map = self._GetClassValueMapByHash(class_name_hash)

    instance = Instance(debug=self._debug, output_writer=self._output_writer)

    instance.ReadInstanceBlockData(
        class_value_data_map, instance_reference.data,
        record_data_offset=instance_reference.offset)

    # pylint: disable=attribute-defined-outside-init
    instance.class_name = class_value_data_map.class_name
    instance.derivation = class_value_data_map.derivation
    instance.dynasty = class_value_data_map.dynasty
    instance.super_class_name = class_value_data_map.super_class_name

    if self._debug:
      instance.DebugPrint()

    return instance

  # TODO: remove after refactor
  def _ReadInstanceFromObjectRecord(self, object_record):
    """Reads an instance.

    Args:
      object_record (ObjectRecord): object record.

    Returns:
      Instance: instance or None.
    """
    instance_reference = InstanceReference(
        self.format_version, debug=self._debug,
        output_writer=self._output_writer)

    instance_reference.ReadObjectRecord(object_record.data)

    instance = Instance(
        debug=self._debug, output_writer=self._output_writer)

    class_value_data_map = self._GetClassValueMapByHash(
        instance_reference.class_name_hash)
    instance.ReadInstanceBlockData(
        class_value_data_map, instance_reference.data,
        record_data_offset=instance_reference.offset)

    if self._debug:
      instance.DebugPrint()

    # pylint: disable=attribute-defined-outside-init
    instance.class_name = class_value_data_map.class_name
    instance.derivation = class_value_data_map.derivation
    instance.dynasty = class_value_data_map.dynasty
    instance.super_class_name = class_value_data_map.super_class_name

    return instance

  def _ReadInstanceObjectRecords(self):
    """Reads instance object records.

    Yields:
      tuple[str, ObjectRecord]: name hash and instance object record.
    """
    index_page = self._GetIndexRootPage()
    for key in self._GetKeysFromIndexPage(index_page):
      key_segments = key.split(self._KEY_SEGMENT_SEPARATOR)

      data_type, name_hash, mapped_page_number, record_identifier, data_size = (
          self._GetObjectRecordValuesFromKey(key_segments[-1]))

      if data_type not in ('I', 'IL'):
        continue

      object_record = self._GetObjectRecord(
          data_type, mapped_page_number, record_identifier, data_size)

      yield name_hash, object_record

  def _ReadNamespacesFromObjectRecords(self):
    """Reads namespaces from object records."""
    class_name_hash = self._GetHashFromString('__NAMESPACE')

    object_record_values = set()
    instances_per_namespace = {}
    parent_namespaces = set()

    index_page = self._GetIndexRootPage()
    for key in self._GetKeysFromIndexPage(index_page):
      key_segments = key.split(self._KEY_SEGMENT_SEPARATOR)

      key_segment = key_segments[1]
      if not key_segment.startswith('NS_'):
        continue

      namespace_hash = key_segment[3:].lower()
      parent_namespaces.add(namespace_hash)

      _, _, key_segment = key_segments[2].partition('_')
      if key_segment.lower() != class_name_hash:
        continue

      data_type, _, mapped_page_number, record_identifier, data_size = (
          self._GetObjectRecordValuesFromKey(key_segments[-1]))

      if data_type not in ('I', 'IL'):
        continue

      if (mapped_page_number, record_identifier) in object_record_values:
        continue

      object_record = self._GetObjectRecord(
          data_type, mapped_page_number, record_identifier, data_size)

      object_record_values.add((mapped_page_number, record_identifier))

      instance = self._ReadInstanceFromObjectRecord(object_record)

      if namespace_hash not in instances_per_namespace:
        instances_per_namespace[namespace_hash] = []

      instances_per_namespace[namespace_hash].append(instance)

    namespaces_by_hash = {}
    for namespace in self._COMMON_NAMESPACES:
      namespace_hash = self._GetHashFromString(namespace)
      namespaces_by_hash[namespace_hash] = namespace

    for _ in range(5):
      unresolved_namespaces = set()
      for parent_namespace_hash in parent_namespaces:
        parent_namespace = namespaces_by_hash.get(parent_namespace_hash, None)
        if not parent_namespace:
          unresolved_namespaces.add(parent_namespace_hash)
          continue

        instances = instances_per_namespace.get(parent_namespace_hash, None)
        if not instances:
          continue

        for instance in instances:
          name_property = instance.properties.get('Name', None)

          namespace = '\\'.join([parent_namespace, name_property])

          namespace_hash = self._GetHashFromString(namespace)
          namespaces_by_hash[namespace_hash] = namespace

          instance.namespace = namespace
          self._namespace_instances.append(instance)

      parent_namespaces = unresolved_namespaces

  def Close(self):
    """Closes the CIM repository."""
    self._class_definitions_by_hash = {}
    self._class_value_data_map_by_hash = {}
    self._namespace_instances = []

    self._index_mapping_table = None
    self._index_root_page = None
    self._objects_mapping_table = None

    if self._objects_data_file:
      self._objects_data_file.Close()
      self._objects_data_file = None

    if self._index_binary_tree_file:
      self._index_binary_tree_file.Close()
      self._index_binary_tree_file = None

  def GetInstances(self):
    """Retrieves instances.

    Yields:
      Instance: an instance.
    """
    if self._repository_file:
      for instance in self._repository_file.ReadInstances():
        yield instance

    else:
      for _, object_record in self._ReadInstanceObjectRecords():
        instance_reference = InstanceReference(
            self.format_version, debug=self._debug,
            output_writer=self._output_writer)

        instance_reference.ReadObjectRecord(object_record.data)

        yield self._ReadInstance(instance_reference)

  def GetNamespaces(self):
    """Retrieves namespaces.

    Yields:
      Instance: an instance.
    """
    if self._repository_file:
      for instance in self._repository_file.ReadNamespaces():
        yield instance

    else:
      if not self._namespace_instances:
        self._ReadNamespacesFromObjectRecords()

      for instance in self._namespace_instances:
        yield instance

  def GetIndexKeys(self):
    """Retrieves the index keys.

    Yields:
      str: an index key path.
    """
    if self._index_binary_tree_file:
      index_page = self._GetIndexRootPage()
      for key in self._GetKeysFromIndexPage(index_page):
        yield key

  # TODO: remove after debugging.
  def GetObjectRecordByKey(self, key):
    """Retrieves a specific object record.

    Args:
      key (str): a CIM key.

    Returns:
      ObjectRecord: an object record or None.
    """
    key_segments = key.split(self._KEY_SEGMENT_SEPARATOR)

    data_type, _, mapped_page_number, record_identifier, data_size = (
        self._GetObjectRecordValuesFromKey(key_segments[-1]))

    return self._GetObjectRecord(
        data_type, mapped_page_number, record_identifier, data_size)

  def Open(self, path):
    """Opens the CIM repository.

    Args:
      path (str): path to the CIM repository or an individual file.
    """
    basename = os.path.basename(path).lower()

    if basename in ('index.map', 'mapping1.map', 'mapping2.map', 'mapping3.map',
                    'objects.map'):
      path = os.path.dirname(path)
      self._OpenMappingFile(path, basename)

      return

    if basename in ('cim.rep', 'index.btr'):
      path = os.path.dirname(path)

    active_mapping_file = None

    if basename == 'cim.rep':
      self.format_version = '2.0'

      self._repository_file = self._OpenRepositoryFile(path)
    else:
      index_mapping_file = self._OpenMappingFile(path, 'index.map')
      if not index_mapping_file:
        active_mapping_file = self._GetActiveMappingFile(path)
        index_mapping_file = active_mapping_file

      self._index_mapping_table = index_mapping_file.GetIndexMappingTable()

      if index_mapping_file.format_version == 1:
        self.format_version = '2.1'
      else:
        self.format_version = '2.2'

      if basename == 'index.btr' or not active_mapping_file:
        index_mapping_file.Close()

      self._index_binary_tree_file = self._OpenIndexBinaryTreeFile(path)

      if basename == 'index.btr':
        return

      objects_mapping_file = self._OpenMappingFile(path, 'objects.map')
      if not objects_mapping_file:
        if not active_mapping_file:
          active_mapping_file = self._GetActiveMappingFile(path)
        objects_mapping_file = active_mapping_file

      self._objects_mapping_table = (
          objects_mapping_file.GetObjectsMappingTable())

      objects_mapping_file.Close()

      self._objects_data_file = self._OpenObjectsDataFile(path)

      self._ReadClassDefinitionsFromObjectRecords()
