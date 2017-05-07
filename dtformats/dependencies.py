# -*- coding: utf-8 -*-
"""Functionality to check for the availability and version of dependencies."""

from __future__ import print_function
import re


# Dictionary that contains version tuples per module name.
#
# A version tuple consists of:
# (version_attribute_name, minimum_version, maximum_version, is_required)
#
# Where version_attribute_name is either a name of an attribute,
# property or method.
PYTHON_DEPENDENCIES = {
    u'dtfabric': (u'__version__', u'20170507', None, True),
    u'pyfwsi': (u'get_version()', u'20150606', None, True),
    u'pylnk': (u'get_version()', u'20150830', None, True),
    u'pyolecf': (u'get_version()', u'20151223', None, True),
    u'yaml': (u'__version__', u'3.10', None, True)}

PYTHON_TEST_DEPENDENCIES = {
    u'mock': (u'__version__', u'0.7.1', None, True)}

# Maps Python module names to DPKG packages.
_DPKG_PACKAGE_NAMES = {
    u'pyfwsi': u'libfwsi-python',
    u'pylnk': u'liblnk-python',
    u'pyolecf': u'libolecf-python'}

# Maps Python module names to l2tbinaries packages.
_L2TBINARIES_PACKAGE_NAMES = {
    u'pyfwsi': u'libfwsi',
    u'pylnk': u'liblnk',
    u'pyolecf': u'libolecf',
    u'yaml': u'PyYAML'}

# Maps Python module names to PyPI projects.
_PYPI_PROJECT_NAMES = {
    u'pyfwsi': u'libfwsi-python',
    u'pylnk': u'liblnk-python',
    u'pyolecf': u'libolecf-python',
    u'yaml': u'PyYAML'}

# Maps Python module names to RPM packages.
_RPM_PACKAGE_NAMES = {
    u'pyfwsi': u'libfwsi-python',
    u'pylnk': u'liblnk-python',
    u'pyolecf': u'libolecf-python'}

_VERSION_SPLIT_REGEX = re.compile(r'\.|\-')


def _CheckPythonModule(
    module_name, version_attribute_name, minimum_version,
    is_required=True, maximum_version=None, verbose_output=True):
  """Checks the availability of a Python module.

  Args:
    module_name (str): name of the module.
    version_attribute_name (str): name of the attribute that contains
       the module version or method to retrieve the module version.
    is_required (Optional[bool]): True if the Python module is a required
        dependency.
    minimum_version (str): minimum required version.
    maximum_version (Optional[str]): maximum required version. Should only be
        used if there is a later version that is not supported.
    verbose_output (Optional[bool]): True if output should be verbose.

  Returns:
    bool: True if the Python module is available and conforms to
        the minimum required version, False otherwise.
  """
  module_object = _ImportPythonModule(module_name)
  if not module_object:
    if not is_required:
      print(u'[OPTIONAL]\tmissing: {0:s}.'.format(module_name))
      return True

    print(u'[FAILURE]\tmissing: {0:s}.'.format(module_name))
    return False

  if not version_attribute_name or not minimum_version:
    if verbose_output:
      print(u'[OK]\t\t{0:s}'.format(module_name))
    return True

  module_version = None
  if not version_attribute_name.endswith(u'()'):
    module_version = getattr(module_object, version_attribute_name, None)
  else:
    version_method = getattr(module_object, version_attribute_name[:-2], None)
    if version_method:
      module_version = version_method()

  if not module_version:
    print((
        u'[FAILURE]\tunable to determine version information '
        u'for: {0:s}').format(module_name))
    return False

  # Make sure the module version is a string.
  module_version = u'{0!s}'.format(module_version)

  # Split the version string and convert every digit into an integer.
  # A string compare of both version strings will yield an incorrect result.
  module_version_map = list(
      map(int, _VERSION_SPLIT_REGEX.split(module_version)))
  minimum_version_map = list(
      map(int, _VERSION_SPLIT_REGEX.split(minimum_version)))

  if module_version_map < minimum_version_map:
    print((
        u'[FAILURE]\t{0:s} version: {1!s} is too old, {2!s} or later '
        u'required.').format(module_name, module_version, minimum_version))
    return False

  if maximum_version:
    maximum_version_map = list(
        map(int, _VERSION_SPLIT_REGEX.split(maximum_version)))
    if module_version_map > maximum_version_map:
      print((
          u'[FAILURE]\t{0:s} version: {1!s} is too recent, {2!s} or earlier '
          u'required.').format(module_name, module_version, maximum_version))
      return False

  if verbose_output:
    print(u'[OK]\t\t{0:s} version: {1!s}'.format(module_name, module_version))

  return True


def _ImportPythonModule(module_name):
  """Imports a Python module.

  Args:
    module_name (str): name of the module.

  Returns:
    module: Python module or None if the module cannot be imported.
  """
  try:
    module_object = list(map(__import__, [module_name]))[0]
  except ImportError:
    return

  # If the module name contains dots get the upper most module object.
  if u'.' in module_name:
    for submodule_name in module_name.split(u'.')[1:]:
      module_object = getattr(module_object, submodule_name, None)

  return module_object


def CheckDependencies(verbose_output=True):
  """Checks the availability of the dependencies.

  Args:
    verbose_output (Optional[bool]): True if output should be verbose.

  Returns:
    bool: True if the dependencies are available, False otherwise.
  """
  print(u'Checking availability and versions of dependencies.')
  check_result = True

  for module_name, version_tuple in sorted(PYTHON_DEPENDENCIES.items()):
    if not _CheckPythonModule(
        module_name, version_tuple[0], version_tuple[1],
        maximum_version=version_tuple[2], verbose_output=verbose_output):
      check_result = False

  if check_result and not verbose_output:
    print(u'[OK]')

  print(u'')
  return check_result


def CheckModuleVersion(module_name):
  """Checks the version requirements of a module.

  Args:
    module_name (str): name of the module.

  Raises:
    ImportError: if the module does not exists or does not meet
        the version requirements.
  """
  try:
    module_object = list(map(__import__, [module_name]))[0]
  except ImportError:
    raise

  if module_name not in PYTHON_DEPENDENCIES:
    return

  version_attribute_name, minimum_version, maximum_version, _ = (
      PYTHON_DEPENDENCIES[module_name])

  module_version = None
  if not version_attribute_name.endswith(u'()'):
    module_version = getattr(module_object, version_attribute_name, None)
  else:
    version_method = getattr(module_object, version_attribute_name[:-2], None)
    if version_method:
      module_version = version_method()

  if not module_version:
    raise ImportError(u'Unable to determine version of module: {0:s}'.format(
        module_name))

  # Split the version string and convert every digit into an integer.
  # A string compare of both version strings will yield an incorrect result.
  module_version_map = list(
      map(int, _VERSION_SPLIT_REGEX.split(module_version)))
  minimum_version_map = list(
      map(int, _VERSION_SPLIT_REGEX.split(minimum_version)))

  if module_version_map < minimum_version_map:
    raise ImportError((
        u'Module: {0:s} version: {1!s} is too old, {2!s} or later '
        u'required.').format(module_name, module_version, minimum_version))

  if maximum_version:
    maximum_version_map = list(
        map(int, _VERSION_SPLIT_REGEX.split(maximum_version)))
    if module_version_map > maximum_version_map:
      raise ImportError((
          u'Module; {0:s} version: {1!s} is too recent, {2!s} or earlier '
          u'required.').format(module_name, module_version, maximum_version))


def CheckTestDependencies(verbose_output=True):
  """Checks the availability of the dependencies when running tests.

  Args:
    verbose_output (Optional[bool]): True if output should be verbose.

  Returns:
    bool: True if the dependencies are available, False otherwise.
  """
  if not CheckDependencies(verbose_output=verbose_output):
    return False

  print(u'Checking availability and versions of test dependencies.')
  for module_name, version_tuple in sorted(PYTHON_TEST_DEPENDENCIES.items()):
    if not _CheckPythonModule(
        module_name, version_tuple[0], version_tuple[1],
        is_required=version_tuple[3], maximum_version=version_tuple[2],
        verbose_output=verbose_output):
      return False

  return True


def GetDPKGDepends(exclude_version=False):
  """Retrieves the DPKG control file installation requirements.

  Args:
    exclude_version (Optional[bool]): True if the version should be excluded
        from the dependency definitions.

  Returns:
    list[str]: dependency definitions for requires for DPKG control file.
  """
  requires = []
  for module_name, version_tuple in sorted(PYTHON_DEPENDENCIES.items()):
    module_version = version_tuple[1]

    # Map the import name to the DPKG package name.
    module_name = _DPKG_PACKAGE_NAMES.get(
        module_name, u'python-{0:s}'.format(module_name))
    if module_name == u'python-libs':
      # Override the python-libs version since it does not match
      # the sqlite3 version.
      module_version = None

    if exclude_version or not module_version:
      requires.append(module_name)
    else:
      requires.append(u'{0:s} (>= {1!s})'.format(module_name, module_version))

  return sorted(requires)


def GetL2TBinaries():
  """Retrieves the l2tbinaries requirements.

  Returns:
    list[str]: dependency definitions for l2tbinaries.
  """
  requires = []
  for module_name, _ in sorted(PYTHON_DEPENDENCIES.items()):
    # Map the import name to the l2tbinaries package name.
    module_name = _L2TBINARIES_PACKAGE_NAMES.get(module_name, module_name)

    requires.append(module_name)

  return sorted(requires)


def GetInstallRequires():
  """Retrieves the setup.py installation requirements.

  Returns:
    list[str]: dependency definitions for install_requires for setup.py.
  """
  install_requires = []
  for module_name, version_tuple in sorted(PYTHON_DEPENDENCIES.items()):
    module_version = version_tuple[1]
    maximum_version = version_tuple[2]

    # Map the import name to the PyPI project name.
    module_name = _PYPI_PROJECT_NAMES.get(module_name, module_name)
    if module_name == u'pysqlite':
      # Override the pysqlite version since it does not match
      # the sqlite3 version.
      module_version = None

    if not module_version:
      install_requires.append(module_name)
    elif not maximum_version:
      install_requires.append(u'{0:s} >= {1!s}'.format(
          module_name, module_version))
    else:
      install_requires.append(u'{0:s} >= {1!s},<= {2!s}'.format(
          module_name, module_version, maximum_version))

  return sorted(install_requires)


def GetRPMRequires(exclude_version=False):
  """Retrieves the setup.cfg RPM installation requirements.

  Args:
    exclude_version (Optional[bool]): True if the version should be excluded
        from the dependency definitions.

  Returns:
    list[str]: dependency definitions for requires for setup.cfg.
  """
  requires = []
  for module_name, version_tuple in sorted(PYTHON_DEPENDENCIES.items()):
    module_version = version_tuple[1]

    # Map the import name to the RPM package name.
    module_name = _RPM_PACKAGE_NAMES.get(
        module_name, u'python-{0:s}'.format(module_name))
    if module_name == u'python-libs':
      # Override the python-libs version since it does not match
      # the sqlite3 version.
      module_version = None

    if exclude_version or not module_version:
      requires.append(module_name)
    else:
      requires.append(u'{0:s} >= {1!s}'.format(module_name, module_version))

  return sorted(requires)
