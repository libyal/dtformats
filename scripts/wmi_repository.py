#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to parse WMI Common Information Model (CIM) repository files."""

from __future__ import print_function
from __future__ import unicode_literals

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
  source_basename = source_basename.upper()

  cim_repository = wmi_repository.CIMRepository(
      debug=options.debug, output_writer=output_writer)

  if source_basename == 'INDEX.BTR':
    source = os.path.dirname(options.source)
    cim_repository.OpenIndexBinaryTree(source)

  else:
    cim_repository.Open(options.source)

    object_record_keys = {}
    for key in cim_repository.GetKeys():
      if '.' not in key:
        continue

      _, _, key_name = key.rpartition('\\')
      key_name, _, _ = key_name.partition('.')

      if key_name not in object_record_keys:
        object_record_keys[key_name] = []

      object_record_keys[key_name].append(key)

    for key_name, keys in iter(object_record_keys.items()):
      for key in keys:
        print(key)
        object_record = cim_repository.GetObjectRecordByKey(key)
        object_record.Read()

  cim_repository.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
