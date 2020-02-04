# -*- coding: utf-8 -*-
"""Windows AMCache files."""

from __future__ import unicode_literals

import pyregf

from dtformats import data_format


class WindowsTaskSchedularJobFile(data_format.BinaryDataFile):
  """Windows AMCache (AMCache.hve) file."""

  def ReadFileObject(self, file_object):
    """Reads a Windows AMCache file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    _ = pyregf.file()
