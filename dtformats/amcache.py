# -*- coding: utf-8 -*-
"""Windows AMCache files."""

from __future__ import unicode_literals

from dtformats import data_format

import pyregf


class WindowsTaskSchedularJobFile(data_format.BinaryDataFile):
  """Windows AMCache (AMCache.hve) file."""

  def ReadFileObject(self, file_object):
    """Reads a Windows AMCache file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
