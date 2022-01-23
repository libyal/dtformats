#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse WMI Common Information Model (CIM) repository files."""

import argparse
import logging
import os
import sys

from dtformats import output_writers
from dtformats import wmi_repository


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts information from WMI Common Information Model (CIM) '
      'repository files.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH',
      default=None, help=(
          'path of the directory containing the WMI Common Information '
          'Model (CIM) repository files.'))

  options = argument_parser.parse_args()

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
    print('Unable to open output writer with error: {0!s}'.format(exception))
    print('')
    return False

  source_basename = os.path.basename(options.source)
  source_basename = source_basename.lower()

  cim_repository = wmi_repository.CIMRepository(
      debug=options.debug, output_writer=output_writer)

  if source_basename == 'index.btr':
    source = os.path.dirname(options.source)
    cim_repository.OpenIndexBinaryTree(source)

  elif source_basename in (
      'index.map', 'mapping1.map', 'mapping2.map', 'mapping3.map',
      'objects.map'):
    cim_repository.OpenMappingFile(options.source)

  else:
    cim_repository.Open(options.source)

    if options.debug:
      # pylint: disable=protected-access
      for class_definition in (
          cim_repository._class_definitions_by_name.values()):
        cim_repository._DebugPrintClassDefinition(class_definition)

    object_record_keys = {}
    for key in cim_repository.GetKeys():
      if '.' not in key:
        continue

      _, _, key_name = key.rpartition('\\')
      key_name, _, _ = key_name.partition('.')

      if key_name not in object_record_keys:
        object_record_keys[key_name] = []

      object_record_keys[key_name].append(key)

    for key_name, keys in object_record_keys.items():
      for key in keys:
        print(key)
        if options.debug:
          object_record = cim_repository.GetObjectRecordByKey(key)

          if object_record.data_type in ('I', 'IL'):
            instance = wmi_repository.Instance(
                cim_repository.format_version, debug=options.debug,
                output_writer=output_writer)
            instance.ReadObjectRecord(object_record)

            class_definition = cim_repository.GetClassDefinition(
                instance.digest_hash)
            # pylint: disable=protected-access
            cim_repository._DebugPrintClassDefinition(class_definition)

          elif object_record.data_type == 'R':
            registration = wmi_repository.Registration(
                debug=options.debug, output_writer=output_writer)
            registration.ReadObjectRecord(object_record)

  cim_repository.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
