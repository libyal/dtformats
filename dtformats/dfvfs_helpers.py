# -*- coding: utf-8 -*-
"""dfVFS helpers."""

from dfvfs.helpers import command_line as dfvfs_command_line
from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner
from dfvfs.lib import definitions as dfvfs_definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver as dfvfs_resolver

from dtformats import file_system


class DFVFSFileSystemHelper(
    file_system.FileSystemHelper, dfvfs_volume_scanner.VolumeScanner):
  """dfVFS file system helper."""

  def __init__(self, mediator):
    """dfVFS file system helper.

    Args:
      mediator (dfvfs.VolumeScannerMediator): mediator.
    """
    super(DFVFSFileSystemHelper, self).__init__()
    self._file_system = None
    self._parent_path_spec = None
    self._mediator = mediator

  def BasenamePath(self, path):
    """Determines the basename of the path.

    Args:
      path (str): path.

    Returns:
      str: basename of the path.
    """
    return self._file_system.BasenamePath(path)

  def CheckFileExistsByPath(self, path):
    """Checks if a specific file exists.

    Args:
      path (str): path of the file.

    Returns:
      bool: True if the file exists, False otherwise.
    """
    path_spec = path_spec_factory.Factory.NewPathSpec(
        self._file_system.type_indicator, location=path,
        parent=self._parent_path_spec)

    return self._file_system.FileEntryExistsByPathSpec(path_spec)

  def DirnamePath(self, path):
    """Determines the directory name of the path.

    Args:
      path (str): path.

    Returns:
      str: directory name of the path or None.
    """
    return self._file_system.DirnamePath(path)

  def GetFileSizeByPath(self, path):
    """Retrieves the size of a specific file.

    Args:
      path (str): path of the file.

    Returns:
      int: size of the file in bytes or None if not available.
    """
    path_spec = path_spec_factory.Factory.NewPathSpec(
        self._file_system.type_indicator, location=path,
        parent=self._parent_path_spec)

    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    if not file_entry:
      return None

    return file_entry.size

  def JoinPath(self, path_segments):
    """Joins the path segments into a path.

    Args:
      path_segments (list[str]): path segments.

    Returns:
      str: joined path segments prefixed with the path separator.
    """
    return self._file_system.JoinPath(path_segments)

  def ListDirectory(self, path):
    """Lists the entries in a directory.

    Args:
      path (str): path of the directory.

    Yields:
      str: name of a directory entry.
    """
    path_spec = path_spec_factory.Factory.NewPathSpec(
        self._file_system.type_indicator, location=path,
        parent=self._parent_path_spec)

    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    if file_entry:
      for sub_file_entry in file_entry.sub_file_entries:
        yield sub_file_entry.name

  def OpenFileByPath(self, path):
    """Opens a specific file.

    Args:
      path (str): path of the file.

    Returns:
      file: file-like object of the file.
    """
    path_spec = path_spec_factory.Factory.NewPathSpec(
        self._file_system.type_indicator, location=path,
        parent=self._parent_path_spec)

    return self._file_system.GetFileObjectByPathSpec(path_spec)

  def OpenFileSystem(self, path_spec):
    """Opens a file system.

    Args:
      path_spec (dfvfs.PathSpec): file system path specification.
    """
    self._file_system = dfvfs_resolver.Resolver.OpenFileSystem(path_spec)
    self._parent_path_spec = path_spec.parent

  def SplitPath(self, path):
    """Splits the path into path segments.

    Args:
      path (str): path.

    Returns:
      list[str]: path segments without the root path segment, which is
          an empty string.
    """
    return self._file_system.SplitPath(path)


def SetDFVFSBackEnd(back_end):
  """Sets the dfVFS back-end.

  Args:
    back_end (str): dfVFS back-end.
  """
  if back_end == 'APM':
    dfvfs_definitions.PREFERRED_APM_BACK_END = (
        dfvfs_definitions.TYPE_INDICATOR_APM)

  elif back_end == 'EXT':
    dfvfs_definitions.PREFERRED_EXT_BACK_END = (
        dfvfs_definitions.TYPE_INDICATOR_EXT)

  elif back_end == 'FAT':
    dfvfs_definitions.PREFERRED_FAT_BACK_END = (
        dfvfs_definitions.TYPE_INDICATOR_FAT)

  elif back_end == 'GPT':
    dfvfs_definitions.PREFERRED_GPT_BACK_END = (
        dfvfs_definitions.TYPE_INDICATOR_GPT)

  elif back_end == 'HFS':
    dfvfs_definitions.PREFERRED_HFS_BACK_END = (
        dfvfs_definitions.TYPE_INDICATOR_HFS)

  elif back_end == 'NTFS':
    dfvfs_definitions.PREFERRED_NTFS_BACK_END = (
        dfvfs_definitions.TYPE_INDICATOR_NTFS)

  elif back_end == 'TSK':
    dfvfs_definitions.PREFERRED_APM_BACK_END = (
        dfvfs_definitions.TYPE_INDICATOR_TSK)
    dfvfs_definitions.PREFERRED_EXT_BACK_END = (
        dfvfs_definitions.TYPE_INDICATOR_TSK)
    dfvfs_definitions.PREFERRED_FAT_BACK_END = (
        dfvfs_definitions.TYPE_INDICATOR_TSK)
    dfvfs_definitions.PREFERRED_GPT_BACK_END = (
        dfvfs_definitions.TYPE_INDICATOR_TSK_PARTITION)
    dfvfs_definitions.PREFERRED_HFS_BACK_END = (
        dfvfs_definitions.TYPE_INDICATOR_TSK)
    dfvfs_definitions.PREFERRED_NTFS_BACK_END = (
        dfvfs_definitions.TYPE_INDICATOR_TSK)


def AddDFVFSCLIArguments(argument_parser):
  """Adds dfVFS command line arguments.

  Args:
    argument_parser (argparse.ArgumentParser): argument parser.
  """
  argument_parser.add_argument(
      '--back_end', '--back-end', dest='back_end', action='store',
      metavar='NTFS', default=None, help='preferred dfVFS back-end.')

  argument_parser.add_argument(
      '--image', dest='image', action='store', type=str, default=None,
      help='path of the storage media image.')

  argument_parser.add_argument(
      '--partitions', '--partition', dest='partitions', action='store',
      type=str, default=None, help=(
          'Define partitions to be processed. A range of partitions can be '
          'defined as: "3..5". Multiple partitions can be defined as: "1,3,5" '
          '(a list of comma separated values). Ranges and lists can also be '
          'combined as: "1,3..5". The first partition is 1. All partitions '
          'can be specified with: "all".'))

  argument_parser.add_argument(
      '--snapshots', '--snapshot', dest='snapshots', action='store', type=str,
      default=None, help=(
          'Define snapshots to be processed. A range of snapshots can be '
          'defined as: "3..5". Multiple snapshots can be defined as: "1,3,5" '
          '(a list of comma separated values). Ranges and lists can also be '
          'combined as: "1,3..5". The first snapshot is 1. All snapshots can '
          'be specified with: "all".'))

  argument_parser.add_argument(
      '--volumes', '--volume', dest='volumes', action='store', type=str,
      default=None, help=(
          'Define volumes to be processed. A range of volumes can be defined '
          'as: "3..5". Multiple volumes can be defined as: "1,3,5" (a list '
          'of comma separated values). Ranges and lists can also be combined '
          'as: "1,3..5". The first volume is 1. All volumes can be specified '
          'with: "all".'))


def ParseDFVFSCLIArguments(options):
  """Parses dfVFS command line arguments.

  Args:
    options (argparse.Namespace): command line arguments.

  Returns:
    DFVFSFileSystemHelper: dfVFS file system helper or None if no file system
        could be found.
  """
  SetDFVFSBackEnd(options.back_end)

  mediator = dfvfs_command_line.CLIVolumeScannerMediator()

  volume_scanner_options = dfvfs_volume_scanner.VolumeScannerOptions()
  volume_scanner_options.partitions = mediator.ParseVolumeIdentifiersString(
      options.partitions)

  if options.snapshots == 'none':
    volume_scanner_options.snapshots = ['none']
  else:
    volume_scanner_options.snapshots = mediator.ParseVolumeIdentifiersString(
        options.snapshots)

  volume_scanner_options.volumes = mediator.ParseVolumeIdentifiersString(
      options.volumes)

  file_system_helper = DFVFSFileSystemHelper(mediator)

  base_path_specs = file_system_helper.GetBasePathSpecs(
      options.image, options=volume_scanner_options)
  if len(base_path_specs) != 1:
    return None

  file_system_helper.OpenFileSystem(base_path_specs[0])

  return file_system_helper
