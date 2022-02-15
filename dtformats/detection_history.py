# -*- coding: utf-8 -*-
"""Windows Defender scan DetectionHistory files."""

from dtformats import data_format


class WindowsDefenderScanDetectionHistoryFile(data_format.BinaryDataFile):
  """Windows Defender scan DetectionHistory file."""

  # Using a class constant significantly speeds up the time required to load
  # the dtFabric definition file.
  _FABRIC = data_format.BinaryDataFile.ReadDefinitionFile(
      'detection_history.yaml')

  _DEBUG_INFO_VALUE = [
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('data_type', 'Data type', '_FormatIntegerAsHexadecimal8'),
      ('data', 'Data', '_FormatDataInHexadecimal'),
      ('value_filetime', 'Value FILETIME', '_FormatIntegerAsFiletime'),
      ('value_guid', 'Value GUID', '_FormatUUIDAsString'),
      ('value_integer', 'Value integer', '_FormatIntegerAsDecimal'),
      ('value_string', 'Value string', '_FormatString'),
      ('alignment_padding', 'Alignment padding', '_FormatDataInHexadecimal')]

  _VALUE_DESCRIPTIONS = [
      {0: 'Threat identifier',
       1: 'Identifier'},
      {0: 'UnknownMagic1',
       1: 'Threat name',
       4: 'Category'},
      {0: 'UnknownMagic2',
       1: 'Resource type',
       2: 'Resource location',
       4: 'Threat data size',
       5: 'Threat data',
       6: 'Unknown date and time1',
       12: 'User/System account name1',
       18: 'Unknown date and time2',
       20: 'Unknown date and time3',
       24: 'User/System account name2'}]

  _CATEGORY_NAME = {
      0: 'INVALID',
      1: 'ADWARE',
      2: 'SPYWARE',
      3: 'PASSWORDSTEALER',
      4: 'TROJANDOWNLOADER',
      5: 'WORM',
      6: 'BACKDOOR',
      7: 'REMOTEACCESSTROJAN',
      8: 'TROJAN',
      9: 'EMAILFLOODER',
      10: 'KEYLOGGER',
      11: 'DIALER',
      12: 'MONITORINGSOFTWARE',
      13: 'BROWSERMODIFIER',
      14: 'COOKIE',
      15: 'BROWSERPLUGIN',
      16: 'AOLEXPLOIT',
      17: 'NUKER',
      18: 'SECURITYDISABLER',
      19: 'JOKEPROGRAM',
      20: 'HOSTILEACTIVEXCONTROL',
      21: 'SOFTWAREBUNDLER',
      22: 'STEALTHNOTIFIER',
      23: 'SETTINGSMODIFIER',
      24: 'TOOLBAR',
      25: 'REMOTECONTROLSOFTWARE',
      26: 'TROJANFTP',
      27: 'POTENTIALUNWANTEDSOFTWARE',
      28: 'ICQEXPLOIT',
      29: 'TROJANTELNET',
      30: 'FILESHARINGPROGRAM',
      31: 'MALWARE_CREATION_TOOL',
      32: 'REMOTE_CONTROL_SOFTWARE',
      33: 'TOOL',
      34: 'TROJAN_DENIALOFSERVICE',
      36: 'TROJAN_DROPPER',
      37: 'TROJAN_MASSMAILER',
      38: 'TROJAN_MONITORINGSOFTWARE',
      39: 'TROJAN_PROXYSERVER',
      40: 'VIRUS',
      42: 'KNOWN',
      43: 'UNKNOWN',
      44: 'SPP',
      45: 'BEHAVIOR',
      46: 'VULNERABILTIY',
      47: 'POLICY'}

  def _ReadValue(self, file_object, file_offset):
    """Reads the value.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the value relative to the start of the file.

    Returns:
      object: value.

    Raises:
      IOError: if the value cannot be read.
    """
    data_type_map = self._GetDataTypeMap('detection_history_value')

    value, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'value')

    if self._debug:
      self._DebugPrintStructureObject(value, self._DEBUG_INFO_VALUE)

    value_object = None
    if value.data_type in (
        0x00000000, 0x00000005, 0x00000006, 0x00000008):
      value_object = value.value_integer
    elif value.data_type == 0x0000000a:
      value_object = value.value_filetime
    elif value.data_type == 0x00000015:
      value_object = value.value_string
    elif value.data_type == 0x0000001e:
      value_object = value.value_guid
    elif value.data_type == 0x00000028:
      value_object = value.data

    return value_object

  def ReadFileObject(self, file_object):
    """Reads a Windows Defender scan DetectionHistory file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    value_objects = []

    file_offset = 0
    while file_offset < self._file_size:
      value_object = self._ReadValue(file_object, file_offset)
      value_objects.append(value_object)

      file_offset = file_object.tell()

    if self._debug:
      value_index_set = 0
      value_index = 0
      for value_object in value_objects:
        if value_object == 'Magic.Version:1.2':
          if value_index_set < 2:
            value_index_set += 1
          value_index = 0

        description = self._VALUE_DESCRIPTIONS[value_index_set].get(
            value_index, 'UNKNOWN_{0:d}_{1:d}'.format(
                value_index_set, value_index))

        if (value_index_set, value_index) == (1, 4):
          value_string = '{0!s} ({1:s})'.format(
              value_object, self._CATEGORY_NAME.get(value_object, 'UNKNOWN'))
        else:
          value_string = '{0!s}'.format(value_object)

        self._DebugPrintValue(description, value_string)

        value_index += 1
