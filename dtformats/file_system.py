# -*- coding: utf-8 -*-
"""File system helper."""

import abc
import os


class FileSystemHelper(object):
  """File system helper interface."""

  @abc.abstractmethod
  def BasenamePath(self, path):
    """Determines the basename of the path.

    Args:
      path (str): path.

    Returns:
      str: basename of the path.
    """

  @abc.abstractmethod
  def CheckFileExistsByPath(self, path):
    """Checks if a specific file exists.

    Args:
      path (str): path of the file.

    Returns:
      bool: True if the file exists, False otherwise.
    """

  @abc.abstractmethod
  def DirnamePath(self, path):
    """Determines the directory name of the path.

    Args:
      path (str): path.

    Returns:
      str: directory name of the path or None.
    """

  @abc.abstractmethod
  def GetFileSizeByPath(self, path):
    """Retrieves the size of a specific file.

    Args:
      path (str): path of the file.

    Returns:
      int: size of the file in bytes.
    """

  @abc.abstractmethod
  def JoinPath(self, path_segments):
    """Joins the path segments into a path.

    Args:
      path_segments (list[str]): path segments.

    Returns:
      str: joined path segments prefixed with the path separator.
    """

  @abc.abstractmethod
  def ListDirectory(self, path):
    """Lists the entries in a directory.

    Args:
      path (str): path of the directory.

    Yields:
      str: name of a directory entry.
    """

  @abc.abstractmethod
  def OpenFileByPath(self, path):
    """Opens a specific file.

    Args:
      path (str): path of the file.

    Returns:
      file: file-like object of the file.
    """

  @abc.abstractmethod
  def SplitPath(self, path):
    """Splits the path into path segments.

    Args:
      path (str): path.

    Returns:
      list[str]: path segments without the root path segment, which is
          an empty string.
    """


class NativeFileSystemHelper(object):
  """Python native system helper."""

  def BasenamePath(self, path):
    """Determines the basename of the path.

    Args:
      path (str): path.

    Returns:
      str: basename of the path.
    """
    return os.path.basename(path)

  def CheckFileExistsByPath(self, path):
    """Checks if a specific file exists.

    Args:
      path (str): path of the file.

    Returns:
      bool: True if the file exists, False otherwise.
    """
    return os.path.exists(path)

  def DirnamePath(self, path):
    """Determines the directory name of the path.

    Args:
      path (str): path.

    Returns:
      str: directory name of the path or None.
    """
    return os.path.dirname(path)

  def GetFileSizeByPath(self, path):
    """Retrieves the size of a specific file.

    Args:
      path (str): path of the file.

    Returns:
      int: size of the file in bytes.
    """
    stat_object = os.stat(path)

    return stat_object.st_size

  def JoinPath(self, path_segments):
    """Joins the path segments into a path.

    Args:
      path_segments (list[str]): path segments.

    Returns:
      str: joined path segments prefixed with the path separator.
    """
    return ''.join([os.path.sep, os.path.sep.join(path_segments)])

  def ListDirectory(self, path):
    """Lists the entries in a directory.

    Args:
      path (str): path of the directory.

    Yields:
      str: name of a directory entry.
    """
    yield from os.listdir(path)

  def OpenFileByPath(self, path):
    """Opens a specific file.

    Args:
      path (str): path of the file.

    Returns:
      file: file-like object of the file.
    """
    return open(path, 'rb')  # pylint: disable=consider-using-with

  def SplitPath(self, path):
    """Splits the path into path segments.

    Args:
      path (str): path.

    Returns:
      list[str]: path segments without the root path segment, which is
          an empty string.
    """
    # Split the path with the path separator and remove empty path segments.
    return list(filter(None, path.split(os.path.sep)))
