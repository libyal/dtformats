# -*- coding: utf-8 -*-
"""YAML-based debug definitions file."""

import collections
import yaml

from dtformats import errors


class DebugDefinitionAttribute(object):
  """Debug definition attribute.

  Attributes:
    description (str): description of the attribute.
    format (str): format in which the attribute values should be represented.
    name (str): name of the corresponding attribute.
  """

  def __init__(self, name=None):
    """Initialized a debug definition attribute.

    Args:
      name (Optional[str]): name of the corresponding attribute.
    """
    super(DebugDefinitionAttribute, self).__init__()
    self.description = None
    self.format = None
    self.name = name


class DebugDefinition(object):
  """Debug definition.

  Attributes:
    attributes (dict[str, DebugDefinitionAttribute]): debug definitions
        attributes per name.
    data_type_map (str): name of the corresponding dtFabric data type map.
  """

  def __init__(self, data_type_map=None):
    """Initialized a debug definition.

    Args:
      data_type_map (str): name of the corresponding dtFabric data type map.
    """
    super(DebugDefinition, self).__init__()
    self.attributes = collections.OrderedDict()
    self.data_type_map = data_type_map


class YAMLDebugDefinitionsFile(object):
  """YAML-based debug definitions file.

  A YAML-based debug definitions file contains one or more debug definitions.
  A debug definition consists of:

  data_type_map: job_fixed_length_data_section
  attributes:
  - name: signature
    description: "Signature"
    format: custom

  Where:
  * data_type_map, unique identifier of the corresponding data type map;
  * attributes, debug definition attributes.
  """

  _SUPPORTED_KEYS = frozenset([
      'attributes',
      'data_type_map'])

  _SUPPORTED_FORMATS = frozenset([
      'binary_data',
      'decimal',
      'floating_point',
      'hexadecimal',
      'hexadecimal_2digits',
      'hexadecimal_4digits',
      'hexadecimal_8digits',
      'string',
      'uuid'])

  def _ReadDefinition(self, definition_values):
    """Reads a definition from a dictionary.

    Args:
      definition_values (dict[str, object]): debug definition
          values.

    Returns:
      DebugDefinition: a debug definition.

    Raises:
      ParseError: if the definition is not set or incorrect.
    """
    if not definition_values:
      raise errors.ParseError('Missing debug definition values.')

    different_keys = set(definition_values) - self._SUPPORTED_KEYS
    if different_keys:
      different_keys = ', '.join(different_keys)
      raise errors.ParseError(f'Undefined keys: {different_keys:s}')

    data_type_map = definition_values.get('data_type_map', None)
    if not data_type_map:
      raise errors.ParseError('Invalid debug definition missing data type map.')

    attributes = definition_values.get('attributes', None)
    if not attributes:
      raise errors.ParseError(
          f'Invalid debug definition: {data_type_map:s} missing attributes.')

    debug_definition = DebugDefinition(data_type_map=data_type_map)

    for attribute_index, attribute_values in enumerate(attributes):
      attribute_name = attribute_values.get('name', None)
      if not attribute_name:
        raise errors.ParseError((
            f'Invalid debug definition: {data_type_map:s} name missing of '
            f'attribute: {attribute_index:d}.'))

      if attribute_name in debug_definition.attributes:
        raise errors.ParseError((
            f'Invalid debug definition: {data_type_map:s} attribute: '
            f'{attribute_name:s} already set.'))

      attribute_description = attribute_values.get('description', None)
      if not attribute_description:
        raise errors.ParseError((
            f'Invalid debug definition: {data_type_map:s} description '
            f'missing of attribute: {attribute_name:s}.'))

      attribute_format = attribute_values.get('format', None)
      if not attribute_format:
        raise errors.ParseError((
            f'Invalid debug definition: {data_type_map:s} format '
            f'missing of attribute: {attribute_name:s}.'))

      if (attribute_format not in self._SUPPORTED_FORMATS and
          not attribute_format.startswith('custom:')):
        raise errors.ParseError((
            f'Invalid debug definition: {data_type_map:s} unsupported '
            f'format: {attribute_format:s} in attribute: {attribute_name:s}.'))

      definition_attribute = DebugDefinitionAttribute(name=attribute_name)
      definition_attribute.description = attribute_description
      definition_attribute.format = attribute_format

      debug_definition.attributes[attribute_name] = definition_attribute

    return debug_definition

  def _ReadFromFileObject(self, file_object):
    """Reads the definitions from a file-like object.

    Args:
      file_object (file): definitions file-like object.

    Yields:
      DebugDefinition: a debug definition.
    """
    yaml_generator = yaml.safe_load_all(file_object)

    for yaml_definition in yaml_generator:
      yield self._ReadDefinition(yaml_definition)

  def ReadFromFile(self, path):
    """Reads the definitions from a YAML file.

    Args:
      path (str): path to a definitions file.

    Yields:
      DebugDefinition: a debug definition.
    """
    with open(path, 'r', encoding='utf-8') as file_object:
      for yaml_definition in self._ReadFromFileObject(file_object):
        yield yaml_definition
