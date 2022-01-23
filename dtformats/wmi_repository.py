# -*- coding: utf-8 -*-
"""WMI Common Information Model (CIM) repository files."""

import glob
import logging
import os

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import data_maps as dtfabric_data_maps

from dtformats import data_format
from dtformats import errors


class CIMClassDefinition(object):
  """CIM class definition.

  Attributes:
    name (str): name of the class.
    properties (dict[str, CIMClassDefinitionProperty]): properties.
    qualifiers (dict[str, object]): qualifiers.
    super_class_name (str): name of the super class.
  """

  def __init__(self):
    """Initializes a CIM class definition."""
    super(CIMClassDefinition, self).__init__()
    self.name = None
    self.properties = {}
    self.qualifiers = {}
    self.super_class_name = None


class CIMClassDefinitionProperty(object):
  """CIM class definition property.

  Attributes:
    name (str): name of the property.
    qualifiers (dict[str, object]): qualifiers.
  """

  def __init__(self):
    """Initializes a CIM class property."""
    super(CIMClassDefinitionProperty, self).__init__()
    self.name = None
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


class ObjectRecord(data_format.BinaryDataFormat):
  """Object record.

  Attributes:
    data (bytes): object record data.
    data_type (str): object record data type.
    file_offset (int): offset of the object record data relative to
        the start of the file.
  """

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile('wmi_repository.yaml')

  # TODO: replace streams by block type
  # TODO: add more values.

  _INTERFACE_OBJECT_RECORD = _FABRIC.CreateDataTypeMap(
      'interface_object_record')

  _REGISTRATION_OBJECT_RECORD = _FABRIC.CreateDataTypeMap(
      'registration_object_record')

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
       '_FormatIntegerAsPropertiesBlockSize'),
      ('properties_block_data', 'Properties block data',
       '_FormatDataInHexadecimal')]

  _DEBUG_INFO_CLASS_NAME = [
      ('string_flags', 'Class name string flags',
       '_FormatIntegerAsHexadecimal2'),
      ('string', 'Class name string', '_FormatString')]

  _DEBUG_INFO_QUALIFIER_DESCRIPTOR = [
      ('name_offset', 'Name offset', '_FormatIntegerAsHexadecimal8'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal2'),
      ('value_data_type', 'Value data type', '_FormatIntegerAsDataType'),
      ('value_boolean', 'Value', '_FormatIntegerAsDecimal'),
      ('value_floating_point', 'Value', '_FormatFloatingPoint'),
      ('value_integer', 'Value', '_FormatIntegerAsDecimal'),
      ('value_offset', 'Value offset', '_FormatIntegerAsHexadecimal8')]

  _DEBUG_INFO_PROPERTY_DEFINITION = [
      ('value_data_type', 'Value data type', '_FormatIntegerAsDataType'),
      ('index', 'Index', '_FormatIntegerAsDecimal'),
      ('offset', 'Offset', '_FormatIntegerAsHexadecimal8'),
      ('level', 'Level', '_FormatIntegerAsDecimal'),
      ('qualifiers_block_size', 'Qualifiers block size',
       '_FormatIntegerAsDecimal'),
      ('qualifiers_block_data', 'Qualifiers block data',
       '_FormatDataInHexadecimal'),
      ('value_boolean', 'Value', '_FormatIntegerAsDecimal'),
      ('value_floating_point', 'Value', '_FormatFloatingPoint'),
      ('value_integer', 'Value', '_FormatIntegerAsDecimal'),
      ('value_offset', 'Value offset', '_FormatIntegerAsHexadecimal8')]

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

  _PREDEFINED_NAMES = {
      1: 'key',
      3: 'read',
      4: 'write',
      6: 'provider',
      7: 'dynamic',
      10: 'type'}

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
    self.file_offset = 0

  def _DebugPrintCIMClassDefinition(self, cim_class_definition):
    """Prints CIM class definition information.

    Args:
      cim_class_definition (CIMClassDefinition): CIM class definition.
    """
    self._DebugPrintText('CIM class definition:\n')
    self._DebugPrintValue('    Name', cim_class_definition.name)
    self._DebugPrintValue(
        '    Super class name', cim_class_definition.super_class_name)

    for qualifier_name, qualifier_value in (
        cim_class_definition.qualifiers.items()):
      description = '    Qualifier: {0:s}'.format(qualifier_name)
      value_string = '{0!s}'.format(qualifier_value)
      self._DebugPrintValue(description, value_string)

    for property_name, cim_class_definition_property in (
        cim_class_definition.properties.items()):
      self._DebugPrintText('    Property: {0:s}\n'.format(property_name))

      for qualifier_name, qualifier_value in (
          cim_class_definition_property.qualifiers.items()):
        description = '        Qualifier: {0:s}'.format(qualifier_name)
        value_string = '{0!s}'.format(qualifier_value)
        self._DebugPrintValue(description, value_string)

    self._DebugPrintText('\n')

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

  def _ReadClassDefinition(self, object_record_data, file_offset):
    """Reads a class definition object record.

    Args:
      object_record_data (bytes): object record data.
      file_offset (int): offset of the object record data relative to
          the start of the file.

    Returns:
      CIMClassDefinition: class definition.

    Raises:
      ParseError: if the object record cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          'Reading class definition object record at offset: {0:d} '
          '(0x{0:08x}).\n').format(file_offset))

    data_type_map = self._GetDataTypeMap('class_definition_object_record')

    context = dtfabric_data_maps.DataTypeMapContext()

    try:
      class_definition_object_record = self._ReadStructureFromByteStream(
          object_record_data, file_offset, data_type_map,
          'Class definition object record', context=context)
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map class definition object record data at offset: '
          '0x{0:08x} with error: {1!s}').format(file_offset, exception))

    file_offset += context.byte_size

    if self._debug:
      self._DebugPrintStructureObject(
          class_definition_object_record,
          self._DEBUG_INFO_CLASS_DEFINITION_OBJECT_RECORD)

    class_definition_header = self._ReadClassDefinitionHeader(
        class_definition_object_record.data, file_offset)

    qualifiers_block_file_offset = (
        file_offset + 9 + class_definition_header.super_class_name_block_size)

    properties_block_file_offset = (
        qualifiers_block_file_offset +
        class_definition_header.qualifiers_block_size + 4 + (
            class_definition_header.number_of_property_descriptors * 8 ) +
        class_definition_header.default_value_size)

    class_name = self._ReadClassDefinitionName(
        class_definition_header.class_name_offset,
        class_definition_header.properties_block_data,
        properties_block_file_offset)

    class_qualifiers = {}
    if class_definition_header.qualifiers_block_size > 4:
      class_qualifiers = self._ReadQualifiers(
          class_definition_header.qualifiers_block_data,
          qualifiers_block_file_offset,
          class_definition_header.properties_block_data,
          properties_block_file_offset)

    cim_class_definition = CIMClassDefinition()
    cim_class_definition.super_class_name = (
        class_definition_object_record.super_class_name)
    cim_class_definition.name = class_name
    cim_class_definition.qualifiers = class_qualifiers

    self._ReadClassDefinitionProperties(
        class_definition_header.property_descriptors,
        class_definition_header.properties_block_data,
        properties_block_file_offset, cim_class_definition)

    data_offset = (
        12 + (class_definition_object_record.super_class_name_size * 2) +
        class_definition_object_record.data_size)

    if data_offset < len(object_record_data):
      if self._debug:
        self._DebugPrintData('Methods data', object_record_data[data_offset:])

      self._ReadClassDefinitionMethods(object_record_data[data_offset:])

    return cim_class_definition

  def _ReadClassDefinitionHeader(self, class_definition_data, file_offset):
    """Reads a class definition header.

    Args:
      class_definition_data (bytes): class definition data.
      file_offset (int): offset of the class definition data relative to
          the start of the file.

    Returns:
      class_definition_header: class definition header.

    Raises:
      ParseError: if the class definition cannot be read.
    """
    if self._debug:
      self._DebugPrintText((
          'Reading class definition header at offset: {0:d} '
          '(0x{0:08x}).\n').format(file_offset))

    data_type_map = self._GetDataTypeMap('class_definition_header')

    try:
      class_definition_header = self._ReadStructureFromByteStream(
          class_definition_data, file_offset, data_type_map,
          'Class definition header')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map class definition header data at offset: 0x{0:08x} '
          'with error: {1!s}').format(file_offset, exception))

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
    # TODO: set file_offset
    file_offset = 0

    if self._debug:
      self._DebugPrintText((
          'Reading class definition methods at offset: {0:d} '
          '(0x{0:08x}).\n').format(file_offset))

    data_type_map = self._GetDataTypeMap('class_definition_methods')

    try:
      class_definition_methods = self._ReadStructureFromByteStream(
          class_definition_data, file_offset, data_type_map,
          'Class definition methods')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map class definition methods data at offset: 0x{0:08x} '
          'with error: {1!s}').format(file_offset, exception))

    methods_block_size = class_definition_methods.methods_block_size

    if self._debug:
      value_string = '{0:d} (0x{1:08x})'.format(
          methods_block_size & 0x7fffffff, methods_block_size)
      self._DebugPrintValue('Methods block size', value_string)

      self._DebugPrintData(
          'Methods block data', class_definition_methods.methods_block_data)

  def _ReadClassDefinitionName(
      self, name_offset, properties_data, properties_data_file_offset):
    """Reads a class definition name.

    Args:
      name_offset (int): name offset.
      properties_data (bytes): class definition properties data.
      properties_data_file_offset (int): offset of the class definition
          properties data relative to the start of the file.

    Returns:
      str: class name.

    Raises:
      ParseError: if the name cannot be read.
    """
    file_offset = properties_data_file_offset + name_offset
    data_type_map = self._GetDataTypeMap('cim_string')

    try:
      class_name = self._ReadStructureFromByteStream(
          properties_data[name_offset:], file_offset, data_type_map,
          'Class name')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map class name data at offset: 0x{0:08x} with error: '
          '{1!s}').format(file_offset, exception))

    if self._debug:
      self._DebugPrintStructureObject(class_name, self._DEBUG_INFO_CLASS_NAME)

    return class_name.string

  def _ReadClassDefinitionPropertyDefinition(
      self, definition_offset, properties_data, properties_data_file_offset):
    """Reads a class definition property definition.

    Args:
      definition_offset (int): definition offset.
      properties_data (bytes): class definition properties data.
      properties_data_file_offset (int): offset of the class definition
          properties data relative to the start of the file.

    Returns:
      property_definition: property definition.

    Raises:
      ParseError: if the property name cannot be read.
    """
    file_offset = properties_data_file_offset + definition_offset
    data_type_map = self._GetDataTypeMap('property_definition')

    try:
      property_definition = self._ReadStructureFromByteStream(
          properties_data[definition_offset:], file_offset, data_type_map,
          'Property definition')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map property definition data at offset: 0x{0:08x} with '
          'error: {1!s}').format(file_offset, exception))

    if self._debug:
      self._DebugPrintStructureObject(
          property_definition, self._DEBUG_INFO_PROPERTY_DEFINITION)

    return property_definition

  def _ReadClassDefinitionPropertyName(
      self, property_index, name_offset, properties_data,
      properties_data_file_offset):
    """Reads a class definition property name.

    Args:
      index (int): property index.
      name_offset (int): name offset.
      properties_data (bytes): class definition properties data.
      properties_data_file_offset (int): offset of the class definition
          properties data relative to the start of the file.

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
      file_offset = properties_data_file_offset + name_offset
      data_type_map = self._GetDataTypeMap('cim_string')

      try:
        cim_string = self._ReadStructureFromByteStream(
            properties_data[name_offset:], file_offset, data_type_map,
           'Property name')
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            'Unable to map property name data at offset: 0x{0:08x} with '
            'error: {1!s}').format(file_offset, exception))

      if self._debug:
        self._DebugPrintPropertyName(property_index, cim_string)

      property_name = cim_string.string

    return property_name

  def _ReadClassDefinitionProperties(
      self, property_descriptors, properties_data, properties_data_file_offset,
      cim_class_definition):
    """Reads class definition properties.

    Args:
      property_descriptors (list[property_descriptor]): property descriptors.
      properties_data (bytes): class definition properties data.
      properties_data_file_offset (int): offset of the class definition
          properties data relative to the start of the file.
      cim_class_definition (CIMClassDefinition): CIM class definition.

    Raises:
      ParseError: if the properties cannot be read.
    """
    if self._debug:
      self._DebugPrintText('Reading class definition properties.\n')

    for property_index, property_descriptor in enumerate(property_descriptors):
      property_name = self._ReadClassDefinitionPropertyName(
          property_index, property_descriptor.name_offset, properties_data,
          properties_data_file_offset)

      property_definition = self._ReadClassDefinitionPropertyDefinition(
          property_descriptor.definition_offset, properties_data,
          properties_data_file_offset)

      qualifiers_block_file_offset = property_descriptor.definition_offset + 18

      property_qualifiers = self._ReadQualifiers(
          property_definition.qualifiers_block_data,
          qualifiers_block_file_offset,
          properties_data, properties_data_file_offset)

      cim_class_definition_property = CIMClassDefinitionProperty()
      cim_class_definition_property.name = property_name
      cim_class_definition_property.qualifiers = property_qualifiers

      cim_class_definition.properties[property_name] = (
          cim_class_definition_property)

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

  def _ReadQualifierName(
      self, qualifier_index, name_offset, properties_data, file_offset):
    """Reads a qualifier name.

    Args:
      qualifier_index (int): qualifier index.
      name_offset (int): name offset.
      properties_data (bytes): properties data.
      file_offset (int): offset of the properties data relative to the start of
          the file.

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
      file_offset += name_offset
      data_type_map = self._GetDataTypeMap('cim_string')

      try:
        cim_string = self._ReadStructureFromByteStream(
            properties_data[name_offset:], file_offset, data_type_map,
            'Qualifier name')
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            'Unable to map qualifier name data at offset: 0x{0:08x} with '
            'error: {1!s}').format(file_offset, exception))

      if self._debug:
        self._DebugPrintQualifierName(qualifier_index, cim_string)

      qualifier_name = cim_string.string

    return qualifier_name

  def _ReadQualifiers(
      self, qualifiers_data, qualifiers_data_file_offset, properties_data,
      properties_data_file_offset):
    """Reads qualifiers.

    Args:
      qualifiers_data (bytes): qualifiers data.
      qualifiers_data_file_offset (int): offset of the qualifiers data relative
          to the start of the file.
      properties_data (bytes): properties data.
      properties_data_file_offset (int): offset of the properties data relative
          to the start of the file.

    Returns:
      dict[str, object]: qualifier names and values.

    Raises:
      ParseError: if the qualifiers cannot be read.
    """
    if self._debug:
      self._DebugPrintText(
          'Reading qualifiers at offset: {0:d} (0x{0:08x}).\n'.format(
              qualifiers_data_file_offset))

    qualifiers = {}
    qualifiers_data_offset = 0
    qualifier_index = 0

    while qualifiers_data_offset < len(qualifiers_data):
      file_offset = qualifiers_data_file_offset + qualifiers_data_offset
      data_type_map = self._GetDataTypeMap('qualifier_descriptor')

      context = dtfabric_data_maps.DataTypeMapContext()

      try:
        qualifier_descriptor = self._ReadStructureFromByteStream(
            qualifiers_data[qualifiers_data_offset:], file_offset,
            data_type_map, 'Qualifier descriptor', context=context)
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            'Unable to map qualifier descriptor data at offset: 0x{0:08x} with '
            'error: {1!s}').format(file_offset, exception))

      if self._debug:
        self._DebugPrintStructureObject(
            qualifier_descriptor, self._DEBUG_INFO_QUALIFIER_DESCRIPTOR)

      qualifier_name = self._ReadQualifierName(
          qualifier_index, qualifier_descriptor.name_offset, properties_data,
          properties_data_file_offset)

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
            properties_data_file_offset)

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
      self, value_offset, properties_data, file_offset):
    """Reads a qualifier value.

    Args:
      value_offset (int): value offset.
      properties_data (bytes): properties data.
      file_offset (int): offset of the properties data relative to the start of
          the file.

    Returns:
      str: qualifier value.

    Raises:
      ParseError: if the qualifier value cannot be read.
    """
    file_offset += value_offset
    data_type_map = self._GetDataTypeMap('cim_string')

    try:
      cim_string = self._ReadStructureFromByteStream(
          properties_data[value_offset:], file_offset, data_type_map,
          'Qualifier value')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError((
          'Unable to map qualifier value string data at offset: 0x{0:08x} '
          'with error: {1!s}').format(file_offset, exception))

    if self._debug:
      self._DebugPrintCIMString(cim_string)

    return cim_string.string

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
        cim_class_definition = self._ReadClassDefinition(
            self.data, self.file_offset)
        self._DebugPrintCIMClassDefinition(cim_class_definition)

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

    # TODO: set file_offset
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
