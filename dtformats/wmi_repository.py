# -*- coding: utf-8 -*-
"""WMI Common Information Model (CIM) repository files."""

import glob
import logging
import os

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import data_maps as dtfabric_data_maps

from dtformats import data_format
from dtformats import errors


class ClassDefinitionProperty(object):
  """Class definition property.

  Attributes:
    name (str): name of the property.
    offset (int): offset of the property.
    qualifiers (dict[str, object]): qualifiers.
  """

  def __init__(self):
    """Initializes a class property."""
    super(ClassDefinitionProperty, self).__init__()
    self.name = None
    self.offset = None
    self.qualifiers = {}


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


class ObjectRecord(object):
  """Object record.

  Attributes:
    data (bytes): object record data.
    data_type (str): object record data type.
  """

  def __init__(self, data_type, data):
    """Initializes an object record.

    Args:
      data_type (str): object record data type.
      data (bytes): object record data.
    """
    super(ObjectRecord, self).__init__()
    self.data = data
    self.data_type = data_type


class ObjectsDataPage(data_format.BinaryDataFormat):
  """An objects data page.

  Attributes:
    page_offset (int): offset of the page relative to the start of the file.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _OBJECT_DESCRIPTOR = _FABRIC.CreateDataTypeMap('cim_object_descriptor')

  _OBJECT_DESCRIPTOR_SIZE = _OBJECT_DESCRIPTOR.GetByteSize()

  _EMPTY_OBJECT_DESCRIPTOR = b'\x00' * _OBJECT_DESCRIPTOR_SIZE

  _DEBUG_INFO_OBJECT_DESCRIPTOR = [
      ('identifier', 'Identifier', '_FormatIntegerAsHexadecimal8'),
      ('data_offset', 'Data offset (relative)', '_FormatIntegerAsOffset'),
      ('data_file_offset', 'Data offset (file)', '_FormatIntegerAsOffset'),
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('data_checksum', 'Data checksum', '_FormatIntegerAsHexadecimal8')]

  PAGE_SIZE = 8192

  def __init__(self, debug=False, output_writer=None):
    """Initializes an objects data page.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(ObjectsDataPage, self).__init__(
        debug=debug, output_writer=output_writer)
    self._object_descriptors = []

    self.page_offset = None

  def _ReadObjectDescriptor(self, file_object):
    """Reads an object descriptor.

    Args:
      file_object (file): a file-like object.

    Returns:
      cim_object_descriptor: an object descriptor or None.

    Raises:
      ParseError: if the object descriptor cannot be read.
    """
    file_offset = file_object.tell()
    if self._debug:
      self._DebugPrintText(
          'Reading object descriptor at offset: 0x{0:08x}\n'.format(
              file_offset))

    object_descriptor_data = file_object.read(self._OBJECT_DESCRIPTOR_SIZE)

    if self._debug:
      self._DebugPrintData('Object descriptor data', object_descriptor_data)

    # The last object descriptor (terminator) is filled with 0-byte values.
    if object_descriptor_data == self._EMPTY_OBJECT_DESCRIPTOR:
      return None

    try:
      object_descriptor = self._OBJECT_DESCRIPTOR.MapByteStream(
          object_descriptor_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError(
          'Unable to parse object descriptor with error: {0!s}'.format(
              exception))

    setattr(object_descriptor, 'data_file_offset',
            file_offset + object_descriptor.data_offset)

    if self._debug:
      self._DebugPrintStructureObject(
          object_descriptor, self._DEBUG_INFO_OBJECT_DESCRIPTOR)

    return object_descriptor

  def _ReadObjectDescriptors(self, file_object):
    """Reads object descriptors.

    Args:
      file_object (file): a file-like object.

    Raises:
      ParseError: if the object descriptor cannot be read.
    """
    while True:
      object_descriptor = self._ReadObjectDescriptor(file_object)
      if not object_descriptor:
        break

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

  def ReadPage(self, file_object, file_offset, data_page=False):
    """Reads a page.

    Args:
      file_object (file): a file-like object.
      file_offset (int): offset of the page relative to the start of the file.
      data_page (Optional[bool]): True if the page is a data page.

    Raises:
      ParseError: if the page cannot be read.
    """
    file_object.seek(file_offset, os.SEEK_SET)

    if self._debug:
      self._DebugPrintText(
          'Reading objects data page at offset: 0x{0:08x}\n'.format(
              file_offset))

    self.page_offset = file_offset

    if not data_page:
      self._ReadObjectDescriptors(file_object)

  def ReadObjectRecordData(self, file_object, data_offset, data_size):
    """Reads the data of an object record.

    Args:
      file_object (file): a file-like object.
      data_offset (int): offset of the object record data relative to
          the start of the page.
      data_size (int): object record data size.

    Returns:
      bytes: object record data.

    Raises:
      ParseError: if the object record cannot be read.
    """
    # Make the offset relative to the start of the file.
    file_offset = self.page_offset + data_offset

    file_object.seek(file_offset, os.SEEK_SET)

    if self._debug:
      self._DebugPrintText(
          'Reading object record at offset: 0x{0:08x}\n'.format(file_offset))

    available_page_size = self.PAGE_SIZE - data_offset

    if data_size > available_page_size:
      read_size = available_page_size
    else:
      read_size = data_size

    return file_object.read(read_size)


class IndexBinaryTreeFile(data_format.BinaryDataFile):
  """Index binary-tree (Index.btr) file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _PAGE_SIZE = 8192

  _PAGE_HEADER = _FABRIC.CreateDataTypeMap('cim_page_header')

  _PAGE_HEADER_SIZE = _PAGE_HEADER.GetByteSize()

  _PAGE_BODY = _FABRIC.CreateDataTypeMap('cim_page_body')

  _PAGE_KEY = _FABRIC.CreateDataTypeMap('cim_page_key')

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

  def __init__(
      self, format_version, index_mapping_table, debug=False,
      output_writer=None):
    """Initializes an index binary-tree file.

    Args:
      format_version (int): format version.
      index_mapping_table (mapping_table): an index mapping table.
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(IndexBinaryTreeFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._first_mapped_page = None
    self._format_version = format_version
    self._index_mapping_table = index_mapping_table
    self._root_page = None

  def _DebugPrintPageBody(self, page_body):
    """Prints page body debug information.

    Args:
      page_body (cim_page_body): page body.
    """
    self._DebugPrintDecimalValue('Number of keys', page_body.number_of_keys)

    for index, value in enumerate(page_body.unknown2):
      description = 'Unknown2: {0:d}'.format(index)
      self._DebugPrintDecimalValue(description, value)

    for index, page_number in enumerate(page_body.sub_pages):
      description = 'Sub page: {0:d} mapped page number'.format(index)
      self._DebugPrintPageNumber(
          description, page_number,
          unavailable_page_numbers=set([0, 0xffffffff]))

    for index, key_offset in enumerate(page_body.key_offsets):
      description = 'Key: {0:d} offset'.format(index)
      value_string = '0x{0:04x}'.format(key_offset)
      self._DebugPrintValue(description, value_string)

    value_string = '{0:d} ({1:d} bytes)'.format(
        page_body.key_data_size, page_body.key_data_size * 2)
    self._DebugPrintValue('Key data size', value_string)

    self._DebugPrintData('Key data', page_body.key_data)

    self._DebugPrintDecimalValue(
        'Number of values', page_body.number_of_values)

    for index, offset in enumerate(page_body.value_offsets):
      description = 'Value: {0:d} offset'.format(index)
      value_string = '0x{0:04x}'.format(offset)
      self._DebugPrintValue(description, value_string)

    value_string = '{0:d} ({1:d} bytes)'.format(
        page_body.value_data_size, page_body.value_data_size * 2)
    self._DebugPrintValue('Value data size', value_string)

    self._DebugPrintData('Value data', page_body.value_data)

  def _DebugPrintPageNumber(
      self, description, page_number, unavailable_page_numbers=None):
    """Prints a page number debug information.

    Args:
      description (str): description.
      page_number (int): page number.
      unavailable_page_numbers (Optional[set[int]]): unavailable page numbers.
    """
    if not unavailable_page_numbers:
      unavailable_page_numbers = set()

    if page_number in unavailable_page_numbers:
      value_string = '0x{0:08x} (unavailable)'.format(page_number)
    else:
      value_string = '{0:d}'.format(page_number)

    self._DebugPrintValue(description, value_string)

  def _FormatIntegerAsPageType(self, integer):
    """Formats an integer as a page type.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a page type.
    """
    page_type_string = self._PAGE_TYPES.get(integer, 'Unknown')
    return '0x{0:04x} ({1:s})'.format(integer, page_type_string)

  def _GetPage(self, page_number):
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
      self._DebugPrintText(
          'Reading page: {0:d} at offset: {1:d} (0x{1:08x}).\n'.format(
              file_offset // self._PAGE_SIZE, file_offset))

    page_data = self._ReadData(
        file_object, file_offset, self._PAGE_SIZE, 'index binary-tree page')

    if self._debug:
      self._DebugPrintData(
          'Page header data', page_data[:self._PAGE_HEADER_SIZE])

    try:
      page_header = self._PAGE_HEADER.MapByteStream(page_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          'Unable to map page header data at offset: 0x{0:08x} with error: '
          '{1!s}').format(file_offset, exception))

    if self._debug:
      self._DebugPrintStructureObject(page_header, self._DEBUG_INFO_PAGE_HEADER)

    index_binary_tree_page = IndexBinaryTreePage()
    index_binary_tree_page.page_type = page_header.page_type
    index_binary_tree_page.root_page_number = page_header.root_page_number

    page_data_size = self._PAGE_HEADER_SIZE
    if page_header.page_type == 0xaccc:
      context = dtfabric_data_maps.DataTypeMapContext()

      try:
        page_body = self._PAGE_BODY.MapByteStream(
            page_data[self._PAGE_HEADER_SIZE:], context=context)
      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError((
            'Unable to map page body data at offset: 0x{0:08x} with error: '
            '{1!s}').format(file_offset, exception))

      page_data_size += context.byte_size

      if self._debug:
        self._DebugPrintData(
            'Page body data', page_data[self._PAGE_HEADER_SIZE:page_data_size])

      if self._debug:
        self._DebugPrintPageBody(page_body)

    if self._debug:
      trailing_data_size = self._PAGE_SIZE - page_data_size
      if trailing_data_size > 0:
        self._DebugPrintData('Trailing data', page_data[page_data_size:])

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

        key_path = '{0:s}{1:s}'.format(
            self._KEY_SEGMENT_SEPARATOR,
            self._KEY_SEGMENT_SEPARATOR.join(key_segments))

        index_binary_tree_page.keys.append(key_path)

    return index_binary_tree_page

  def _ReadPageKeyData(self, index_binary_tree_page, page_body):
    """Reads page key data.

    Args:
      index_binary_tree_page (IndexBinaryTreePage): index binary-tree page.
      page_body (cim_page_body): page body.

    Raises:
      ParseError: if the page key data cannot be read.
    """
    key_data = page_body.key_data

    for index, key_offset in enumerate(page_body.key_offsets):
      page_key_offset = key_offset * 2

      if self._debug:
        description = 'Page key: {0:d} offset'.format(index)
        value_string = '{0:d} (0x{0:08x})'.format(page_key_offset)
        self._DebugPrintValue(description, value_string)

      try:
        page_key = self._PAGE_KEY.MapByteStream(key_data[page_key_offset:])
      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError(
            'Unable to parse page key: {0:d} with error: {1:s}'.format(
                index, exception))

      page_key_size = page_key_offset + 2 + (page_key.number_of_segments * 2)

      if self._debug:
        description = 'Page key: {0:d} data:'.format(index)
        self._DebugPrintData(
            description, key_data[page_key_offset:page_key_size])

      index_binary_tree_page.page_key_segments.append(page_key.segments)

      if self._debug:
        description = 'Page key: {0:d} number of segments'.format(index)
        self._DebugPrintDecimalValue(description, page_key.number_of_segments)

        description = 'Page key: {0:d} segments'.format(index)
        value_string = ', '.join([
            '{0:d}'.format(segment_index)
            for segment_index in page_key.segments])
        self._DebugPrintValue(description, value_string)

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
            'Unable to parse page value: {0:d} string with error: '
            '{1!s}').format(index, exception))

      if self._debug:
        description = 'Page value: {0:d} data'.format(index)
        self._DebugPrintValue(description, value_string)

      index_binary_tree_page.page_values.append(value_string)

    if self._debug and index_binary_tree_page.page_value_offsets:
      self._DebugPrintText('\n')

  def _ResolveMappedPageNumber(self, mapped_page_number):
    """Resolves a mapped page number.

    Args:
      mapped_page_number (int): mapped page number.

    Returns:
      int: (physical) page number.
    """
    mapping_table_entry = self._index_mapping_table.entries[mapped_page_number]
    return mapping_table_entry.page_number

  def GetFirstMappedPage(self):
    """Retrieves the first mapped page.

    Returns:
      IndexBinaryTreePage: an index binary-tree page or None.
    """
    if not self._first_mapped_page:
      page_number = self._ResolveMappedPageNumber(0)

      index_page = self._GetPage(page_number)
      if not index_page:
        logging.warning((
            'Unable to read first mapped index binary-tree page: '
            '{0:d}.').format(page_number))
        return None

      if index_page.page_type != 0xaddd:
        logging.warning((
            'Unsupported first mapped index binary-tree page type: '
            '0x{0:04x}').format(index_page.page_type))

      self._first_mapped_page = index_page

    return self._first_mapped_page

  def GetMappedPage(self, mapped_page_number):
    """Retrieves a specific mapped page.

    Args:
      mapped_page_number (int): mapped page number.

    Returns:
      IndexBinaryTreePage: an index binary-tree page or None.
    """
    page_number = self._ResolveMappedPageNumber(mapped_page_number)

    index_page = self._GetPage(page_number)
    if not index_page:
      logging.warning('Unable to read index binary-tree page: {0:d}.'.format(
          page_number))
      return None

    return index_page

  def GetRootPage(self):
    """Retrieves the root page.

    Returns:
      IndexBinaryTreePage: an index binary-tree page or None.
    """
    if not self._root_page:
      if self._format_version == 1:
        first_mapped_page = self.GetFirstMappedPage()
        if not first_mapped_page:
          return None

        root_page_number = first_mapped_page.root_page_number
      else:
        root_page_number = 1

      page_number = self._ResolveMappedPageNumber(root_page_number)

      index_page = self._GetPage(page_number)
      if not index_page:
        logging.warning(
            'Unable to read index binary-tree root page: {0:d}.'.format(
                page_number))
        return None

      self._root_page = index_page

    return self._root_page

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
    format_version (int): format version.
    sequence_number (int): sequence number.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _UINT32LE = _FABRIC.CreateDataTypeMap('uint32le')

  _UINT32LE_SIZE = _UINT32LE.GetByteSize()

  _DEBUG_INFO_FILE_FOOTER = [
      ('signature', 'Signature', '_FormatIntegerAsHexadecimal8'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8')]

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
    super(MappingFile, self).__init__(
        debug=debug, output_writer=output_writer)
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
      self._DebugPrintText('  Entry: {0:d}:\n'.format(index))
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
      description = '  Entry: {0:d} page number'.format(index)
      value_string = self._FormatIntegerAsPageNumber(page_number)
      self._DebugPrintValue(description, value_string)

    self._DebugPrintText('\n')

  def _FormatIntegerAsPageNumber(self, integer):
    """Formats an integer as a page number.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a page number.
    """
    if integer in self._unavailable_page_numbers:
      return '0x{0:08x} (unavailable)'.format(integer)

    return '{0:d}'.format(integer)

  def _ReadFileFooter(self, file_object, format_version=None):
    """Reads the file footer.

    Args:
      file_object (file): file-like object.
      format_version (Optional[int]): format version.

    Returns:
      cim_map_footer: file footer.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    if not format_version:
      format_version = self.format_version

    file_offset = file_object.tell()

    if format_version == 1:
      data_type_map = self._GetDataTypeMap('cim_map_footer_v1')
    else:
      data_type_map = self._GetDataTypeMap('cim_map_footer_v2')

    file_footer, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'file footer')

    if self._debug:
      self._DebugPrintStructureObject(file_footer, self._DEBUG_INFO_FILE_FOOTER)

    return file_footer

  def _ReadDetermineFormatVersion(self, file_object):
    """Reads the file footer to determine the format version.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    file_object.seek(-4, os.SEEK_END)

    try:
      file_footer = self._ReadFileFooter(file_object, format_version=1)
      self.format_version = 1

    except errors.ParseError:
      file_footer = None

    if not file_footer:
      file_object.seek(-8, os.SEEK_END)

      try:
        file_footer = self._ReadFileFooter(file_object, format_version=2)
        self.format_version = 2
      except errors.ParseError:
        file_footer = None

    if not file_footer:
      raise errors.ParseError('Unable to read file footer.')

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (file): file-like object.

    Returns:
      cim_map_header: file header.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()

    if self.format_version == 1:
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
      mapping_table: index mapping table.
    """
    return self._mapping_table2 or self._mapping_table1

  def GetObjectsMappingTable(self):
    """Retrieves the objects mapping table.

    Returns:
      mapping_table: objects mapping table.
    """
    return self._mapping_table1

  def ReadFileObject(self, file_object):
    """Reads a mappings file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._ReadDetermineFormatVersion(file_object)

    file_object.seek(0, os.SEEK_SET)

    file_header = self._ReadFileHeader(file_object)
    self.sequence_number = file_header.sequence_number

    self._mapping_table1 = self._ReadMappingTable(file_object)

    self._ReadUnknownTable(file_object)
    self._ReadFileFooter(file_object, format_version=1)

    if self.format_version == 2:
      self._ReadFileHeader(file_object)

      self._mapping_table2 = self._ReadMappingTable(file_object)

      self._ReadUnknownTable(file_object)
      self._ReadFileFooter(file_object, format_version=2)


class ObjectsDataFile(data_format.BinaryDataFile):
  """An objects data (Objects.data) file."""

  _KEY_SEGMENT_SEPARATOR = '\\'
  _KEY_VALUE_SEPARATOR = '.'

  _KEY_VALUE_PAGE_NUMBER_INDEX = 1
  _KEY_VALUE_RECORD_IDENTIFIER_INDEX = 2
  _KEY_VALUE_DATA_SIZE_INDEX = 3

  def __init__(self, objects_mapping_table, debug=False, output_writer=None):
    """Initializes an objects data file.

    Args:
      objects_mapping_table (mapping_table): objects mapping table.
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(ObjectsDataFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._objects_mapping_table = objects_mapping_table

  def _GetKeyValues(self, key):
    """Retrieves the key values from the key.

    Args:
      key (str): a CIM key.

    Returns:
      tuple[str, int, int, int]: name of the key, corresponding page number,
          record identifier and record data size or None.
    """
    _, _, key = key.rpartition(self._KEY_SEGMENT_SEPARATOR)

    if self._KEY_VALUE_SEPARATOR not in key:
      return None

    key_values = key.split(self._KEY_VALUE_SEPARATOR)
    if not len(key_values) == 4:
      logging.warning('Unsupported number of key values.')
      return None

    try:
      page_number = int(key_values[self._KEY_VALUE_PAGE_NUMBER_INDEX], 10)
    except ValueError:
      logging.warning('Unsupported key value page number.')
      return None

    try:
      record_identifier = int(
          key_values[self._KEY_VALUE_RECORD_IDENTIFIER_INDEX], 10)
    except ValueError:
      logging.warning('Unsupported key value record identifier.')
      return None

    try:
      data_size = int(key_values[self._KEY_VALUE_DATA_SIZE_INDEX], 10)
    except ValueError:
      logging.warning('Unsupported key value data size.')
      return None

    return key_values[0], page_number, record_identifier, data_size

  def _GetPage(self, page_number, data_page=False):
    """Retrieves a specific page.

    Args:
      page_number (int): page number.
      data_page (Optional[bool]): True if the page is a data page.

    Returns:
      ObjectsDataPage: objects data page or None.
    """
    file_offset = page_number * ObjectsDataPage.PAGE_SIZE
    if file_offset >= self._file_size:
      return None

    # TODO: cache pages.
    return self._ReadPage(file_offset, data_page=data_page)

  def _ReadPage(self, file_offset, data_page=False):
    """Reads a page.

    Args:
      file_offset (int): offset of the page relative to the start of the file.
      data_page (Optional[bool]): True if the page is a data page.

    Return:
      ObjectsDataPage: objects data page or None.

    Raises:
      ParseError: if the page cannot be read.
    """
    objects_page = ObjectsDataPage(
        debug=self._debug, output_writer=self._output_writer)
    objects_page.ReadPage(self._file_object, file_offset, data_page=data_page)
    return objects_page

  def _ResolveMappedPageNumber(self, mapped_page_number):
    """Resolves a mapped page number.

    Args:
      mapped_page_number (int): mapped page number.

    Returns:
      int: (physical) page number.
    """
    mapping_table_entry = self._objects_mapping_table.entries[
        mapped_page_number]
    return mapping_table_entry.page_number

  def GetMappedPage(self, mapped_page_number, data_page=False):
    """Retrieves a specific mapped page.

    Args:
      mapped_page_number (int): mapped page number.
      data_page (Optional[bool]): True if the page is a data page.

    Returns:
      ObjectsDataPage: objects data page or None.
    """
    page_number = self._ResolveMappedPageNumber(mapped_page_number)

    objects_page = self._GetPage(page_number, data_page=data_page)
    if not objects_page:
      logging.warning('Unable to read objects data page: {0:d}.'.format(
          page_number))
      return None

    return objects_page

  def GetObjectRecordByKey(self, key):
    """Retrieves a specific object record.

    Args:
      key (str): a CIM key.

    Returns:
      ObjectRecord: an object record or None.

    Raises:
      ParseError: if the object record cannot be retrieved.
    """
    key, mapped_page_number, record_identifier, data_size = (
        self._GetKeyValues(key))

    data_segments = []
    data_page = False
    data_segment_index = 0
    while data_size > 0:
      object_page = self.GetMappedPage(mapped_page_number, data_page=data_page)
      if not object_page:
        errors.ParseError(
            'Unable to read objects record: {0:d} data segment: {1:d}.'.format(
                record_identifier, data_segment_index))

      if not data_page:
        object_descriptor = object_page.GetObjectDescriptor(
            record_identifier, data_size)

        data_offset = object_descriptor.data_offset
        data_page = True
      else:
        data_offset = 0

      data_segment = object_page.ReadObjectRecordData(
          self._file_object, data_offset, data_size)
      if not data_segment:
        errors.ParseError(
            'Unable to read objects record: {0:d} data segment: {1:d}.'.format(
                record_identifier, data_segment_index))

      data_segments.append(data_segment)
      data_size -= len(data_segment)
      data_segment_index += 1
      mapped_page_number += 1

    _, _, key_name = key.rpartition('\\')
    data_type, _, _ = key_name.partition('_')
    object_record_data = b''.join(data_segments)

    return ObjectRecord(data_type, object_record_data)

  def ReadFileObject(self, file_object):
    """Reads an objects data file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._file_object = file_object


class ClassDefinition(data_format.BinaryDataFormat):
  """Class definition.

  Attributes:
    name (str): name of the class.
    properties (dict[str, ClassDefinitionProperty]): properties.
    qualifiers (dict[str, object]): qualifiers.
    super_class_name (str): name of the super class.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _CIM_DATA_TYPES = _FABRIC.CreateDataTypeMap('cim_data_types')

  _DEBUG_INFO_CLASS_DEFINITION_OBJECT_RECORD = [
      ('super_class_name_size', 'Super class name size',
       '_FormatIntegerAsDecimal'),
      ('super_class_name', 'Super class name', '_FormatString'),
      ('date_time', 'Unknown date and time', '_FormatIntegerAsFiletime'),
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('data', 'Data', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_CLASS_DEFINITION_HEADER = [
      ('unknown1', 'Unknown1', '_FormatIntegerAsDecimal'),
      ('class_name_offset', 'Class name offset', '_FormatIntegerAsOffset'),
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
      ('properties_block_size', 'Properties block size',
       '_FormatIntegerAsPropertiesBlockSize'),
      ('properties_block_data', 'Properties block data',
       '_FormatDataInHexadecimal')]

  _DEBUG_INFO_CLASS_NAME = [
      ('string_flags', 'Class name string flags',
       '_FormatIntegerAsHexadecimal2'),
      ('string', 'Class name string', '_FormatString')]

  _DEBUG_INFO_QUALIFIER_DESCRIPTOR = [
      ('name_offset', 'Name offset', '_FormatIntegerAsOffset'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal2'),
      ('value_data_type', 'Value data type', '_FormatIntegerAsDataType'),
      ('value_boolean', 'Value', '_FormatIntegerAsDecimal'),
      ('value_floating_point', 'Value', '_FormatFloatingPoint'),
      ('value_integer', 'Value', '_FormatIntegerAsDecimal'),
      ('value_offset', 'Value offset', '_FormatIntegerAsOffset')]

  _DEBUG_INFO_PROPERTY_DEFINITION = [
      ('value_data_type', 'Value data type', '_FormatIntegerAsDataType'),
      ('index', 'Index', '_FormatIntegerAsDecimal'),
      ('offset', 'Offset', '_FormatIntegerAsOffset'),
      ('level', 'Level', '_FormatIntegerAsDecimal'),
      ('qualifiers_block_size', 'Qualifiers block size',
       '_FormatIntegerAsDecimal'),
      ('qualifiers_block_data', 'Qualifiers block data',
       '_FormatDataInHexadecimal'),
      ('value_boolean', 'Value', '_FormatIntegerAsDecimal'),
      ('value_floating_point', 'Value', '_FormatFloatingPoint'),
      ('value_integer', 'Value', '_FormatIntegerAsDecimal'),
      ('value_offset', 'Value offset', '_FormatIntegerAsOffset')]

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
    self.properties = {}
    self.qualifiers = {}
    self.super_class_name = None

  def _DebugPrintCIMString(self, cim_string):
    """Prints CIM string information.

    Args:
      cim_string (cim_string): CIM string.
    """
    value_string = '0x{0:02x}'.format(cim_string.string_flags)
    self._DebugPrintValue('String flags', value_string)

    self._DebugPrintValue('String', cim_string.string)

  def _DebugPrintQualifierName(self, index, cim_string):
    """Prints qualifier name information.

    Args:
      index (int): qualifier index.
      cim_string (cim_string): CIM string.
    """
    description = 'Qualifier: {0:d} name string flags'.format(index)
    value_string = '0x{0:02x}'.format(cim_string.string_flags)
    self._DebugPrintValue(description, value_string)

    description = 'Qualifier: {0:d} name string'.format(index)
    self._DebugPrintValue(description, cim_string.string)

  def _DebugPrintPropertyName(self, index, cim_string):
    """Prints property name information.

    Args:
      index (int): property index.
      cim_string (cim_string): CIM string.
    """
    description = 'Property: {0:d} name string flags'.format(index)
    value_string = '0x{0:02x}'.format(cim_string.string_flags)
    self._DebugPrintValue(description, value_string)

    description = 'Property: {0:d} name string'.format(index)
    self._DebugPrintValue(description, cim_string.string)

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
      description = '    Property descriptor: {0:d} name offset'.format(index)
      value_string = '0x{0:08x}'.format(property_descriptor.name_offset)
      line = self._FormatValue(description, value_string)
      lines.append(line)

      description = '    Property descriptor: {0:d} definition offset'.format(
          index)
      value_string = '0x{0:08x}'.format(property_descriptor.definition_offset)
      line = self._FormatValue(description, value_string)
      lines.append(line)

    return ''.join(lines)

  def _FormatIntegerAsDataType(self, integer):
    """Formats an integer as a data type.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a data type.
    """
    data_type_string = self._CIM_DATA_TYPES.GetName(integer & 0x0fff)
    # TODO: format flags 0x2000 and 0x4000
    return '0x{0:08x} ({1:s})'.format(integer, data_type_string or 'UNKNOWN')

  def _FormatIntegerAsPropertiesBlockSize(self, integer):
    """Formats an integer as a properties block size.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a properties block size.
    """
    return '{0:d} (0x{1:08x})'.format(integer & 0x7fffffff, integer)

  def _ReadClassDefinitionHeader(
      self, class_definition_data, record_data_offset):
    """Reads a class definition header.

    Args:
      class_definition_data (bytes): class definition data.
      record_data_offset (int): offset of the class definition data relative to
          the start of the record data.

    Returns:
      class_definition_header: class definition header.

    Raises:
      ParseError: if the class definition cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          'Reading class definition header at offset: {0:d} '
          '(0x{0:08x}).\n').format(record_data_offset))

    data_type_map = self._GetDataTypeMap('class_definition_header')

    try:
      class_definition_header = self._ReadStructureFromByteStream(
          class_definition_data, record_data_offset, data_type_map,
          'Class definition header')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map class definition header data at offset: 0x{0:08x} '
          'with error: {1!s}').format(record_data_offset, exception))

    if self._debug:
      self._DebugPrintStructureObject(
          class_definition_header, self._DEBUG_INFO_CLASS_DEFINITION_HEADER)

    return class_definition_header

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
          'Reading class definition methods at offset: {0:d} '
          '(0x{0:08x}).\n').format(record_data_offset))

    data_type_map = self._GetDataTypeMap('class_definition_methods')

    try:
      class_definition_methods = self._ReadStructureFromByteStream(
          class_definition_data, record_data_offset, data_type_map,
          'Class definition methods')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map class definition methods data at offset: 0x{0:08x} '
          'with error: {1!s}').format(record_data_offset, exception))

    methods_block_size = class_definition_methods.methods_block_size

    if self._debug:
      value_string = '{0:d} (0x{1:08x})'.format(
          methods_block_size & 0x7fffffff, methods_block_size)
      self._DebugPrintValue('Methods block size', value_string)

      self._DebugPrintData(
          'Methods block data', class_definition_methods.methods_block_data)

  def _ReadClassDefinitionName(
      self, name_offset, properties_data, properties_data_offset):
    """Reads a class definition name.

    Args:
      name_offset (int): name offset.
      properties_data (bytes): class definition properties data.
      properties_data_offset (int): offset of the class definition
          properties data relative to the start of the record data.

    Returns:
      str: class name.

    Raises:
      ParseError: if the name cannot be read.
    """
    record_data_offset = properties_data_offset + name_offset
    data_type_map = self._GetDataTypeMap('cim_string')

    try:
      class_name = self._ReadStructureFromByteStream(
          properties_data[name_offset:], record_data_offset, data_type_map,
          'Class name')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map class name data at offset: 0x{0:08x} with error: '
          '{1!s}').format(record_data_offset, exception))

    if self._debug:
      self._DebugPrintStructureObject(class_name, self._DEBUG_INFO_CLASS_NAME)

    return class_name.string

  def _ReadClassDefinitionPropertyDefinition(
      self, definition_offset, properties_data, properties_data_offset):
    """Reads a class definition property definition.

    Args:
      definition_offset (int): definition offset.
      properties_data (bytes): class definition properties data.
      properties_data_offset (int): offset of the class definition
          properties data relative to the start of the record data.

    Returns:
      property_definition: property definition.

    Raises:
      ParseError: if the property name cannot be read.
    """
    record_data_offset = properties_data_offset + definition_offset
    data_type_map = self._GetDataTypeMap('property_definition')

    try:
      property_definition = self._ReadStructureFromByteStream(
          properties_data[definition_offset:], record_data_offset,
          data_type_map, 'Property definition')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map property definition data at offset: 0x{0:08x} with '
          'error: {1!s}').format(record_data_offset, exception))

    if self._debug:
      self._DebugPrintStructureObject(
          property_definition, self._DEBUG_INFO_PROPERTY_DEFINITION)

    return property_definition

  def _ReadClassDefinitionPropertyName(
      self, property_index, name_offset, properties_data,
      properties_data_offset):
    """Reads a class definition property name.

    Args:
      index (int): property index.
      name_offset (int): name offset.
      properties_data (bytes): class definition properties data.
      properties_data_offset (int): offset of the class definition
          properties data relative to the start of the record data.

    Returns:
      str: property name.

    Raises:
      ParseError: if the property name cannot be read.
    """
    if name_offset & 0x80000000:
      name_index = name_offset & 0x7fffffff
      property_name = self._PREDEFINED_NAMES.get(
          name_index, 'UNKNOWN_{0:d}'.format(name_index))

      if self._debug:
        description = 'Property: {0:d} name index'.format(property_index)
        value_string = '{0:d}'.format(name_index)
        self._DebugPrintValue(description, value_string)

        description = 'Property: {0:d} name'.format(property_index)
        self._DebugPrintValue(description, property_name)

    else:
      record_data_offset = properties_data_offset + name_offset
      data_type_map = self._GetDataTypeMap('cim_string')

      try:
        cim_string = self._ReadStructureFromByteStream(
            properties_data[name_offset:], record_data_offset, data_type_map,
           'Property name')
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            'Unable to map property name data at offset: 0x{0:08x} with '
            'error: {1!s}').format(record_data_offset, exception))

      if self._debug:
        self._DebugPrintPropertyName(property_index, cim_string)

      property_name = cim_string.string

    return property_name

  def _ReadClassDefinitionProperties(
      self, property_descriptors, properties_data, properties_data_offset):
    """Reads class definition properties.

    Args:
      property_descriptors (list[property_descriptor]): property descriptors.
      properties_data (bytes): class definition properties data.
      properties_data_offset (int): offset of the class definition
          properties data relative to the start of the record data.

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
          property_index, property_descriptor.name_offset, properties_data,
          properties_data_offset)

      property_definition = self._ReadClassDefinitionPropertyDefinition(
          property_descriptor.definition_offset, properties_data,
          properties_data_offset)

      qualifiers_block_offset = property_descriptor.definition_offset + 18

      property_qualifiers = self._ReadQualifiers(
          property_definition.qualifiers_block_data, qualifiers_block_offset,
          properties_data, properties_data_offset)

      class_definition_property = ClassDefinitionProperty()
      class_definition_property.name = property_name
      class_definition_property.offset = property_definition.offset
      class_definition_property.qualifiers = property_qualifiers

      properties[property_name] = class_definition_property

    return properties

  def _ReadQualifierName(
      self, qualifier_index, name_offset, properties_data, record_data_offset):
    """Reads a qualifier name.

    Args:
      qualifier_index (int): qualifier index.
      name_offset (int): name offset.
      properties_data (bytes): properties data.
      record_data_offset (int): offset of the properties data relative to
          the start of the record data.

    Returns:
      str: qualifier name.

    Raises:
      ParseError: if the qualifier name cannot be read.
    """
    if name_offset & 0x80000000:
      name_index = name_offset & 0x7fffffff
      qualifier_name = self._PREDEFINED_NAMES.get(
          name_index, 'UNKNOWN_{0:d}'.format(name_index))

      if self._debug:
        description = 'Qualifier: {0:d} name index'.format(qualifier_index)
        value_string = '{0:d}'.format(name_index)
        self._DebugPrintValue(description, value_string)

        description = 'Qualifier: {0:d} name'.format(qualifier_index)
        self._DebugPrintValue(description, qualifier_name)

    else:
      record_data_offset += name_offset
      data_type_map = self._GetDataTypeMap('cim_string')

      try:
        cim_string = self._ReadStructureFromByteStream(
            properties_data[name_offset:], record_data_offset, data_type_map,
            'Qualifier name')
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            'Unable to map qualifier name data at offset: 0x{0:08x} with '
            'error: {1!s}').format(record_data_offset, exception))

      if self._debug:
        self._DebugPrintQualifierName(qualifier_index, cim_string)

      qualifier_name = cim_string.string

    return qualifier_name

  def _ReadQualifiers(
      self, qualifiers_data, qualifiers_data_offset, properties_data,
      properties_data_offset):
    """Reads qualifiers.

    Args:
      qualifiers_data (bytes): qualifiers data.
      qualifiers_data_offset (int): offset of the qualifiers data relative
          to the start of the record data.
      properties_data (bytes): properties data.
      properties_data_offset (int): offset of the properties data relative
          to the start of the record data.

    Returns:
      dict[str, object]: qualifier names and values.

    Raises:
      ParseError: if the qualifiers cannot be read.
    """
    if self._debug:
      self._DebugPrintText(
          'Reading qualifiers at offset: {0:d} (0x{0:08x}).\n'.format(
              qualifiers_data_offset))

    qualifiers = {}
    qualifiers_data_offset = 0
    qualifier_index = 0

    while qualifiers_data_offset < len(qualifiers_data):
      record_data_offset = qualifiers_data_offset + qualifiers_data_offset
      data_type_map = self._GetDataTypeMap('qualifier_descriptor')

      context = dtfabric_data_maps.DataTypeMapContext()

      try:
        qualifier_descriptor = self._ReadStructureFromByteStream(
            qualifiers_data[qualifiers_data_offset:], record_data_offset,
            data_type_map, 'Qualifier descriptor', context=context)
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            'Unable to map qualifier descriptor data at offset: 0x{0:08x} with '
            'error: {1!s}').format(record_data_offset, exception))

      if self._debug:
        self._DebugPrintStructureObject(
            qualifier_descriptor, self._DEBUG_INFO_QUALIFIER_DESCRIPTOR)

      qualifier_name = self._ReadQualifierName(
          qualifier_index, qualifier_descriptor.name_offset, properties_data,
          properties_data_offset)

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
        qualifier_value = self._ReadQualifierValueString(
            qualifier_descriptor.value_offset, properties_data,
            properties_data_offset)

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

      qualifiers[qualifier_name] = qualifier_value

      qualifiers_data_offset += context.byte_size
      qualifier_index += 1

    return qualifiers

  def _ReadQualifierValueString(
      self, value_offset, properties_data, record_data_offset):
    """Reads a qualifier value.

    Args:
      value_offset (int): value offset.
      properties_data (bytes): properties data.
      record_data_offset (int): offset of the properties data relative to
          the start of the record data.

    Returns:
      str: qualifier value.

    Raises:
      ParseError: if the qualifier value cannot be read.
    """
    record_data_offset += value_offset
    data_type_map = self._GetDataTypeMap('cim_string')

    try:
      cim_string = self._ReadStructureFromByteStream(
          properties_data[value_offset:], record_data_offset, data_type_map,
          'Qualifier value')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map qualifier value string data at offset: 0x{0:08x} '
          'with error: {1!s}').format(record_data_offset, exception))

    if self._debug:
      self._DebugPrintCIMString(cim_string)

    return cim_string.string

  def ReadObjectRecord(self, object_record):
    """Reads a class definition from an object record.

    Args:
      object_record (ObjectRecord): object record.

    Raises:
      ParseError: if the class definition cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading class definition object record.\n')
      self._DebugPrintData('Object redord data', object_record.data)

    record_data_offset = 0
    data_type_map = self._GetDataTypeMap('class_definition_object_record')

    context = dtfabric_data_maps.DataTypeMapContext()

    try:
      class_definition_object_record = self._ReadStructureFromByteStream(
          object_record.data, record_data_offset, data_type_map,
          'Class definition object record', context=context)
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map class definition object record data at offset: '
          '0x{0:08x} with error: {1!s}').format(record_data_offset, exception))

    record_data_offset += context.byte_size

    if self._debug:
      self._DebugPrintStructureObject(
          class_definition_object_record,
          self._DEBUG_INFO_CLASS_DEFINITION_OBJECT_RECORD)

    class_definition_header = self._ReadClassDefinitionHeader(
        class_definition_object_record.data, record_data_offset)

    qualifiers_block_offset = (
        record_data_offset + 9 +
        class_definition_header.super_class_name_block_size)

    properties_block_offset = (
        qualifiers_block_offset +
        class_definition_header.qualifiers_block_size + 4 + (
            class_definition_header.number_of_property_descriptors * 8 ) +
        class_definition_header.default_value_size)

    class_name = self._ReadClassDefinitionName(
        class_definition_header.class_name_offset,
        class_definition_header.properties_block_data,
        properties_block_offset)

    class_qualifiers = {}
    if class_definition_header.qualifiers_block_size > 4:
      class_qualifiers = self._ReadQualifiers(
          class_definition_header.qualifiers_block_data,
          qualifiers_block_offset,
          class_definition_header.properties_block_data,
          properties_block_offset)

    class_properties = self._ReadClassDefinitionProperties(
        class_definition_header.property_descriptors,
        class_definition_header.properties_block_data,
        properties_block_offset)

    data_offset = (
        12 + (class_definition_object_record.super_class_name_size * 2) +
        class_definition_object_record.data_size)

    if data_offset < len(object_record.data):
      if self._debug:
        self._DebugPrintData('Methods data', object_record.data[data_offset:])

      self._ReadClassDefinitionMethods(object_record.data[data_offset:])

    self.super_class_name = class_definition_object_record.super_class_name
    self.name = class_name
    self.properties = class_properties
    self.qualifiers = class_qualifiers


class Instance(data_format.BinaryDataFormat):
  """Instance.

  Attributes:
    digest_hash (str): digest hash.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _DEBUG_INFO_INSTANCE_OBJECT_RECORD = [
      ('digest_hash', 'Digest hash', '_FormatString'),
      ('date_time1', 'Unknown data and time1', '_FormatIntegerAsFiletime'),
      ('date_time2', 'Unknown data and time2', '_FormatIntegerAsFiletime'),
      ('instance_block_size', 'Instance block size', '_FormatIntegerAsDecimal'),
      ('instance_block_data', 'Instance block data',
       '_FormatDataInHexadecimal')]

  def __init__(self, format_version, debug=False, output_writer=None):
    """Initializes an instance.

    Args:
      format_version (int): format version.
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(Instance, self).__init__(debug=debug, output_writer=output_writer)
    self._format_version = format_version

    self.digest_hash = None

  def ReadObjectRecord(self, object_record):
    """Reads a class definition from an object record.

    Args:
      object_record (ObjectRecord): object record.

    Raises:
      ParseError: if the class definition cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading instance object record.\n')
      self._DebugPrintData('Object redord data', object_record.data)

    record_data_offset = 0

    if self._format_version == 1:
      data_type_map = self._GetDataTypeMap('instance_object_record_v1')
    else:
      data_type_map = self._GetDataTypeMap('instance_object_record_v2')

    try:
      instance_object_record = self._ReadStructureFromByteStream(
          object_record.data, record_data_offset, data_type_map,
          'Instance object record')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map instance object record data at offset: 0x{0:08x} '
          'with error: {1!s}').format(record_data_offset, exception))

    if self._debug:
      self._DebugPrintStructureObject(
          instance_object_record, self._DEBUG_INFO_INSTANCE_OBJECT_RECORD)

    self.digest_hash = instance_object_record.digest_hash


class Registration(data_format.BinaryDataFormat):
  """Registration.

  Attributes:
    name (str): name of the registration.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _DEBUG_INFO_REGISTRATION_OBJECT_RECORD = [
      ('name_space_string_size', 'Name space string size',
       '_FormatIntegerAsDecimal'),
      ('name_space_string', 'Name space string', '_FormatString'),
      ('class_name_string_size', 'Class name string size',
       '_FormatIntegerAsDecimal'),
      ('class_name_string', 'Class name string', '_FormatString'),
      ('attribute_name_string_size', 'Attribute name string size',
       '_FormatIntegerAsDecimal'),
      ('attribute_name_string', 'Attribute name string', '_FormatString'),
      ('attribute_value_string_size', 'Attribute value string size',
       '_FormatIntegerAsDecimal'),
      ('attribute_value_string', 'Attribute value string', '_FormatString')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a registration.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(Registration, self).__init__(debug=debug, output_writer=output_writer)
    self.name = None

  def ReadObjectRecord(self, object_record):
    """Reads a class definition from an object record.

    Args:
      object_record (ObjectRecord): object record.

    Raises:
      ParseError: if the class definition cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading registration object record.\n')
      self._DebugPrintData('Object redord data', object_record.data)

    record_data_offset = 0
    data_type_map = self._GetDataTypeMap('registration_object_record')

    try:
      registration_object_record = self._ReadStructureFromByteStream(
          object_record.data, record_data_offset, data_type_map,
          'Registration object record')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map registration object record data at offset: 0x{0:08x} '
          'with error: {1!s}').format(record_data_offset, exception))

    if self._debug:
      self._DebugPrintStructureObject(
          registration_object_record,
          self._DEBUG_INFO_REGISTRATION_OBJECT_RECORD)


class CIMRepository(data_format.BinaryDataFormat):
  """A CIM repository.

  Attributes:
    format_version (int): format version.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _MAPPING_VERSION = _FABRIC.CreateDataTypeMap('uint32le')

  _MAPPING_VERSION_SIZE = _MAPPING_VERSION.GetByteSize()

  def __init__(self, debug=False, output_writer=None):
    """Initializes a CIM repository.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(CIMRepository, self).__init__()
    self._debug = debug
    self._class_definitions_by_digest_hash = {}
    self._class_definitions_by_name = {}
    self._index_binary_tree_file = None
    self._objects_data_file = None
    self._output_writer = output_writer

    self.format_version = None

  def _DebugPrintClassDefinition(self, class_definition):
    """Prints class definition information.

    Args:
      class_definition (ClassDefinition): class definition.
    """
    self._DebugPrintText('Class definition:\n')
    self._DebugPrintValue('    Name', class_definition.name)
    self._DebugPrintValue(
        '    Super class name', class_definition.super_class_name)

    for qualifier_name, qualifier_value in (
        class_definition.qualifiers.items()):
      description = '    Qualifier: {0:s}'.format(qualifier_name)
      value_string = '{0!s}'.format(qualifier_value)
      self._DebugPrintValue(description, value_string)

    for property_name, class_definition_property in (
        class_definition.properties.items()):
      self._DebugPrintText('    Property: {0:s}\n'.format(property_name))

      value_string = '{0:d} (0x{0:08x})'.format(
          class_definition_property.offset)
      self._DebugPrintValue('        Offset', value_string)

      for qualifier_name, qualifier_value in (
          class_definition_property.qualifiers.items()):
        description = '        Qualifier: {0:s}'.format(qualifier_name)
        value_string = '{0!s}'.format(qualifier_value)
        self._DebugPrintValue(description, value_string)

    self._DebugPrintText('\n')

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
        glob_part = '[{0:s}{1:s}]'.format(character.upper(), character.lower())
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
      try:
        mapping_ver_file_number = self._ReadStructure(
            file_object, 0, self._MAPPING_VERSION_SIZE, self._MAPPING_VERSION,
            'Mapping.ver')
      finally:
        file_object.close()

      if self._debug:
        self._DebugPrintText('Mapping.ver file number: {0:d}\n'.format(
            mapping_ver_file_number))

    active_mapping_file = None
    active_mapping_file_number = None

    # Unsure how reliable this method is since multiple index[1-3].map files
    # can have the same sequence number but contain different mappings.
    for mapping_file_number in range(1, 4):
      filename_as_glob = self._FormatFilenameAsGlob(
          'mapping{0:d}.map'.format(mapping_file_number))
      mapping_file_glob = glob.glob(os.path.join(path, filename_as_glob))
      if not mapping_file_glob:
        continue

      if self._debug:
        self._DebugPrintText('Reading: {0:s}\n'.format(mapping_file_glob[0]))

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
      self._DebugPrintText('Active mapping file: mapping{0:d}.map\n'.format(
          active_mapping_file_number))

    return active_mapping_file

  def _GetKeysFromIndexPage(self, index_page):
    """Retrieves the keys from an index page.

    Yields:
      str: a CIM key.
    """
    if index_page:
      for key in index_page.keys:
        yield key

      for mapped_page_number in index_page.sub_pages:
        sub_index_page = self._index_binary_tree_file.GetMappedPage(
            mapped_page_number)
        for key in self._GetKeysFromIndexPage(sub_index_page):
          yield key

  def _OpenIndexBinaryTreeFile(self, path, index_mapping_table):
    """Opens an index binary tree.

    Args:
      path (str): path to the CIM repository.
      index_mapping_table (mapping_table): index mapping table.

    Returns:
      IndexBinaryTreeFile: index binary tree file or None if not available.
    """
    filename_as_glob = self._FormatFilenameAsGlob('index.btr')
    index_binary_tree_file_glob = os.path.join(path, filename_as_glob)

    index_binary_tree_file_path = glob.glob(index_binary_tree_file_glob)
    if not index_binary_tree_file_path:
      return None

    if self._debug:
      self._DebugPrintText('Reading: {0:s}\n'.format(
          index_binary_tree_file_path[0]))

    index_binary_tree_file = IndexBinaryTreeFile(
        self.format_version, index_mapping_table, debug=self._debug,
        output_writer=self._output_writer)
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
    mapping_file_glob = os.path.join(path, filename_as_glob)

    mapping_file_path = glob.glob(mapping_file_glob)
    if not mapping_file_path:
      return None

    if self._debug:
      self._DebugPrintText('Reading: {0:s}\n'.format(
          mapping_file_path[0]))

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
    mapping_version_file_glob = os.path.join(path, filename_as_glob)

    mapping_version_file_path = glob.glob(mapping_version_file_glob)
    if not mapping_version_file_path:
      return None

    return open(mapping_version_file_path[0], 'rb')  # pylint: disable=consider-using-with

  def _OpenObjectsDataFile(self, path, objects_mapping_table):
    """Opens an objects data file.

    Args:
      path (str): path to the CIM repository.
      objects_mapping_table (mapping_table): objects mapping table.

    Returns:
      ObjectsDataFile: objects data file or None if not available.
    """
    filename_as_glob = self._FormatFilenameAsGlob('objects.data')
    objects_data_file_glob = os.path.join(path, filename_as_glob)

    objects_data_file_path = glob.glob(objects_data_file_glob)
    if not objects_data_file_path:
      return None

    if self._debug:
      self._DebugPrintText('Reading: {0:s}\n'.format(objects_data_file_path[0]))

    objects_data_file = ObjectsDataFile(
        objects_mapping_table, debug=self._debug,
        output_writer=self._output_writer)
    objects_data_file.Open(objects_data_file_path[0])

    return objects_data_file

  def _ReadClassDefinitions(self):
    """Reads the class definitions."""
    index_page = self._index_binary_tree_file.GetRootPage()
    for key in self._GetKeysFromIndexPage(index_page):
      if '.' not in key:
        continue

      _, _, key_name = key.rpartition('\\')
      data_type, _, key_name = key_name.partition('_')
      if data_type != 'CD':
        continue

      object_record = self._objects_data_file.GetObjectRecordByKey(key)

      class_definition = ClassDefinition(
          debug=self._debug, output_writer=self._output_writer)
      class_definition.ReadObjectRecord(object_record)

      self._class_definitions_by_name[class_definition.name] = class_definition

      digest_hash, _, _ = key_name.partition('.')
      self._class_definitions_by_digest_hash[digest_hash] = class_definition

  def Close(self):
    """Closes the CIM repository."""
    if self._objects_data_file:
      self._objects_data_file.Close()
      self._objects_data_file = None

    if self._index_binary_tree_file:
      self._index_binary_tree_file.Close()
      self._index_binary_tree_file = None

  def GetClassDefinition(self, digest_hash):
    """Retrieves a class definition.

    Args:
      digest_hash (str): digest hash of the class definition.

    Returns:
      ClassDefinition: class definitions or None.
    """
    return self._class_definitions_by_digest_hash.get(digest_hash, None)

  def GetKeys(self):
    """Retrieves the keys.

    Yields:
      str: a CIM key.
    """
    if self._index_binary_tree_file:
      index_page = self._index_binary_tree_file.GetRootPage()
      for key in self._GetKeysFromIndexPage(index_page):
        yield key

  def GetObjectRecordByKey(self, key):
    """Retrieves a specific object record.

    Args:
      key (str): a CIM key.

    Returns:
      ObjectRecord: an object record or None.
    """
    if not self._objects_data_file:
      return None

    return self._objects_data_file.GetObjectRecordByKey(key)

  def Open(self, path):
    """Opens the CIM repository.

    Args:
      path (str): path to the CIM repository.
    """
    active_mapping_file = None

    index_mapping_file = self._OpenMappingFile(path, 'index.map')
    if not index_mapping_file:
      active_mapping_file = self._GetActiveMappingFile(path)
      index_mapping_file = active_mapping_file

    self.format_version = index_mapping_file.format_version
    index_mapping_table = index_mapping_file.GetIndexMappingTable()

    if not active_mapping_file:
      index_mapping_file.Close()

    self._index_binary_tree_file = self._OpenIndexBinaryTreeFile(
        path, index_mapping_table)

    objects_mapping_file = active_mapping_file
    if not objects_mapping_file:
      objects_mapping_file = self._OpenMappingFile(path, 'objects.map')

    object_mapping_table = objects_mapping_file.GetObjectsMappingTable()

    objects_mapping_file.Close()

    self._objects_data_file = self._OpenObjectsDataFile(
        path, object_mapping_table)

    self._ReadClassDefinitions()

  def OpenIndexBinaryTree(self, path):
    """Opens the CIM repository index binary tree.

    Args:
      path (str): path to the CIM repository.
    """
    index_mapping_file = self._OpenMappingFile(path, 'index.map')
    if not index_mapping_file:
      index_mapping_file = self._GetActiveMappingFile(path)

    self.format_version = index_mapping_file.format_version
    index_mapping_table = index_mapping_file.GetIndexMappingTable()

    index_mapping_file.Close()

    self._index_binary_tree_file = self._OpenIndexBinaryTreeFile(
        path, index_mapping_table)

  def OpenMappingFile(self, path):
    """Opens a CIM repository mapping file.

    Args:
      path (str): path to the CIM repository.
    """
    path, _, filename = path.rpartition(os.path.sep)
    self._OpenMappingFile(path, filename)
