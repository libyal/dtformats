# -*- coding: utf-8 -*-
"""Output writer."""

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

  @abc.abstractmethod
  def WriteValue(self, description, value):
    """Writes a value.

    Args:
      description (str): description.
      value (str): value to write.
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

  def WriteValue(self, description, value):
    """Writes a value.

    Args:
      description (str): description.
      value (object): value.
    """
    description_no_tabs = description.replace('\t', ' ' * 8)
    alignment, _ = divmod(len(description_no_tabs), 8)
    alignment_string = '\t' * (8 - alignment + 1)
    self.WriteText(f'{description:s}{alignment_string:s}: {value!s}\n')
