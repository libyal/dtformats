#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to parse WMI Common Information Model (CIM) repository files."""

from __future__ import print_function
import argparse
import logging
import sys

from dtformats import output_writers
from dtformats import wmi_repository


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Extracts information from WMI Common Information Model (CIM) '
      u'repository files.'))

  argument_parser.add_argument(
      u'-d', u'--debug', dest=u'debug', action=u'store_true', default=False,
      help=u'enable debug output.')

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH',
      default=None, help=(
          u'path of the directory containing the WMI Common Information '
          u'Model (CIM) repository files.'))

  options = argument_parser.parse_args()

  if not options.source:
    print(u'Source file missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  output_writer = output_writers.StdoutWriter()

  try:
    output_writer.Open()
  except IOError as exception:
    print(u'Unable to open output writer with error: {0!s}'.format(exception))
    print(u'')
    return False

  cim_repository = wmi_repository.CIMRepository(
      debug=options.debug, output_writer=output_writer)

  cim_repository.Open(options.source)

  object_record_keys = {}
  for key in cim_repository.GetKeys():
    if u'.' not in key:
      continue

    _, _, key_name = key.rpartition(u'\\')
    key_name, _, _ = key_name.partition(u'.')

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
