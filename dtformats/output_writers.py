# -*- coding: utf-8 -*-
"""Output writer."""

from __future__ import print_function
from __future__ import unicode_literals

import abc


class OutputWriter(object):
  """Output writer."""

  @abc.abstractmethod
  def Close(self):
    """Closes the output writer object.

    Raises:
      IOError: if the output writer cannot be closed.
    """

  @abc.abstractmethod
  def Open(self):
    """Opens the output writer object.

    Raises:
      IOError: if the output writer cannot be opened.
    """

  @abc.abstractmethod
  def WriteText(self, text):
    """Writes text to the output.

    Args:
      text (str): text to write.
    """


class StdoutWriter(OutputWriter):
  """Stdout output writer."""

  def Close(self):
    """Closes the output writer object."""
    return

  def Open(self):
    """Opens the output writer object."""
    return

  def WriteText(self, text):
    """Writes text to the output.

    Args:
      text (str): text to write.
    """
    print(text, end='')
