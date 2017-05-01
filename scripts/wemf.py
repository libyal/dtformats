#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to parse Windows (Enhanced) Metafile Format (WMF and EMF) files."""

from __future__ import print_function
import argparse
import logging
import os
import sys

from dtformats import output_writers
from dtformats import wemf


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Extracts information from Windows (Enhanced) Metafile files.'))

  argument_parser.add_argument(
      u'-d', u'--debug', dest=u'debug', action=u'store_true', default=False,
      help=u'enable debug output.')

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH',
      default=None, help=u'path of the Windows (Enhanced) Metafile file.')

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

  with open(options.source, 'rb') as file_object:
    file_object.seek(40, os.SEEK_SET)
    emf_signature = file_object.read(4)

  if emf_signature == b'FME ':
    wemf_file = wemf.EMFFile(debug=options.debug, output_writer=output_writer)
  else:
    wemf_file = wemf.WMFFile(debug=options.debug, output_writer=output_writer)

  wemf_file.Open(options.source)

  description = u'{0:s} information:'.format(wemf_file.FILE_TYPE)
  output_writer.WriteText(description)

  wemf_file.Close()

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
