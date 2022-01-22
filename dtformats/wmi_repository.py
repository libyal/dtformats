# -*- coding: utf-8 -*-
"""WMI Common Information Model (CIM) repository files."""

import glob
import logging
import os

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import data_maps as dtfabric_data_maps

from dtformats import data_format
from dtformats import errors


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


class ObjectRecord(data_format.BinaryDataFormat):
  """Object record.

  Attributes:
    data (bytes): object record data.
    data_type (str): object record data type.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  # TODO: replace streams by block type
  # TODO: add more values.

  _CLASS_DEFINITION_HEADER = _FABRIC.CreateDataTypeMap(
      'class_definition_header')

  _CLASS_DEFINITION_OBJECT_RECORD = _FABRIC.CreateDataTypeMap(
      'class_definition_object_record')

  _CLASS_DEFINITION_METHODS = _FABRIC.CreateDataTypeMap(
      'class_definition_methods')

  _SUPER_CLASS_NAME_BLOCK = _FABRIC.CreateDataTypeMap('super_class_name_block')

  _PROPERTY_DEFINITION = _FABRIC.CreateDataTypeMap('property_definition')

  _INTERFACE_OBJECT_RECORD = _FABRIC.CreateDataTypeMap(
      'interface_object_record')

  _REGISTRATION_OBJECT_RECORD = _FABRIC.CreateDataTypeMap(
      'registration_object_record')

  _PROPERTY_TYPES = _FABRIC.CreateDataTypeMap('cim_property_types')

  # A size of 0 indicates variable of size.
  _PROPERTY_TYPE_VALUE_SIZES = {
      0x00000002: 2,
      0x00000003: 4,
      0x00000004: 4,
      0x00000005: 8,
      0x00000008: 0,
      0x0000000b: 2,
      0x0000000d: 0,
      0x00000010: 1,
      0x00000011: 1,
      0x00000012: 2,
      0x00000013: 4,
      0x00000014: 8,
      0x00000015: 8,
      0x00000065: 0,
      0x00000066: 2,
      0x00000067: 2,
  }

  _DEBUG_INFO_CLASS_DEFINITION_OBJECT_RECORD = [
      ('super_class_name_size', 'Super class name size',
       '_FormatIntegerAsDecimal'),
      ('super_class_name', 'Super class name', '_FormatString'),
      ('date_time', 'Unknown date and time', '_FormatIntegerAsFiletime'),
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('data', 'Data', '_FormatDataInHexadecimal')]

  _DEBUG_INFO_CLASS_DEFINITION_HEADER = [
      ('unknown1', 'Unknown1', '_FormatIntegerAsDecimal'),
      ('class_name_offset', 'Class name offset',
       '_FormatIntegerAsHexadecimal8'),
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
       '_FormatIntegerAsPropertiesBlockSize')]

  _DEBUG_INFO_INTERFACE_OBJECT_RECORD = [
      ('string_digest_hash', 'String digest hash', '_FormatDataInHexadecimal'),
      ('date_time1', 'Unknown data and time1', '_FormatIntegerAsFiletime'),
      ('date_time2', 'Unknown data and time2', '_FormatIntegerAsFiletime'),
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('data', 'Data', '_FormatDataInHexadecimal')]

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

  DATA_TYPE_CLASS_DEFINITION = 'CD'

  def __init__(self, data_type, data, debug=False, output_writer=None):
    """Initializes an object record.

    Args:
      data_type (str): object record data type.
      data (bytes): object record data.
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(ObjectRecord, self).__init__(debug=debug, output_writer=output_writer)
    self.data = data
    self.data_type = data_type

  def _DebugPrintPropertyName(self, index, property_name):
    """Prints property name information.

    Args:
      index (int): property index.
      property_name (property_name): property name.
    """
    description = 'Property: {0:d} name string flags'.format(index)
    value_string = '0x{0:02x}'.format(property_name.string_flags)
    self._DebugPrintValue(description, value_string)

    description = 'Property: {0:d} name string'.format(index)
    self._DebugPrintValue(description, property_name.string)

  def _DebugPrintPropertyDefinition(self, index, property_definition):
    """Prints property definition information.

    Args:
      index (int): property index.
      property_definition (property_definition): property definition.
    """
    property_type_string = self._PROPERTY_TYPES.GetName(
        property_definition.type)
    description = 'Property: {0:d} type'.format(index)
    value_string = '0x{0:08x} ({1:s})'.format(
        property_definition.type, property_type_string or 'UNKNOWN')
    self._DebugPrintValue(description, value_string)

    description = 'Property: {0:d} index'.format(index)
    self._DebugPrintDecimalValue(description, property_definition.index)

    description = 'Property: {0:d} offset'.format(index)
    value_string = '0x{0:08x}'.format(property_definition.offset)
    self._DebugPrintValue(description, value_string)

    description = 'Property: {0:d} level'.format(index)
    self._DebugPrintDecimalValue(description, property_definition.level)

    description = 'Property: {0:d} qualifiers block size'.format(index)
    self._DebugPrintDecimalValue(
        description, property_definition.qualifiers_block_size)

    description = 'Property: {0:d} qualifiers block data'.format(index)
    self._DebugPrintData(description, property_definition.qualifiers_block_data)

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

      description = '    Property descriptor: {0:d} defintion offset'.format(
          index)
      value_string = '0x{0:08x}'.format(property_descriptor.definition_offset)
      line = self._FormatValue(description, value_string)
      lines.append(line)

    return ''.join(lines)

  def _FormatIntegerAsPropertiesBlockSize(self, integer):
    """Formats an integer as a properties block size.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a properties block size.
    """
    return '{0:d} (0x{1:08x})'.format(integer & 0x7fffffff, integer)

  def _ReadClassDefinition(self, object_record_data):
    """Reads a class definition object record.

    Args:
      object_record_data (bytes): object record data.

    Raises:
      ParseError: if the object record cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading class definition object record.\n')

    try:
      class_definition_object_record = (
          self._CLASS_DEFINITION_OBJECT_RECORD.MapByteStream(
              object_record_data))
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          'Unable to parse class definition object record with '
          'error: {0:s}').format(exception))

    if self._debug:
      self._DebugPrintStructureObject(
          class_definition_object_record,
          self._DEBUG_INFO_CLASS_DEFINITION_OBJECT_RECORD)

    self._ReadClassDefinitionHeader(class_definition_object_record.data)

    data_offset = (
        12 + (class_definition_object_record.super_class_name_size * 2) +
        class_definition_object_record.data_size)

    if data_offset < len(object_record_data):
      if self._debug:
        self._DebugPrintData('Methods data', object_record_data[data_offset:])

      self._ReadClassDefinitionMethods(object_record_data[data_offset:])

  def _ReadClassDefinitionHeader(self, class_definition_data):
    """Reads a class definition header.

    Args:
      class_definition_data (bytes): class definition data.

    Raises:
      ParseError: if the class definition cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading class definition header.\n')

    try:
      class_definition_header = self._CLASS_DEFINITION_HEADER.MapByteStream(
          class_definition_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          'Unable to parse class definition header with error: {0!s}').format(
              exception))

    if self._debug:
      self._DebugPrintStructureObject(
          class_definition_header, self._DEBUG_INFO_CLASS_DEFINITION_HEADER)

    self._ReadClassDefinitionProperties(
        class_definition_header.properties_block_data,
        class_definition_header.property_descriptors)

  def _ReadClassDefinitionMethods(self, class_definition_data):
    """Reads a class definition methods.

    Args:
      class_definition_data (bytes): class definition data.

    Raises:
      ParseError: if the class definition cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading class definition methods.\n')

    try:
      class_definition_methods = self._CLASS_DEFINITION_METHODS.MapByteStream(
          class_definition_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          'Unable to parse class definition methods with error: {0!s}').format(
              exception))

    methods_block_size = class_definition_methods.methods_block_size

    if self._debug:
      value_string = '{0:d} (0x{1:08x})'.format(
          methods_block_size & 0x7fffffff, methods_block_size)
      self._DebugPrintValue('Methods block size', value_string)

      self._DebugPrintData(
          'Methods block data', class_definition_methods.methods_block_data)

  def _ReadClassDefinitionProperties(
      self, properties_data, property_descriptors):
    """Reads class definition properties.

    Args:
      properties_data (bytes): class definition properties data.
      property_descriptors (list[property_descriptor]): property descriptors.

    Raises:
      ParseError: if the class definition properties cannot be read.
    """
    # TODO: set file offset
    file_offset = 0

    if self._debug:
      self._DebugPrintText('Reading class definition properties.\n')

    if self._debug:
      self._DebugPrintData('Properties data', properties_data)

    data_type_map = self._GetDataTypeMap('property_name')

    for index, property_descriptor in enumerate(property_descriptors):
      name_offset = property_descriptor.name_offset & 0x7fffffff

      if property_descriptor.name_offset & 0x80000000:
        property_name_data = properties_data
      else:
        property_name_data = properties_data[name_offset:]

      data_type_map = self._GetDataTypeMap('property_name')

      try:
        property_name = self._ReadStructureFromByteStream(
            property_name_data, file_offset, data_type_map, 'Property name')
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            'Unable to map property name data at offset: 0x{0:08x} with error: '
            '{1!s}').format(file_offset, exception))

      if self._debug:
        self._DebugPrintPropertyName(index, property_name)

      definition_offset = property_descriptor.definition_offset & 0x7fffffff
      property_definition_data = properties_data[definition_offset:]

      try:
        property_definition = self._PROPERTY_DEFINITION.MapByteStream(
            property_definition_data)
      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError(
            'Unable to parse property definition with error: {0!s}'.format(
                exception))

      if self._debug:
        self._DebugPrintPropertyDefinition(index, property_definition)

      property_value_size = self._PROPERTY_TYPE_VALUE_SIZES.get(
          property_definition.type & 0x00001fff, None)
      # TODO: handle property value data.
      property_value_data = b''

      if property_value_size is not None:
        if self._debug:
          description = 'Property: {0:d} value size'.format(index)
          self._DebugPrintDecimalValue(description, property_value_size)

          # TODO: handle variable size value data.
          # TODO: handle array.
          description = 'Property: {0:d} value data'.format(index)
          self._DebugPrintData(
              description, property_value_data[:property_value_size])

  def _ReadInterface(self, object_record_data):
    """Reads an interface object record.

    Args:
      object_record_data (bytes): object record data.

    Raises:
      ParseError: if the object record cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading interface object record.\n')

    try:
      interface_object_record = self._INTERFACE_OBJECT_RECORD.MapByteStream(
          object_record_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError(
          'Unable to parse interace object record with error: {0!s}'.format(
              exception))

    if self._debug:
      self._DebugPrintStructureObject(
          interface_object_record, self._DEBUG_INFO_INTERFACE_OBJECT_RECORD)

  def _ReadRegistration(self, object_record_data):
    """Reads a registration object record.

    Args:
      object_record_data (bytes): object record data.

    Raises:
      ParseError: if the object record cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading registration object record.\n')

    try:
      registration_object_record = (
          self._REGISTRATION_OBJECT_RECORD.MapByteStream(
              object_record_data))
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          'Unable to parse registration object record with '
          'error: {0:s}').format(exception))

    if self._debug:
      self._DebugPrintStructureObject(
          registration_object_record,
          self._DEBUG_INFO_REGISTRATION_OBJECT_RECORD)

  def Read(self):
    """Reads an object record."""
    if self._debug:
      self._DebugPrintData('Object record data', self.data)

    if self._debug:
      if self.data_type == self.DATA_TYPE_CLASS_DEFINITION:
        self._ReadClassDefinition(self.data)
      elif self.data_type in ('I', 'IL'):
        self._ReadInterface(self.data)
      elif self.data_type == 'R':
        self._ReadRegistration(self.data)


class ObjectsDataPage(data_format.BinaryDataFormat):
  """An objects data page.

  Attributes:
    page_offset (int): page offset or None.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _OBJECT_DESCRIPTOR = _FABRIC.CreateDataTypeMap('cim_object_descriptor')

  _OBJECT_DESCRIPTOR_SIZE = _OBJECT_DESCRIPTOR.GetByteSize()

  _EMPTY_OBJECT_DESCRIPTOR = b'\x00' * _OBJECT_DESCRIPTOR_SIZE

  _DEBUG_INFO_OBJECT_DESCRIPTOR = [
      ('identifier', 'Identifier', '_FormatIntegerAsHexadecimal8'),
      ('data_offset', 'Data offset (relative)', '_FormatIntegerAsHexadecimal8'),
      ('data_file_offset', 'Data offset (file)',
       '_FormatIntegerAsHexadecimal8'),
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

  _UINT16LE = _FABRIC.CreateDataTypeMap('uint16le')

  _UINT16LE_SIZE = _UINT16LE.GetByteSize()

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

  def __init__(self, index_mapping_file, debug=False, output_writer=None):
    """Initializes an index binary-tree file.

    Args:
      index_mapping_file (MappingFile): an index mapping file.
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(IndexBinaryTreeFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._index_mapping_file = index_mapping_file
    self._first_mapped_page = None
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
          key_segments.append(index_binary_tree_page.page_values[segment_index])

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
        self._DebugPrintValue(description, value_string[:-1])

      index_binary_tree_page.page_values.append(value_string)

    if self._debug and index_binary_tree_page.page_value_offsets:
      self._DebugPrintText('\n')

  def GetFirstMappedPage(self):
    """Retrieves the first mapped page.

    Returns:
      IndexBinaryTreePage: an index binary-tree page or None.
    """
    if not self._first_mapped_page:
      page_number = self._index_mapping_file.mappings[0]

      index_page = self._GetPage(page_number)
      if not index_page:
        logging.warning((
            'Unable to read first mapped index binary-tree page: '
            '{0:d}.').format(page_number))
        return None

      if index_page.page_type != 0xaddd:
        logging.warning('First mapped index binary-tree page type mismatch.')
        return None

      self._first_mapped_page = index_page

    return self._first_mapped_page

  def GetMappedPage(self, page_number):
    """Retrieves a specific mapped page.

    Args:
      page_number (int): page number.

    Returns:
      IndexBinaryTreePage: an index binary-tree page or None.
    """
    mapped_page_number = self._index_mapping_file.mappings[page_number]

    index_page = self._GetPage(mapped_page_number)
    if not index_page:
      logging.warning(
          'Unable to read index binary-tree mapped page: {0:d}.'.format(
              page_number))
      return None

    return index_page

  def GetRootPage(self):
    """Retrieves the root page.

    Returns:
      IndexBinaryTreePage: an index binary-tree page or None.
    """
    if not self._root_page:
      first_mapped_page = self.GetFirstMappedPage()
      if not first_mapped_page:
        return None

      page_number = self._index_mapping_file.mappings[
          first_mapped_page.root_page_number]

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
    data_size (int): data size of the mappings file.
    mapping (list[int]): mappings to page numbers in the index binary-tree
        or objects data file.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _UINT32LE = _FABRIC.CreateDataTypeMap('uint32le')

  _UINT32LE_SIZE = _UINT32LE.GetByteSize()

  _FILE_HEADER_SIGNATURE = 0x0000abcd

  _FILE_HEADER = _FABRIC.CreateDataTypeMap('cim_map_header')

  _FILE_HEADER_SIZE = _FILE_HEADER.GetByteSize()

  _FILE_FOOTER_SIGNATURE = 0x0000dcba

  _FILE_FOOTER = _FABRIC.CreateDataTypeMap('cim_map_footer')

  _FILE_FOOTER_SIZE = _FILE_FOOTER.GetByteSize()

  _PAGE_NUMBERS = _FABRIC.CreateDataTypeMap('cim_map_page_numbers')

  _DEBUG_INFO_FILE_FOOTER = [
      ('signature', 'Signature', '_FormatIntegerAsHexadecimal8')]

  _DEBUG_INFO_FILE_HEADER = [
      ('signature', 'Signature', '_FormatIntegerAsHexadecimal8'),
      ('format_version', 'Format version', '_FormatIntegerAsHexadecimal8'),
      ('number_of_pages', 'Number of pages', '_FormatIntegerAsDecimal')]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a mappings file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(MappingFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self.data_size = 0
    self.mappings = []

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

  def _DebugPrintPageNumbersTable(
      self, description, page_number_table, unavailable_page_numbers=None):
    """Prints a page number table debug information.

    Args:
      description (str): description.
      page_number_table (tuple[int, ...]): page number table.
      unavailable_page_numbers (Optional[set[int]]): unavailable page numbers.
    """
    for index, page_number in enumerate(page_number_table):
      sub_description = '{0:s}: {1:d} page number'.format(description, index)
      self._DebugPrintPageNumber(
          sub_description, page_number,
          unavailable_page_numbers=unavailable_page_numbers)

    self._DebugPrintText('\n')

  def _ReadFileFooter(self, file_object):
    """Reads the file footer.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file footer cannot be read.
    """
    file_offset = file_object.tell()

    file_footer = self._ReadStructure(
        file_object, file_offset, self._FILE_FOOTER_SIZE, self._FILE_FOOTER,
        'file footer')

    if self._debug:
      self._DebugPrintStructureObject(file_footer, self._DEBUG_INFO_FILE_FOOTER)

    if file_footer.signature != self._FILE_FOOTER_SIGNATURE:
      raise errors.ParseError(
          'Unsupported file footer signature: 0x{0:08x}'.format(
              file_footer.signature))

  def _ReadFileHeader(self, file_object, file_offset=0):
    """Reads the file header.

    Args:
      file_object (file): file-like object.
      file_offset (Optional[int]): offset of the mappings file header
          relative to the start of the file.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_header = self._ReadStructure(
        file_object, file_offset, self._FILE_HEADER_SIZE, self._FILE_HEADER,
        'file header')

    if self._debug:
      self._DebugPrintStructureObject(file_header, self._DEBUG_INFO_FILE_HEADER)

    if file_header.signature != self._FILE_HEADER_SIGNATURE:
      raise errors.ParseError(
          'Unsupported file header signature: 0x{0:08x}'.format(
              file_header.signature))

  def _ReadMappings(self, file_object):
    """Reads the mappings.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the mappings cannot be read.
    """
    file_offset = file_object.tell()
    mappings_array = self._ReadPageNumbersTable(
        file_object, file_offset, 'mappings')

    if self._debug:
      self._DebugPrintPageNumbersTable(
          'Mapping entry', mappings_array,
          unavailable_page_numbers=set([0xffffffff]))

    self.mappings = mappings_array

  def _ReadPageNumbersTable(self, file_object, file_offset, description):
    """Reads a page numbers table.

    Args:
      file_object (file): a file-like object.
      file_offset (int): offset of the data relative to the start of
          the file-like object.
      description (str): description of the page numbers table.

    Returns:
      tuple[int, ...]: page number array.

    Raises:
      ParseError: if the page numbers table cannot be read.
    """
    file_object.seek(file_offset, os.SEEK_SET)

    if self._debug:
      self._DebugPrintText('Reading {0:s} at offset: 0x{1:08x}\n'.format(
          description, file_offset))

    try:
      number_of_entries_data = file_object.read(self._UINT32LE_SIZE)
    except IOError as exception:
      raise errors.ParseError((
          'Unable to read number of entries data at offset: 0x{0:08x} '
          'with error: {1!s}').format(file_offset, exception))

    if len(number_of_entries_data) != self._UINT32LE_SIZE:
      raise errors.ParseError((
          'Unable to read number of entries data at offset: 0x{0:08x} '
          'with error: missing data').format(file_offset))

    try:
      number_of_entries = self._UINT32LE.MapByteStream(number_of_entries_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          'Unable to parse number of entries at offset: 0x{0:08x} with error '
          'error: {1!s}').format(file_offset, exception))

    if number_of_entries == 0:
      entries_data = b''
    else:
      entries_data_size = number_of_entries * self._UINT32LE_SIZE

      try:
        entries_data = file_object.read(entries_data_size)
      except IOError as exception:
        raise errors.ParseError((
            'Unable to read entries data at offset: 0x{0:08x} with error: '
            '{1!s}').format(file_offset, exception))

      if len(entries_data) != entries_data_size:
        raise errors.ParseError((
            'Unable to read entries data at offset: 0x{0:08x} with error: '
            'missing data').format(file_offset))

    if self._debug:
      data_description = '{0:s} data'.format(description.title())
      self._DebugPrintData(data_description, b''.join([
          number_of_entries_data, entries_data]))

      self._DebugPrintDecimalValue('Number of entries', number_of_entries)

    if not entries_data:
      page_numbers = tuple()
    else:
      context = dtfabric_data_maps.DataTypeMapContext(values={
          'number_of_entries': number_of_entries})

      try:
        page_numbers = self._PAGE_NUMBERS.MapByteStream(
            entries_data, context=context)

      except dtfabric_errors.MappingError as exception:
        raise errors.ParseError((
            'Unable to parse entries data at offset: 0x{0:08x} with error: '
            '{1!s}').format(file_offset, exception))

    return page_numbers

  def _ReadUnknownEntries(self, file_object):
    """Reads unknown entries.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the unknown entries cannot be read.
    """
    file_offset = file_object.tell()
    unknown_entries_array = self._ReadPageNumbersTable(
        file_object, file_offset, 'unknown entries')

    if self._debug:
      self._DebugPrintPageNumbersTable(
          'Unknown entry', unknown_entries_array,
          unavailable_page_numbers=set([0xffffffff]))

      self._DebugPrintText('\n')

  def ReadFileObject(self, file_object):
    """Reads a mappings file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_offset = file_object.tell()

    self._ReadFileHeader(file_object, file_offset=file_offset)
    self._ReadMappings(file_object)
    self._ReadUnknownEntries(file_object)
    self._ReadFileFooter(file_object)

    self.data_size = file_object.tell() - file_offset


class ObjectsDataFile(data_format.BinaryDataFile):
  """An objects data (Objects.data) file."""

  _KEY_SEGMENT_SEPARATOR = '\\'
  _KEY_VALUE_SEPARATOR = '.'

  _KEY_VALUE_PAGE_NUMBER_INDEX = 1
  _KEY_VALUE_RECORD_IDENTIFIER_INDEX = 2
  _KEY_VALUE_DATA_SIZE_INDEX = 3

  def __init__(self, objects_mapping_file, debug=False, output_writer=None):
    """Initializes an objects data file.

    Args:
      objects_mapping_file (MappingFile): objects mapping file.
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(ObjectsDataFile, self).__init__(
        debug=debug, output_writer=output_writer)
    self._objects_mapping_file = objects_mapping_file

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

  def GetMappedPage(self, page_number, data_page=False):
    """Retrieves a specific mapped page.

    Args:
      page_number (int): page number.
      data_page (Optional[bool]): True if the page is a data page.

    Returns:
      ObjectsDataPage: objects data page or None.
    """
    mapped_page_number = self._objects_mapping_file.mappings[page_number]

    objects_page = self._GetPage(mapped_page_number, data_page=data_page)
    if not objects_page:
      logging.warning(
          'Unable to read objects data mapped page: {0:d}.'.format(
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
    key, page_number, record_identifier, data_size = self._GetKeyValues(key)

    data_segments = []
    data_page = False
    data_segment_index = 0
    while data_size > 0:
      object_page = self.GetMappedPage(page_number, data_page=data_page)
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
      page_number += 1

    data_type, _, _ = key.partition('_')
    object_record_data = b''.join(data_segments)

    return ObjectRecord(
        data_type, object_record_data, debug=self._debug,
        output_writer=self._output_writer)

  def ReadFileObject(self, file_object):
    """Reads an objects data file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    self._file_object = file_object


class CIMRepository(data_format.BinaryDataFormat):
  """A CIM repository."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  _MAPPING_VER = _FABRIC.CreateDataTypeMap('uint32le')

  _MAPPING_VER_SIZE = _MAPPING_VER.GetByteSize()

  def __init__(self, debug=False, output_writer=None):
    """Initializes a CIM repository.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(CIMRepository, self).__init__()
    self._debug = debug
    self._index_binary_tree_file = None
    self._index_mapping_file = None
    self._objects_data_file = None
    self._objects_mapping_file = None
    self._output_writer = output_writer

  def _DebugPrintText(self, text):
    """Prints text for debugging.

    Args:
      text (str): text.
    """
    if self._output_writer:
      self._output_writer.WriteText(text)

  def _GetCurrentMappingFile(self, path):
    """Retrieves the current mapping file.

    Args:
      path (str): path to the CIM repository.

    Raises:
      ParseError: if the current mapping file cannot be read.
    """
    mapping_file_glob = glob.glob(
        os.path.join(path, '[Mm][Aa][Pp][Pp][Ii][Nn][Gg].[Vv][Ee][Rr]'))

    active_mapping_file = 0
    if mapping_file_glob:
      with open(mapping_file_glob[0], 'rb') as file_object:
        active_mapping_file = self._ReadStructure(
            file_object, 0, self._MAPPING_VER_SIZE, self._MAPPING_VER,
            'Mapping.ver')

      if self._debug:
        self._DebugPrintText('Active mapping file: {0:d}'.format(
            active_mapping_file))

    if mapping_file_glob:
      mapping_file_glob = glob.glob(os.path.join(
          path, '[Mm][Aa][Pp][Pp][Ii][Nn][Gg]{0:d}.[Mm][Aa][Pp]'.format(
              active_mapping_file)))
    else:
      mapping_file_glob = glob.glob(os.path.join(
          path, '[Mm][Aa][Pp][Pp][Ii][Nn][Gg][1-3].[Mm][Aa][Pp]'))

    # TODO: determine active mapping file for Windows Vista and later.
    for mapping_file_path in mapping_file_glob:
      if self._debug:
        self._DebugPrintText('Reading: {0:s}'.format(mapping_file_path))

      objects_mapping_file = MappingFile(
          debug=self._debug, output_writer=self._output_writer)
      objects_mapping_file.Open(mapping_file_path)

      index_mapping_file = MappingFile(
          debug=self._debug, output_writer=self._output_writer)
      index_mapping_file.Open(mapping_file_path)
      # TODO: pass file_offset=objects_mapping_file.data_size) ?

  def _GetKeysFromIndexPage(self, index_page):
    """Retrieves the keys from an index page.

    Yields:
      str: a CIM key.
    """
    for key in index_page.keys:
      yield key

    for sub_page_number in index_page.sub_pages:
      sub_index_page = self._index_binary_tree_file.GetMappedPage(
          sub_page_number)
      for key in self._GetKeysFromIndexPage(sub_index_page):
        yield key

  def _OpenIndexBinaryTree(self, path):
    """Opens the CIM repository index binary tree.

    Args:
      path (str): path to the CIM repository.
    """
    index_binary_tree_file_glob = os.path.join(
        path, '[Ii][Nn][Dd][Ee][Xx].[Bb][Tt][Rr]')
    index_binary_tree_file_path = glob.glob(index_binary_tree_file_glob)
    if index_binary_tree_file_path:
      index_binary_tree_file_path = index_binary_tree_file_path[0]

      if self._debug:
        self._DebugPrintText('Reading: {0:s}\n'.format(
            index_binary_tree_file_path))

      # TODO: warn about missing index_mapping_file

      self._index_binary_tree_file = IndexBinaryTreeFile(
          self._index_mapping_file, debug=self._debug,
          output_writer=self._output_writer)
      self._index_binary_tree_file.Open(index_binary_tree_file_path)

  def _OpenObjectsDataFile(self, path):
    """Opens the CIM repository objects data file.

    Args:
      path (str): path to the CIM repository.
    """
    objects_data_file_glob = os.path.join(
        path, '[Oo][Bb][Jj][Ee][Cc][Tt][Ss].[Da][Aa][Tt][Aa]')
    objects_data_file_path = glob.glob(objects_data_file_glob)
    if objects_data_file_path:
      objects_data_file_path = objects_data_file_path[0]

      if self._debug:
        self._DebugPrintText('Reading: {0:s}\n'.format(objects_data_file_path))

      # TODO: warn about missing objects_mapping_file

      self._objects_data_file = ObjectsDataFile(
          self._objects_mapping_file, debug=self._debug,
          output_writer=self._output_writer)
      self._objects_data_file.Open(objects_data_file_path)

  def _OpenIndexMappingsFile(self, path):
    """Opens the CIM repository index mappings file.

    Args:
      path (str): path to the CIM repository.
    """
    index_mapping_file_glob = os.path.join(
        path, '[Ii][Nn][Dd][Ee][Xx].[Mm][Aa][Pp]')
    index_mapping_file_path = glob.glob(index_mapping_file_glob)
    if index_mapping_file_path:
      index_mapping_file_path = index_mapping_file_path[0]

      if self._debug:
        self._DebugPrintText('Reading: {0:s}\n'.format(
            index_mapping_file_path))

      self._index_mapping_file = MappingFile(
          debug=self._debug, output_writer=self._output_writer)
      self._index_mapping_file.Open(index_mapping_file_path)

  def _OpenObjectsMappingsFile(self, path):
    """Opens the CIM repository objects mappings file.

    Args:
      path (str): path to the CIM repository.
    """
    objects_mapping_file_glob = os.path.join(
        path, '[Oo][Bb][Jj][Ee][Cc][Tt][Ss].[Mm][Aa][Pp]')
    objects_mapping_file_path = glob.glob(objects_mapping_file_glob)
    if objects_mapping_file_path:
      objects_mapping_file_path = objects_mapping_file_path[0]

      if self._debug:
        self._DebugPrintText('Reading: {0:s}\n'.format(
            objects_mapping_file_path))

      self._objects_mapping_file = MappingFile(
          debug=self._debug, output_writer=self._output_writer)
      self._objects_mapping_file.Open(objects_mapping_file_path)

  def Close(self):
    """Closes the CIM repository."""
    if self._index_binary_tree_file:
      self._index_binary_tree_file.Close()
      self._index_binary_tree_file = None

    if self._index_mapping_file:
      self._index_mapping_file.Close()
      self._index_mapping_file = None

    if self._objects_data_file:
      self._objects_data_file.Close()
      self._objects_data_file = None

    if self._objects_mapping_file:
      self._objects_mapping_file.Close()
      self._objects_mapping_file = None

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
    # TODO: self._GetCurrentMappingFile(path)

    self._OpenIndexMappingsFile(path)
    self._OpenIndexBinaryTree(path)
    self._OpenObjectsMappingsFile(path)
    self._OpenObjectsDataFile(path)

  def OpenIndexBinaryTree(self, path):
    """Opens the CIM repository index binary tree.

    Args:
      path (str): path to the CIM repository.
    """
    self._OpenIndexMappingsFile(path)
    self._OpenIndexBinaryTree(path)
