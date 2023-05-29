#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the YAML-based debug definitions file."""

import io
import unittest

from dtformats import errors
from dtformats import yaml_definitions_file

from tests import test_lib as shared_test_lib


class YAMLDebugDefinitionsFileTest(shared_test_lib.BaseTestCase):
  """Tests for the YAML-based debug definitions file."""

  # pylint: disable=protected-access

  _FORMATTERS_YAML = {
      'data_type_map': 'test_data_type_map',
      'attributes': [
          {'name': 'signature', 'description': 'Signature',
           'format': 'custom:signature'}]}

  def testReadDefinition(self):
    """Tests the _ReadDefinition function."""
    test_definitions_file = (
        yaml_definitions_file.YAMLDebugDefinitionsFile())

    debug_definition = test_definitions_file._ReadDefinition(
        self._FORMATTERS_YAML)

    self.assertIsNotNone(debug_definition)
    self.assertEqual(debug_definition.data_type_map, 'test_data_type_map')
    self.assertEqual(len(debug_definition.attributes), 1)

    debug_definition_attribute = debug_definition.attributes.get(
        'signature', None)
    self.assertIsNotNone(debug_definition_attribute)
    self.assertEqual(debug_definition_attribute.name, 'signature')
    self.assertEqual(debug_definition_attribute.description, 'Signature')
    self.assertEqual(debug_definition_attribute.format, 'custom:signature')

    with self.assertRaises(errors.ParseError):
      test_definitions_file._ReadDefinition({})

    with self.assertRaises(errors.ParseError):
      test_definitions_file._ReadDefinition({
          'data_type_map': 'test_data_type_map',
          'attributes': []})

    with self.assertRaises(errors.ParseError):
      test_definitions_file._ReadDefinition({
          'data_type_map': 'test_data_type_map',
          'attributes': [{'description': 'Signature',
                          'format': 'custom:signature'}]})

    with self.assertRaises(errors.ParseError):
      test_definitions_file._ReadDefinition({
          'data_type_map': 'test_data_type_map',
          'attributes': [{'name': 'path', 'format': 'custom:signature'}]})

    with self.assertRaises(errors.ParseError):
      test_definitions_file._ReadDefinition({
          'data_type_map': 'test_data_type_map',
          'attributes': [{'name': 'path', 'description': 'Signature'}]})

  def testReadFromFileObject(self):
    """Tests the _ReadFromFileObject function."""
    test_file_path = self._GetTestFilePath(['definitions.debug.yaml'])
    self._SkipIfPathNotExists(test_file_path)

    test_definitions_file = (
        yaml_definitions_file.YAMLDebugDefinitionsFile())

    with io.open(test_file_path, 'r', encoding='utf-8') as file_object:
      definitions = list(test_definitions_file._ReadFromFileObject(file_object))

    self.assertEqual(len(definitions), 1)

  def testReadFromFile(self):
    """Tests the ReadFromFile function."""
    test_file_path = self._GetTestFilePath(['definitions.debug.yaml'])
    self._SkipIfPathNotExists(test_file_path)

    test_definitions_file = (
        yaml_definitions_file.YAMLDebugDefinitionsFile())

    definitions = list(test_definitions_file.ReadFromFile(test_file_path))

    self.assertEqual(len(definitions), 1)

    self.assertEqual(definitions[0].data_type_map, 'test_data_type_map')


if __name__ == '__main__':
  unittest.main()
