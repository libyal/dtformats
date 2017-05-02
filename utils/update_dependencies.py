#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to update the dependencies in various configuration files."""

import os
import sys

# Change PYTHONPATH to include dtformats.
sys.path.insert(0, u'.')

import dtformats.dependencies  # pylint: disable=wrong-import-position


class AppveyorYmlWriter(object):
  """Appveyor.yml file writer."""

  _PATH = os.path.join(u'appveyor.yml')

  _FILE_HEADER = [
      u'environment:',
      u'  matrix:',
      u'    - PYTHON: "C:\\\\Python27"',
      u'',
      u'install:',
      (u'  - cmd: \'"C:\\Program Files\\Microsoft SDKs\\Windows\\v7.1\\Bin\\'
       u'SetEnv.cmd" /x86 /release\''),
      (u'  - ps: (new-object net.webclient).DownloadFile('
       u'\'https://bootstrap.pypa.io/get-pip.py\', '
       u'\'C:\\Projects\\get-pip.py\')'),
      (u'  - ps: (new-object net.webclient).DownloadFile('
       u'\'https://github.com/log2timeline/l2tbinaries/raw/master/win32/'
       u'pywin32-220.win32-py2.7.exe\', '
       u'\'C:\\Projects\\pywin32-220.win32-py2.7.exe\')'),
      (u'  - ps: (new-object net.webclient).DownloadFile('
       u'\'https://github.com/log2timeline/l2tbinaries/raw/master/win32/'
       u'WMI-1.4.9.win32.exe\', \'C:\\Projects\\WMI-1.4.9.win32.exe\')'),
      u'  - cmd: "%PYTHON%\\\\python.exe C:\\\\Projects\\\\get-pip.py"',
      (u'  - cmd: "%PYTHON%\\\\Scripts\\\\easy_install.exe '
       u'C:\\\\Projects\\\\pywin32-220.win32-py2.7.exe"'),
      (u'  - cmd: "%PYTHON%\\\\Scripts\\\\easy_install.exe '
       u'C:\\\\Projects\\\\WMI-1.4.9.win32.exe"'),
      (u'  - cmd: git clone https://github.com/log2timeline/l2tdevtools.git '
       u'&& move l2tdevtools ..\\')]

  _L2TDEVTOOLS_UPDATE = (
      u'  - cmd: mkdir dependencies && set PYTHONPATH=..\\l2tdevtools && '
      u'"%PYTHON%\\\\python.exe" ..\\l2tdevtools\\tools\\update.py '
      u'--download-directory dependencies --machine-type x86 '
      u'--msi-targetdir "%PYTHON%" {0:s}')

  _FILE_FOOTER = [
      u'',
      u'build: off',
      u'',
      u'test_script:',
      u'  - "%PYTHON%\\\\python.exe run_tests.py"',
      u'']

  def Write(self):
    """Writes an appveyor.yml file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = dtformats.dependencies.GetL2TBinaries()
    dependencies.extend([u'funcsigs', u'mock', u'pbr', u'six'])
    dependencies = u' '.join(dependencies)

    l2tdevtools_update = self._L2TDEVTOOLS_UPDATE.format(dependencies)
    file_content.append(l2tdevtools_update)

    file_content.extend(self._FILE_FOOTER)

    file_content = u'\n'.join(file_content)
    file_content = file_content.encode(u'utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class DPKGControlWriter(object):
  """Dpkg control file writer."""

  _PATH = os.path.join(u'config', u'dpkg', u'control')

  _MAINTAINER = u'Joachim Metz <joachim.metz@gmail.com>'

  _FILE_HEADER = [
      u'Source: dtformats',
      u'Section: python',
      u'Priority: extra',
      u'Maintainer: {0:s}'.format(_MAINTAINER),
      (u'Build-Depends: debhelper (>= 7), python-all (>= 2.7~), '
       u'python-setuptools, python3-all (>= 3.4~), python3-setuptools'),
      u'Standards-Version: 3.9.5',
      u'X-Python-Version: >= 2.7',
      u'X-Python3-Version: >= 3.4',
      u'Homepage: https://github.com/libyal/dtformats',
      u'']

  _PYTHON2_PACKAGE_HEADER = [
      u'Package: python-dtformats',
      u'Architecture: all']

  _PYTHON3_PACKAGE_HEADER = [
      u'Package: python3-dtformats',
      u'Architecture: all']

  _PYTHON_PACKAGE_FOOTER = [
      u'Description: Data formats (dtformats)',
      u' dtFormats is a collection of various file formats.',
      u'']

  def Write(self):
    """Writes a dpkg control file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)
    file_content.extend(self._PYTHON2_PACKAGE_HEADER)

    dependencies = dtformats.dependencies.GetDPKGDepends()
    dependencies.extend([u'${python:Depends}', u'${misc:Depends}'])
    dependencies = u', '.join(dependencies)

    file_content.append(u'Depends: {0:s}'.format(dependencies))

    file_content.extend(self._PYTHON_PACKAGE_FOOTER)
    file_content.extend(self._PYTHON3_PACKAGE_HEADER)

    dependencies = dependencies.replace(u'python', u'python3')

    file_content.append(u'Depends: {0:s}'.format(dependencies))

    file_content.extend(self._PYTHON_PACKAGE_FOOTER)

    file_content = u'\n'.join(file_content)
    file_content = file_content.encode(u'utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class RequirementsWriter(object):
  """Requirements.txt file writer."""

  _PATH = u'requirements.txt'

  _FILE_HEADER = [
      u'pip >= 7.0.0',
      u'pytest',
      u'mock']

  def Write(self):
    """Writes a requirements.txt file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = dtformats.dependencies.GetInstallRequires()
    for dependency in dependencies:
      file_content.append(u'{0:s}'.format(dependency))

    file_content = u'\n'.join(file_content)
    file_content = file_content.encode(u'utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class SetupCfgWriter(object):
  """Setup.cfg file writer."""

  _PATH = u'setup.cfg'

  _MAINTAINER = u'Joachim Metz <joachim.metz@gmail.com>'

  _FILE_HEADER = [
      u'[bdist_rpm]',
      u'release = 1',
      u'packager = {0:s}'.format(_MAINTAINER),
      u'doc_files = ACKNOWLEDGEMENTS',
      u'            AUTHORS',
      u'            LICENSE',
      u'            README',
      u'build_requires = python-setuptools']

  def Write(self):
    """Writes a setup.cfg file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = dtformats.dependencies.GetRPMRequires()
    for index, dependency in enumerate(dependencies):
      if index == 0:
        file_content.append(u'requires = {0:s}'.format(dependency))
      else:
        file_content.append(u'           {0:s}'.format(dependency))

    file_content = u'\n'.join(file_content)
    file_content = file_content.encode(u'utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class TravisBeforeInstallScriptWriter(object):
  """Travis-CI install.sh file writer."""

  _PATH = os.path.join(u'config', u'travis', u'install.sh')

  _FILE_HEADER = [
      u'#!/bin/bash',
      u'#',
      u'# Script to set up Travis-CI test VM.',
      u'',
      (u'COVERALL_DEPENDENCIES="python-coverage python-coveralls '
       u'python-docopt";'),
      u'']

  _FILE_FOOTER = [
      u'',
      u'# Exit on error.',
      u'set -e;',
      u'',
      u'if test `uname -s` = "Darwin";',
      u'then',
      u'\tgit clone https://github.com/log2timeline/l2tdevtools.git;',
      u'',
      u'\tmv l2tdevtools ../;',
      u'\tmkdir dependencies;',
      u'',
      (u'\tPYTHONPATH=../l2tdevtools ../l2tdevtools/tools/update.py '
       u'--download-directory=dependencies ${L2TBINARIES_DEPENDENCIES} '
       u'${L2TBINARIES_TEST_DEPENDENCIES};'),
      u'',
      u'elif test `uname -s` = "Linux";',
      u'then',
      u'\tsudo add-apt-repository ppa:gift/dev -y;',
      u'\tsudo apt-get update -q;',
      (u'\tsudo apt-get install -y ${COVERALL_DEPENDENCIES} '
       u'${PYTHON2_DEPENDENCIES} ${PYTHON2_TEST_DEPENDENCIES} '
       u'${PYTHON3_DEPENDENCIES} ${PYTHON3_TEST_DEPENDENCIES};'),
      u'fi',
      u'']

  def Write(self):
    """Writes an install.sh file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = dtformats.dependencies.GetL2TBinaries()
    dependencies = u' '.join(dependencies)
    file_content.append(u'L2TBINARIES_DEPENDENCIES="{0:s}";'.format(
        dependencies))

    file_content.append(u'')
    file_content.append(
        u'L2TBINARIES_TEST_DEPENDENCIES="funcsigs mock pbr six";')

    file_content.append(u'')

    dependencies = dtformats.dependencies.GetDPKGDepends(exclude_version=True)
    dependencies = u' '.join(dependencies)
    file_content.append(u'PYTHON2_DEPENDENCIES="{0:s}";'.format(dependencies))

    file_content.append(u'')
    file_content.append(u'PYTHON2_TEST_DEPENDENCIES="python-mock";')

    file_content.append(u'')

    dependencies = dtformats.dependencies.GetDPKGDepends(exclude_version=True)
    dependencies = u' '.join(dependencies)
    dependencies = dependencies.replace(u'python', u'python3')
    file_content.append(u'PYTHON3_DEPENDENCIES="{0:s}";'.format(dependencies))

    file_content.append(u'')
    file_content.append(u'PYTHON3_TEST_DEPENDENCIES="python3-mock";')

    file_content.extend(self._FILE_FOOTER)

    file_content = u'\n'.join(file_content)
    file_content = file_content.encode(u'utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


if __name__ == u'__main__':
  for writer_class in (
      AppveyorYmlWriter, DPKGControlWriter, RequirementsWriter, SetupCfgWriter,
      TravisBeforeInstallScriptWriter):
    writer = writer_class()
    writer.Write()
