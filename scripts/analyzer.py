#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to analyze a data format using a dtFabric definition."""

import argparse
import logging
import sys

from dtfabric import definitions
from dtformats import data_format
from dtformats import output_writers


class BinaryDataFormatAnalyzer(data_format.BinaryDataFormat):
  """Binary data format analyzer."""

  _VALUE_FORMAT_CALLBACKS = {
      definitions.TYPE_INDICATOR_FLOATING_POINT: '_FormatFloatingPoint',
      definitions.TYPE_INDICATOR_INTEGER: '_FormatIntegerAsDecimal',
      definitions.TYPE_INDICATOR_SEQUENCE: '_FormatSequence',
      definitions.TYPE_INDICATOR_STREAM: '_FormatDataInHexadecimal',
      definitions.TYPE_INDICATOR_STRING: '_FormatString',
      definitions.TYPE_INDICATOR_UUID: '_FormatUUIDAsString'}

  def __init__(self, debug=False, output_writer=None):
    """Initializes a binary data file.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(BinaryDataFormatAnalyzer, self).__init__(
        debug=debug, output_writer=output_writer)
    self._debug_info_per_data_type = {}

  def _AnalyzeDataTypeMap(self, file_object, file_offset, name):
    """Reads a structure from the file-like object and maps it to data types.

    Args:
      file_object (file): file-like object to analyze.
      file_offset (int): offset of the structure data relative to the start
          of the file-like object.
      name (str): name of the data type map.
    """
    data_type_map = self._GetDataTypeMap(name)

    structure_object, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, name)

    if self._debug:
      # pylint: disable=protected-access
      data_type_definition = (
          self._FABRIC._definitions_registry.GetDefinitionByName(name))

      self._DebugPrintDataTypeMap(name, data_type_definition, structure_object)

  def _DebugPrintDataTypeMap(
      self, name, data_type_definition, structure_object):
    """Prints data type map debug debug information.

    Args:
      name (str): name of the data type map.
      data_type_definition (dtfabric.DataTypeDefinition): dtFabric data type
          definition.
      structure_object (object): structure object.
    """
    text = self._FormatDataTypeMap(name, data_type_definition, structure_object)
    self._output_writer.WriteText(text)

  def _DetermineDebugInfo(self, data_type_definition):
    """Determines the debug information from a data type definition.

    Args:
      data_type_definition (dtfabric.DataTypeDefinition): dtFabric data type
          definition.

    Returns:
      list[tuple[str, str, str]]: debug information.
    """
    debug_info = []
    members = getattr(data_type_definition, 'members', [])
    for member in members:
      description = member.name.replace('_', ' ').capitalize()
      data_type = getattr(member, 'member_data_type_definition', member)
      if member.name.endswith('checksum') or member.name.endswith('offset'):
        value_format_callback = '_FormatIntegerAsHexadecimal8'
      else:
        value_format_callback = self._VALUE_FORMAT_CALLBACKS.get(
            data_type.TYPE_INDICATOR, None)

      if value_format_callback:
        debug_info_tuple = (member.name, description, value_format_callback)
        debug_info.append(debug_info_tuple)

    return debug_info

  def _FormatSequence(self, sequence):
    """Formats a sequence.

    Args:
      sequence (list[object]): sequence.

    Returns:
      str: formatted string.
    """
    lines = ['\n']
    for element_number, element in enumerate(sequence):
      lines.append(f'Entry: {element_number:d}\n')

      name = element.__class__.__name__
      # pylint: disable=protected-access
      data_type_definition = (
          self._FABRIC._definitions_registry.GetDefinitionByName(name))

      text = self._FormatDataTypeMap(name, data_type_definition, element)
      lines.append(text)

    return ''.join(lines)

  def _FormatDataTypeMap(self, name, data_type_definition, structure_object):
    """Formats data type map debug information.

    Args:
      name (str): name of the data type map.
      data_type_definition (dtfabric.DataTypeDefinition): dtFabric data type
          definition.
      structure_object (object): structure object.

    Returns:
      str: structure object debug information.
    """
    debug_info = self._debug_info_per_data_type.get(name, None)
    if not debug_info:
      debug_info = self._DetermineDebugInfo(data_type_definition)
      self._debug_info_per_data_type[name] = debug_info

    return self._FormatStructureObject(structure_object, debug_info)

  def ReadDefinition(self, filename):
    """Reads a dtFabric definition.

    Args:
      filename (str): name of the dtFabric definition file.
    """
    self._FABRIC = self.ReadDefinitionFile(filename)  # pylint: disable=invalid-name

  def ReadFileObject(self, file_object):
    """Reads binary data from a file-like object.

    Args:
      file_object (file): file-like object.
    """
    # TODO: map dtFabric definitions to file data and print structures
    # * which structure to map first?
    # * how to map additional structures?

    self._AnalyzeDataTypeMap(file_object, 0, 'file_information')
    self._AnalyzeDataTypeMap(file_object, 64 * 1024, 'header')
    self._AnalyzeDataTypeMap(file_object, 2 * 64 * 1024, 'header')
    self._AnalyzeDataTypeMap(file_object, 3 * 64 * 1024, 'region_table')
    self._AnalyzeDataTypeMap(file_object, 4 * 64 * 1024, 'region_table')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Analyzes a data format using a dtFabric definition.'))

  argument_parser.add_argument(
      'definition', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the dtFabric definition file.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the source file.')

  options = argument_parser.parse_args()

  if not options.definition:
    print('Definition file missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  # TODO: remove when layout functionality has been implemented.
  if options.definition != 'vhdx.yaml':
    print('Definition file currently not supported.')
    print('')
    return False

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
    print(f'Unable to open output writer with error: {exception!s}')
    print('')
    return False

  analyzer = BinaryDataFormatAnalyzer(debug=True, output_writer=output_writer)

  analyzer.ReadDefinition(options.definition)

  # TODO: load formatting definitions if defined

  with open(options.source, 'rb') as file_object:
    analyzer.ReadFileObject(file_object)

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
