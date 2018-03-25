# -*- coding: utf-8 -*-
"""Windows (Enhanced) Metafile Format (WMF and EMF) files."""

from __future__ import unicode_literals

import os

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import fabric as dtfabric_fabric

from dtformats import data_format
from dtformats import errors


class Record(object):
  """Windows (Enhanced) Metafile Format (WMF and EMF) record.

  Attributes:
    data_offset (int): record data offset.
    data_size (int): record data size.
    record_type (int): record type.
    size (int): record size.
  """

  def __init__(self, record_type, size, data_offset, data_size):
    """Initializes an EMF or WMF record.

    Args:
      record_type (int): record type.
      size (int): record size.
      data_offset (int): record data offset.
      data_size (int): record data size.
    """
    super(Record, self).__init__()
    self.data_offset = data_offset
    self.data_size = data_size
    self.record_type = record_type
    self.size = size


class EMFFile(data_format.BinaryDataFile):
  """Enhanced Metafile Format (EMF) file."""

  FILE_TYPE = 'Windows Enhanced Metafile'

  _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
      os.path.dirname(__file__), 'emf.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _RECORD_TYPE = _DATA_TYPE_FABRIC.CreateDataTypeMap('emf_record_type')

  _FILE_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap('emf_file_header')

  _FILE_HEADER_SIZE = _FILE_HEADER.GetByteSize()

  _RECORD_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap('emf_record_header')

  _RECORD_HEADER_SIZE = _RECORD_HEADER.GetByteSize()

  _EMF_SIGNATURE = b'FME\x20'

  # Here None represents that the record has no additional data.
  _EMF_RECORD_DATA_STRUCT_TYPES = {
      0x0018: _DATA_TYPE_FABRIC.CreateDataTypeMap('emf_settextcolor'),
      0x0025: _DATA_TYPE_FABRIC.CreateDataTypeMap('emf_selectobject')}

  _EMF_STOCK_OBJECT = _DATA_TYPE_FABRIC.CreateDataTypeMap('emf_stock_object')

  def _DebugPrintFileHeader(self, file_header):
    """Prints file header debug information.

    Args:
      file_header (emf_file_header): file header.
    """
    record_type_string = self._RECORD_TYPE.GetName(file_header.record_type)
    value_string = '0x{0:04x} ({1:s})'.format(
        file_header.record_type, record_type_string or 'UNKNOWN')
    self._DebugPrintValue('Record type', value_string)

    value_string = '{0:d}'.format(file_header.record_size)
    self._DebugPrintValue('Record size', value_string)

    value_string = '0x{0:04x}'.format(file_header.signature)
    self._DebugPrintValue('Signature', value_string)

    value_string = '0x{0:04x}'.format(file_header.format_version)
    self._DebugPrintValue('Format version', value_string)

    value_string = '{0:d}'.format(file_header.file_size)
    self._DebugPrintValue('File size', value_string)

    value_string = '{0:d}'.format(file_header.number_of_records)
    self._DebugPrintValue('Number of records', value_string)

    value_string = '{0:d}'.format(file_header.number_of_handles)
    self._DebugPrintValue('Number of handles', value_string)

    value_string = '0x{0:04x}'.format(file_header.unknown1)
    self._DebugPrintValue('Unknown (reserved)', value_string)

    value_string = '{0:d}'.format(file_header.description_string_size)
    self._DebugPrintValue('Description string size', value_string)

    value_string = '0x{0:04x}'.format(file_header.description_string_offset)
    self._DebugPrintValue('Description string offset', value_string)

    self._DebugPrintText('\n')

  def _DebugPrintRecordHeader(self, record_header):
    """Prints record header debug information.

    Args:
      record_header (emf_record_header): record header.
    """
    record_type_string = self._RECORD_TYPE.GetName(record_header.record_type)
    value_string = '0x{0:04x} ({1:s})'.format(
        record_header.record_type, record_type_string or 'UNKNOWN')
    self._DebugPrintValue('Record type', value_string)

    value_string = '{0:d}'.format(record_header.record_size)
    self._DebugPrintValue('Record size', value_string)

    self._DebugPrintText('\n')

  def _ReadFileHeader(self, file_object):
    """Reads a file header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file header cannot be read.
    """
    file_offset = file_object.tell()
    file_header = self._ReadStructure(
        file_object, file_offset, self._FILE_HEADER_SIZE, self._FILE_HEADER,
        'file header')

    if self._debug:
      self._DebugPrintFileHeader(file_header)

    # TODO: check record type
    # TODO: check record size
    # TODO: check signature

  def _ReadRecord(self, file_object, file_offset):
    """Reads a record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data relative from the start of
          the file-like object.

    Raises:
      ParseError: if the record cannot be read.
    """
    record_header = self._ReadStructure(
        file_object, file_offset, self._RECORD_HEADER_SIZE, self._RECORD_HEADER,
        'record header')

    if self._debug:
      self._DebugPrintRecordHeader(record_header)

    data_offset = file_offset + self._RECORD_HEADER_SIZE
    data_size = record_header.record_size - self._RECORD_HEADER_SIZE

    if self._debug:
      self._ReadRecordData(
          file_object, record_header.record_type, data_size)

    return Record(
        record_header.record_type,
        record_header.record_size, data_offset, data_size)

  def _ReadRecordData(self, file_object, record_type, data_size):
    """Reads a record.

    Args:
      file_object (file): file-like object.
      record_type (int): record type.
      data_size (int): size of the record data.

    Raises:
      ParseError: if the record data cannot be read.
    """
    record_data = file_object.read(data_size)

    if self._debug and data_size > 0:
      self._DebugPrintData('Record data', record_data)

    # TODO: use lookup dict with callback.
    data_type_map = self._EMF_RECORD_DATA_STRUCT_TYPES.get(record_type, None)
    if not data_type_map:
      return

    try:
      record = data_type_map.MapByteStream(record_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          'Unable to parse record data with error: {0:s}').format(exception))

    if self._debug:
      if record_type == 0x0018:
        value_string = '0x{0:04x}'.format(record.color)
        self._DebugPrintValue('Color', value_string)

      elif record_type == 0x0025:
        stock_object_string = self._EMF_STOCK_OBJECT.GetName(
            record.object_identifier)

        if stock_object_string:
          value_string = '0x{0:08x} ({1:s})'.format(
              record.object_identifier, stock_object_string)
        else:
          value_string = '0x{0:08x}'.format(
              record.object_identifier)

        self._DebugPrintValue('Object identifier', value_string)

      self._DebugPrintText('\n')

  def ReadFileObject(self, file_object):
    """Reads a Enhanced Metafile Format (EMF) file-like object.

    Args:
      file_object (file): file-like object.
    """
    self._ReadFileHeader(file_object)

    file_offset = file_object.tell()
    while file_offset < self._file_size:
      record = self._ReadRecord(file_object, file_offset)

      file_offset += record.size


class WMFFile(data_format.BinaryDataFile):
  """Windows Metafile Format (WMF) file."""

  FILE_TYPE = 'Windows Metafile'

  _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
      os.path.dirname(__file__), 'wmf.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  # https://msdn.microsoft.com/en-us/library/cc250370.aspx

  # TODO: merge with YAML file
  _TODO = b'\n'.join([
      b'---',
      b'name: wmf_record',
      b'type: structure',
      b'description: WMF record',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250387.aspx"]',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: record_size',
      b'  aliases: [RecordSize]',
      b'  description: Size of the record as number of 16-bit values',
      b'  data_type: uint32',
      # TODO: link to wmf_record_type
      b'- name: record_type',
      b'  aliases: [RecordFunction]',
      b'  data_type: uint16',
      b'- name: record_data',
      b'  aliases: [rdParam]',
      b'  type: stream',
      b'  element_data_type: byte',
      b'  element_data_size: (wmf_record.record_size * 2) - 6',
      b'---',
      b'name: wmf_restoredc_record',
      b'type: structure',
      b'description: Restores the playback device context',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250469.aspx"]',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: record_size',
      b'  data_type: uint32',
      b'- name: record_type',
      b'  data_type: uint16',
      # TODO: or support wmf_record_type.META_RESTOREDC
      b'  value: 0x0127',
      b'- name: number_of_saved_device_context',
      b'  data_type: uint16',
      b'---',
      b'name: wmf_setmapmode_record',
      b'type: structure',
      b'description: Defines the mapping mode',
      b'urls: ["https://msdn.microsoft.com/en-us/library/cc250483.aspx"]',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: record_size',
      b'  data_type: uint32',
      b'- name: record_type',
      b'  data_type: uint16',
      # TODO: or support wmf_record_type.META_SETMAPMODE
      b'  value: 0x0103',
      b'- name: map_mode',
      b'  data_type: uint16',
      # TODO: map to wmf_map_mode
  ])

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap('wmf_header')

  _HEADER_SIZE = _HEADER.GetByteSize()

  _PLACEABLE = _DATA_TYPE_FABRIC.CreateDataTypeMap('wmf_placeable')

  _PLACEABLE_SIZE = _PLACEABLE.GetByteSize()

  _RECORD_TYPE = _DATA_TYPE_FABRIC.CreateDataTypeMap('wmf_record_type')

  _RECORD_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap('wmf_record_header')

  _RECORD_HEADER_SIZE = _RECORD_HEADER.GetByteSize()

  _WMF_PLACEABLE_SIGNATURE = b'\xd7\xcd\xc6\x9a'

  _MAP_MODE = _DATA_TYPE_FABRIC.CreateDataTypeMap('wmf_map_mode')

  _STRETCH_MODE = _DATA_TYPE_FABRIC.CreateDataTypeMap('wmf_stretch_mode')

  # record_size == ((record_type >> 8) + 3)
  # DIB: https://msdn.microsoft.com/en-us/library/cc250593.aspx

  # Here None represents that the record has no additional data.
  _WMF_RECORD_DATA_STRUCT_TYPES = {
      0x0000: None,
      0x001e: None,
      0x0103: _DATA_TYPE_FABRIC.CreateDataTypeMap('wmf_setmapmode'),
      0x0107: _DATA_TYPE_FABRIC.CreateDataTypeMap('wmf_setstretchbltmode'),
      0x0127: _DATA_TYPE_FABRIC.CreateDataTypeMap('wmf_restoredc'),
      0x020b: _DATA_TYPE_FABRIC.CreateDataTypeMap('wmf_setwindoworg'),
      0x020c: _DATA_TYPE_FABRIC.CreateDataTypeMap('wmf_setwindowext'),
      0x0b41: _DATA_TYPE_FABRIC.CreateDataTypeMap('wmf_dibstretchblt')}

  # Reverse Polish wmf_raster_operation_code
  _WMF_RASTER_OPERATIONS = {
      0x00000042: 'BLACKNESS',
      0x00010289: 'DPSOO',
      0x00020C89: 'DPSON',
      0x000300AA: 'PSO',
      0x00040C88: 'SDPON',
      0x000500A9: 'DPO',
      0x00060865: 'PDSXNO',
      0x000702C5: 'PDSAO',
      0x00080F08: 'SDPNA',
      0x00090245: 'PDSXO',
      0x000A0329: 'DPN',
      0x000B0B2A: 'PSDNAO',
      0x000C0324: 'SPN',
      0x000D0B25: 'PDSNAO',
      0x000E08A5: 'PDSONO',
      0x000F0001: 'P',
      0x00100C85: 'PDSON',
      0x001100A6: 'NOTSRCERAS',
      0x00120868: 'SDPXNO',
      0x001302C8: 'SDPAO',
      0x00140869: 'DPSXNO',
      0x001502C9: 'DPSAO',
      0x00165CCA: 'PSDPSANAX',
      0x00171D54: 'SSPXDSXAX',
      0x00180D59: 'SPXPDX',
      0x00191CC8: 'SDPSANAX',
      0x001A06C5: 'PDSPAO',
      0x001B0768: 'SDPSXAX',
      0x001C06CA: 'PSDPAO',
      0x001D0766: 'DSPDXAX',
      0x001E01A5: 'PDSO',
      0x001F0385: 'PDSOA',
      0x00200F09: 'DPSNA',
      0x00210248: 'SDPXO',
      0x00220326: 'DSN',
      0x00230B24: 'SPDNAO',
      0x00240D55: 'SPXDSX',
      0x00251CC5: 'PDSPANAX',
      0x002606C8: 'SDPSAO',
      0x00271868: 'SDPSXNOX',
      0x00280369: 'DPSXA',
      0x002916CA: 'PSDPSAOXXN',
      0x002A0CC9: 'DPSANA',
      0x002B1D58: 'SSPXPDXAXN',
      0x002C0784: 'SPDSOAX',
      0x002D060A: 'PSDNOX',
      0x002E064A: 'PSDPXOX',
      0x002F0E2A: 'PSDNOAN',
      0x0030032A: 'PSNA',
      0x00310B28: 'SDPNAON',
      0x00320688: 'SDPSOOX',
      0x00330008: 'NOTSRCCOPY',
      0x003406C4: 'SPDSAOX',
      0x00351864: 'SPDSXNOX',
      0x003601A8: 'SDPOX',
      0x00370388: 'SDPOAN',
      0x0038078A: 'PSDPOAX',
      0x00390604: 'SPDNOX',
      0x003A0644: 'SPDSXOX',
      0x003B0E24: 'SPDNOAN',
      0x003C004A: 'PSX',
      0x003D18A4: 'SPDSONOX',
      0x003E1B24: 'SPDSNAOX',
      0x003F00EA: 'PSAN',
      0x00400F0A: 'PSDNAA',
      0x00410249: 'DPSXON',
      0x00420D5D: 'SDXPDXA',
      0x00431CC4: 'SPDSANAXN',
      0x00440328: 'SRCERASE',
      0x00450B29: 'DPSNAON',
      0x004606C6: 'DSPDAOX',
      0x0047076A: 'PSDPXAXN',
      0x00480368: 'SDPXA',
      0x004916C5: 'PDSPDAOXXN',
      0x004A0789: 'DPSDOAX',
      0x004B0605: 'PDSNOX',
      0x004C0CC8: 'SDPANA',
      0x004D1954: 'SSPXDSXOXN',
      0x004E0645: 'PDSPXOX',
      0x004F0E25: 'PDSNOAN',
      0x00500325: 'PDNA',
      0x00510B26: 'DSPNAON',
      0x005206C9: 'DPSDAOX',
      0x00530764: 'SPDSXAXN',
      0x005408A9: 'DPSONON',
      0x00550009: 'DSTINVERT',
      0x005601A9: 'DPSOX',
      0x000570389: 'DPSOAN',
      0x00580785: 'PDSPOAX',
      0x00590609: 'DPSNOX',
      0x005A0049: 'PATINVERT',
      0x005B18A9: 'DPSDONOX',
      0x005C0649: 'DPSDXOX',
      0x005D0E29: 'DPSNOAN',
      0x005E1B29: 'DPSDNAOX',
      0x005F00E9: 'DPAN',
      0x00600365: 'PDSXA',
      0x006116C6: 'DSPDSAOXXN',
      0x00620786: 'DSPDOAX',
      0x00630608: 'SDPNOX',
      0x00640788: 'SDPSOAX',
      0x00650606: 'DSPNOX',
      0x00660046: 'SRCINVERT',
      0x006718A8: 'SDPSONOX',
      0x006858A6: 'DSPDSONOXXN',
      0x00690145: 'PDSXXN',
      0x006A01E9: 'DPSAX',
      0x006B178A: 'PSDPSOAXXN',
      0x006C01E8: 'SDPAX',
      0x006D1785: 'PDSPDOAXXN',
      0x006E1E28: 'SDPSNOAX',
      0x006F0C65: 'PDXNAN',
      0x00700CC5: 'PDSANA',
      0x00711D5C: 'SSDXPDXAXN',
      0x00720648: 'SDPSXOX',
      0x00730E28: 'SDPNOAN',
      0x00740646: 'DSPDXOX',
      0x00750E26: 'DSPNOAN',
      0x00761B28: 'SDPSNAOX',
      0x007700E6: 'DSAN',
      0x007801E5: 'PDSAX',
      0x00791786: 'DSPDSOAXXN',
      0x007A1E29: 'DPSDNOAX',
      0x007B0C68: 'SDPXNAN',
      0x007C1E24: 'SPDSNOAX',
      0x007D0C69: 'DPSXNAN',
      0x007E0955: 'SPXDSXO',
      0x007F03C9: 'DPSAAN',
      0x008003E9: 'DPSAA',
      0x00810975: 'SPXDSXON',
      0x00820C49: 'DPSXNA',
      0x00831E04: 'SPDSNOAXN',
      0x00840C48: 'SDPXNA',
      0x00851E05: 'PDSPNOAXN',
      0x008617A6: 'DSPDSOAXX',
      0x008701C5: 'PDSAXN',
      0x008800C6: 'SRCAND',
      0x00891B08: 'SDPSNAOXN',
      0x008A0E06: 'DSPNOA',
      0x008B0666: 'DSPDXOXN',
      0x008C0E08: 'SDPNOA',
      0x008D0668: 'SDPSXOXN',
      0x008E1D7C: 'SSDXPDXAX',
      0x008F0CE5: 'PDSANAN',
      0x00900C45: 'PDSXNA',
      0x00911E08: 'SDPSNOAXN',
      0x009217A9: 'DPSDPOAXX',
      0x009301C4: 'SPDAXN',
      0x009417AA: 'PSDPSOAXX',
      0x009501C9: 'DPSAXN',
      0x00960169: 'DPSXX',
      0x0097588A: 'PSDPSONOXX',
      0x00981888: 'SDPSONOXN',
      0x00990066: 'DSXN',
      0x009A0709: 'DPSNAX',
      0x009B07A8: 'SDPSOAXN',
      0x009C0704: 'SPDNAX',
      0x009D07A6: 'DSPDOAXN',
      0x009E16E6: 'DSPDSAOXX',
      0x009F0345: 'PDSXAN',
      0x00A000C9: 'DPA',
      0x00A11B05: 'PDSPNAOXN',
      0x00A20E09: 'DPSNOA',
      0x00A30669: 'DPSDXOXN',
      0x00A41885: 'PDSPONOXN',
      0x00A50065: 'PDXN',
      0x00A60706: 'DSPNAX',
      0x00A707A5: 'PDSPOAXN',
      0x00A803A9: 'DPSOA',
      0x00A90189: 'DPSOXN',
      0x00AA0029: 'D',
      0x00AB0889: 'DPSONO',
      0x00AC0744: 'SPDSXAX',
      0x00AD06E9: 'DPSDAOXN',
      0x00AE0B06: 'DSPNAO',
      0x00AF0229: 'DPNO',
      0x00B00E05: 'PDSNOA',
      0x00B10665: 'PDSPXOXN',
      0x00B21974: 'SSPXDSXOX',
      0x00B30CE8: 'SDPANAN',
      0x00B4070A: 'PSDNAX',
      0x00B507A9: 'DPSDOAXN',
      0x00B616E9: 'DPSDPAOXX',
      0x00B70348: 'SDPXAN',
      0x00B8074A: 'PSDPXAX',
      0x00B906E6: 'DSPDAOXN',
      0x00BA0B09: 'DPSNAO',
      0x00BB0226: 'MERGEPAINT',
      0x00BC1CE4: 'SPDSANAX',
      0x00BD0D7D: 'SDXPDXAN',
      0x00BE0269: 'DPSXO',
      0x00BF08C9: 'DPSANO',
      0x00C000CA: 'MERGECOPY',
      0x00C11B04: 'SPDSNAOXN',
      0x00C21884: 'SPDSONOXN',
      0x00C3006A: 'PSXN',
      0x00C40E04: 'SPDNOA',
      0x00C50664: 'SPDSXOXN',
      0x00C60708: 'SDPNAX',
      0x00C707AA: 'PSDPOAXN',
      0x00C803A8: 'SDPOA',
      0x00C90184: 'SPDOXN',
      0x00CA0749: 'DPSDXAX',
      0x00CB06E4: 'SPDSAOXN',
      0x00CC0020: 'SRCCOPY',
      0x00CD0888: 'SDPONO',
      0x00CE0B08: 'SDPNAO',
      0x00CF0224: 'SPNO',
      0x00D00E0A: 'PSDNOA',
      0x00D1066A: 'PSDPXOXN',
      0x00D20705: 'PDSNAX',
      0x00D307A4: 'SPDSOAXN',
      0x00D41D78: 'SSPXPDXAX',
      0x00D50CE9: 'DPSANAN',
      0x00D616EA: 'PSDPSAOXX',
      0x00D70349: 'DPSXAN',
      0x00D80745: 'PDSPXAX',
      0x00D906E8: 'SDPSAOXN',
      0x00DA1CE9: 'DPSDANAX',
      0x00DB0D75: 'SPXDSXAN',
      0x00DC0B04: 'SPDNAO',
      0x00DD0228: 'SDNO',
      0x00DE0268: 'SDPXO',
      0x00DF08C8: 'SDPANO',
      0x00E003A5: 'PDSOA',
      0x00E10185: 'PDSOXN',
      0x00E20746: 'DSPDXAX',
      0x00E306EA: 'PSDPAOXN',
      0x00E40748: 'SDPSXAX',
      0x00E506E5: 'PDSPAOXN',
      0x00E61CE8: 'SDPSANAX',
      0x00E70D79: 'SPXPDXAN',
      0x00E81D74: 'SSPXDSXAX',
      0x00E95CE6: 'DSPDSANAXXN',
      0x00EA02E9: 'DPSAO',
      0x00EB0849: 'DPSXNO',
      0x00EC02E8: 'SDPAO',
      0x00ED0848: 'SDPXNO',
      0x00EE0086: 'SRCPAINT',
      0x00EF0A08: 'SDPNOO',
      0x00F00021: 'PATCOPY',
      0x00F10885: 'PDSONO',
      0x00F20B05: 'PDSNAO',
      0x00F3022A: 'PSNO',
      0x00F40B0A: 'PSDNAO',
      0x00F50225: 'PDNO',
      0x00F60265: 'PDSXO',
      0x00F708C5: 'PDSANO',
      0x00F802E5: 'PDSAO',
      0x00F90845: 'PDSXNO',
      0x00FA0089: 'DPO',
      0x00FB0A09: 'PATPAINT',
      0x00FC008A: 'PSO',
      0x00FD0A0A: 'PSDNOO',
      0x00FE02A9: 'DPSOO',
      0x00FF0062: 'WHITENESS'}

  def _DebugPrintHeader(self, file_header):
    """Prints header debug information.

    Args:
      file_header (wmf_header): file header.
    """
    value_string = '0x{0:04x}'.format(file_header.file_type)
    self._DebugPrintValue('File type', value_string)

    value_string = '{0:d}'.format(file_header.record_size)
    self._DebugPrintValue('Record size', value_string)

    value_string = '{0:d}'.format(file_header.format_version)
    self._DebugPrintValue('Format version', value_string)

    value_string = '{0:d}'.format(file_header.file_size_lower)
    self._DebugPrintValue('File size lower', value_string)

    value_string = '{0:d}'.format(file_header.file_size_upper)
    self._DebugPrintValue('File size upper', value_string)

    value_string = '{0:d}'.format(file_header.maximum_number_of_objects)
    self._DebugPrintValue('Maximum number of object', value_string)

    value_string = '{0:d}'.format(file_header.largest_record_size)
    self._DebugPrintValue('Largest record size', value_string)

    value_string = '{0:d}'.format(file_header.number_of_records)
    self._DebugPrintValue('Number of records', value_string)

    self._DebugPrintText('\n')

  def _DebugPrintPlaceable(self, placeable):
    """Prints placeable debug information.

    Args:
      placeable (wmf_placeable): placeable.
    """
    value_string = '0x{0:08x}'.format(placeable.signature)
    self._DebugPrintValue('Signature', value_string)

    value_string = '0x{0:04x}'.format(placeable.resource_handle)
    self._DebugPrintValue('Resource handle', value_string)

    self._DebugPrintData('Bounding box', placeable.bounding_box)

    value_string = '{0:d}'.format(placeable.number_of_units_per_inch)
    self._DebugPrintValue('Number of units per inch', value_string)

    value_string = '0x{0:08x}'.format(placeable.unknown1)
    self._DebugPrintValue('Unknown1', value_string)

    value_string = '0x{0:04x}'.format(placeable.checksum)
    self._DebugPrintValue('Checksum', value_string)

    self._DebugPrintText('\n')

  def _DebugPrintRecordHeader(self, record_header):
    """Prints record header debug information.

    Args:
      record_header (wmf_record_header): record header.
    """
    value_string = '{0:d} ({1:d} bytes)'.format(
        record_header.record_size, record_header.record_size * 2)
    self._DebugPrintValue('Record size', value_string)

    record_type_string = self._RECORD_TYPE.GetName(record_header.record_type)
    value_string = '0x{0:04x} ({1:s})'.format(
        record_header.record_type, record_type_string or 'UNKNOWN')
    self._DebugPrintValue('Record type', value_string)

    self._DebugPrintText('\n')

  def _ReadHeader(self, file_object):
    """Reads a header.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the header cannot be read.
    """
    file_offset = file_object.tell()
    file_header = self._ReadStructure(
        file_object, file_offset, self._HEADER_SIZE, self._HEADER, 'header')

    if self._debug:
      self._DebugPrintHeader(file_header)

    if file_header.file_type not in (1, 2):
      raise errors.ParseError('Unsupported file type: {0:d}'.format(
          file_header.file_type))

    if file_header.record_size != 9:
      raise errors.ParseError('Unsupported record size: {0:d}'.format(
          file_header.record_size))

  def _ReadPlaceable(self, file_object):
    """Reads a placeable.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the placeable cannot be read.
    """
    file_offset = file_object.tell()
    placeable = self._ReadStructure(
        file_object, file_offset, self._PLACEABLE_SIZE, self._PLACEABLE,
        'placeable')

    if self._debug:
      self._DebugPrintPlaceable(placeable)

  def _ReadRecord(self, file_object, file_offset):
    """Reads a record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the data relative from the start of
          the file-like object.

    Raises:
      ParseError: if the record cannot be read.
    """
    record_header = self._ReadStructure(
        file_object, file_offset, self._RECORD_HEADER_SIZE, self._RECORD_HEADER,
        'record header')

    if self._debug:
      self._DebugPrintRecordHeader(record_header)

    record_size = record_header.record_size * 2

    data_offset = file_offset + self._RECORD_HEADER_SIZE
    data_size = record_size - self._RECORD_HEADER_SIZE

    if self._debug:
      self._ReadRecordData(
          file_object, record_header.record_type, data_size)

    return Record(
        record_header.record_type, record_size, data_offset, data_size)

  def _ReadRecordData(self, file_object, record_type, data_size):
    """Reads a record.

    Args:
      file_object (file): file-like object.
      record_type (int): record type.
      data_size (int): size of the record data.

    Raises:
      ParseError: if the record cannot be read.
    """
    record_data = file_object.read(data_size)

    if self._debug and data_size > 0:
      self._DebugPrintData('Record data', record_data)

    # TODO: use lookup dict with callback.
    data_type_map = self._WMF_RECORD_DATA_STRUCT_TYPES.get(record_type, None)
    if not data_type_map:
      return

    try:
      record = data_type_map.MapByteStream(record_data)
    except dtfabric_errors.MappingError as exception:
      raise errors.ParseError((
          'Unable to parse record data with error: {0:s}').format(exception))

    if self._debug:
      if record_type == 0x0103:
        map_mode_string = self._MAP_MODE.GetName(record.map_mode)
        value_string = '0x{0:04x} ({1:s})'.format(
            record.map_mode, map_mode_string or 'UNKNOWN')
        self._DebugPrintValue('Map mode', value_string)

      elif record_type == 0x0107:
        stretch_mode_string = self._MAP_MODE.GetName(
            record.stretch_mode)
        value_string = '0x{0:04x} ({1:s})'.format(
            record.stretch_mode, stretch_mode_string or 'UNKNOWN')
        self._DebugPrintValue('Stretch mode', value_string)

      elif record_type == 0x0127:
        value_string = '{0:d}'.format(
            record.number_of_saved_device_context)
        self._DebugPrintValue('Number of saved device context', value_string)

      elif record_type in (0x020b, 0x020c):
        value_string = '{0:d}'.format(record.x_coordinate)
        self._DebugPrintValue('X coordinate', value_string)

        value_string = '{0:d}'.format(record.y_coordinate)
        self._DebugPrintValue('Y coordinate', value_string)

      elif record_type == 0x0b41:
        raster_operation_string = self._WMF_RASTER_OPERATIONS.get(
            record.raster_operation, 'UNKNOWN')
        value_string = '0x{0:08x} ({1:s})'.format(
            record.raster_operation, raster_operation_string)
        self._DebugPrintValue('Raster operation', value_string)

        value_string = '{0:d}'.format(record.source_height)
        self._DebugPrintValue('Source height', value_string)

        value_string = '{0:d}'.format(record.source_width)
        self._DebugPrintValue('Source width', value_string)

        value_string = '{0:d}'.format(record.source_x_coordinate)
        self._DebugPrintValue('Source X coordinate', value_string)

        value_string = '{0:d}'.format(record.source_y_coordinate)
        self._DebugPrintValue('Source Y coordinate', value_string)

        value_string = '{0:d}'.format(record.destination_height)
        self._DebugPrintValue('Destination height', value_string)

        value_string = '{0:d}'.format(record.destination_width)
        self._DebugPrintValue('Destination width', value_string)

        value_string = '{0:d}'.format(record.destination_x_coordinate)
        self._DebugPrintValue('Destination X coordinate', value_string)

        value_string = '{0:d}'.format(record.destination_y_coordinate)
        self._DebugPrintValue('Destination Y coordinate', value_string)

      self._DebugPrintText('\n')

  def ReadFileObject(self, file_object):
    """Reads a Windows Metafile Format (WMF) file-like object.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    try:
      signature = file_object.read(4)
      file_object.seek(-4, os.SEEK_CUR)
    except IOError as exception:
      raise errors.ParseError(
          'Unable to read file signature with error: {0!s}'.format(
              exception))

    if signature == self._WMF_PLACEABLE_SIGNATURE:
      self._ReadPlaceable(file_object)

    self._ReadHeader(file_object)

    file_offset = file_object.tell()
    while file_offset < self._file_size:
      record = self._ReadRecord(file_object, file_offset)

      file_offset += record.size
